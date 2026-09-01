#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import json
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

    return p, counts

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate independently scoped HAIP assurance mappings")
    parser.add_argument("--profile", help="validate one profile slug")
    parser.add_argument("--init", metavar="SLUG", help="create a new draft profile from profiles/_template")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.init:
            if not SLUG.fullmatch(args.init):
                raise ValidationError("--init SLUG must use lowercase kebab-case")
            source = root / "profiles" / "_template"
            target = root / "profiles" / args.init
            if target.exists():
                raise ValidationError(f"profile already exists: {args.init}")
            shutil.copytree(source, target)
            replacements = {
                "REPLACE_SLUG": args.init,
                "REPLACE_PROFILE_ID": f"haip-profile.{args.init}.v1",
                "YYYY-MM-DD": date.today().isoformat(),
            }
            for file in (target / "README.md", target / "profile.toml"):
                body = file.read_text(encoding="utf-8")
                for old, new in replacements.items():
                    body = body.replace(old, new)
                file.write_text(body, encoding="utf-8")
            print(f"CREATED profiles/{args.init}/ (2 maintained files)")
            print("NEXT replace remaining REPLACE_* text, add evidence, then run validation.")
            return 0
        actions = load_toml(root / "data" / "haip_actions.toml")
        profiles = discover(root)
        selected = {args.profile: profiles[args.profile]} if args.profile else profiles
        for slug, path in selected.items():
            p, counts = validate_profile(root, actions, path)
            digest = canonical_digest(actions, p)
            print(f"PASS profile={slug} obligations={sum(counts.values())} evidence={len(p.get('evidence', []))} sha256={digest}")
            print("  D/P/S/U/N/A=" + "/".join(str(counts[x]) for x in ["DIRECT", "PARTIAL", "SUPPORTING_ONLY", "NOT_COVERED", "NOT_ASSESSED", "NOT_APPLICABLE"]))
        print(f"PASS profiles={len(selected)} portfolio_aggregation=DISABLED generated_files=NONE")
        return 0
    except KeyError as exc:
        print(f"FAIL unknown profile: {exc}", file=sys.stderr)
    except (OSError, tomllib.TOMLDecodeError, ValidationError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
