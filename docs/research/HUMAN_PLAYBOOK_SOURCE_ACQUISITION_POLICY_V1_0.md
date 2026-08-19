# HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0

> Date: 2026-08-19
> Status: ACTIVE / OWNER_APPROVED_SOURCE_ACQUISITION_POLICY
> Scope: Human Playbook source discovery and acquisition

## 1. Default rule

The project defaults to free, public, unauthenticated source material.

```text
SOURCE_ACQUISITION_DEFAULT=FREE_PUBLIC_UNAUTHENTICATED_FIRST
PAID_SOURCE_PURCHASE_DEFAULT=NO
PAYWALL_BYPASS=FORBIDDEN
LOGIN_OR_SUBSCRIPTION_REQUIRED_SOURCE=NON_DEFAULT
```

The project should use the large amount of publicly available material before considering paid material.

## 2. Paid material

Paid books, courses, subscriptions, authenticated archives or other paid sources may be recorded as source candidates when relevant, but they are not purchased or used by default.

They may be listed with:
- source identity;
- why they may be useful;
- price/access class if known;
- what specific evidence gap they might fill.

Listing a paid source does not authorize purchase, subscription, login, credential use, DRM bypass or authenticated scraping.

Any actual paid commitment remains an explicit Owner gate.

## 3. Replacement rule

If a paid/inaccessible source is not uniquely necessary, the project should continue with adequate free public alternatives rather than stop the research package.

```text
PAID_OR_INACCESSIBLE_SOURCE
AND ADEQUATE_PUBLIC_ALTERNATIVE_EXISTS
-> USE_PUBLIC_ALTERNATIVE
-> RECORD_ORIGINAL_AS_OPTIONAL_CANDIDATE
-> DO_NOT_BLOCK
```

A paid source may become a genuine blocker only when a specific important claim, provenance fact or semantic distinction cannot be established from sufficiently reliable public material and the missing evidence matters to the research question. In that case the project records the gap; it still does not purchase automatically.

## 4. Evidence quality is not lowered

Free/public-first does not mean lower provenance standards.

Public alternatives still need the normal source rules:
- original/nearest-original provenance when possible;
- attributable anchors;
- derivative chain disclosure;
- failure/negative context preservation;
- source claim != project interpretation != machine operationalization;
- UNKNOWN rather than invented facts.

If only weak derivative public material exists, preserve the limitation instead of pretending it equals the inaccessible original.

## 5. Current operational consequence

For `REAL_SOURCE_FAITHFUL_CLAIM_EXTRACTION_WAVE_1`:
- prefer official public webpages/articles/interviews/videos that require no payment or authentication;
- if the initially selected source cannot provide a sufficient free public bundle, choose another already-admitted traceable public source rather than treating the package as blocked;
- source substitution must be based on provenance and extraction suitability, never expected strategy performance;
- no candidate outcome data may be used in source selection.

## 6. Owner authority

Owner instruction on 2026-08-19:
- existing project data/source budget is effectively fixed by default;
- do not assume additional paid data or paid source purchases;
- paid options may be listed for awareness;
- default research should proceed using free/public material whenever adequate alternatives exist.

This policy does not alter Research Protocol v1.0, the frozen 12/6/6 chronology, candidate-outcome access, Validation access, historical-final access, or the Human Playbook First research direction.
