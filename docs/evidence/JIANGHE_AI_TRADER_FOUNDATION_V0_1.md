# 江河 AI 交易员基础 V0.1

状态：已实现的无结果基础；模型推理与真实行情连接均未实现。

## 交付物

- `src/jianghe_ai_trader.py`：知识包和 AI 身份、因果 Observation、观察区、追加式工作记忆、紧凑决策、受约束交易意图、审计记录、单向回放时钟、厂商中立协议与失败闭合默认提供者。
- `tools/build_jianghe_knowledge_pack_v0_1.py`：从江河 V1.1 的权威内容构建确定性知识包身份。
- `docs/evidence/JIANGHE_AI_TRADER_FOUNDATION_V0_1.json`：构建产物，记录当前知识包内容哈希。
- `tests/test_jianghe_ai_trader_foundation.py`：仅合成夹具；不读取候选行情或收益。

## 已验证边界

```text
FUTURE_BAR_DENIED=YES
AVAILABLE_AT_CAUSAL_CUTOFF=YES
PARTIAL_BAR_EXPLICIT_AND_HISTORICAL_REPLAY_DENIED=YES
P_AND_L_EXCLUDED_FROM_OBSERVATION=YES
POSITION_AND_ORDER_FACTS_AVAILABLE=YES
KNOWLEDGE_CONTENT_CHANGE_CHANGES_IDENTITY=YES
CWD_PATH_MTIME_NOT_IN_IDENTITY=YES
MEMORY_MUTATION_AUDITED=YES
MODEL_LATENCY_PREVENTS_TIME_TRAVEL=YES
REAL_MODEL_PROVIDER=FAIL_CLOSED
```

## 江河 SOURCE_ONLY 状态

V1.1 的“完整二次梳理”证明来源覆盖，不等于 SOURCE_ONLY 验证。当前仍为：

```text
FINAL_SOURCE_DISTILLATION=COMPLETE_AFTER_EXHAUSTIVE_SECOND_PASS
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
```

精确下一门：必须在项目 `SourceOnlyPolicy` 下，为这个内容绑定的江河知识包建立新的已验证 SOURCE_ONLY 会话，并持久记录模型身份、提示词规格、知识包身份/哈希、检索模式、技术拒绝受保护市场结果的证据与暴露说明。随后仍须按研究协议处理 claim/PRIMARY；本基础包不提升任何状态。

## 未授权事项

候选结果、Validation、Final、真实 Shadow、Broker、真钱、API 密钥、模型厂商采纳均未执行且仍未授权。
