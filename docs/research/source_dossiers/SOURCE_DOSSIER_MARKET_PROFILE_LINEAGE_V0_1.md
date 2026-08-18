# SOURCE_DOSSIER_MARKET_PROFILE_LINEAGE_V0_1

> Date: 2026-08-19
> Status: SOURCE_DOSSIER_COMPLETE / SOURCE-LEVEL ONLY
> Schema: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
> Source cluster: `SRC-MARKET-PROFILE-LINEAGE`
>
> This dossier treats Market Profile material as a lineage cluster, not as multiple independent confirmations. It does not extract or validate any trading rule.

## 1. Identity

Primary lineage anchor:
- J. Peter Steidlmayer / Steven B. Hawkins, *Steidlmayer on Markets: Trading with Market Profile*.

Major descendant/popularization material:
- James F. Dalton, Robert Bevan Dalton, Eric T. Jones, *Markets in Profile: Profiting from the Auction Process*.
- Jim Dalton's later official educational/books material.

Source type:
- publisher books;
- later official educational/commercial material.

Language: English.

Identity status: TRACEABLE.

## 2. Original provenance

Primary provenance anchors:

- Wiley-VCH, *Steidlmayer on Markets*: `https://www.wiley-vch.de/en?isbn=9780471215561&option=com_eshop&view=product`
- ProfileTrading official book page: `https://www.profiletrading.com/book/`
- Wiley Online Books, *Markets in Profile*: `https://onlinelibrary.wiley.com/doi/book/10.1002/9781119196709`
- Jim Dalton Trading official books page: `https://jimdaltontrading.com/books/`

Classification: `TRACEABLE_ORIGINAL_AND_DESCENDANT_LINEAGE`.

Wiley identifies Steidlmayer/Hawkins as Market Profile authors and identifies Dalton's *Markets in Profile* as a later book centered on Market Profile, auction process, behavioral finance and related interpretation. Dalton's own site explicitly describes *Markets in Profile* as expanding upon Market Profile theory.

## 3. Material scale and continuity

Material scale: MULTI-BOOK / MULTI-GENERATION LINEAGE.

This is not one source duplicated across websites; it is a lineage with an originator and later interpreters/educators.

Important consequence:
- Steidlmayer and Dalton must not be counted as two independent confirmations of the same Market Profile claim merely because both discuss it.
- Later Market Profile educators should inherit a lineage link unless strong evidence shows independent derivation.

## 4. Trading-loop coverage presence

Source-level publisher descriptions indicate the material covers:
- market organization / auction interpretation;
- market structure and change;
- real-time decision context;
- time-frame/inventory concepts in later Dalton material.

Exact setup/confirmation/invalidation/exit/no-trade claims are not extracted here.

`TRADING_LOOP_COVERAGE_PRESENCE=PRESENT_BUT_NOT_CLAIM_EXTRACTED`

## 5. Failure visibility

`FAILURE_VISIBILITY=UNKNOWN`

Publisher/official descriptions are not enough to establish whether the books systematically preserve failed interpretations, invalidations, no-trade cases or losing examples.

This uncertainty is material because a source can be rich in explanatory theory while still underrepresenting failed examples.

## 6. Incentive / marketing notes

- Wiley publisher material is formal provenance, not performance validation.
- ProfileTrading and Jim Dalton Trading are commercial education/trading businesses.
- Promotional claims about opportunities, interpretation quality or trader advantage are not evidence that a playbook is valid.

`INCENTIVE_HYGIENE=COMMERCIAL_EDUCATION_PRESENT`

## 7. Lineage / independence

`LINEAGE_STATUS=STRONG_LINEAGE_DEPENDENCE`

Lineage rule for this cluster:

```text
Steidlmayer origin / codification
-> Hawkins collaboration / application
-> Dalton expansion / popularization
-> later Market Profile educators
```

The exact historical details of every downstream branch are not frozen here, but source agreement inside this family must be discounted for dependence.

This cluster should be represented as one family in later evidence aggregation unless specific material demonstrates independent reasoning.

## 8. Observed information surface / observability compatibility

Observed source surface includes:
- Market Profile graphical organization;
- time-price structure;
- auction-process interpretation;
- volume/inventory/time-frame concepts;
- in some Steidlmayer/Hawkins material, Liquidity Data Bank / volume-related information.

Current project corpus is 1-minute OHLCV bars across concrete contracts. It does not automatically contain every original Market Profile or floor/auction information input.

`OBSERVABILITY_COMPATIBILITY=PARTIALLY_OBSERVABLE`

Project rule:
- concepts that can be causally reconstructed from point-in-time 1-minute price/volume may be candidates later;
- concepts that require unavailable volume-at-price, floor information, order-flow or other non-bar inputs must be tagged `NOT_OBSERVABLE_WITH_CURRENT_DATA` at claim level;
- never invent a bar proxy merely to make a source testable.

## 9. Source-level admission

`SOURCE_ADMISSION_CLASSIFICATION=PRIORITY_DEEP_DIVE_AS_LINEAGE_CLUSTER`

Why:
- historically important and traceable source family;
- materially different market-reading language from conventional bar-pattern sources;
- useful test of whether Human Playbook can represent auction/context reasoning;
- partial observability risk is explicit and therefore research-useful.

This classification applies to the lineage cluster, not to every downstream educator.

## 10. Open source-level questions

- Which original inputs are required by each major concept: bars, time-price distribution, volume-at-price, floor/auction information, or other data?
- How much explicit failure/no-trade material appears in the books?
- Which Dalton extensions are interpretation changes versus faithful restatements of Steidlmayer concepts?
- Which parts can be honestly represented with the accepted 1-minute corpus without changing meaning?

## 11. Current boundary

STOP HERE.

Not authorized:
- Market Profile setup extraction;
- profile level definitions;
- threshold construction;
- synthetic volume-at-price proxies presented as source-equivalent;
- backtesting;
- treating lineage agreement as independent confirmation.
