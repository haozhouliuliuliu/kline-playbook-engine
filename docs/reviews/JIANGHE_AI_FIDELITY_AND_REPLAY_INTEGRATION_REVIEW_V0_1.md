# 江河 AI 忠实度语料 + 观察/回放工程 V0.2 — 统一整合审查 V0.1

> 日期：2026-08-23
> 范围：`research/jianghe-ai-fidelity-fixtures-v01`（fidelity 语料）+ 本地 WorkBuddy
> 观察/回放实现，统一整合进 `main` 之前的 code review。
> 结论：两项成果与 V0.1 冻结基础构成单一体系；未发现需要修复的普通 bug。

## 整合对象

| 输入 | 来源 | 集成内容 |
|---|---|---|
| A. Fidelity 夹具语料 | `research/jianghe-ai-fidelity-fixtures-v01` @ `2cf678d` | 20 个合成非结果夹具、A/B/C/D/NONE、9 类硬负例、评分核心与校验 CLI |
| B. WorkBuddy 本地回放 | 保护 commit `2d885a5`（4 个文件） | `RollingMarketState` / `JiangheObservationBuilder` / `WakeScheduler` / `JiangheMarketReplaySession` / `JiangheChartRenderer` |

`src/jianghe_market_replay.py` 与 `src/jianghe_chart_renderer.py` 复用 V0.1 基础类型
（`JiangheMarketReplay`、`JiangheObservation`、`ObservationBar`、`ChartRender`、
`validate_transition` 等），`src/jianghe_fidelity_scoring.py` 复用
`JiangheDecision`/`Direction`/`StrategyFamily`；不存在第二套重复 authority。

## 审查清单

| 检查项 | 结果 |
|---|---|
| RollingMarketState：1m→5m/15m/1h 因果聚合 | 通过（桶累积 + 边界收盘） |
| 未来 K 线不可见 / 拒绝倒退或重复 | 通过 |
| partial 与 closed 明确分离 | 通过（`is_closed`、`partial_bar`、`closed_bars`） |
| 不从 1m OHLCV 伪造亚分钟序列 | 通过（分钟对齐 + 恰好 1 分钟校验） |
| Observation 为 point-in-time（决策不早于可用时间） | 通过（`earliest_decision_time`） |
| 金额 PnL 对 AI brain 默认隐藏 | 通过（观察类型无 PnL 字段） |
| 持仓/订单事实合法可见 | 通过（`positions`/`active_order_ids`） |
| AI 标注不得包装成市场事实 | 通过（`ChartOverlay`/annotations 明确为 AI 假设） |
| Renderer 固定布局 / deterministic | 通过（同一输入 → 同一文本与内容哈希） |
| 缩放只依赖当时可见数据，不用未来 high/low | 通过（只取窗口内 K 线；拒绝未来收盘） |
| AI watch/key/invalidation 标记明确为 AI hypothesis | 通过（图例 `AI hypotheses; NOT market facts`） |
| Wake：new closed bars / watch enter-exit / invalidation touch | 通过（11 种唤醒类型全部可达） |
| Wake：order/position/safety/session 外部事件 | 通过（`emit_external` 限定四种外部类型） |
| Replay 时间只能前进 | 通过（`ReplayClock` 拒绝倒流） |
| 会话内 WorkingMemory 持续，不 rewind 擦除 | 通过（归档会话、只追加追踪） |
| model latency 推迟最早 `intent_available_at` | 通过（`request_at + latency`） |
| 不计算候选 PnL / win rate / Sharpe / equity curve | 通过（全模块无此类逻辑） |
| 不使用 Development / Validation / Final outcome | 通过 |

## Fidelity 语料审查

| 检查项 | 结果 |
|---|---|
| 全部 anchors 在当前 Jianghe V1.1 authority 中存在 | 通过（`tools/validate_jianghe_ai_fidelity_corpus.py` OK，20 夹具，无污染） |
| UNKNOWN / contradiction 未被偷偷解决 | 通过（仅引用注册表条目，不填补语义） |
| no-trade 仍是一等合法结果 | 通过（NONE 夹具 + NO_TRADE 语义） |
| 无未来价格 / 盈亏污染 | 通过（污染扫描零命中） |
| `SOURCE_ONLY_VERIFIED=YES` 准确表达 | 通过（已从 `NO` 修正为 `YES`） |
| `PRIMARY_ELIGIBLE=NO` 保持 | 通过（未因 SOURCE_ONLY 通过而升级） |
| knowledge pack 身份绑定 | 绑定当前正式 V1.1 身份 `3f2ddbf9…`（内容派生、构建幂等） |

## Metadata 修正

- `docs/evidence/JIANGHE_AI_FIDELITY_FIXTURES_V0_1.json`：新增 `knowledge_pack_identity`
  （`3f2ddbf9…`）、`integration_state=INTEGRATED_NON_OUTCOME`、`integrated_on_main=YES`；
  `non_outcome_guarantee.authority` 由 `SOURCE_ONLY_VERIFIED=NO` 更新为 `YES`
  （`PRIMARY_ELIGIBLE=NO` 保持不变）。
- `docs/evidence/JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1.md`：新增
  `KNOWLEDGE_PACK_IDENTITY`、`HISTORICAL_BASELINE/HISTORICAL_BRANCH`（保留 provenance）、
  `INTEGRATION_STATE=INTEGRATED_NON_OUTCOME`；边界 `SOURCE_ONLY_VERIFIED` 更新为 `YES`。
- `docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.md`：修正陈旧的
  `KNOWLEDGE_PACK_IDENTITY=7170f0d5…` 为权威机器可读值 `3f2ddbf9…`
  （`.json` 证据两处一致且与 foundation 构建幂等一致）。

历史 provenance 保留：fixture corpus originally authored from `ebc9da7`；这不等同于当前
integrated authority 仍停在 `ebc9da7`。

## 测试与验证

```text
python -m unittest discover -s tests -v   -> 952 tests OK
python -m compileall -q src tools tests   -> OK
git diff --check                          -> OK
python tools/validate_jianghe_ai_fidelity_corpus.py -> OK
```

## 边界

本整合不创建、不启用真实模型 provider，不计算任何候选结果，不打开 Validation / Final /
Broker / 真钱。所有授权锁不变：

```text
JIANGHE_SOURCE_ONLY_VERIFIED=YES
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```
