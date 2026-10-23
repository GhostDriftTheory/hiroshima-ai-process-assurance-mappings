# 自治体AI・回答採用アシュアランス・マッピング  
## Civic AI Answer-Adoption Assurance Mapping

[マッピング集トップ / Repository home](../../README.md) · [機械可読な正本 / Machine-readable source](profile.toml) · [数理モデル / Formal model](../../formal/FORMAL_MODEL.md)

> **自治体AI領域の独立Profileです。** 広島AIプロセスの11行動を、架空の制度資料・合成相談条件に基づく回答案の採用判定、職員確認用出力及び記録の再検証に関する義務へ分解し、版固定された証拠と対応付けます。

本Profileは株式会社AIアシュアランス（AI Assurance, Inc.）による民間の技術成果です。HAIPへの全面適合、G7・日本政府・OECDによる認証、実自治体への導入、本番運用準備又は独立第三者監査を意味しません。更新日：2026年10月23日。

## 構成要素の役割

- **Civic AI Answer-Adoption Assurance PoC — `PRIMARY_IMPLEMENTATION`**  
  固定の合成資料に対する8採用条件、PASS／HOLD／REJECT、職員確認用出力及び判定記録の再検証を扱う参照実装。

原PoCの公開体制は、株式会社クラウドシエンが自治体業務・導入要件を検討し、株式会社AIアシュアランスが技術設計・実装・検証を担当する構成です。本ProfileはこのPoCだけを証拠単位とし、他のPoCとの自動接続や統合運転は主張しません。

主対象はローカルの回答採用モデルです。同リポジトリの実API実験は別の通信・原文解析境界を持ち、本Profileではその成績をモデルの形式保証へ読み替えません。

別途、[実API実験の公開記録](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/blob/22fa50166f5be2db3adaa5679532073a82d92eb4/answer_api_evidence.json)と[結果レポート](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/blob/22fa50166f5be2db3adaa5679532073a82d92eb4/report.html)があります。本Profileの形式証明又は現行CIによる当該記録の再検証の証拠には用いていません。


[`CivicAnswerAdoption.lean`](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/blob/22fa50166f5be2db3adaa5679532073a82d92eb4/CivicAnswerAdoption.lean)は45の名前付き定理を収録します。`adoption_iff_all_checks_pass`は8条件の全通過、`missing_binding_blocks_adoption`は根拠不足時の非採用、`reverification_does_not_upgrade`は再検証による判定格上げの禁止を扱います。証明対象は定義済みLeanモデルです。観測値の抽出、JSON・暗号・OS・入出力又はPython全体の全入力に対する正しさを証明したものではありません。具体入力での実装照合は別の検査です。

## 現在の証拠カバレッジ

| 判定 | 件数 |
|---|---:|
| `DIRECT` | 8 |
| `PARTIAL` | 0 |
| `SUPPORTING_ONLY` | 4 |
| `NOT_COVERED` | 11 |
| `NOT_ASSESSED` | 0 |
| `NOT_APPLICABLE` | 0 |

これはProfile内の義務件数であり、HAIP適合点、適合率、企業評価点又は認証点ではありません。`DIRECT`は記載した狭い技術義務についての判定であり、HAIP行動全体を満たすとの判定ではありません。

`D / P / S / U / N / A`は上表と同じ順序です。

| HAIP行動 | 概要 | D / P / S / U / N / A |
|---:|---|---:|
| 1 | AIライフサイクル全体でリスクを特定・評価・試験・文書化し、軽減する。 | 2 / 0 / 0 / 1 / 0 / 0 |
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

23義務の全文、証拠ID、閾値、根拠及び不足は [`profile.toml`](profile.toml) が正本です。他Profileの証拠で不足を埋めたり、カバレッジを合算したりしません。

## Reporting Framework v2.0との限定的ブリッジ

このProfileは、OECD Reporting Framework v2.0の完成回答、質問票複製、提出支援、参加資格判定又は承認ツールではありません。この技術証拠を各セクションへ補助的に利用できる範囲を示します。

| # | セクション | 状態 | このProfileから補助できること | 推論してはいけないこと |
|---:|---|---|---|---|
| 1 | リスクの特定及び評価 | `TECHNICAL_EVIDENCE_INPUT` | 固定合成ケースの条件判定、形式モデルの証明及び具体入力の実装照合。 | 全AIの安全性、実運用の事故率、独立評価又は法令適合を推論しない。 |
| 2 | リスク管理及び情報セキュリティ | `TECHNICAL_EVIDENCE_INPUT` | 条件不成立時の停止、職員確認用出力、厳格な入力検査及び記録の再計算。 | 本番の防御能力、真正性、全社リスク管理又は個人情報保護の十分性を推論しない。 |
| 3 | 高度AIシステムに関する透明性報告 | `TECHNICAL_EVIDENCE_INPUT` | PoCの目的・検査手順・評価範囲・限界の公開と、安全性に関する証明・合成試験仕様・再検証方法の共有。 | 完成したOECD報告、全面的なモデルカード又は独立認証とみなさない。 |
| 4 | 組織ガバナンス、インシデント管理及び透明性 | `LIMITED_CONTEXT_INPUT` | 判断・未確認状態の記録、職員確認用という利用境界及び公開可能な安全性評価資料の共有。 | 記録の存在から組織のガバナンス又は当局報告体制を実証済みと推論しない。 |
| 5 | コンテンツ認証及び来歴管理の仕組み | `NO_PROFILE_COVERAGE` | このProfileにコンテンツ認証・来歴機構の実装カバレッジはない。 | ハッシュ、API応答ID又は再計算可能性を、署名・透かし・認証された来歴と同一視しない。 |
| 6 | AI安全性の向上及び社会的リスク軽減のための研究・投資 | `LIMITED_CONTEXT_INPUT` | 安全性・信頼性に関する公開参照実装、形式モデル及び再検証方法という研究成果。 | 公開コードや定理件数から、継続的投資、研究成熟度又は標準適合を推論しない。 |
| 7 | 人類及び世界全体の利益の推進 | `LIMITED_CONTEXT_INPUT` | 自治体業務での適切なAI利用を想定した合成ユースケース。 | 実自治体での導入、社会的便益、職員工数削減又は公平性改善を実証済みと推論しない。 |

記載例、報告に利用する場合に組織側で別途示す必要がある事実及び証拠IDは [`profile.toml`](profile.toml) の`reporting.sections`に収録しています。

## 主要な版固定ソース

- [Civic AI Answer-Adoption Assurance PoC](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/tree/22fa50166f5be2db3adaa5679532073a82d92eb4)  
  `GhostDriftTheory/civic-ai-answer-adoption-assurance`  
  commit `22fa50166f5be2db3adaa5679532073a82d92eb4`
- [公開説明](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/blob/22fa50166f5be2db3adaa5679532073a82d92eb4/README.md)・[参照実装](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/blob/22fa50166f5be2db3adaa5679532073a82d92eb4/poc.py)・[合成仕様とケース](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/blob/22fa50166f5be2db3adaa5679532073a82d92eb4/cases.json)・[Leanモデル](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/blob/22fa50166f5be2db3adaa5679532073a82d92eb4/CivicAnswerAdoption.lean)
- [検査手順](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/blob/22fa50166f5be2db3adaa5679532073a82d92eb4/.github/workflows/lean.yml)と、[同一コミットで成功した2026年10月22日のCI](https://github.com/GhostDriftTheory/civic-ai-answer-adoption-assurance/actions/runs/39785797822)。CIの成功は独立第三者監査を意味しません。
- HAIP行動規範：[外務省掲載の公式PDF](https://www.mofa.go.jp/files/100573473.pdf)
- HAIP Reporting Framework v2.0：[OECD.AI公式情報](https://oecd.ai/en/transparency/overview)。公式情報の確認日：2026年10月23日。共通行動定義は既存の2026年9月1日スナップショットを維持します。

元の実装・データ・証明は各リポジトリで管理し、本Profileへ複製しません。利用条件は原リポジトリの著作権・利用条件に従います。ハッシュは署名ではなく、記録の再検証成立は不採用・保留を採用可へ変更しません。

## 対外的に使える表現

> 広島AIプロセスの一部行動を、合成の自治体情報に対する回答採用条件、判定記録の再検証及びLeanの形式モデルへ対応付けた、民間の証拠裏付け型技術成果。公式認証、実自治体への導入又は全面適合を意味しない。

## 検証

マッピング集のルートで実行します。検証対象はこのマッピングの参照・主張境界の整合性です。元PoCの実行検査又はLeanビルドをこのコマンドで再実行するものではありません。

```bash
python validate.py --profile civic-ai-answer-adoption
```

---

## English summary

This independent profile maps all eleven HAIP actions to 23 scoped obligations for the Civic AI Answer-Adoption Assurance PoC. AI Assurance, Inc. publishes the mapping. The source PoC identifies Crowdsien Inc. as examining municipal requirements and AI Assurance, Inc. as responsible for technical design, implementation, and verification.

Reference implementation of eight adoption checks, PASS/HOLD/REJECT, staff-review drafts, and decision-record replay over fixed synthetic sources. The principal subject is the local adoption model. The repository also contains a real-API experiment with separate communication and text-parsing boundaries; its outcomes are not promoted to formal guarantees here. Its 45 Lean theorems cover the defined model; finite implementation-conformance checks do not prove all-input correctness of the entire software stack. Evidence is pinned to commit `22fa50166f5be2db3adaa5679532073a82d92eb4` with a successful run at that commit.

The seven Reporting Framework v2.0 sections provide bounded evidence-use guidance. Action 7 remains `NOT_COVERED`, and reporting section 5 has `NO_PROFILE_COVERAGE`: record hashes are not authenticated AI-content provenance. No municipal deployment, independent audit, full HAIP compliance, integrated operation with other PoCs, or aggregated compliance score is claimed.
