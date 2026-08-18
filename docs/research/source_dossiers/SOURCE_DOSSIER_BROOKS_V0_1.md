# SOURCE_DOSSIER_BROOKS_V0_1

> Date: 2026-08-19
> Status: SOURCE_DOSSIER_COMPLETE / SOURCE-LEVEL ONLY
> Schema: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
> Source ID: `SRC-BROOKS`
> Material ID: `MAT-BROOKS-PA`
>
> This dossier evaluates source quality, continuity, incentives and observability. It does not extract or validate any trading rule.

## 1. Identity

- Canonical person: Al Brooks.
- Core materials: Wiley *Trading Price Action* series; earlier *Reading Price Charts Bar by Bar*; official Brooks Trading Course / archive.
- Source type: publisher books + long-form commercial video education.
- Language: English.
- Identity status: TRACEABLE.

## 2. Original provenance

Primary anchors:
- Wiley, *Trading Price Action Trends*: `https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202592`
- Wiley, *Trading Price Action Trading Ranges*: `https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202608`
- Wiley, *Trading Price Action Reversals*: `https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202622`
- Wiley, *Reading Price Charts Bar by Bar*: `https://onlinelibrary.wiley.com/doi/book/10.1002/9781119203117`
- Official site/course portal: `https://www.brookspriceaction.com/`

Classification: `TRACEABLE_ORIGINAL`.

## 3. Material scale and continuity

Material scale: VERY_LARGE / MULTI-BOOK / LONG-FORM_VIDEO.

The official course advertises 100+ hours and 52 modules, and the site references a 2010-2024 video archive. The Wiley series is explicitly structured across trends, trading ranges and reversals.

This scale is useful for reducing cherry-picked-example bias, but it creates a different risk: dense proprietary vocabulary can invite AI to over-interpret or silently normalize ambiguous terms.

## 4. Trading-loop coverage presence

Publisher descriptions and chapter summaries show extensive context, chart reading, entries/setups and examples across market states.

Wiley's Reversals introduction explicitly notes that most trend reversals fail and that selectivity matters. That establishes failure awareness at the source level, but not the density or quality of explicit losing-example documentation across the full corpus.

`TRADING_LOOP_COVERAGE_PRESENCE=PRESENT_BUT_NOT_CLAIM_EXTRACTED`

## 5. Failure visibility

`FAILURE_VISIBILITY=PRESENT_AT_CONCEPT_LEVEL / SAMPLE_DENSITY_UNCHECKED`

The source explicitly discusses failed breakouts/reversals and the fact that many apparent reversal attempts fail. However, this dossier has not sampled enough long-form material to determine whether failed/invalidated trades are preserved as systematically as successful examples.

## 6. Incentive / marketing notes

- Official education is commercial.
- Current official materials advertise a paid course, paid live trading room, archives and subscriptions.
- Publisher copy and testimonials are promotional material, not evidence of edge.
- Statements about consistent profitability or cross-market effectiveness are source/marketing claims, not project conclusions.

`INCENTIVE_HYGIENE=STRONG_COMMERCIAL_EDUCATION_PRESENT`

## 7. Lineage / independence

Brooks is treated as a distinct modern price-action source, but not automatically as an independent confirmation of every classical charting concept embedded in the material.

Future overlap with classical charting/candlestick/price-action educators must be lineage-adjusted.

`LINEAGE_STATUS=MODERN_PRICE_ACTION_SOURCE_WITH_POSSIBLE_CLASSICAL_OVERLAP`

## 8. Observed information surface / observability compatibility

Source surface is strongly chart/bar oriented. Wiley material repeatedly describes price-action reading using bars, highs/lows, opens/closes, trend lines/channels, prior highs/lows and failed breakouts.

At source-envelope level:

`OBSERVABILITY_COMPATIBILITY=OBSERVABLE_NOW`

Important limit: "observable" does not mean "already machine-defined." Terms such as strong bar, context, pressure, good signal, failed breakout or quality of reversal must remain source-language concepts until later protocol-governed interpretation.

## 9. Source-level admission

`SOURCE_ADMISSION_CLASSIFICATION=PRIORITY_DEEP_DIVE`

Why:
- strong original/publisher provenance;
- unusually large corpus;
- price/bar observation surface matches current data well;
- explicit failure-aware language exists;
- excellent stress test for AI over-interpretation risk.

## 10. Open source-level questions

- How often are failed/invalidated/no-trade examples shown in the full corpus?
- Which vocabulary is explicitly defined by Brooks versus only contextually implied?
- Which concepts depend on exact 5-minute/session context and may not transfer to the project's 1-minute Chinese futures corpus without semantic change?
- Which later instructors/course materials are Brooks-original versus downstream restatements?

## 11. Current boundary

STOP HERE.

No concrete setup extraction, thresholding, backtesting, profitability judgment or machine operationalization is authorized by this dossier.
