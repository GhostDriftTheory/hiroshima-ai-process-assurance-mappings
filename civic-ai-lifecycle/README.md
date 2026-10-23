# 自治体AI・派生情報ライフサイクル保証マッピング  
## Civic AI Derived-Information Lifecycle Assurance Mapping

[マッピング集トップ / Repository home](../../README.md) · [機械可読な正本 / Machine-readable source](profile.toml) · [数理モデル / Formal model](../../formal/FORMAL_MODEL.md)

> **派生情報の条件承継・継続利用・利用終了を対象とする公開Profileです。** 広島AIプロセスの11行動を、合成の自治体相談情報を使う参照PoCの義務へ分解し、版固定された実装・モデル証明・公開記録と対応付けます。自治体相談は適用例であり、技術全体の適用分野を限定するものではありません。

本Profileは株式会社AIアシュアランスによる民間の技術成果です。HAIPへの全面適合、G7・日本政府・OECDによる認証、本番運用準備、実在自治体への導入又は独立第三者監査を意味しません。第1・第2弾とは独立した検証単位であり、3件の統合実行機能やProfile間のカバレッジ合算は主張しません。

## 構成要素の役割

- **Civic AI Derived-Information Lifecycle Assurance PoC — `PRIMARY_IMPLEMENTATION`**  
  起源別の条件承継、証拠に基づく限定変更、`PASS / HOLD / REJECT`による後続利用、管理対象コピー・未終結操作の確認、範囲付きの業務利用終了及び独立した履歴再計算を行う主実装です。公開参照実装はクラウドシエンとAIアシュアランスの技術PoCとして整理され、前者が自治体業務・導入要件、後者が技術設計・実装・検証を担当します。

証明対象は[`CivicLifecycleAssurance.lean`](https://github.com/GhostDriftTheory/civic-ai-lifecycle-assurance/blob/a410d4171734a56a789d3d0742a9db17d17b7e3d/CivicLifecycleAssurance.lean)の判定モデルです。`unknown_support_does_not_drop_conditions`は寄与不明時の条件保持、`missing_evidence_cannot_relax`は証拠なしの緩和禁止、`other_condition_unchanged`は対象外条件の保持、`residual_route_blocks_certificate`及び`pending_operation_blocks_certificate`は残存経路・未終結操作による終了阻止を示します。状態・世代・期限が変わった証明の流用も拒否します。

**利用終了は、指定した管理ゲート経由の業務利用の終了です。** `end_record_is_not_erasure`が示すとおり、物理消去、未知の管理外コピーの不存在、監査記録の消失又はOpenAI等の提供者内部の削除の証明ではありません。管理経路の捕捉・真正性・認証・JSON・SHA-256・I/Oは観測境界にあり、全実装の全入力に対する正当性やAI文章の意味的正確性を証明しません。

## 現在の証拠カバレッジ

| 判定 | 件数 |
|---|---:|
| `DIRECT` | 8 |
| `PARTIAL` | 0 |
| `SUPPORTING_ONLY` | 4 |
| `NOT_COVERED` | 10 |
| `NOT_ASSESSED` | 1 |
| `NOT_APPLICABLE` | 0 |

これはProfile内の義務・証拠件数であり、HAIP適合点、適合率、企業評価点又は認証点ではありません。`DIRECT`も、ここに定義した限定的な技術義務についての判定です。

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
| 8 | AIの安全・セキュリティ・信頼性及び社会的リスク軽減の研究・投資を優先する。 | 0 / 0 / 1 / 0 / 1 / 0 |
| 9 | グローバルヘルスを含む世界的課題及び人間の利益のため、責任あるAIを推進する。 | 0 / 0 / 1 / 1 / 0 / 0 |
| 10 | 相互運用可能な国際技術標準及びベストプラクティスを推進し、必要に応じて採用する。 | 0 / 0 / 1 / 1 / 0 / 0 |
| 11 | データ品質措置並びに個人データ及び知的財産の保護を実施する。 | 2 / 0 / 0 / 1 / 0 / 0 |

23義務の全文、9件の証拠、閾値、根拠及び不足は[`profile.toml`](profile.toml)が正本です。

固定版に対応する[GitHub Actionsの成功記録](https://github.com/GhostDriftTheory/civic-ai-lifecycle-assurance/actions/runs/39787514011)では、Leanモデル証明、実装照合・証明依存及び公開API記録のオフライン再検証が成功しています。固定版READMEは、70モデル定理、8,095具体命題、181処理列・817操作のPython／JavaScript照合、249自己テスト、13シナリオ・85操作を報告しています。これらは検査の異なる側面を含むため、独立した実証件数として合算しません。

公開API実験は**2026年10月11日の1回の呼出し**です。合成相談Aだけを`gpt-5.4-mini`へ送信し、記録した生成文について条件承継・限定変更・コピー・終了判定の16操作を再計算できます。内部限定の資料Bは送信していません。**参照版のコミット日（2026年10月22日）と実験日を区別します。** 応答IDとローカルのハッシュは提供者の署名・発行者認証ではなく、この記録はOpenAIによる成果認証を意味しません。

## Reporting Framework v2.0との限定的ブリッジ

このProfileは、OECD Reporting Framework v2.0の完成回答、質問票複製、提出支援、参加資格判定又は承認ツールではありません。各セクションで、この技術証拠をどこまで補助的に使えるかだけを示します。

| # | セクション | 状態 | このProfileから補助できること | 推論してはいけないこと |
|---:|---|---|---|---|
| 1 | リスクの特定及び評価 | `TECHNICAL_EVIDENCE_INPUT` | 条件喪失、未承認変更、残存経路・未終結操作及び過大な終了主張に対する固定PoCの判定と試験を示せます。 | 独立外部評価、全AIシステムの安全性、生成文の意味的正確性又は全実装の全入力に対する証明を推論してはいけません。 |
| 2 | リスク管理及び情報セキュリティ | `TECHNICAL_EVIDENCE_INPUT` | 用途・提供先・期限・模擬権限による利用制御、証拠付き限定変更、現在状態での証明再確認及び記録再計算を示せます。 | OS全体のアクセス制御、媒体の物理消去、未知の管理外コピーの不存在又はAPI提供者内部の削除を推論してはいけません。 |
| 3 | 高度AIシステムに関する透明性報告 | `TECHNICAL_EVIDENCE_INPUT` | 公開範囲、再検証方法、モデル・実装・実API記録の区別、合成データ及び保証の限界を公開しています。 | 本Profileを完成済みOECD報告書、全システムの透明性報告、独立監査又は提供者による成果認証と呼んではいけません。 |
| 4 | 組織ガバナンス、インシデント管理及び透明性 | `LIMITED_CONTEXT_INPUT` | 技術的な保留・拒否理由、模擬承認との対応及び履歴の再現を説明する補助材料になります。 | 模擬承認を実在主体の認証、履歴を実際のインシデント対応又は組織全体の統制と同一視してはいけません。 |
| 5 | コンテンツ認証及び来歴管理の仕組み | `NO_PROFILE_COVERAGE` | 信頼できるAI生成コンテンツ認証の直接証拠はありません。宣言された起源・モデル識別子とローカル記録の整合性を、出所認証と区別します。 | 起源別の条件承継、応答ID、SHA-256又は整合的な履歴を、信頼できるコンテンツの出所認証と同一視してはいけません。 |
| 6 | AI安全性の向上及び社会的リスク軽減のための研究・投資 | `LIMITED_CONTEXT_INPUT` | 条件承継・利用終了のモデル証明、複数実装の照合及び公開実験記録という限定された応用研究成果を示せます。 | 公開実装から継続的な投資義務、投資規模、正式な標準採用又は外部システムとの相互運用実証を推論してはいけません。 |
| 7 | 人類及び世界全体の利益の推進 | `LIMITED_CONTEXT_INPUT` | 自治体相談情報の適切な継続利用と利用終了を支援する技術的な目的を示せます。 | 住民便益、業務効率、公共サービスの公平性、導入済みの自治体実績又は教育活動の効果を実証済みと主張してはいけません。 |

詳しい記載例、報告を行う場合に組織側で補う事実及び証拠IDは[`profile.toml`](profile.toml)の`reporting.sections`に収録しています。このProfileは定期測定・定期報告・継続公表の義務を新設しません。宣言された起源・モデル識別子と記録ハッシュをコンテンツ認証の証拠には扱わず、第7行動は`NOT_COVERED`、Reporting第5節は`NO_PROFILE_COVERAGE`です。

## 主要な版固定ソース

- [Civic AI Derived-Information Lifecycle Assurance PoC](https://github.com/GhostDriftTheory/civic-ai-lifecycle-assurance/tree/a410d4171734a56a789d3d0742a9db17d17b7e3d)  
  `GhostDriftTheory/civic-ai-lifecycle-assurance`  
  commit `a410d4171734a56a789d3d0742a9db17d17b7e3d`（2026年10月22日）
- [固定コミットに対するCI成功記録](https://github.com/GhostDriftTheory/civic-ai-lifecycle-assurance/actions/runs/39787514011)  
  run `39787514011`、2026年10月22日、モデル・実装照合・公開記録の検査が成功
- [公開API実験記録](https://github.com/GhostDriftTheory/civic-ai-lifecycle-assurance/blob/a410d4171734a56a789d3d0742a9db17d17b7e3d/evidence/openai-api-2026-10-11/live_evidence.json)・[呼出し意図／完了記録](https://github.com/GhostDriftTheory/civic-ai-lifecycle-assurance/blob/a410d4171734a56a789d3d0742a9db17d17b7e3d/evidence/openai-api-2026-10-11/api_intent.json)  
  実験日：2026年10月11日。固定コミット内の記録を参照し、本マッピングには複製しません。
- HAIP行動規範：[外務省掲載の公式PDF](https://www.mofa.go.jp/files/100573473.pdf)
- HAIP Reporting Framework v2.0：[OECD.AI公式情報](https://oecd.ai/en/transparency/overview)  
  本Profileの証拠確認日：2026年10月23日。共通の11行動定義は既存版を維持しています。

## 対外的に使える表現

> 広島AIプロセスの一部行動を、AIが生成した派生情報の条件承継・継続利用・管理範囲の業務利用終了に関する技術義務へ落とし、版固定された公開参照実装、Lean4のモデル証明及び再計算可能な記録に接続した、民間の証拠裏付け型技術成果。公式認証、全面適合又は管理範囲外の消去保証を意味しない。

## 検証

マッピング集のルートで実行します。

```bash
python validate.py --profile civic-ai-lifecycle
```

公開実験の記録を確認する場合は、参照PoCの固定版を取得し、同リポジトリ内で実行します。APIキー・新たなAPI呼出しは不要です。

```bash
python poc.py verify evidence/openai-api-2026-10-11/live_evidence.json
```

前者はマッピングの参照・判定条件・主張境界の検査、後者は保存済み生成文を使ったローカル処理記録の再計算です。Leanモデルと具体的照合の全検査は参照PoCの`python poc.py ci`が担当します。

---

## English summary

This independent profile maps all eleven HAIP actions to scoped obligations for condition inheritance, continued use and termination of business use of information derived from synthetic municipal consultations. It references one pinned primary implementation, seventy Lean 4 model theorems, finite Python/JavaScript/Lean conformance checks and a successful run for that same commit. The separately dated 11 October 2026 API experiment contains one recorded call and sixteen replayable local operations; replay does not contact the API or authenticate the provider as issuer.

Termination is restricted to business-use paths captured by the specified management gates. It is not physical erasure, absence of unmanaged copies, removal of retained audit evidence or deletion inside the provider. Recorded lineage, model identifiers and hashes do not establish content authentication, so HAIP action 7 and Reporting section 5 have no implementation coverage. The Reporting v2.0 bridge is limited evidence-use guidance, and does not create reporting commitments, establish full compliance or combine this profile with the other civic PoCs into an integrated runtime.
