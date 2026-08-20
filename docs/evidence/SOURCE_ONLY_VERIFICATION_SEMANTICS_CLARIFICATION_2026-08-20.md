# SOURCE_ONLY_VERIFICATION_SEMANTICS_CLARIFICATION_2026-08-20

> Date: 2026-08-20
> Status: ACTIVE / CANONICAL CLARIFICATION (does not rewrite history)
> Package: F — source-evidence hardening (S-04)
> Authority: `docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md`
> Outcome access: NONE — no candidate outcome data was used to produce this document.

## 1. Purpose and boundary

This document is a **prospective clarification** of what the historical
`SOURCE_ONLY_VERIFIED=YES` flag means and, equally importantly, what it does not
prove. It deliberately does **not** rewrite any historical evidence JSON, does
not retract a recorded verification, and does not add new verification claims.

Historical artifacts that record `SOURCE_ONLY_VERIFIED=YES` remain historical
records. Their wording is not edited.

## 2. What historical `SOURCE_ONLY_VERIFIED=YES` means

```text
HISTORICAL_MEANING=PROJECT_API_SESSION_MECHANISM_REPORTED_VERIFIED
```

A historical `SOURCE_ONLY_VERIFIED=YES` means that, at the time it was recorded,
the project API/session mechanism reported the session as verified under the
controls that were then implemented. It is a truthful record of what the
then-current mechanism reported.

## 3. What historical `SOURCE_ONLY_VERIFIED=YES` does NOT prove

```text
NOT_PROOF_OF_OS_PROCESS_SANDBOX=YES
NOT_PROOF_OF_NO_SHELL_OR_FILE_ACCESS=YES
NOT_PROOF_OF_OLD_TOKEN_UNFORGEABILITY=YES
```

The historical flag does not prove:

- that the worker ran inside an OS/process sandbox;
- that the worker had no shell, repository, or file-system access;
- that any historical deterministic verification token was cryptographically
  unforgeable.

These are stronger guarantees than "the project API/session mechanism reported
verified". They were not established by the historical flag.

## 4. Package B prospectively closed the fixed-nonce forge path

```text
PACKAGE_B_FIXED_NONCE_FORGE_PATH_CLOSED=PROSPECTIVE
OLD_DETERMINISTIC_TOKEN_FORGEABLE_AS_IMPLEMENTED=YES
```

The second-pass audit found (F-10) that the earlier SOURCE_ONLY verification
evidence was reproducible from public deterministic inputs. Package B closed
this path **prospectively**:

- `open_verified_session()` is the only path that issues verification; the token
  is drawn from a cryptographically secure random source;
- `record_session()` can never promote a manually constructed session to
  verified;
- `is_verified()` accepts only project-issued sessions whose stored identity
  exactly matches the issued identity.

This does **not** retroactively prove that older deterministic tokens were
unforgeable. It only means that going forward the fixed-nonce forge path is
closed.

## 5. Protected-period market-outcome API remained technically denied

```text
SOURCE_ONLY_PROTECTED_MARKET_OUTCOME_API=DENIED_AT_ALL_TIMES
TECHNICAL_DENIAL_RETAINED=YES
```

The SOURCE_ONLY surface has never exposed a protected-period project
market-outcome retrieval path. The only market-outcome-related entry point
always returned `DENIED` / `SOURCE_ONLY_TECHNICAL_DENIAL` and audited the
attempt. This remains true in the current implementation.

The API-level denial is a mechanism fact. It is not, by itself, proof that a
worker with broader shell/repository access could not have accessed protected
data through some other path.

## 6. No evidence of actual prior candidate-outcome access

```text
EVIDENCE_OF_PRIOR_WORKER_ACCESSING_CANDIDATE_OUTCOMES=FOUND_NONE
```

The audit found no evidence that any prior worker actually accessed candidate
market outcomes. The clarification of what the verification flag proves must not
be misread as evidence that protected data was accessed.

## 7. Scope of code/docstring changes

Per the Package F repair spec (S-04), current code/docstrings are updated **only**
where they still clearly present API-level verification as a stronger guarantee
than it is. Concretely, in `src/research_firewall.py`:

- the `SourceOnlyPolicy` class docstring now states the S-04 boundary: project
  verification is not a claim of OS/process isolation, no-shell/file-access, or
  historical token unforgeability;
- the issued-verified registry comment now qualifies the "not reproducible from
  a public fixed formula" statement as a prospective Package B hardening that
  does not prove historical tokens were unforgeable and does not make
  SOURCE_ONLY an OS/process sandbox.

No historical evidence JSON was modified.

## 8. Prospective material-bound sessions (F-C01)

Prospective material-bound SOURCE_ONLY sessions bind the deterministic
material-derived bundle binding identity/hash (`session_binding_identity` /
`session_binding_hash`); historical sessions are not retroactively upgraded.
The historical recorded bundle id/hash remain historical metadata only and are
never treated as byte proof.
