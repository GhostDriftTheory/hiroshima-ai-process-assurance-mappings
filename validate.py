#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import time
from urllib.parse import quote, unquote, urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, HTTPRedirectHandler, build_opener
import re
import shutil
import sys
from datetime import date
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    print("Python 3.11 or newer is required.", file=sys.stderr)
    raise SystemExit(2)

ASSESSMENTS = {"DIRECT", "PARTIAL", "SUPPORTING_ONLY", "NOT_COVERED", "NOT_ASSESSED", "NOT_APPLICABLE"}
ROLES = {"PRIMARY_IMPLEMENTATION", "SUPPORTING_IMPLEMENTATION", "META_ASSURANCE"}
BRIDGE_STATUSES = {"TECHNICAL_EVIDENCE_INPUT", "LIMITED_CONTEXT_INPUT", "NO_PROFILE_COVERAGE"}
OFFICIAL_SECTIONS = {
    1: ("Risk identification and evaluation", "リスクの特定及び評価"),
    2: ("Risk management and information security", "リスク管理及び情報セキュリティ"),
    3: ("Transparency reporting on advanced AI systems", "高度AIシステムに関する透明性報告"),
    4: ("Organizational governance, incident management, and transparency", "組織ガバナンス、インシデント管理及び透明性"),
    5: ("Content authentication & provenance mechanisms", "コンテンツ認証及び来歴管理の仕組み"),
    6: ("Research & investment to advance AI safety & mitigate societal risks", "AI安全性の向上及び社会的リスク軽減のための研究・投資"),
    7: ("Advancing human and global interests", "人類及び世界全体の利益の推進"),
}
FORBIDDEN_WORKFLOW_KEYS = {
    "portal_question_id", "portal_question_text", "questionnaire_item", "response_text",
    "response_status", "approval_status", "approver", "owner", "raci", "preflight",
    "submission_pack", "submission_readiness", "eligibility_decision",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

class ValidationError(ValueError):
    pass

def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)

def unique(items: list[dict], key: str, label: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for item in items:
        value = item.get(key)
        if not isinstance(value, str) or not value:
            raise ValidationError(f"{label}: missing {key}")
        if value in out:
            raise ValidationError(f"{label}: duplicate {key}={value}")
        out[value] = item
    return out

def require_text(record: dict, keys: list[str], label: str) -> None:
    for key in keys:
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValidationError(f"{label}: {key} must be non-empty text")

def all_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from all_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from all_keys(nested)

def canonical_digest(actions: dict, profile: dict) -> str:
    payload = json.dumps({"actions": actions, "profile": profile}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def discover(root: Path) -> dict[str, Path]:
    result = {}
    profiles = root / "profiles"
    if not profiles.is_dir():
        raise ValidationError("profiles/ directory is required")
    for folder in sorted(profiles.iterdir()):
        if folder.is_dir() and not folder.name.startswith(("_", ".")):
            if not (folder / "profile.toml").is_file():
                raise ValidationError(f"{folder}: profile.toml is required; partial profile directory")
    for path in sorted(profiles.glob("*/profile.toml")):
        if path.parent.name.startswith("_"):
            continue
        data = load_toml(path)
        slug = data.get("slug")
        if not isinstance(slug, str) or not slug:
            raise ValidationError(f"{path}: missing slug")
        if slug != path.parent.name:
            raise ValidationError(f"{path}: slug must equal directory name")
        if slug in result:
            raise ValidationError(f"duplicate profile slug: {slug}")
        result[slug] = path
    if not result:
        raise ValidationError("no profiles found")
    return result

def validate_profile(root: Path, actions_doc: dict, path: Path) -> tuple[dict, collections.Counter]:
    p = load_toml(path)
    slug = p["slug"]
    require_text(p, ["schema_version", "profile_id", "version", "snapshot_date", "title_ja", "title_en", "publisher", "public_claim_ja", "public_claim_en"], slug)
    if p["schema_version"] != "haip-assurance-profile.v1":
        raise ValidationError(f"{slug}: unsupported schema_version")
    if not isinstance(p.get("published"), bool):
        raise ValidationError(f"{slug}: published must be true or false")
    if p.get("published") and "REPLACE_" in json.dumps(p, ensure_ascii=False):
        raise ValidationError(f"{slug}: published profile still contains REPLACE_ placeholders")
    if not (path.parent / "README.md").is_file():
        raise ValidationError(f"{slug}: README.md is required beside profile.toml")
    for phrase in p.get("prohibited_claim_phrases", []):
        phrase_cf = phrase.casefold()
        if phrase_cf in p["public_claim_ja"].casefold() or phrase_cf in p["public_claim_en"].casefold():
            raise ValidationError(f"{slug}: prohibited phrase in public claim: {phrase}")

    action_index = unique(actions_doc.get("actions", []), "id", "actions")
    if set(action_index) != {f"HAIP-A{i}" for i in range(1, 12)}:
        raise ValidationError("shared actions must be exactly HAIP-A1 through HAIP-A11")

    sources = unique(p.get("sources", []), "id", f"{slug}.sources")
    for source in sources.values():
        require_text(source, ["kind", "title"], f"{slug}.source.{source['id']}")
        commit = source.get("commit")
        if commit is not None and not SHA40.fullmatch(commit):
            raise ValidationError(f"{slug}.source.{source['id']}: commit must be full 40-char SHA")

    components = p.get("components", [])
    if not components:
        raise ValidationError(f"{slug}: at least one component is required")
    component_sources = set()
    meta_sources = set()
    for component in components:
        source_id = component.get("source_id")
        if source_id not in sources:
            raise ValidationError(f"{slug}: component references unknown source {source_id}")
        if component.get("role") not in ROLES:
            raise ValidationError(f"{slug}: invalid component role")
        if source_id in component_sources:
            raise ValidationError(f"{slug}: duplicate component source {source_id}")
        component_sources.add(source_id)
        if component["role"] == "META_ASSURANCE":
            meta_sources.add(source_id)

    evidence = unique(p.get("evidence", []), "id", f"{slug}.evidence")
    for item in evidence.values():
        require_text(item, ["title_ja", "title_en", "origin", "mode", "source_pin_id"], f"{slug}.evidence.{item['id']}")
        if item["source_pin_id"] not in sources:
            raise ValidationError(f"{slug}.evidence.{item['id']}: unknown source_pin_id")
        if item.get("origin") == "this_repository":
            local_path = item.get("path")
            if not isinstance(local_path, str) or not (root / local_path).is_file():
                raise ValidationError(f"{slug}.evidence.{item['id']}: local evidence path must exist")
        source_commit = sources[item["source_pin_id"]].get("commit")
        evidence_commit = item.get("commit")
        if source_commit and evidence_commit and source_commit != evidence_commit:
            raise ValidationError(f"{slug}.evidence.{item['id']}: commit differs from pinned source")
        if not isinstance(item.get("strength"), int) or not 0 <= item["strength"] <= 4:
            raise ValidationError(f"{slug}.evidence.{item['id']}: strength must be 0..4")
        digest = item.get("expected_sha256_lf")
        if digest is not None and not SHA256.fullmatch(digest):
            raise ValidationError(f"{slug}.evidence.{item['id']}: invalid expected_sha256_lf")

    obligations = p.get("obligations", [])
    obligation_index = unique(obligations, "obligation_id", f"{slug}.obligations")
    unique(obligations, "id", f"{slug}.mapping-records")
    if {o.get("haip_action_id") for o in obligations} != set(action_index):
        missing = set(action_index) - {o.get("haip_action_id") for o in obligations}
        extra = {o.get("haip_action_id") for o in obligations} - set(action_index)
        raise ValidationError(f"{slug}: every HAIP action must be represented; missing={sorted(missing)} extra={sorted(extra)}")

    boundaries = p.get("boundaries", {})
    meta_barred_actions = set(boundaries.get("meta_assurance_not_direct_for_actions", []))
    forced_outside = set(boundaries.get("forced_outside_profile_actions", []))
    meta_evidence = {eid for eid, item in evidence.items() if item["source_pin_id"] in meta_sources}
    counts = collections.Counter()

    for o in obligations:
        label = f"{slug}.{o['obligation_id']}"
        require_text(o, ["id", "obligation_ja", "obligation_en", "applicability", "assessment", "rationale_ja", "rationale_en"], label)
        assessment = o["assessment"]
        if assessment not in ASSESSMENTS:
            raise ValidationError(f"{label}: invalid assessment")
        counts[assessment] += 1
        direct = o.get("evidence_ids", [])
        supporting = o.get("supporting_evidence_ids", [])
        gaps = o.get("gaps", [])
        if not all(isinstance(x, str) for x in direct + supporting + gaps):
            raise ValidationError(f"{label}: evidence and gap lists must contain strings")
        if set(direct) & set(supporting):
            raise ValidationError(f"{label}: direct/supporting evidence overlap")
        unknown = (set(direct) | set(supporting)) - set(evidence)
        if unknown:
            raise ValidationError(f"{label}: unknown evidence {sorted(unknown)}")
        threshold = o.get("minimum_evidence_strength")
        if not isinstance(threshold, int) or not 0 <= threshold <= 4:
            raise ValidationError(f"{label}: minimum_evidence_strength must be 0..4")
        qualifying_external = [
            evidence[e]
            for e in direct
            if evidence[e]["origin"] not in {"official_policy", "this_repository"}
            and evidence[e]["strength"] >= threshold
        ]
        if assessment == "DIRECT":
            if not qualifying_external or gaps:
                raise ValidationError(f"{label}: DIRECT requires qualifying external evidence and no gaps")
        elif assessment == "PARTIAL":
            if not qualifying_external or not gaps:
                raise ValidationError(f"{label}: PARTIAL requires qualifying external evidence and explicit gaps")
        elif assessment == "SUPPORTING_ONLY":
            if not (direct or supporting) or not gaps:
                raise ValidationError(f"{label}: SUPPORTING_ONLY requires evidence and an explicit boundary")
        else:
            if direct or not gaps:
                raise ValidationError(f"{label}: {assessment} cannot declare direct evidence and must state a reason")
        if o["haip_action_id"] in meta_barred_actions and set(direct) & meta_evidence:
            raise ValidationError(f"{label}: META_ASSURANCE cannot directly prove this action")
        if o["haip_action_id"] in forced_outside and assessment != "NOT_APPLICABLE":
            raise ValidationError(f"{label}: forced outside-profile action must be NOT_APPLICABLE")

    reporting = p.get("reporting")
    if reporting:
        if FORBIDDEN_WORKFLOW_KEYS & set(all_keys(reporting)):
            raise ValidationError(f"{slug}: reporting bridge contains submission/workflow fields")
        official_source_id = reporting.get("official_source_id")
        if official_source_id not in sources or sources[official_source_id].get("kind") != "official_reporting_framework":
            raise ValidationError(f"{slug}: reporting.official_source_id must reference the official reporting framework")
        sections = reporting.get("sections", [])
        if [s.get("section_number") for s in sections] != list(range(1, 8)):
            raise ValidationError(f"{slug}: reporting bridge must contain sections 1..7 in order")
        meta_barred_sections = set(boundaries.get("meta_assurance_not_evidence_for_reporting_sections", []))
        forced_no_coverage = set(boundaries.get("reporting_sections_forced_no_profile_coverage", []))
        for s in sections:
            n = s["section_number"]
            label = f"{slug}.reporting.{n}"
            expected_en, expected_ja = OFFICIAL_SECTIONS[n]
            if s.get("title_en") != expected_en or s.get("title_ja") != expected_ja:
                raise ValidationError(f"{label}: official section title changed")
            if s.get("bridge_status") not in BRIDGE_STATUSES:
                raise ValidationError(f"{label}: invalid bridge_status")
            supported = set(s.get("supported_obligation_ids", []))
            gaps = set(s.get("known_gap_obligation_ids", []))
            ev = set(s.get("evidence_ids", []))
            if supported & gaps:
                raise ValidationError(f"{label}: supported and gap obligations overlap")
            if not supported <= set(obligation_index) or not gaps <= set(obligation_index):
                raise ValidationError(f"{label}: unknown obligation reference")
            if not ev <= set(evidence):
                raise ValidationError(f"{label}: unknown evidence reference")
            if any(obligation_index[x]["assessment"] not in {"DIRECT", "PARTIAL", "SUPPORTING_ONLY"} for x in supported):
                raise ValidationError(f"{label}: unsupported obligation labelled as supported")
            if any(obligation_index[x]["assessment"] not in {"NOT_COVERED", "NOT_ASSESSED", "NOT_APPLICABLE"} for x in gaps):
                raise ValidationError(f"{label}: covered obligation labelled as known gap")
            if s["bridge_status"] == "NO_PROFILE_COVERAGE" and (supported or ev):
                raise ValidationError(f"{label}: NO_PROFILE_COVERAGE cannot contain support or evidence")
            if n in forced_no_coverage and s["bridge_status"] != "NO_PROFILE_COVERAGE":
                raise ValidationError(f"{label}: section is forced to NO_PROFILE_COVERAGE")
            if n in meta_barred_sections and ev & meta_evidence:
                raise ValidationError(f"{label}: META_ASSURANCE evidence is barred from this section")
            require_text(s, [
                "profile_can_support_ja", "profile_can_support_en",
                "organisation_must_add_ja", "organisation_must_add_en",
                "illustrative_wording_ja", "illustrative_wording_en",
                "do_not_infer_ja", "do_not_infer_en",
            ], label)

    check_extended_profile(root, p, path, counts)
    return p, counts


# Additional integrity checks. These check declared metadata, not claim semantics.
ASSESSMENT_ORDER = (
    "DIRECT", "PARTIAL", "SUPPORTING_ONLY", "NOT_COVERED",
    "NOT_ASSESSED", "NOT_APPLICABLE",
)
REPOSITORY_URL = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\Z")
CI_MODES = {"CI_RUN", "CONTINUOUS_INTEGRATION_RUN"}
ORIGINS = {"external_repository", "official_policy", "this_repository"}
MAX_DOWNLOAD_BYTES = 8 * 1024 * 1024


def safe_relative_path(value: str, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValidationError(f"{label}: expected a nonempty relative POSIX path")
    if any(ord(c) < 32 for c in value) or any(x in {"", ".", ".."} for x in value.split("/")):
        raise ValidationError(f"{label}: unsafe relative path")
    if ":" in value.split("/")[0]:
        raise ValidationError(f"{label}: absolute or drive-qualified path is not allowed")
    return value


def repository_name(url: str, label: str) -> str:
    match = REPOSITORY_URL.fullmatch(url) if isinstance(url, str) else None
    if not match:
        raise ValidationError(f"{label}: expected https://github.com/OWNER/REPOSITORY")
    return match.group(1)


def equivalent_url(actual: str, expected: str, label: str) -> None:
    if not isinstance(actual, str):
        raise ValidationError(f"{label}: URL is required")
    a, b = urlsplit(actual), urlsplit(expected)
    if (a.scheme, a.netloc, unquote(a.path), a.query, a.fragment) != (
        b.scheme, b.netloc, unquote(b.path), b.query, b.fragment
    ):
        raise ValidationError(f"{label}: URL does not match its declared repository, commit and path/run")


def evidence_locator(item: dict, sources: dict) -> tuple[str, str, str]:
    """Bind external evidence to its registered source; never trust a raw URL alone."""
    label = item["id"]
    source = sources[item["source_pin_id"]]
    repo = repository_name(source.get("repository"), label)
    commit = source.get("commit")
    if not isinstance(commit, str) or not SHA40.fullmatch(commit):
        raise ValidationError(f"{label}: external evidence requires a full source commit SHA")
    if item.get("repository") != source["repository"] or item.get("commit") != commit:
        raise ValidationError(f"{label}: repository/commit differs from pinned source")
    if item.get("mode") in CI_MODES:
        run_id = item.get("run_id")
        if type(run_id) is not int or run_id <= 0 or item.get("conclusion") != "success":
            raise ValidationError(f"{label}: CI evidence requires a positive run_id and success conclusion")
        equivalent_url(item.get("url"), f"https://github.com/{repo}/actions/runs/{run_id}", label)
        if "workflow_path" in item:
            safe_relative_path(item["workflow_path"], label)
        return "run", f"https://api.github.com/repos/{repo}/actions/runs/{run_id}", repo
    path = safe_relative_path(item.get("path"), label)
    equivalent_url(item.get("url"), f"https://github.com/{repo}/blob/{commit}/{path}", label)
    raw = f"https://raw.githubusercontent.com/{repo}/{commit}/{quote(path, safe='/')}"
    if "raw_url" in item:
        equivalent_url(item["raw_url"], raw, label)
    return "file", raw, repo


def check_extended_profile(root: Path, p: dict, path: Path, counts: collections.Counter) -> None:
    sources = {s["id"]: s for s in p.get("sources", [])}
    if not SLUG.fullmatch(p["slug"]) or p["slug"] != path.parent.name:
        raise ValidationError(f"{path}: slug must equal the actual profile directory name")
    if p["published"]:
        date.fromisoformat(p["snapshot_date"])
        if "YYYY-MM-DD" in json.dumps(p, ensure_ascii=False):
            raise ValidationError(f"{p['slug']}: published profile contains an unset date")
        for component in p.get("components", []):
            source = sources[component["source_id"]]
            repository_name(source.get("repository"), component["source_id"])
            if not isinstance(source.get("commit"), str) or not SHA40.fullmatch(source["commit"]):
                raise ValidationError(f"{component['source_id']}: published implementation must be version-pinned")
    for e in p.get("evidence", []):
        if e["origin"] not in ORIGINS:
            raise ValidationError(f"{e['id']}: unknown evidence origin")
        if type(e["strength"]) is not int:
            raise ValidationError(f"{e['id']}: boolean is not an evidence-strength integer")
        if e["origin"] == "external_repository":
            evidence_locator(e, sources)
        if e["origin"] == "this_repository":
            local = (root / safe_relative_path(e.get("path"), e["id"])).resolve()
            if not local.is_relative_to(root.resolve()) or not local.is_file():
                raise ValidationError(f"{e['id']}: local evidence must be a file inside the repository")
        if "expected_size_bytes_lf" in e:
            if type(e["expected_size_bytes_lf"]) is not int or e["expected_size_bytes_lf"] < 0:
                raise ValidationError(f"{e['id']}: invalid LF-normalized byte count")
    for o in p["obligations"]:
        if type(o["minimum_evidence_strength"]) is not int:
            raise ValidationError(f"{o['obligation_id']}: boolean is not an evidence-strength threshold")
    if p["published"]:
        check_profile_readme(path.parent / "README.md", p, counts)


def check_profile_readme(path: Path, p: dict, counts: collections.Counter) -> None:
    text = path.read_text(encoding="utf-8")
    if "REPLACE_" in text:
        raise ValidationError(f"{path}: published README contains placeholders")
    declared = re.findall(r"^\|\s*`([A-Z_]+)`\s*\|\s*(\d+)\s*\|\s*$", text, re.M)
    declared = [(name, int(n)) for name, n in declared if name in ASSESSMENTS]
    if len(declared) != 6 or dict(declared) != {k: counts[k] for k in ASSESSMENT_ORDER}:
        raise ValidationError(f"{path}: coverage counts differ from profile.toml or are missing/duplicated")
    rows = re.findall(r"^\|\s*(\d+)\s*\|[^\n]*?\|\s*(\d+\s*/\s*\d+\s*/\s*\d+\s*/\s*\d+\s*/\s*\d+\s*/\s*\d+)\s*\|\s*$", text, re.M)
    if len(rows) != 11 or {int(n) for n, _ in rows} != set(range(1, 12)):
        raise ValidationError(f"{path}: expected exactly eleven per-action count rows")
    for n, values in rows:
        actual = collections.Counter(o["assessment"] for o in p["obligations"] if o["haip_action_id"] == f"HAIP-A{n}")
        if [int(x.strip()) for x in values.split("/")] != [actual[k] for k in ASSESSMENT_ORDER]:
            raise ValidationError(f"{path}: HAIP-A{n} counts differ from profile.toml")
    for slug in re.findall(r"python(?:3)?\s+validate\.py\s+--profile\s+([a-z0-9-]+)", text):
        if slug != p["slug"]:
            raise ValidationError(f"{path}: validation command uses the wrong profile slug")


def check_catalogue_and_links(root: Path, profiles: dict[str, Path]) -> None:
    home = root / "README.md"
    if not home.is_file():
        raise ValidationError("root README.md is required")
    public = {slug for slug, path in profiles.items() if load_toml(path).get("published") is True}
    text = home.read_text(encoding="utf-8")
    catalogue = re.findall(r"\]\(profiles/([a-z0-9-]+)/README\.md\)", text)
    if len(catalogue) != len(set(catalogue)) or set(catalogue) != public:
        raise ValidationError(f"root README catalogue differs from published profiles: missing={sorted(public-set(catalogue))} extra={sorted(set(catalogue)-public)}")
    paths = [home, root / "NOTICE.md", root / "profiles/README.md", root / "formal/FORMAL_MODEL.md"]
    paths += [p.parent / "README.md" for p in profiles.values()]
    for doc in paths:
        if not doc.is_file():
            raise ValidationError(f"required documentation is missing: {doc}")
        content = doc.read_text(encoding="utf-8")
        # The maintained documents use inline Markdown links. No external fetch here.
        for target in re.findall(r"\]\(([^\s)]+)\)", content):
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            dest = (doc.parent / unquote(parts.path)).resolve()
            if not dest.is_relative_to(root.resolve()) or not dest.is_file():
                raise ValidationError(f"{doc.relative_to(root)}: broken/unsafe internal link: {target}")


def normalized_text(raw: bytes) -> bytes:
    """Use UTF-8 and universal LF newlines; preserve all other bytes/text."""
    return raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


class SameHostRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        before, after = urlsplit(req.full_url), urlsplit(newurl)
        if after.scheme != "https" or before.netloc != after.netloc:
            raise ValidationError("cross-host or non-HTTPS redirect rejected")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class GitHubReader:
    """Read-only, bounded downloads. Tokens are sent only to api.github.com."""
    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout
        self.cache: dict[str, bytes] = {}
        self.opener = build_opener(SameHostRedirect())

    def __call__(self, url: str) -> bytes:
        parts = urlsplit(url)
        if parts.scheme != "https" or parts.netloc not in {"raw.githubusercontent.com", "api.github.com"} or parts.query or parts.fragment:
            raise ValidationError("remote checks permit only canonical HTTPS GitHub evidence URLs")
        if url in self.cache:
            return self.cache[url]
        headers = {"User-Agent": "HAIP-Assurance-Mappings-Integrity-Check", "Accept": "application/vnd.github+json" if parts.netloc == "api.github.com" else "text/plain"}
        if parts.netloc == "api.github.com":
            token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        for attempt in range(2):
            try:
                with self.opener.open(Request(url, headers=headers), timeout=self.timeout) as response:
                    payload = response.read(MAX_DOWNLOAD_BYTES + 1)
                if len(payload) > MAX_DOWNLOAD_BYTES:
                    raise ValidationError("remote evidence exceeds the 8 MiB download limit")
                self.cache[url] = payload
                return payload
            except HTTPError as exc:
                if attempt == 0 and exc.code in {429, 500, 502, 503, 504}:
                    time.sleep(1)
                    continue
                raise ValidationError(f"remote evidence HTTP {exc.code}: {url}") from exc
            except (URLError, TimeoutError, OSError) as exc:
                if attempt == 0:
                    time.sleep(1)
                    continue
                raise ValidationError(f"remote evidence unavailable: {url} ({type(exc).__name__})") from exc
        raise ValidationError("remote evidence was not retrieved")


def check_remote_profile(p: dict, reader, emit=print) -> collections.Counter:
    stats = collections.Counter()
    if not p["published"]:
        emit(f"SKIP remote profile={p['slug']} reason=UNPUBLISHED_DRAFT")
        return stats
    sources = {s["id"]: s for s in p["sources"]}
    for e in p.get("evidence", []):
        if e["origin"] != "external_repository":
            continue
        kind, url, repo = evidence_locator(e, sources)
        payload = reader(url)
        if kind == "run":
            data = json.loads(payload)
            expected = {"id": e["run_id"], "head_sha": e["commit"], "status": "completed", "conclusion": e["conclusion"]}
            if any(data.get(k) != v for k, v in expected.items()) or data.get("repository", {}).get("full_name") != repo:
                raise ValidationError(f"{e['id']}: remote CI repository, ID, commit, status or conclusion mismatch")
            equivalent_url(data.get("html_url"), e["url"], e["id"])
            if "workflow_path" in e and data.get("path", "").split("@", 1)[0] != e["workflow_path"]:
                raise ValidationError(f"{e['id']}: remote CI workflow path mismatch")
            stats["ci_runs"] += 1
            emit(f"PASS remote profile={p['slug']} evidence={e['id']} ci_metadata=VERIFIED head_sha={data['head_sha']}")
        else:
            content = normalized_text(payload)
            expected_hash = e.get("expected_sha256_lf")
            if expected_hash and hashlib.sha256(content).hexdigest() != expected_hash:
                raise ValidationError(f"{e['id']}: LF-normalized SHA-256 mismatch")
            if "expected_size_bytes_lf" in e and len(content) != e["expected_size_bytes_lf"]:
                raise ValidationError(f"{e['id']}: LF-normalized byte count mismatch")
            stats["files"] += 1
            stats["digest_verified" if expected_hash else "digest_not_declared"] += 1
            emit(f"PASS remote profile={p['slug']} evidence={e['id']} retrieved=YES sha256={'VERIFIED' if expected_hash else 'NOT_DECLARED'}")
    return stats

def run_self_tests(root: Path) -> int:
    """Regression tests use temporary copies and mocked remote bytes; no network."""
    import copy
    import tempfile
    import unittest
    from unittest.mock import patch

    class LocalRegressionTests(unittest.TestCase):
        def setUp(self):
            self.tmp = tempfile.TemporaryDirectory(prefix="haip-mappings-test-")
            self.addCleanup(self.tmp.cleanup)
            self.root = Path(self.tmp.name) / "repo"
            shutil.copytree(root, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))

        def validate(self):
            paths = discover(self.root)
            check_catalogue_and_links(self.root, paths)
            actions = load_toml(self.root / "data/haip_actions.toml")
            for path in paths.values():
                validate_profile(self.root, actions, path)
            return paths

        def test_complete_repository(self):
            self.assertGreaterEqual(len(self.validate()), 1)

        def test_missing_root_readme(self):
            (self.root / "README.md").unlink()
            with self.assertRaisesRegex(ValidationError, "root README"):
                self.validate()

        def test_slug_directory_mismatch(self):
            path = self.root / "profiles/civic-answer-adoption/profile.toml"
            path.write_text(path.read_text(encoding="utf-8").replace('slug = "civic-answer-adoption"', 'slug = "civic-ai-answer-adoption"'), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "slug must equal"):
                self.validate()

        def test_orphan_profile_directory(self):
            folder = self.root / "profiles/orphan-profile"
            folder.mkdir()
            (folder / "README.md").write_text("Orphan", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "profile.toml"):
                self.validate()

        def test_missing_profile_readme(self):
            (self.root / "profiles/civic-answer-adoption/README.md").unlink()
            with self.assertRaises(ValidationError):
                self.validate()

        def test_broken_internal_link(self):
            with (self.root / "README.md").open("a", encoding="utf-8") as handle:
                handle.write("\n[missing](not-a-file.md)\n")
            with self.assertRaisesRegex(ValidationError, "internal link"):
                self.validate()

        def test_catalogue_omission(self):
            path = self.root / "README.md"
            text = path.read_text(encoding="utf-8")
            text = "\n".join(line for line in text.splitlines() if "](profiles/civic-answer-adoption/README.md)" not in line)
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "catalogue"):
                self.validate()

        def test_wrong_documented_command(self):
            path = self.root / "profiles/civic-answer-adoption/README.md"
            path.write_text(path.read_text(encoding="utf-8").replace("--profile civic-answer-adoption", "--profile civic-ai-answer-adoption"), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "command"):
                self.validate()

        def test_summary_count_drift(self):
            path = self.root / "profiles/civic-answer-adoption/README.md"
            path.write_text(path.read_text(encoding="utf-8").replace("| `DIRECT` | 8 |", "| `DIRECT` | 9 |"), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "coverage counts"):
                self.validate()

        def test_action_count_drift(self):
            path = self.root / "profiles/civic-answer-adoption/README.md"
            path.write_text(path.read_text(encoding="utf-8").replace("2 / 0 / 0 / 1 / 0 / 0", "3 / 0 / 0 / 1 / 0 / 0", 1), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "counts differ"):
                self.validate()

        def test_new_draft_stays_unpublished(self):
            initialize_profile(self.root, "test-draft")
            path = self.root / "profiles/test-draft/profile.toml"
            data = load_toml(path)
            self.assertIs(data["published"], False)
            self.assertTrue(all(o["assessment"] == "NOT_ASSESSED" for o in data["obligations"]))
            self.assertTrue(all(s["bridge_status"] == "NO_PROFILE_COVERAGE" for s in data["reporting"]["sections"]))
            self.validate()

        def test_init_rejects_overwrite(self):
            with self.assertRaisesRegex(ValidationError, "already exists"):
                initialize_profile(self.root, "civic-answer-adoption")

        def test_init_rejects_traversal(self):
            with self.assertRaises(ValidationError):
                initialize_profile(self.root, "../escape")

        def mutate_profile(self, change):
            path = self.root / "profiles/civic-answer-adoption/profile.toml"
            data = copy.deepcopy(load_toml(path))
            change(data)
            actions = load_toml(self.root / "data/haip_actions.toml")
            with patch.dict(globals(), {"load_toml": lambda ignored: data}):
                validate_profile(self.root, actions, path)

        def test_direct_requires_qualifying_evidence(self):
            def change(data):
                next(o for o in data["obligations"] if o["assessment"] == "DIRECT")["evidence_ids"] = []
            with self.assertRaisesRegex(ValidationError, "DIRECT"):
                self.mutate_profile(change)

        def test_direct_cannot_hide_declared_gap(self):
            def change(data):
                next(o for o in data["obligations"] if o["assessment"] == "DIRECT")["gaps"] = ["unresolved"]
            with self.assertRaisesRegex(ValidationError, "DIRECT"):
                self.mutate_profile(change)

        def test_unknown_origin_cannot_qualify(self):
            def change(data):
                next(e for e in data["evidence"] if e["origin"] == "external_repository")["origin"] = "unknown_origin"
            with self.assertRaisesRegex(ValidationError, "origin"):
                self.mutate_profile(change)

        def test_no_coverage_cannot_claim_evidence(self):
            def change(data):
                data["reporting"]["sections"][4]["evidence_ids"] = [data["evidence"][0]["id"]]
            with self.assertRaisesRegex(ValidationError, "NO_PROFILE_COVERAGE"):
                self.mutate_profile(change)

    class RemoteRegressionTests(unittest.TestCase):
        def setUp(self):
            self.content = b"alpha\n"
            self.repo = "example-owner/example-repo"
            self.sha = "a" * 40
            self.e = {"id": "E", "origin": "external_repository", "source_pin_id": "S", "mode": "PUBLIC_DOCUMENT", "repository": f"https://github.com/{self.repo}", "commit": self.sha, "path": "README.md", "url": f"https://github.com/{self.repo}/blob/{self.sha}/README.md", "raw_url": f"https://raw.githubusercontent.com/{self.repo}/{self.sha}/README.md", "expected_sha256_lf": hashlib.sha256(self.content).hexdigest(), "expected_size_bytes_lf": len(self.content)}
            self.p = {"slug": "fixture", "published": True, "sources": [{"id": "S", "repository": self.e["repository"], "commit": self.sha}], "evidence": [self.e]}

        def check(self, content=None):
            return check_remote_profile(self.p, lambda url: self.content if content is None else content, emit=lambda line: None)

        def test_hash_and_length(self):
            self.assertEqual(self.check()["digest_verified"], 1)

        def test_crlf_normalization(self):
            self.assertEqual(self.check(b"alpha\r\n")["digest_verified"], 1)

        def test_hash_mismatch(self):
            with self.assertRaisesRegex(ValidationError, "SHA-256"):
                self.check(b"other\n")

        def test_size_mismatch(self):
            self.e["expected_size_bytes_lf"] += 1
            with self.assertRaisesRegex(ValidationError, "byte count"):
                self.check()

        def test_unhashed_is_not_reported_hash_verified(self):
            del self.e["expected_sha256_lf"]
            stats = self.check()
            self.assertEqual(stats["digest_not_declared"], 1)
            self.assertEqual(stats["digest_verified"], 0)

        def test_wrong_source_repository(self):
            self.e["repository"] = "https://github.com/other/repo"
            with self.assertRaisesRegex(ValidationError, "repository/commit"):
                self.check()

        def test_wrong_commit(self):
            self.e["commit"] = "b" * 40
            with self.assertRaises(ValidationError):
                self.check()

        def test_mutable_branch_is_not_a_pin(self):
            self.p["sources"][0]["commit"] = self.e["commit"] = "main"
            with self.assertRaisesRegex(ValidationError, "full source commit"):
                self.check()

        def test_wrong_raw_url(self):
            self.e["raw_url"] = self.e["raw_url"].replace(self.sha, "b" * 40)
            with self.assertRaisesRegex(ValidationError, "URL"):
                self.check()

        def test_remote_path_escape(self):
            self.e["path"] = "../outside"
            with self.assertRaisesRegex(ValidationError, "unsafe"):
                self.check()

        def test_non_github_source(self):
            self.p["sources"][0]["repository"] = "https://example.invalid/repo"
            with self.assertRaises(ValidationError):
                self.check()

        def test_reader_rejects_non_https(self):
            with self.assertRaises(ValidationError):
                GitHubReader()("http://api.github.com/repos/example/repo")

        def test_redirect_cannot_send_credentials_elsewhere(self):
            req = Request("https://api.github.com/repos/example/repo", headers={"Authorization": "Bearer fixture"})
            with self.assertRaises(ValidationError):
                SameHostRedirect().redirect_request(req, None, 302, "Found", {}, "https://example.invalid/collect")

        def ci(self):
            self.e.clear()
            self.e.update({"id": "E", "origin": "external_repository", "source_pin_id": "S", "mode": "CI_RUN", "repository": f"https://github.com/{self.repo}", "commit": self.sha, "run_id": 123, "conclusion": "success", "workflow_path": ".github/workflows/lean.yml", "url": f"https://github.com/{self.repo}/actions/runs/123"})
            return {"id": 123, "head_sha": self.sha, "status": "completed", "conclusion": "success", "repository": {"full_name": self.repo}, "html_url": self.e["url"], "path": self.e["workflow_path"]}

        def test_ci_metadata(self):
            self.assertEqual(self.check(json.dumps(self.ci()).encode())["ci_runs"], 1)

        def test_ci_rejects_wrong_binding_or_result(self):
            for field, value in (("id", 124), ("head_sha", "b" * 40), ("status", "in_progress"), ("conclusion", "failure"), ("repository", {"full_name": "other/repo"}), ("path", ".github/workflows/other.yml")):
                with self.subTest(field=field):
                    data = self.ci()
                    data[field] = value
                    with self.assertRaises(ValidationError):
                        self.check(json.dumps(data).encode())

        def test_unavailable_is_not_success(self):
            def unavailable(url):
                raise ValidationError("unavailable")
            with self.assertRaisesRegex(ValidationError, "unavailable"):
                check_remote_profile(self.p, unavailable, emit=lambda line: None)

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(LocalRegressionTests))
    suite.addTests(loader.loadTestsFromTestCase(RemoteRegressionTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1

def initialize_profile(root: Path, slug: str) -> None:
    if not SLUG.fullmatch(slug):
        raise ValidationError("--init SLUG must use lowercase kebab-case")
    source = root / "profiles/_template"
    target = root / "profiles" / slug
    if target.exists():
        raise ValidationError(f"profile already exists: {slug}")
    replacements = {"REPLACE_SLUG": slug, "REPLACE_PROFILE_ID": f"haip-profile.{slug}.v1", "YYYY-MM-DD": date.today().isoformat()}
    # Prepare and parse the draft before writing either maintained file.
    prepared = {}
    for name in ("README.md", "profile.toml"):
        body = (source / name).read_text(encoding="utf-8")
        for old, new in replacements.items():
            body = body.replace(old, new)
        prepared[name] = body
    data = tomllib.loads(prepared["profile.toml"])
    if data.get("slug") != slug or data.get("published") is not False:
        raise ValidationError("template must create an unpublished draft with the requested slug")
    target.mkdir(parents=False)
    try:
        for name, body in prepared.items():
            (target / name).write_text(body, encoding="utf-8", newline="\n")
    except OSError:
        shutil.rmtree(target)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check HAIP mapping integrity, not claim semantics or HAIP compliance")
    operations = parser.add_mutually_exclusive_group()
    operations.add_argument("--profile", help="validate one profile using its actual directory name")
    operations.add_argument("--init", metavar="SLUG", help="create a new unpublished draft from profiles/_template")
    operations.add_argument("--self-test", action="store_true", help="run regression tests using temporary copies and mocked remote data")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--check-remote", action="store_true", help="also retrieve pinned GitHub evidence and verify declared digests/CI metadata")
    parser.add_argument("--timeout", type=float, default=20.0, help="remote request timeout in seconds (1..120; default 20)")
    args = parser.parse_args(argv)
    if args.check_remote and (args.init or args.self_test):
        parser.error("--check-remote cannot be combined with --init or --self-test")
    if not 1 <= args.timeout <= 120:
        parser.error("--timeout must be in the range 1..120")
    root = args.root.resolve()
    try:
        if args.self_test:
            return run_self_tests(root)
        if args.init:
            initialize_profile(root, args.init)
            print(f"CREATED profiles/{args.init}/ (2 maintained files, published=false)")
            print("NEXT replace placeholders, review evidence and boundaries, then validate; publication is not automatic.")
            return 0
        actions = load_toml(root / "data/haip_actions.toml")
        profiles = discover(root)
        check_catalogue_and_links(root, profiles)
        if args.profile and args.profile not in profiles:
            raise ValidationError(f"unknown profile: {args.profile}; use its actual directory name")
        selected = {args.profile: profiles[args.profile]} if args.profile else profiles
        checked = []
        for slug, path in selected.items():
            p, counts = validate_profile(root, actions, path)
            checked.append(p)
            digest = canonical_digest(actions, p)
            print(f"PASS mapping profile={slug} published={str(p['published']).lower()} obligations={sum(counts.values())} evidence={len(p.get('evidence', []))} sha256={digest}")
            print("  D/P/S/U/N/A=" + "/".join(str(counts[x]) for x in ASSESSMENT_ORDER))
        if args.check_remote:
            reader = GitHubReader(args.timeout)
            stats = collections.Counter()
            for p in checked:
                stats.update(check_remote_profile(p, reader))
            print(f"PASS remote files={stats['files']} digest_verified={stats['digest_verified']} digest_not_declared={stats['digest_not_declared']} ci_runs={stats['ci_runs']}")
        else:
            print("REMOTE evidence_retrieval=NOT_REQUESTED (use --check-remote)")
        print(f"PASS profiles={len(selected)} portfolio_aggregation=DISABLED generated_files=NONE")
        print("SCOPE claim_semantics=NOT_CHECKED policy_content=NOT_FETCHED source_PoC=NOT_RUN Lean=NOT_RERUN certification=NOT_PROVIDED")
        return 0
    except KeyError as exc:
        print(f"FAIL missing required field: {exc}", file=sys.stderr)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
