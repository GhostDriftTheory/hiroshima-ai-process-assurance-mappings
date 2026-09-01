# 医薬品コールドチェーン引渡し保証マッピング  
## Medical Cold-Chain Handoff Assurance Mapping

[マッピング集トップ / Repository home](../../README.md) · [機械可読な正本 / Machine-readable source](profile.toml) · [数理モデル / Formal model](../../formal/FORMAL_MODEL.md)

> **第1公開Profileです。** 広島AIプロセスの11行動を、医薬品2〜8℃コールドチェーンの引渡し判断に関する義務へ分解し、版固定された証拠と対応付けます。これはマッピング集の完結又は将来範囲の限定を意味しません。

本Profileは民間の技術実装成果です。HAIPへの全面適合、G7・日本政府・OECDによる認証、医薬品品質認証、本番運用準備又は独立第三者監査を意味しません。

## 構成要素の役割

- **Cold-Chain Handoff Assurance PoC — `PRIMARY_IMPLEMENTATION`**  
  証拠・温度指標を検査し、`RELEASE / HOLD / QA_REVIEW / REJECT`を返し、最初の非`RELEASE`区間で後続処理を停止する主実装証拠です。
- **ONZALINKS Evaluation OS — `META_ASSURANCE`**  
  公開主張と公開証拠の関係が評価条件を変えても反転しないかを扱う別建てのメタ保証です。コールドチェーン実行安全性の直接証拠には使いません。

## 現在の証拠カバレッジ

| 判定 | 件数 |
|---|---:|
| `DIRECT` | 11 |
| `PARTIAL` | 1 |
| `SUPPORTING_ONLY` | 5 |
| `NOT_COVERED` | 13 |
| `NOT_ASSESSED` | 4 |
| `NOT_APPLICABLE` | 1 |

これはProfile内の義務・証拠件数であり、HAIP適合点、適合率、企業評価点又は認証点ではありません。

`D / P / S / U / N / A`は上表と同じ順序です。

| HAIP行動 | 概要 | D / P / S / U / N / A |
|---:|---|---:|
| 1 | AIライフサイクル全体でリスクを特定・評価・試験・文書化し、軽減する。 | 3 / 0 / 0 / 2 / 0 / 0 |
| 2 | 導入後の脆弱性、インシデント、新たなリスク及び誤用を特定し、軽減する。 | 0 / 0 / 1 / 2 / 0 / 0 |
| 3 | 能力、限界、適切な利用、評価及び重要なリスクを公開報告する。 | 3 / 1 / 1 / 0 / 0 / 0 |
| 4 | 安全情報を責任ある形で共有し、関係主体とインシデントを報告する。 | 1 / 0 / 0 / 1 / 1 / 0 |
| 5 | リスクベースのAIガバナンス及びリスク管理方針を策定・実施・開示・更新する。 | 1 / 0 / 0 / 3 / 0 / 0 |
| 6 | 堅牢な物理・サイバー・アクセス制御・内部脅威対策を実施する。 | 2 / 0 / 0 / 2 / 0 / 0 |
| 7 | 可能な場合、AI生成コンテンツの認証及び来歴機構を用いる。 | 0 / 0 / 0 / 0 / 0 / 1 |
| 8 | AIの安全・セキュリティ・信頼性及び社会的リスク軽減の研究・投資を優先する。 | 0 / 0 / 1 / 0 / 1 / 0 |
| 9 | グローバルヘルスを含む世界的課題及び人間の利益のため、責任あるAIを推進する。 | 0 / 0 / 1 / 1 / 0 / 0 |
| 10 | 相互運用可能な国際技術標準及びベストプラクティスを推進し、必要に応じて採用する。 | 0 / 0 / 1 / 1 / 0 / 0 |
| 11 | データ品質措置並びに個人データ及び知的財産の保護を実施する。 | 1 / 0 / 0 / 1 / 2 / 0 |

35義務の全文、証拠ID、閾値、根拠及び不足は [`profile.toml`](profile.toml) が正本です。

## Reporting Framework v2.0との限定的ブリッジ

このProfileは、OECD Reporting Framework v2.0の完成回答、質問票複製、提出支援、参加資格判定又は承認ツールではありません。各セクションで、この技術証拠をどこまで補助的に使えるかだけを示します。

| # | セクション | 状態 | このProfileから補助できること | 推論してはいけないこと |
|---:|---|---|---|---|
| 1 | リスクの特定及び評価 | `TECHNICAL_EVIDENCE_INPUT` | 限定されたPoCについて、引渡し前の証拠・温度リスクゲート、厳格な入力検査、再実行可能なテスト、レッドチーム形式シナリオ、判断追跡及び次状態への遷移前の安全側判定を示せます。 | 独立外部評価、継続的な本番監視、規制準拠、製品別閾値の妥当性又は上流センサーデータの真正性を推論してはいけません。 |
| 2 | リスク管理及び情報セキュリティ | `TECHNICAL_EVIDENCE_INPUT` | PoCは、順序付けられた安全側判定、最初の失敗地点でのチェーン停止、不正入力の拒否、プロファイル・ルールセット拘束、ハッシュによる成果物検査及びCI上の再現検証を実装しています。 | PoCを、本番グレードのサイバーセキュリティ、エンドツーエンドのデータ真正性、プライバシー準拠、脆弱性管理プログラム又は全社リスク管理システムと表現してはいけません。 |
| 3 | 高度AIシステムに関する透明性報告 | `TECHNICAL_EVIDENCE_INPUT` | 公開リポジトリは、目的、判断状態、方法、選択された評価、固定されたソース版、既知の限界、非主張事項並びにEvaluation OSの別個の役割と関係上の限界を開示しています。 | 本マッピングをOECD報告書、HAIP公式実装、独立監査又は完全なモデル／システムカードと呼んではいけません。 |
| 4 | 組織ガバナンス、インシデント管理及び透明性 | `LIMITED_CONTEXT_INPUT` | 成果物は、技術的な失敗地点の特定、安全側のチェーン停止、テスト・限界情報の公開及び評価者関係の開示を示しますが、組織ガバナンス又はインシデント管理運用を立証しません。 | チェーン停止記録だけから、インシデント対応プログラム、当局報告、教育済み人員、経営監督又は全社的説明責任を推論してはいけません。 |
| 5 | コンテンツ認証及び来歴管理の仕組み | `NO_PROFILE_COVERAGE` | 直接実装証拠はありません。 | SHA-256による成果物拘束、ルールセットダイジェスト又は判断追跡を、コンテンツ透かし、出所認証、C2PA型来歴又はAI生成表示と同一視してはいけません。 |
| 6 | AI安全性の向上及び社会的リスク軽減のための研究・投資 | `LIMITED_CONTEXT_INPUT` | 各リポジトリは、安全性・信頼性研究に関係するテスト方法、再現検証、限定された形式規則、機械可読マッピング及び明示的限界を公開する応用研究成果です。 | 公開コードの存在だけから、継続的投資プログラム、正式な標準採用、外部研究検証又は全社的な安全研究成熟度を推論してはいけません。 |
| 7 | 人類及び世界全体の利益の推進 | `LIMITED_CONTEXT_INPUT` | 対象ユースケースは、医薬品物流の強靱性と医療コールドチェーンにおける不安全な次工程移行の防止に実質的に関係します。 | 導入データ及び関係者証拠なしに、患者便益、廃棄削減、アクセス改善、グローバルヘルス効果、公平性、包摂性又は地域連携を実証済みと主張してはいけません。 |

詳しい記載例、組織側で追加すべき事実及び証拠IDは [`profile.toml`](profile.toml) の`reporting.sections`に収録しています。ポータル設問、担当者、承認状態、RACI、提出パッケージは収録していません。

## 主要な版固定ソース

- Cold-Chain Handoff Assurance PoC  
  `GhostDriftTheory/coldchain-handoff-assurance`  
  commit `1437b21a41b4c2b8623e8ae22ad71db3ef330383`
- ONZALINKS Evaluation OS  
  `GhostDriftTheory/onzalinx-evaluation-os`  
  commit `11eb3f22ea719b286043617a0c0205983aca5c71`
- HAIP行動規範：外務省掲載の公式PDF
- HAIP Reporting Framework v2.0：OECD.AI公式情報、2026年9月1日スナップショット

## 対外的に使える表現

> 広島AIプロセスの一部行動を、コールドチェーン引渡し判断における明示的な技術義務、版固定された証拠及び機械検証可能な主張境界へ落とした、民間の証拠裏付け型技術実装成果。公式認証又は全面適合を意味しない。

## 検証

```bash
python validate.py --profile coldchain-handoff
```

---

## English summary

This first published profile maps all eleven HAIP actions to independently scoped obligations for a medical 2–8°C cold-chain handoff PoC. The cold-chain repository is the primary implementation evidence. Evaluation OS is a separate meta-assurance component and is barred from directly proving runtime safety. The Reporting Framework v2.0 section is limited to evidence-use guidance and is not a reporting, submission, certification, or eligibility tool.
