# KNOWN_LIMITATIONS_AND_TECH_DEBT

As of: `2026-08-25`

This file tracks currently actionable limitations. Closed historical defects remain in their dedicated review/evidence authorities rather than being recopied indefinitely.

## LIMIT-012 — three-provider matched evidence

Status: `RESOLVED__THREE_PROVIDER_MATCHED_EVIDENCE_COMPLETE`

The historical matched provider evidence is complete. Historical attempts are immutable.

## LIMIT-013 — downloaded-Kline input-protocol / timeframe decision

Status: `RESOLVED__OWNER_APPROVED_V0_2_PROTOCOL`

Resolution:

- preserve `DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2`;
- add a separate 4H descriptor;
- test stack `4H / 1H / 15m / 5m`;
- 4H is background context only;
- use `SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1`;
- do not add daily/weekly/monthly in this round without stronger source-backed role evidence.

Authorities:

- `docs/reviews/JIANGHE_HIGHER_TIMEFRAME_BOUNDED_EVIDENCE_REVIEW_V0_2.md`
- `docs/reviews/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_OWNER_DECISION_V0_2.md`

## LIMIT-014 — fresh final-chance plan is not materialized

Status: `OPEN__LOCAL_CANONICAL_CORPUS_REQUIRED`

The repository contains the deterministic builder, verifier, plan spec, and tests, but not the accepted multi-million-row canonical corpus itself.

Consequences:

- no four fresh case identities yet;
- no final request payload identities yet;
- no current rate-card reservation for the new payloads yet;
- no executable paid slot.

Correct resolution:

1. run the materializer on the canonical-corpus host;
2. commit / review the resulting portable plan evidence;
3. reprice against the then-current shared ledger and provider rate-card authorities;
4. pass pre-send review;
5. only then create an explicit slot.

It is forbidden to resolve this limitation by reusing the historical V0.1 cases as if they were fresh.

## LIMIT-015 — permanent Jianghe timeframe doctrine remains unknown

Status: `OPEN__NOT_REQUIRED_FOR_CURRENT_V0_2_TEST`

Current source evidence supports a bounded 4H context role. It does not establish a permanent mandatory timeframe stack, and the current bounded review does not establish a daily/weekly/monthly role.

Do not convert the V0.2 experimental stack into permanent strategy doctrine without a separate semantic authority.
