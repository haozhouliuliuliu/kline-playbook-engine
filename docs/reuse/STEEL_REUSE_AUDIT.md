# steel-radar-lite 清洁室复用审计

审计日期：2026-08-16
新项目：`C:\Users\H\Documents\kline-playbook-engine`
旧项目（只读）：`C:\Users\H\Documents\steel-radar-lite`
旧项目工作树 HEAD：`84c7679445f49d86a66ab53581b99d039f385a4a`
历史候选提交：`2c895f90a0b1a4f7f519fb7708018a147c9d6aaf`
只读备份：`D:\SecureLocalBackups\steel-radar-lite\tqsdk-professional-data-gate\20260813`

## 审计边界

- 旧项目和备份仅是候选材料，不是本项目权威。
- 未读取、未复制旧项目未跟踪文件 `exports/V6_HISTORICAL_36_IAR_REVIEW_PACKET.md`。
- 不继承策略结论、参数、阈值、Track A/B 或 Gate1 语义、历史结果、主力合约规则、风险规则、运行状态、凭据或前瞻证据。
- 下表每项只使用一种规定分类：`REUSE_CANDIDATE`、`BORROW_TEST_OR_DESIGN`、`DO_NOT_REUSE`、`DEFER`。
- 本次分类在任何旧项目代码复制之前完成。本包最终选择独立实现项目自有接口，不复制旧项目源码。

## 逐项分类

| 来源（提交/指纹） | 分类 | 通用性与旧项目耦合 | 是否允许复制 | 可借鉴的测试或设计 | 本项目最终使用决定 |
| --- | --- | --- | --- | --- | --- |
| `steel_radar_lite/historical_replay/lane.py` @ `84c7679` | DO_NOT_REUSE | 同时绑定 RB、虚拟日期、Track A/B、冻结配置和旧回放证据布局；不是通用历史数据层 | 否 | 仅确认“源 K 线时间不能直接当完成可见时间”的失败类别 | 不复制；由现有 `CompletedBar` 独立承担可见性 |
| `steel_radar_lite/historical_replay/launcher_lifecycle.py` @ `84c7679` | DO_NOT_REUSE | 绑定四个预注册样本、旧提交、旧运行目录和 Track 生命周期 | 否 | 凭据不落盘、子进程输出脱敏、失败不盲重试 | 不进入本包 |
| `tests/test_historical_replay_lane.py` @ `84c7679` | BORROW_TEST_OR_DESIGN | 测试本身绑定 RB、虚拟日期、Track A/B 和旧配置 | 否 | 重复/逆序拒绝、夜盘归属、完成时点前不可见、重复运行确定性 | 在新接口上独立重写行为测试 |
| `steel_radar_lite/tick_aggregator.py` @ `84c7679` | BORROW_TEST_OR_DESIGN | 聚合逻辑硬编码 SimNow、5 分钟和旧 JSONL 布局；不适合历史供应商中立接口 | 否 | `partial` 与 `reconnect_gap` 分离；不静默补缺 | 继续使用本项目已有 `BarQuality`，不复制聚合器 |
| `tests/test_simnow_package1.py` @ `84c7679` | BORROW_TEST_OR_DESIGN | 大量绑定 CTP/SimNow、RB 面板和旧运行协议 | 否 | 断线、部分 K 线、确定关闭、重复与缺口类别 | 仅借鉴质量分类，不引入网关代码 |
| `steel_radar_lite/gate1_external_evidence.py` @ `84c7679` | BORROW_TEST_OR_DESIGN | SHFE 年度 ZIP 解析片段可泛化，但整个文件绑定 RB、Gate1、主力选择、规则和研究资格结论 | 否 | ZIP 成员枚举、原始 SHA256、来源 URL 白名单、解析器版本进入清单 | 本包只借鉴清单字段；不复制 Gate1 解析链 |
| `scripts/import_gate1_external_evidence.py` @ `84c7679` | DO_NOT_REUSE | 纯 Gate1 入口并调用旧项目最终器 | 否 | 无 | 不使用 |
| `docs/experiments/GATE1_HISTORICAL_RAW_MANIFEST_2026-08-10.json` @ `84c7679` | BORROW_TEST_OR_DESIGN | 来源清单字段可借鉴，但范围和结论是 RB/Gate1 专属 | 否 | URL、检索时间、大小、SHA256、覆盖、内容类型 | 仅将三个官方 URL 和旧哈希作为待重验线索；不复制旧结论 |
| `docs/experiments/GATE1_DATASET_INVENTORY_V2_2026-08-10.json` @ `84c7679` | BORROW_TEST_OR_DESIGN | 含旧项目 8,677 行数据集、Gate1 资格和主力映射状态 | 否 | 区分来源、PIT、合约映射和覆盖状态 | 不导入数据、不继承资格或结果 |
| `package2/tqsdk_compat_proof/normalizer.py` @ `2c895f9` | REUSE_CANDIDATE | 数值、时间戳、排序检查较通用；但硬编码 5 分钟、日盘时段，会推断交易日并静默丢弃重复项 | 仅允许经新接口改写；本包不直接复制 | 纳秒时间戳、有限数值、OHLC/OI 字段及逆序计数的测试类别 | 独立实现；`SessionMetadata` 和失败关闭规则优先 |
| `package2/tqsdk_compat_proof/api_inventory.py` @ `2c895f9` | DEFER | 静态源码盘点较通用，但覆盖交易能力且不能证明账号权限或真实历史数据 | 否 | 安装版本与实际调用要分开记录 | 本包用官方资料和真实探针，不引入盘点器 |
| `package2/tqsdk_compat_proof/rollback_check.py` @ `2c895f9` | DO_NOT_REUSE | 绑定旧仓库、旧提交和旧工作树布局 | 否 | 隔离临时环境的原则 | 不使用 |
| `package2/tqsdk_compat_proof/parity.py` @ `2c895f9` | DO_NOT_REUSE | RB、5 分钟、DAY_ONLY 和旧字段语义耦合 | 否 | 无可直接继承的事实 | 不使用 |
| `package2/tqsdk_compat_proof/strategy_bridge.py` @ `2c895f9` | DO_NOT_REUSE | 直接桥接旧策略、冻结配置和策略结果 | 否 | 无 | 不读取其结果、不使用 |
| `scripts/run-tqsdk-compat-proof.ps1` @ `2c895f9` | DO_NOT_REUSE | 绑定旧备份路径、旧工作树和旧证明入口 | 否 | 临时虚拟环境应与项目依赖隔离 | 不使用 |
| `tqsdk_professional_data_gate.py`，备份 SHA256 `d6ab10ff...` | BORROW_TEST_OR_DESIGN | 真实静态 API 探针结构可借鉴；合约样本与结论属于旧项目 | 否 | 限定查询、只记录无秘密参数、关闭 API、模式与时段检查 | 新项目只实现安全的独立探针入口 |
| `run_tqsdk_professional_data_gate.ps1`，备份 SHA256 `04da68b0...` | BORROW_TEST_OR_DESIGN | 交互凭据输入和清理较通用，路径和运行器属于旧项目 | 否 | 凭据不写命令行、不落盘、不进入输出 | 新项目如需认证，只允许本地交互或已有安全机制 |
| `entitlement.json`、`kline-probe.json`、`tick-probe.json`、`final-verdict.json`，备份目录 | DEFER | 证明旧项目曾取得具体 RB 合约数据；不能证明当前安装、当前账号权限、当前版本或本项目可用性 | 否 | 旧 API 名称和候选字段仅用于重新核对 | 不继承 VERIFIED；版本归属存在冲突，必须以本项目真实探针为准 |
| `session-causality.md`，备份 SHA256 `a5edf3ad...` | BORROW_TEST_OR_DESIGN | 描述旧版 TqSdk 时间字段；不是当前运行证据 | 否 | K 线 `datetime` 为区间起点，需加周期得到保守完成时点 | 仅作为失败用例线索，最终依据当前官方文档与本项目探针 |
| `track-ab-schema-map.md` 和备份内 Track 相关材料 | DO_NOT_REUSE | 明确绑定 Track A/B 研究语义 | 否 | 无 | 不使用 |
| 备份内 `official-skill/tqsdk-trading-and-data*` | DEFER | 是旧时点官方资料副本，可能过期 | 否 | 无 | 直接核对当前官方文档，不使用备份副本 |

## 审计结论

1. 没有旧项目源码被直接复制到新项目。
2. 新项目只借鉴通用测试类别和清单字段，并通过自己的公开接口重新实现、重新测试。
3. 旧备份中出现的 TqSdk 版本声明不作为本项目事实；本任务明确要求重新验证当前运行版本和权限。
4. 三个 SHFE 年度 ZIP 只作为官方日度/统计数据候选，不得描述为分钟或 Tick 数据，也不得把旧归一化数据当作本项目原始真相。
