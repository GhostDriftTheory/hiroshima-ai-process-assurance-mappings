# Hiroshima AI Process Assurance Mappings / 広島AIプロセス保証マッピング集

[![validate](https://github.com/GhostDriftTheory/hiroshima-ai-process-assurance-mappings/actions/workflows/validate.yml/badge.svg)](https://github.com/GhostDriftTheory/hiroshima-ai-process-assurance-mappings/actions/workflows/validate.yml)

> **継続拡張型の公開マッピング集です。** 広島AIプロセス（HAIP）の各行動を、個別の領域・システム・保証技術ごとに、明示的な義務、版固定された証拠、未解決事項及び機械検証可能な主張境界へ対応付けます。
>
> This is an extensible collection of independently scoped mappings. Each profile has its own evidence and claim boundaries; one profile does not expand the coverage of another.

本リポジトリは株式会社AIアシュアランス（AI Assurance, Inc.、旧称：GhostDrift Mathematical Institute）による民間の技術成果です。G7、日本政府、OECD又はHAIPの公式プロジェクト、認証制度若しくは規制承認ではありません。

## 公開Profile / Published profiles

| Profile | 対象 / Scope | 状態 |
|---|---|---|
| [`coldchain-handoff`](profiles/coldchain-handoff/README.md) | 医薬品2〜8℃コールドチェーンの引渡し判断。コールドチェーンPoCを主実装証拠、Evaluation OSを別建てのメタ保証として扱う。 | Published |
| [`civic-ai-answer-adoption`](profiles/civic-ai-answer-adoption/README.md) | 自治体AIの回答案を、資料・相談条件・根拠との対応に基づいて職員確認用に採用できるかを検証する。 | Published |
| [`civic-ai-privacy`](profiles/civic-ai-privacy/README.md) | 合成データの模擬送信と出力採用について、目的・権限・送信先・累積開示などの条件を検証する。 | Published |
| [`civic-ai-lifecycle`](profiles/civic-ai-lifecycle/README.md) | 派生情報への利用条件の承継・限定変更・継続利用と、指定した管理範囲の業務利用終了を検証する。 | Published |

新しいマッピングは、既存Profileへ証拠を混ぜ込まず、`profiles/<slug>/`へ独立して追加します。Profile間のカバレッジは合算せず、全体のHAIP適合点・認証点も作りません。

## 公開Profileの更新方法

### 既存Profileを更新

1. 原則、正本の`profiles/<slug>/profile.toml`だけ編集
2. 公開説明まで変わる場合だけ、同じフォルダの`README.md`も更新
3. 確認：`python validate.py --profile <slug>`

### 新しいProfileを追加

```bash
python validate.py --init <new-slug>
```

これで安全側の下書き2ファイルが作られます。その2ファイルを編集し、このREADMEの公開Profile表へ1行追加して、`python validate.py`を実行します。

生成済みHTML、CSV、JSONレポート、マニフェスト、複数スキーマ、Pythonパッケージは置きません。通常の更新対象は、Profileごとの`profile.toml`一つ、必要な場合だけ同フォルダの`README.md`です。

## 最小構成

```text
README.md
NOTICE.md
validate.py
.github/workflows/validate.yml
data/haip_actions.toml
formal/FORMAL_MODEL.md
profiles/
  README.md
  _template/
    README.md
    profile.toml
  coldchain-handoff/
    README.md
    profile.toml
  civic-ai-answer-adoption/
    README.md
    profile.toml
  civic-ai-privacy/
    README.md
    profile.toml
  civic-ai-lifecycle/
    README.md
    profile.toml
```

**公開版は全17ファイルです。** 新しいProfileを1件増やすたびに増えるのは2ファイルだけです。

## 検証

Python 3.11以上、外部ライブラリ不要です。

```bash
python validate.py
python validate.py --profile coldchain-handoff
```

検証器は、証拠のない`DIRECT`、重要な不足を残した`DIRECT`、メタ保証の役割越境、Reporting v2への過大な証拠利用、Profile間の合算及び主要な禁止主張を拒否します。結果はファイル生成せず端末へ表示するため、生成物の更新作業はありません。

## マッピングの基本形

```text
HAIP action
  → profile-specific obligation
  → version-pinned evidence
  → DIRECT / PARTIAL / SUPPORTING_ONLY / NOT_COVERED / NOT_ASSESSED / NOT_APPLICABLE
  → permitted claim + explicit gap
```

数理的な判定条件は [`formal/FORMAL_MODEL.md`](formal/FORMAL_MODEL.md) にあります。

## Repository name

```text
GhostDriftTheory/hiroshima-ai-process-assurance-mappings
```

`mappings`を複数形にし、単一PoC専用ではなく今後もProfileを追加する集合であることを名称自体に固定しています。

## English summary

Each profile is an independent verification unit with two maintained files: a bilingual `README.md` and a machine-readable `profile.toml`. The repository shares only the official HAIP action identifiers and a small standard-library validator. It does not aggregate profiles into a compliance score and does not provide OECD submission, certification, or eligibility tooling.

Copyright © 2026 AI Assurance, Inc. (formerly GhostDrift Mathematical Institute). See [`NOTICE.md`](NOTICE.md).

