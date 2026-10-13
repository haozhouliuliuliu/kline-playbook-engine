# PUBLIC RELEASE SCOPE — OWNER DECISION

`DECISION_ID = PUBLIC_RELEASE_SCOPE_2026-10-13`

Status: `OWNER_DECIDED__BINDING`

Date: `2026-10-13`

Owner instruction: repository visibility changed to public, with the capital-amount
question escalated and then decided by the Owner.

This file records the Owner's decision on what the public release does and does not
do. It owns **public-release scope only**. It must not carry current work-package,
phase, lock or next-task values — those remain owned by `CURRENT_STATE.md`.

---

## 1. Context

The repository was changed from private to public. As part of the pre-release review,
the active tree was audited for credentials, personal data, account identifiers,
internal addresses and history-only exposure.

Two items were raised to the Owner rather than resolved unilaterally:

1. **The capital-envelope amount** stated in four Owner-decision/authority documents,
   one architecture document, one evidence record and three code/test comments.
2. **The author email address** present in historical commit metadata.

## 2. Decision — capital-envelope amount

**Decided: the specific amount is removed from the active tree and is NOT removed
from Git history. Git history is preserved as-is.**

Rationale recorded for the decision:

- The amount is the Owner's private information and must not appear in the active
  tree, in current documentation, or in any future file or commit.
- Removing it from history would require rewriting this repository's history. That
  would invalidate the commit identities referenced by this project's own authority
  records (for example the frozen-head and merge-head identities recorded in
  `CURRENT_STATE.md`), and would contradict `PROJECT_GOVERNANCE.md` section 8 and the
  standing instruction to preserve project history.
- The Owner accepted the resulting historical exposure rather than break the
  authority chain.

**Therefore, precisely:**

- The active tree at `main` does not contain the amount. This is verified.
- Earlier commits **do** contain the amount and remain reachable and readable. This
  is known, accepted, and **is not an open or unresolved issue**.
- This decision concerns **history retention only**. It does **not** authorise
  reintroducing the amount into any new file, document, comment, test or commit.

Any future change that reintroduces the amount into the active tree would contradict
this decision and is not permitted without a new explicit Owner instruction.

## 3. Decision — author email in historical commit metadata

**Decided: historical commit metadata is preserved as-is; future commits use the
GitHub noreply address.**

- Historical commits authored with a personal email address remain in history.
  Rewriting them carries the same authority-chain cost as above, so they are retained.
- The local Git identity has been set to the GitHub noreply address with
  `user.useConfigOnly = true`, so that future commits do not introduce a personal
  address.
- This is likewise a **retention decision**, not an unresolved defect.

## 4. Decision — what the public release does not assert

Making this repository public is **not** a statement that:

- the system is profitable, or that it has an established long-term edge;
- the system is ready for, or authorised for, real-money execution;
- the research is complete.

It is a statement about **engineering and research process**: causal observation
discipline, separation of source truth from model hypotheses, deterministic risk
ownership, reconciliation and audit design, and governed promotion.

No paid provider execution, broker/account action or real-money action is authorised
or implied by this release.

## 5. Scope of the audit that preceded this decision

Recorded so that a later reader can tell what was and was not checked.

| Area | Scope | Result |
|---|---|---|
| Credentials | all 2,233 history blobs, all refs, 1,247 commits | no credential values; 3 pattern hits were test fixtures |
| Personal data (phone / national ID / email) | same scope | no real values |
| Broker / fund / investor account identifiers | same scope | none; matches were test fixtures and code identifiers |
| Internal network addresses | same scope | none |
| Deleted files (615 paths, still readable in history) | full content | no credentials or personal data; contains planning figures such as a spend cap |
| Local absolute paths | same scope | present (a one-character username); low severity, retained |

**Not audited / not asserted:** the suitability judgement of every historical
document for public reading. Documents that were deleted from the active tree remain
readable in history, and some contain internal planning detail. This is the same
retention trade-off as section 2 and is accepted on the same grounds.

## 6. What this file does not own

- Current work package, phase, locks, paid-slot state, next task → `CURRENT_STATE.md`
- Tool/provider status and credential seams → `TOOL_REGISTRY.md`
- Long-lived architecture → `ARCHITECTURE_BASELINE.md`
