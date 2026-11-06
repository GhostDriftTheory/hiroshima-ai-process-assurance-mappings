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
| [`civic-answer-adoption`](profiles/civic-answer-adoption/README.md) | 自治体AIの回答案を、資料・相談条件・根拠との対応に基づいて職員確認用に採用できるかを検証する。 | Published |
| [`civic-ai-privacy`](profiles/civic-ai-privacy/README.md) | 合成データの模擬送信と出力採用について、目的・権限・送信先・累積開示などの条件を検証する。 | Published |
| [`civic-ai-lifecycle`](profiles/civic-ai-lifecycle/README.md) | 派生情報への利用条件の承継・限定変更・継続利用と、指定した管理範囲の業務利用終了を検証する。 | Published |

新しいマッピングは、既存Profileへ証拠を混ぜ込まず、`profiles/<slug>/`へ独立して追加します。Profile間のカバレッジは合算せず、全体のHAIP適合点・認証点も作りません。

## 公開Profileの更新方法

### 既存Profileを更新

1. 原則、正本の`profiles/<slug>/profile.toml`だけ編集
2. 公開説明まで変わる場合だけ、同じフォルダの`README.md`も更新
3. 確認：`python validate.py --profile <slug>`。公開前は`python validate.py --check-remote`で全件を確認

### 新しいProfileを追加

```bash
python validate.py --init <new-slug>
```

これで安全側の下書き2ファイルが作られます。下書きのまま検証でき、公開判定は自動的に引き上がりません。内容・証拠・限界を確認した後で`published = true`に変更し、このREADMEの公開Profile表へ1行追加して、`python validate.py --check-remote`を実行します。

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
  civic-answer-adoption/
    README.md
    profile.toml
  civic-ai-privacy/
    README.md
    profile.toml
  civic-ai-lifecycle/
    README.md
    profile.toml
```

新しいProfileを1件増やすたびに増えるのは2ファイルだけです。

## 検証

Python 3.11以上、外部ライブラリ不要です。

```bash
# ローカル：構造・参照・公開説明の整合性
python validate.py

# 指定したProfileの検査（フォルダ名と同じ識別名を指定）
python validate.py --profile civic-answer-adoption

# 公開前：固定版の外部証拠・記載ハッシュ・参照CIも確認
python validate.py --check-remote

# 検証器自身の回帰テスト（ネットワーク接続なし）
python validate.py --self-test
```

**ローカル検査**は、全Profileの配置、ルートREADMEと公開一覧、内部リンク、判定件数、11行動・7報告セクション、証拠参照、版固定、判定に必要な明示条件及び役割分離を確認します。証拠のない`DIRECT`や明示的不足を残した`DIRECT`を拒否します。Profile内の数値は独立した技術義務の件数であり、適合率・認証点には変換しません。

**`--check-remote`**は追加で、公開Profileが参照するGitHubの固定コミットの証拠ファイルを取得し、SHA-256・バイト数が宣言されているものはLF改行正規化後に照合します。ハッシュ未宣言のファイルは取得確認と区別して表示します。参照CIは実行ID、対象リポジトリ、対象コミット、完了状態・結論を確認し、ワークフローパスが宣言されている場合はそれも照合します。取得不能・不一致を成功扱いにしません。通信先はGitHubの公開証拠取得に限定し、AI APIの呼出しは行いません。

**どちらの成功も、証拠の内容が個々の技術主張を実質的に証明するとの自動判定ではありません。** 根拠の妥当性・宣言された証拠強度・前提条件の適切さは別途評価が必要です。元PoCの実行、Leanの再ビルド、公式政策資料の内容確認、実運用監査は実行しません。`--check-remote`を付けない実行では外部証拠は未取得であることを明示します。

結果は端末へ表示します。検証により生成物や元PoCを書き換えることはありません。GitHub Actionsではローカル検査・回帰テスト・外部証拠確認を実行し、検査したコミットをログに残します。手動実行にも対応します。**GitHub Pagesのビルド成功は、この検証の成功とは別です。**

### 公開範囲と統合PoCとの区別

このマッピング集は、コールドチェーン1件・自治体AI3件の独立Profileを収録します。自治体AIの統合PoCを独立Profileとして収録したものではなく、各Profileの証拠を足し合わせて統合運転の保証を主張しません。統合PoCの成果を紹介する場合は、その別リポジトリの実証範囲と、このマッピングの範囲を分けて説明します。

各Profileの`snapshot_date`と固定コミットは証拠の参照時点です。説明・配置・発行者表記の修正を、実験の再実行日や新しい保証範囲へ読み替えません。回答採用Profileの実行用識別名は実フォルダに合わせた`civic-answer-adoption`です。既存の`profile_id`と参照元PoCのリポジトリ名は変更していません。

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

Each profile is an independent verification unit with two maintained files: a bilingual `README.md` and a machine-readable `profile.toml`. The repository shares the HAIP action definitions and a standard-library validator. Local validation checks structure and declared boundaries; optional remote validation checks pinned GitHub evidence, declared digests and referenced CI metadata. Neither mode evaluates claim semantics or reruns the underlying proofs and PoCs. It does not aggregate profiles into a compliance score and does not provide OECD submission, certification, or eligibility tooling.

Copyright © 2026 AI Assurance, Inc. (formerly GhostDrift Mathematical Institute). See [`NOTICE.md`](NOTICE.md).
