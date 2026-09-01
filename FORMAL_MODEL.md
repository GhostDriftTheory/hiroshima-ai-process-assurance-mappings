# Formal model / 数理モデル

## 1. Independent profiles / Profileの独立性

Let \(\mathcal P=\{p_1,\ldots,p_k\}\) be the set of published profiles. Each profile is an independent verification unit. Adding \(p_{k+1}\) must not alter the evidence relation or result of an existing profile.

公開Profileの集合を \(\mathcal P\) とします。新Profileを追加しても、既存Profileの証拠関係・判定・主張境界は変えません。

## 2. Evidence mapping / 証拠マッピング

For a profile \(p\):

- \(H=\{h_1,\ldots,h_{11}\}\): shared HAIP actions;
- \(O_p\): profile-specific obligations;
- \(E_p\): registered evidence;
- \(R_p\subseteq O_p\times E_p\): declared evidence relation;
- \(q_p(e)\in\{0,1,2,3,4\}\): profile-local evidence strength.

An obligation receives one of:

\[
A_p(o)\in\{D,P,S,U,N,X\},
\]

corresponding to `DIRECT`, `PARTIAL`, `SUPPORTING_ONLY`, `NOT_COVERED`, `NOT_ASSESSED`, and `NOT_APPLICABLE`.

## 3. Direct-claim predicate / DIRECTの成立条件

Let \(R_{D,p}(o)\) be direct evidence, \(G_p(o)\) explicit material gaps, and \(\tau_p(o)\) the minimum strength declared for the obligation. `DIRECT` is admissible only if:

\[
R_{D,p}(o)\neq\varnothing,
\qquad
\max_{e\in R_{D,p}(o)}q_p(e)\ge\tau_p(o),
\qquad
G_p(o)=\varnothing.
\]

政策文書又は本マッピング自身の説明だけでは、直接実装証拠になりません。`PARTIAL`は適格証拠と少なくとも一つの明示的不足を必要とします。

## 4. Component-role separation / 構成要素の役割分離

Each component has a role such as `PRIMARY_IMPLEMENTATION`, `SUPPORTING_IMPLEMENTATION`, or `META_ASSURANCE`. A profile may prohibit meta-assurance evidence from selected runtime or reporting claims:

\[
R_{D,p}(o)\cap E_{META,p}=\varnothing
\quad \forall o\in X_p.
\]

第1Profileでは、Evaluation OSの証拠をコールドチェーン実行安全性の直接証拠に利用できません。

## 5. Bounded Reporting v2 bridge / 限定的Reporting v2ブリッジ

For each of the seven official sections, a profile may declare:

- `TECHNICAL_EVIDENCE_INPUT`;
- `LIMITED_CONTEXT_INPUT`; or
- `NO_PROFILE_COVERAGE`.

Supported obligations must already be assessed as `DIRECT`, `PARTIAL`, or `SUPPORTING_ONLY`; known gaps must already be `NOT_COVERED`, `NOT_ASSESSED`, or `NOT_APPLICABLE`. A `NO_PROFILE_COVERAGE` section cannot contain supported obligations or evidence.

このブリッジから、完成報告、受理、認証、参加資格又は対象範囲は導けません。

## 6. Digest and no aggregation / ダイジェストと非合算

The validator canonicalises the shared HAIP actions and one parsed profile, then computes:

\[
D_p=\operatorname{SHA256}(\operatorname{CanonicalJSON}(H,p)).
\]

The digest detects changes to the checked profile bundle; it is not a regulatory certificate.

No portfolio compliance operation is defined:

\[
\operatorname{PortfolioComplianceScore}(\mathcal P)\;\text{is undefined}.
\]

Therefore, direct evidence in one profile does not fill a gap in another, and no combination of profiles implies HAIP certification or full compliance.
