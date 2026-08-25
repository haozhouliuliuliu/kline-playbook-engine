# kline-playbook-engine

A single-purpose China-futures AI-trader project.

Current target:

`A PERSISTENT, AUDITABLE, JIANGHE-TRAINED, EVIDENCE-IMPROVING DEEPSEEK FUTURES TRADER`

## Current product facts

- `MODEL_SOURCE = DEEPSEEK_ONLY`
- current model: `deepseek-v4-flash-vision-exp`
- Jianghe is the initial source-grounded trading foundation.
- The trader keeps project-owned persistent working memory, journal and audited experience across calls/restarts.
- DeepSeek may generate falsifiable hypotheses from experience; active policy changes require governed evidence and independent validation.
- Historical market replay is chronological and causal.
- Hard risk, broker/account truth, order lifecycle and safety remain deterministic project systems.
- Validation/holdout, shadow, broker/account and real-money lanes are locked.

## Start reading

1. `00_READ_FIRST.md`
2. `PROJECT_DIRECTION.md`
3. `PROJECT_BRAIN_RUNTIME_BRIEF.md`
4. `CURRENT_STATE.md`

## Foundation guards

- `STRICT_OUTPUT_ENUM_ENFORCEMENT = IMPLEMENTED_AND_REGRESSION_TESTED`
- `NO_4H_EXACT_VOLUME_RECONCILIATION = IMPLEMENTED_AND_REGRESSION_TESTED`

## Current engineering sequence

1. verify a pinned DeepSeek Harness build for exact model + vision + persistence + project-owned memory/tools/audit;
2. adopt Harness only if the pinned build passes project-specific verification; otherwise use the thinnest project-owned runtime shell;
3. build the smallest persistent-trader prototype;
4. run a small chronological lifecycle replay;
5. design broad historical replay and governed experience learning only after trader identity is stable.

Historical data acceptance authority:

`docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`
