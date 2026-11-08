# 共同配送・参加拡張アシュアランス・マッピング  
## Joint Delivery Participation Assurance Mapping

[マッピング集トップ / Repository home](../../README.md) · [機械可読な正本 / Machine-readable source](profile.toml) · [数理モデル / Formal model](../../formal/FORMAL_MODEL.md)

> **株式会社オンザリンクスと株式会社AIアシュアランスの共同PoCを対象とする、共同配送領域の独立Profileです。** 広島AIプロセスの11行動を、既存荷主の条件を守った追加参加、共同承認、引渡し、採算との分離及び記録再検証に関する義務へ分解し、版固定された証拠と対応付けます。

本Profileの発行者は株式会社AIアシュアランス（AI Assurance, Inc.）です。HAIPへの全面適合、G7・日本政府・OECDによる認証、実運行への導入、本番運用準備又は独立第三者監査を意味しません。更新日：2026年11月8日。

## 構成要素の役割

- **Joint Delivery Participation Assurance PoC — `PRIMARY_IMPLEMENTATION`**  
  固定1ルート、運送会社1社、既存荷主A・B社、追加候補C社又はD社を対象とする合成データの参照実装。R01〜R08による参加判定、引渡しの追加検査、模擬許可の使用時再確認、採算の別判定及び記録再検証を扱います。

原PoCは**株式会社オンザリンクスと株式会社AIアシュアランスの共同PoC**です。本Profileはその公開技術証拠を対応付けるものです。実企業のデータ・契約・料金、実際の参加承認、配車・運行システムへの接続又は実配送を実証範囲に含めません。

### 参加・引渡し・採算を分けて確認

| 対象 | 公開PoCで確かめること |
|---|---|
| 追加参加 | 対象・版と既存貨物、容量・混載、納品条件、費用・役割の合意、開示範囲、共同承認、計画根拠、合成データ・模擬操作の範囲の8条件。納品時間帯と既存荷主の遅延上限は必須条件として検査する。 |
| 引渡し | 参加PASSに加え、送り手・受け手、数量・荷姿、双方の確認、計画との対応及び有効期間。参加PASSだけでは引渡しPASSにしない。 |
| 模擬許可の使用 | 記録・許可の対応、現在の計画・条件、時計の逆戻り及び使用済み状態を再検査する。承認撤回・失効・計画変更後は、過去の許可だけで通さない。 |
| 採算 | 追加売上から輸送・荷役・調整管理・システム・補償・機会損失の6費目を控除する。未確認原価は0にせず、黒字と参加許可を分ける。 |
| 再検証・共有 | 入力から判定・理由・採算を再計算する。共有用要約は許可された識別情報・判定項目だけを選別し、開示条件違反時は停止する。 |

集約順は`REJECT > HOLD > PASS`です。既知の違反はREJECT、不足のみならHOLD、全条件が成立した場合はPASSとなります。正しく保存されたHOLD・REJECTの記録は再検証に成功しますが、PASS又は現在の利用許可に変わるわけではありません。

[`JointDeliveryAssurance.lean`](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/JointDeliveryAssurance.lean)は44の名前付き定理を収録します。`participation_pass_requires_every_check`は参加に必要な全条件、`missing_receipt_blocks_handoff`は受領確認不足時の停止、`economics_cannot_change_participation`は採算との分離、`repeated_gate_is_blocked`は使用状態を保持した模擬ゲートの再使用停止を扱います。証明対象は定義済みLeanモデルです。観測値抽出、識別子・ハッシュの照合、JSON・暗号・OS・入出力及びPython・JavaScript全体の全入力に対する正しさを証明したものではありません。

原READMEの「Lean実コンパイル未確認」は2026年10月24日の確認環境についての記述です。本Profileは、**同じ固定コミットを対象として2026年11月7日に成功した[CI実行](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/actions/runs/42342121660)**を別の実行証拠として参照します。そのログは44定理のビルド・依存確認と、134入力・536の具体的一致命題の検査成功を記録しています。一般のモデル定理と有限入力での実装照合は区別します。

### AI接続実験の扱い

同じ固定コミットに、[API接続コード](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/joint_delivery_openai_experiment.py)と[24ケースの公開記録](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/openai_live_20261024T161205Z_00d42f.json)があります。記録上の参加判定はPASS 5件・HOLD 9件・REJECT 10件です。JD21ではAIの採用推奨を開示条件違反で拒否し、JD04では未確認到着時刻のAIによる補完を採用せず、JD32では参加・引渡しPASSと赤字を分けています。

本Profileの作成時に、公開された24件の入力・判定記録とアダプタ処理を固定実装でオフライン再計算し、全件及び集計の一致を確認しました。公開記録の実験時刻は2026年10月24日UTC（日本時間10月25日）です。今回の照合はAPIの再実行又はAPI応答の外部認証ではありません。現在のCIも、この別ファイルのAPI記録を自動再検証する構成ではありません。

この実験は`SUPPORTING_ONLY`の補助資料として扱います。採用された配送案の数値変更は0件であり、配送最適化の性能、実運行、実測収益又は各API出力の個別Lean証明は主張しません。

## 現在の証拠カバレッジ

| 判定 | 件数 |
|---|---:|
| `DIRECT` | 10 |
| `PARTIAL` | 0 |
| `SUPPORTING_ONLY` | 5 |
| `NOT_COVERED` | 11 |
| `NOT_ASSESSED` | 0 |
| `NOT_APPLICABLE` | 0 |

これはProfile内の義務件数であり、HAIP適合点、適合率、企業評価点又は認証点ではありません。`DIRECT`は記載した狭い技術義務についての判定であり、HAIP行動全体を満たすとの判定ではありません。

`D / P / S / U / N / A`は上表と同じ順序です。

| HAIP行動 | 概要 | D / P / S / U / N / A |
|---:|---|---:|
| 1 | AIライフサイクル全体でリスクを特定・評価・試験・文書化し、軽減する。 | 4 / 0 / 1 / 1 / 0 / 0 |
| 2 | 導入後の脆弱性、インシデント、新たなリスク及び誤用を特定し、軽減する。 | 0 / 0 / 1 / 1 / 0 / 0 |
| 3 | 能力、限界、適切な利用、評価及び重要なリスクを公開報告する。 | 1 / 0 / 0 / 1 / 0 / 0 |
| 4 | 安全情報を責任ある形で共有し、関係主体とインシデントを報告する。 | 1 / 0 / 0 / 1 / 0 / 0 |
| 5 | リスクベースのAIガバナンス及びリスク管理方針を策定・実施・開示・更新する。 | 1 / 0 / 0 / 1 / 0 / 0 |
| 6 | 堅牢な物理・サイバー・アクセス制御・内部脅威対策を実施する。 | 1 / 0 / 0 / 1 / 0 / 0 |
| 7 | 可能な場合、AI生成コンテンツの認証及び来歴機構を用いる。 | 0 / 0 / 0 / 1 / 0 / 0 |
| 8 | AIの安全・セキュリティ・信頼性及び社会的リスク軽減の研究・投資を優先する。 | 0 / 0 / 1 / 1 / 0 / 0 |
| 9 | グローバルヘルスを含む世界的課題及び人間の利益のため、責任あるAIを推進する。 | 0 / 0 / 1 / 1 / 0 / 0 |
| 10 | 相互運用可能な国際技術標準及びベストプラクティスを推進し、必要に応じて採用する。 | 0 / 0 / 1 / 1 / 0 / 0 |
| 11 | データ品質措置並びに個人データ及び知的財産の保護を実施する。 | 2 / 0 / 0 / 1 / 0 / 0 |

26義務の全文、証拠ID、閾値、根拠及び不足は [`profile.toml`](profile.toml) が正本です。他Profileの証拠で不足を埋めたり、カバレッジを合算したりしません。

## Reporting Framework v2.0との限定的ブリッジ

このProfileは、OECD Reporting Framework v2.0の完成回答、質問票複製、提出支援、参加資格判定又は承認ツールではありません。この技術証拠を各セクションへ補助的に利用できる範囲を示します。

| # | セクション | 状態 | このProfileから補助できること | 推論してはいけないこと |
|---:|---|---|---|---|
| 1 | リスクの特定及び評価 | `TECHNICAL_EVIDENCE_INPUT` | 固定合成条件の参加・引渡し検査、採算との分離、モデル証明、具体入力の実装照合及び補助的なAI接続記録。 | 実配送の安全性、AIの汎用信頼性、配送最適化性能、独立評価又は法令適合を推論しない。 |
| 2 | リスク管理及び情報セキュリティ | `TECHNICAL_EVIDENCE_INPUT` | 共同承認、現在条件の再確認、保持状態内の再使用停止、厳格な入力検査、限定要約及び記録再計算。 | 本番の防御能力、真正性、永続的な再使用防止、秘密保持又は全社リスク管理を推論しない。 |
| 3 | 高度AIシステムに関する透明性報告 | `TECHNICAL_EVIDENCE_INPUT` | PoCの目的・条件・操作・評価範囲・限界と、合成試験仕様・証明コード・再検証手順の公開。 | 完成したOECD報告、包括的モデルカード又は独立認証とみなさない。 |
| 4 | 組織ガバナンス、インシデント管理及び透明性 | `LIMITED_CONTEXT_INPUT` | 判断・未確認事項の記録、共同承認と役割の照合、模擬利用境界及び公開可能な評価方法の共有。 | 法的責任の確定、組織ガバナンス又は当局報告体制の実証を推論しない。 |
| 5 | コンテンツ認証及び来歴管理の仕組み | `NO_PROFILE_COVERAGE` | このProfileにAI生成コンテンツの認証・来歴機構の実装カバレッジはない。 | ハッシュ、API応答識別子又は再計算可能性を、署名・透かし・認証された来歴と同一視しない。 |
| 6 | AI安全性の向上及び社会的リスク軽減のための研究・投資 | `LIMITED_CONTEXT_INPUT` | 採用条件と模擬実行の分離に関する公開参照実装、形式モデル及びPython・ブラウザの相互照合方法。 | 定理件数や実装照合から、継続投資、国際標準適合又は任意企業への接続性を推論しない。 |
| 7 | 人類及び世界全体の利益の推進 | `LIMITED_CONTEXT_INPUT` | 既存荷主の条件を尊重し、追加荷主の受入れ条件と増分採算を確かめる共同配送の合成ユースケース。 | 実導入、利益実現、投資回収、工数削減、CO2削減又は商用化の成立を推論しない。 |

記載例、報告に利用する場合に組織側で別途示す必要がある事実及び証拠IDは [`profile.toml`](profile.toml) の`reporting.sections`に収録しています。

## 主要な版固定ソース

- [Joint Delivery Participation Assurance PoC](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/tree/dea7084dfd4b4ac9486c577ba2d2a625cf12de38)  
  `GhostDriftTheory/joint-delivery-participation-assurance`  
  commit `dea7084dfd4b4ac9486c577ba2d2a625cf12de38`
- [公開説明](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/README.md)・[参照実装](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/poc.py)・[合成条件と38ケース](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/cases.json)・[操作画面](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/index.html)・[Leanモデル](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/JointDeliveryAssurance.lean)
- [検査手順](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/.github/workflows/verify.yml)・[Lean版指定](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/lean-toolchain)・[ビルド設定](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/lakefile.toml)と、[同一コミットで成功した2026年11月7日のCI](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/actions/runs/42342121660)。CIの成功は独立第三者監査を意味しません。
- [AI接続コード](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/joint_delivery_openai_experiment.py)・[公開API実験記録](https://github.com/GhostDriftTheory/joint-delivery-participation-assurance/blob/dea7084dfd4b4ac9486c577ba2d2a625cf12de38/openai_live_20261024T161205Z_00d42f.json)。記録の作成時点と今回のオフライン照合を区別します。
- HAIP行動規範：[外務省掲載の公式PDF](https://www.mofa.go.jp/files/100573473.pdf)
- HAIP Reporting Framework v2.0：[OECD.AI公式情報](https://oecd.ai/en/transparency/overview)・[FAQ](https://oecd.ai/en/transparency/faq)。公式情報の確認日：2026年11月8日。共通行動定義は既存の2026年9月1日スナップショットを維持します。

外部証拠10ファイルには、UTF-8・LF改行正規化後のSHA-256とバイト数を宣言しています。元の実装・データ・証明は原リポジトリで管理し、本Profileへ複製しません。利用条件は原リポジトリの著作権・利用条件に従います。

模擬ゲートの再使用停止は保持した使用状態内の性質です。画面の再読込・ケース切替で状態は初期化され、永続化や複数端末間の排他は含みません。共有用要約の項目選別は匿名性・秘密保持・推測防止の証明ではありません。採算、初期費用回収及び工数は合成の仮定であり、実測値ではありません。

## 対外的に使える表現

> 株式会社オンザリンクスと株式会社AIアシュアランスの共同PoCを対象に、広島AIプロセスの一部行動を、共同配送への追加参加条件・共同承認・引渡し・採算との分離及び記録再検証の公開証拠へ対応付けた民間の技術成果。固定合成モデルの形式証明と実装照合を含み、公式認証、実運行への導入又は実測の事業効果を意味しない。

## 検証

マッピング集のルートで実行します。検証対象はこのマッピングの構造・参照・主張境界の整合性です。`--check-remote`は固定版ファイルのハッシュ・バイト数とCIメタデータも照合します。元PoCの実行検査、API実験又はLeanビルドをこれらのコマンドで再実行するものではありません。

```bash
python validate.py --profile joint-delivery-participation
python validate.py --profile joint-delivery-participation --check-remote
```

---

## English summary

This profile covers the **joint PoC of 株式会社オンザリンクス and AI Assurance, Inc. (株式会社AIアシュアランス)**. AI Assurance, Inc. publishes the mapping. The profile maps all eleven HAIP actions to 26 scoped obligations; it is an independent evidence unit within this collection.

The public reference implementation uses one fixed synthetic route, one carrier, existing shippers A/B, and candidate C or D. It checks eight participation conditions, additional handoff conditions, joint approvals, use-time conditions, retained-state duplicate use, strict input handling, limited participant summaries, and record replay. Delivery windows and existing-shipper delay limits remain mandatory. Contribution economics and simple payback calculations are separate from permission; positive economics cannot authorise a blocked plan, and a loss does not itself change participation eligibility.

Evidence is pinned to commit `dea7084dfd4b4ac9486c577ba2d2a625cf12de38`. The successful November 7 CI run checks the Lean build and dependencies of 44 theorems plus 134 projected inputs and 536 concrete equalities. It also checks Python/JavaScript record agreement and browser operation. The source README's earlier unconfirmed-Lean note describes its October 24 checking environment; the later pinned CI is separate execution evidence. Model proofs and finite implementation checks do not prove all-input correctness of the complete software stack or physical-world outcomes.

The published 24-case API experiment is supporting evidence with a separate API/text-parsing boundary. Its embedded records, adapter results, and summary were recomputed offline on November 8 and matched. Replay is not a new API call, provider authentication, or an individual Lean proof of an API output. The experiment records zero accepted numerical changes to proposed plans and does not demonstrate route-optimisation performance.

The seven Reporting Framework v2.0 sections provide bounded evidence-use guidance. Action 7 remains `NOT_COVERED`, and reporting section 5 has `NO_PROFILE_COVERAGE`: record hashes are not authenticated AI-content provenance. No actual dispatch, legal-liability determination, measured profit or effort reduction, independent audit, integrated operation with other profiles, or aggregated HAIP compliance score is claimed.
