# kline-playbook-engine

A single-purpose China-futures AI-trader project.

Current target:

`A PERSISTENT, AUDITABLE, JIANGHE-TRAINED, EVIDENCE-IMPROVING DEEPSEEK FUTURES TRADER`

## Current product facts

- DeepSeek is the only active model source.
- Jianghe is the initial source-grounded trading foundation.
- The trader is intended to keep persistent working memory, journal and audited experience across calls/restarts.
- DeepSeek may propose new hypotheses from experience, but cannot rewrite Jianghe source truth or promote an unvalidated rule into active policy.
- Historical market replay must be chronological and causal.
- Hard risk, broker/account truth, order lifecycle and safety remain deterministic/project-owned.
- Validation/holdout, shadow, broker/account and real-money lanes are currently locked.

## Start reading

1. `00_READ_FIRST.md`
2. `PROJECT_DIRECTION.md`
3. `PROJECT_BRAIN_RUNTIME_BRIEF.md`
4. `CURRENT_STATE.md`

Do not start from old Git history or deleted superseded plans unless performing a specific forensic task.

## Current engineering sequence

1. harden the two observed DeepSeek mechanical failure modes;
2. verify a pinned DeepSeek Harness build for exact model + vision + persistence + project-owned memory/tools/audit;
3. build the smallest persistent-trader prototype;
4. run a small chronological lifecycle replay;
5. only then design broad historical replay and governed experience learning.

Historical data acceptance authority:

`docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`
