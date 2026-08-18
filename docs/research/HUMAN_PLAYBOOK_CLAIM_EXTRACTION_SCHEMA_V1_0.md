# HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0

> Version: 1.0
> Date: 2026-08-19
> Status: ACTIVE / BINDING_UNDER_RESEARCH_PROTOCOL_V1_0
> Protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Supersedes for active use: `HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V0_1.md`

## 1. Boundary

This schema is now authorized for **real source-faithful claim extraction only inside a verified SOURCE_ONLY environment**.

It does not authorize candidate outcome-bearing performance backtests.

## 2. Three-layer separation

```text
SOURCE CLAIM
!=
PROJECT / AI INTERPRETATION
!=
MACHINE OPERATIONALIZATION
```

Claim status:

```text
EXPLICIT
INFERRED
UNKNOWN
```

`UNKNOWN` is preferred over filling a gap by guesswork. `INFERRED` must never be rewritten as if the source said it.

## 3. Required claim record

A claim record must support at least:

```text
claim_id:
source_id:
material_id:
source_anchor:
source_anchor_type:
source_language:
claim_status: EXPLICIT | INFERRED | UNKNOWN
source_excerpt_short_or_paraphrase:
source_context_note:
claim_category:
source_observation_surface:
source_timeframe_or_horizon_if_explicit:
source_market_or_instrument_if_explicit:
source_applicability_if_explicit:
source_invalidation_if_explicit:
source_no_trade_if_explicit:
source_exit_or_management_if_explicit:
source_failure_or_counterexample_anchor:
ambiguity_notes:
lineage_id:
mechanism_signature_status:
observability_compatibility:
observability_missing_inputs:
interpretation_version:
interpretation_status:
interpretation_text:
interpretation_evidence_basis:
primary_branch_status:
primary_branch_id:
alternative_interpretation_ids:
source_example_exposure_reference:
researcher_model_exposure_note:
source_only_session_reference:
machine_operationalization_status:
review_status:
created_at:
updated_at:
```

Fields that are not applicable may be `UNKNOWN` / `NOT_APPLICABLE`; do not create fake precision.

## 4. SOURCE_ONLY session requirement

Every real claim-extraction session must link to a SOURCE_ONLY session record containing at least:
- model identity/version;
- prompt/specification version;
- tool/retrieval mode;
- source-bundle identity/hash;
- protected-period market retrieval mode;
- explicit human/model market-exposure notes where known.

If technical denial of protected-period market outcome retrieval is not verified, the session cannot be marked SOURCE_ONLY verified and its claims cannot progress toward PRIMARY selection under Protocol v1.0.

## 5. Source anchor rule

Every EXPLICIT claim must point back to an attributable source anchor.

Preferred anchors:
- book: edition + page/chapter/figure;
- video: source ID/URL + timestamp;
- article/blog: canonical URL + section/paragraph context;
- interview: original/nearest-original page + question/answer position;
- image/chart: parent material + figure/frame identity.

Derivative/reposted material must preserve the provenance chain.

## 6. Copyright boundary

Store traceability, not a redistribution archive:
- use short excerpts only when useful;
- prefer anchors + concise paraphrase;
- do not commit full copyrighted books/courses/videos/transcripts;
- raw copyrighted material remains outside shareable project artifacts unless rights clearly permit retention.

## 7. Structural claim categories

```text
MARKET_CONTEXT
OBSERVED_CUE
SOURCE_INTERPRETATION
WATCHING_OR_NO_TRADE
ACTION_PERMISSION
CONFIRMATION
INVALIDATION
MANAGEMENT
EXIT
APPLICABILITY
NON_APPLICABILITY
RISK_PROCESS
REVIEW_PROCESS
FAILURE_OR_COUNTEREXAMPLE
OTHER
```

These are structural containers, not machine trading rules.

## 8. PRIMARY_BRANCH rule

Before any candidate outcome-bearing performance test, each source-faithful claim must have exactly one source-justified PRIMARY_BRANCH selected from source evidence alone.

If a unique PRIMARY cannot be justified:

```text
AMBIGUOUS / INSUFFICIENTLY_OPERATIONALIZED -> STOP
```

Alternatives may be preserved explicitly but cannot later rescue a failed PRIMARY and still be called validation of the human source claim.

## 9. Observability gate

Every claim records what the source actually observed and whether the project has that input point-in-time.

Allowed states:

```text
OBSERVABLE_NOW
PARTIALLY_OBSERVABLE
NOT_OBSERVABLE_WITH_CURRENT_DATA
UNKNOWN
NOT_APPLICABLE
```

A missing input does not authorize an invented K-line proxy. A surrogate must be a clearly INFERRED branch justified before outcome testing.

## 10. Failure / negative evidence

Claims may link to:
- positive example;
- near-miss;
- negative/counterexample;
- wrong-context lookalike;
- ambiguous/no-trade case;
- explicit invalidation/failure.

No universal count is required, but missing negative material is a source-quality limitation.

## 11. Lineage and exposure

Claim records must preserve lineage/mechanism relationships where known and link to family-level exposure records.

Source-example exposure uses effective content/version dates plus dated example audit when required by Protocol v1.0.

Renaming does not reset exposure.

## 12. Machine operationalization statuses

```text
NOT_STARTED
NOT_OBSERVABLE
INTERPRETATION_REQUIRED
READY_FOR_NON_OUTCOME_OPERATIONALIZATION
OPERATIONALIZED_VERSIONED_NON_OUTCOME_ONLY
```

No status in this schema authorizes candidate outcome-bearing performance testing.

That remains blocked until the Protocol v1.0 pre-outcome gate is technically satisfied.

## 13. Forbidden transformations

Forbidden:

```text
source says "strong breakout"
-> silently define as > 1.5 ATR
```

```text
source says "selling pressure is weak"
-> invent one indicator
-> call it source-equivalent
```

```text
source does not state invalidation
-> infer a stop
-> mark it EXPLICIT
```

```text
try many interpretations
-> inspect outcomes
-> retain best
-> call winner "what the source meant"
```

## 14. Active-stage permission

After SOURCE_ONLY technical controls are implemented and verified, the project may apply this schema to real approved source materials.

Until then:

```text
REAL_CLAIM_EXTRACTION_READINESS = PENDING_SOURCE_ONLY_IMPLEMENTATION
CANDIDATE_OUTCOME_BACKTEST = NOT_AUTHORIZED
```
