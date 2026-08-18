# SOURCE_DOSSIER_SKEPTICAL_COUNTER_EVIDENCE_V0_1

> Date: 2026-08-19
> Status: SOURCE_DOSSIER_COMPLETE / SOURCE-LEVEL ONLY
> Schema: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
> Source cluster: `SRC-SKEPTICAL-METHODS`
>
> This dossier is a methodological counter-evidence source, not a trading-playbook source. It exists to challenge selection, data-snooping and backtest-overfitting risk in later research.

## 1. Identity

Core materials:

1. Halbert White, *A Reality Check for Data Snooping*, Econometrica 68(5), 2000.
2. Ryan Sullivan, Allan Timmermann, Halbert White, *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*, Journal of Finance 54(5), 1999.
3. David H. Bailey, Jonathan M. Borwein, Marcos López de Prado, Qiji Jim Zhu, *The Probability of Backtest Overfitting*, Journal of Computational Finance / SSRN working version.

Source type: peer-reviewed / academic methodological and empirical research.
Language: English.
Identity status: TRACEABLE.

## 2. Original provenance

Primary provenance anchors:

- White, Wiley/Econometrica DOI: `https://onlinelibrary.wiley.com/doi/10.1111/1468-0262.00152`
- Sullivan/Timmermann/White, Wiley Journal of Finance DOI: `https://onlinelibrary.wiley.com/doi/10.1111/0022-1082.00163`
- Bailey et al., SSRN: `https://papers.ssrn.com/sol3/Papers.cfm?abstract_id=2326253`
- López de Prado publication index confirms Journal of Computational Finance publication details: `https://www.quantresearch.org/Publications.htm`

Classification: `TRACEABLE_ACADEMIC_PRIMARY`.

## 3. Material scale and role

These papers are not trader diaries and are not intended to provide market-reading intuition.

Their project role is adversarial:
- identify ways repeated search over the same history can manufacture apparently strong results;
- quantify or test the effect of data snooping across technical-rule universes;
- provide methods/terminology for backtest-overfitting risk.

This cluster should be consulted whenever future Human Playbook interpretation or bounded parameterization creates multiple choices.

## 4. Trading-loop coverage presence

`TRADING_LOOP_COVERAGE_PRESENCE=NOT_APPLICABLE`

These are not playbook sources. They do not need setup/confirmation/exit/no-trade coverage to be useful.

Their relevance is governance and falsification pressure.

## 5. Failure / counterexample visibility

`FAILURE_VISIBILITY=HIGH_BY_DESIGN`

White explicitly frames the risk that the best model encountered in a specification search can appear superior by chance when the same data are reused.

Sullivan/Timmermann/White explicitly apply data-snooping adjustment to a large technical-trading-rule universe rather than evaluating only selected rules.

Bailey et al. explicitly model the probability that investment backtests are overfit when strategy alternatives are selected using historical simulations.

These papers therefore provide direct counter-pressure against winner-only research narratives.

## 6. Incentive / marketing notes

- Academic publication does not make a method infallible or universally applicable.
- Citation counts, journal prestige or author reputation are not substitutes for checking assumptions.
- This cluster is methodological counter-evidence, not an authority that automatically rejects all technical or discretionary trading ideas.

`INCENTIVE_HYGIENE=ACADEMIC / LOW_DIRECT_PRODUCT_MARKETING_RELEVANCE`

## 7. Lineage / independence

White's Reality Check is a methodological antecedent used directly by Sullivan/Timmermann/White.

Therefore:

```text
White Reality Check
-> Sullivan/Timmermann/White technical-rule application
```

These two are related, not fully independent.

Bailey et al. addresses a closely related but distinct backtest-overfitting problem and should be treated as a separate methodological branch, while still sharing the broad multiple-testing/model-selection concern.

`LINEAGE_STATUS=METHODOLOGICALLY_RELATED / NOT_INDEPENDENT_VOTES`

## 8. Observability compatibility

`OBSERVABILITY_COMPATIBILITY=NOT_APPLICABLE_TO_MARKET_SCENE`

These papers do not require the project to observe a trader's market inputs. Their future use is at the research-governance layer:
- count search freedom;
- document alternative interpretations tried;
- prevent hidden multiple testing;
- distinguish development from validation/final-unseen governance;
- challenge conclusions that arise only after repeated reuse of the same history.

Any concrete statistical method from these papers still requires later protocol review before becoming binding project methodology.

## 9. Source-level admission

`SOURCE_ADMISSION_CLASSIFICATION=PRIORITY_DEEP_DIVE_AS_SKEPTICAL_GUARDRAIL`

Why:
- directly relevant to the project's main failure mode: turning fuzzy human concepts into many machine alternatives and selecting the best historical result;
- primary academic provenance is strong;
- provides explicit falsification pressure without privileging any trader/source family.

This admission means "keep these in the skeptical dossier layer." It does not freeze White Reality Check, CSCV/PBO, or any specific statistical procedure into the research protocol.

## 10. Open source-level questions

- Which ideas from these papers belong in the eventual frozen protocol versus remaining general cautionary guidance?
- How should the project count AI interpretation variants as search freedom?
- How should correlated playbook lineages reduce effective independence?
- Which confirmatory procedures fit the actual number of candidate playbooks and available history?
- What is the appropriate relationship between chronological splits and any resampling/multiple-testing correction?

These are protocol-design questions and remain unresolved until the explicit freeze review.

## 11. Current boundary

STOP HERE.

Not authorized by this dossier:
- freezing a multiple-testing method;
- defining split dates;
- choosing PBO/Reality Check thresholds;
- rejecting or accepting any trading playbook;
- running final-unseen evaluation.
