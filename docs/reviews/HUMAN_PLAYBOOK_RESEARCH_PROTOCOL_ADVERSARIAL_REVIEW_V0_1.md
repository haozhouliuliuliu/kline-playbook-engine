# HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADVERSARIAL_REVIEW_V0_1

> Date: 2026-08-19
> Status: INDEPENDENT_ADVERSARIAL_REVIEW / ADVISORY_ONLY / NOT_FROZEN
> Reviewer role: independent adversarial reviewer. This review attacks the input package and proposes alternatives. It does NOT freeze research semantics, does NOT select a split, does NOT authorize claim extraction, backtesting, final-unseen access, or live trading.
> Reviewed package: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_1.md`
> Supporting authorities read: `AGENTS.md`, `00_READ_FIRST.md`, `OWNER_COLLABORATION_CONTRACT.md`, `CROSS_PROJECT_OPERATING_CONTRACT.md` (v3.1), `ARCHITECTURE_BASELINE.md` (Skeleton v1.0), `RESEARCH_DIRECTION.md`, `CURRENT_STATE.md`, `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`, Claim Extraction Schema v0.1, Source Dossier v0.2, Source Material Inventory, First-Wave Close-out, China-first discovery wave, and all seven first-wave source dossiers.
>
> ---
>
> ## 执行摘要（中文）
>
> 审查结论：**GO_WITH_REQUIRED_CHANGES**。
>
> 输入包的结构方向正确（来源/解释/机器化三层分离、暴露与血统继承、观测性 fail-closed、INSUFFICIENT_EVIDENCE 优先），但**按当前形态不能冻结**。存在若干如果不修改就必然会被钻空子的缺陷，其中最危险的三条是：
>
> 1. **没有“主解释优先”规则**：协议允许登记多个解释分支并做 search-freedom 记账，但没有要求在回测前预注册“最忠实来源的唯一主解释”、并以该主解释是否通过作为验收标准。结果“人说一句模糊的话 → AI 生成 20 种定义 → 挑历史最好”这条伪装数据挖掘路径依然未被堵死（对应 I、C）。
> 2. **family 专属验收门槛可被指标挑选钻空子**：先设计后预注册的 family 数值门槛就是 metric shopping。应改为固定指标菜单 + 全局统一门槛规则 + 全局最小样本量（对应 H）。
> 3. **source-example leakage 没有可执行机制**：出版物日期就是示例日期的硬上限这一规则没有被使用；视频/书中示例日期如何识别、日期未知怎么办、仅口述结果是否算 exposure 都没有可执行定义（对应 B）。
>
> 另外：24 个月、6 个产品并非 6 个独立样本（cu/al/ni 高度相关，au/ag 高度相关），有效独立样本远小于 6×24；协议应在冻结前明确这一点，并把 INSUFFICIENT_EVIDENCE 变成带预注册最小事件数的可执行规则（对应 A）。

---

## 1. REVIEW_VERDICT

**`GO_WITH_REQUIRED_CHANGES`**

理由：

- 方向与骨架（来源→解释→机器化的三层分离、血统/暴露继承、观测性 fail-closed、INSUFFICIENT_EVIDENCE 优先、反对把 validation 当设计作坊）在对抗审查后仍然成立。
- 但是存在至少 3 个 CRITICAL 级漏洞：①“主解释优先”缺失（伪装数据挖掘路径未堵死）；②family 专属验收门槛可被指标挑选（metric shopping）；③source-example leakage 无可执行识别机制且过度保守会杀死来源池。
- 这些不是架构性问题，是协议规则层面的缺口，可以在冻结前补齐。补齐最小集后即可进入 Owner freeze package。

**本审查未冻结任何内容。** 未选择 split，未抽取打法，未修改任何 research 语义。

---

## 2. CRITICAL（不修则不能冻结协议）

### C-1 — 缺少“主解释（primary interpretation）优先”规则 → 伪装数据挖掘未被堵死

- 现状：决策块 C 要求每个分支计入 search freedom，schema 也记录 `search_freedom_branch_id`，并禁止“试很多、留最佳”。但协议从未要求：在**任何回测之前**，从来源忠实度出发预注册**唯一主解释**，且验收以该主解释是否通过为准。
- 攻击路径：`人说一句模糊的话 → 登记 10 个“materially distinct”的解释分支 → 各分支配 6 个产品/多个周期/多个环境 → 全部回测 → 取表现最好的分支作为“验证了人类经验”`。当前协议只是把这些都“记账”，记账不等于阻止选择胜者。
- 反方最有力的单一论据：**“materially distinct”无法定义，也无法在测试前判定**。改一个形容词算不算 branch？AI 重新生成十次怎么办？谁能决定 material/non-material？如果这些要靠人工判断，那么所有计数都可以被“合并解释”合法化。
- 要求：协议必须增加 **PRIMARY_BRANCH 规则**：
  1. 每个 claim 在回测前必须声明唯一主解释（最忠实于来源字面/语境的解释），并对主解释的 operationalization 做哈希。
  2. 验收门槛只作用于主解释；替代分支只作为稳健性/敏感性证据，替代分支通过而主解释不通过 = 不通过（说明来源含义本身不成立）。
  3. 任何分支都必须以完全确定的 machine operationalization（特征、参数、作用域、逻辑）形式预注册；**哈希不同 = 不同 branch**，与措辞是否“看似小改”无关。
  4. 分支总数在回测前锁定并计数；对总数做多重检验校正，而不是只对“胜者”做校正。

### C-2 — family 专属数值验收门槛 = metric shopping 漏洞

- 现状：决策块 J 提出“global structural gates + family 预注册自己的 numeric gates”。表面公平（预注册），实际可被钻空子：设计者先知道自己的玩法，再挑一个它大概率能过的指标（如趋势玩法选盈亏比、震荡玩法选胜率、低样本玩法选最大回撤）。
- 要求：验收门槛改为 **非 shoppable 的公共契约**：
  1. 主指标从一个**固定菜单**选择（如“单笔净期望值（扣除成本）”、“每单位风险期望”）——菜单全局固定，family 只能选其一，且选错不能换。
  2. 门槛是**全局同一规则**（如“期望净值的下置信界 > 0 + 最小事件数”），不是 family 自定阈值。
  3. **全局最小样本量**：最小事件数、最小不同交易日数、最小产品数（或明确单一产品范围）由协议全局规定，family 不得自设。
  4. 诊断性指标允许记录，但**不参与验收**。

### C-3 — source-example leakage 没有可执行机制；过度保守会杀死来源池

- 现状：决策块 D 说“示例日期可识别则记录；不可识别但 plausibly covers 最终窗口则 fail closed”。问题：
  1. “如何识别视频/书里的日期”没有机制（视频图表坐标轴 OCR、书页图表日期、文字日期提及）。
  2. 出版日期是示例日期的**硬上限**这一关键事实未被使用。
  3. “plausibly covers”是主观判断，且把整个 family 一起 fail closed 会过度保守：一本 2026 年出版、内含 2000-2010 年图表的书会被整族污染，即使它根本没有 2024-2025 的示例。
- 要求：改用可执行且不过度保守的 **日期暴露机制**：
  1. **出版日期上限规则**：`publication_date < window_start` 的来源**不可能**展示 window 内示例（未来图表不存在），此类来源免审计、默认干净。
  2. `publication_date ≥ window_start` 的来源必须做 **示例日期清单**：图表坐标轴日期（可识别时）、文字日期提及、口述结果日期；生成该 family 的暴露日期集合。
  3. **仅口述结果、不展示图表也算 exposure**：来源说“2025 年 7 月我的方法抓到大行情”即暴露该日结果。
  4. 日期无法识别时：fail closed 只针对**该示例/该 family 的可能窗口**，不株连来源其他示例。
  5. derivative/repost 继承原内容日期 + 自身新增内容日期（暴露 = 二者并集）。

---

## 3. HIGH（应在 Owner freeze 前解决）

### H-1 — 有效样本量问题未被量化：6 个产品不是 6 个独立样本

- 24 个月、6 个产品中：cu/al/ni 为高度相关的工业金属，au/ag 为高度相关的贵金属，rb 独立度较高。有效独立“产品宇宙”可能只有 2–3 个，而非 6 个。
- 任何按“产品数 × 月份”估算的样本量都系统性高估；半年度验证/最终窗口在强相关产品上极易出现整族同向行情（如 2024 年贵金属单边）。
- 要求：冻结前至少给出**有效独立样本估计**（产品相关性 + regime 数量），并把 INSUFFICIENT_EVIDENCE 操作化为“预注册最小事件数未达标即自动判为 INSUFFICIENT_EVIDENCE”，而非事后软性判断。

### H-2 — validation 修订缺乏“实现 bug 修复 vs 研究逻辑修改”的 fail-safe 分类

- 现状：决策块 H 把“看过 validation 后任何 outcome-affecting 修改”都视为污染后代。这会让 24 个月数据下几乎所有第二版都无法验证。
- 缺口：如果 validation 只是暴露了一个纯实现 bug（如循环边界、引用错列、时区偏移），把“修复到预注册规格”与“改变研究逻辑”混为一谈会误杀。
- 要求（fail-safe 分类）：
  - **Cat-1 实现 bug 修复**：预注册规格无歧义、修复使其回归规格、逻辑未变 → 允许重跑同一 validation 一次；记录 bug + 修复；限制每 family 次数（防“我打错字了”滥用）。
  - **Cat-2 研究逻辑修改 / 看到结果后消歧**：视为新后代，继承暴露，同一 validation 不再视为 fresh confirmation（即当前协议规则）。
  - **Cat-3 规格本身有歧义、只有看到结果才能消歧**：一律按 Cat-2 处理，不允许“选一个能过的解释”。
  - 默认：无法明确归入 Cat-1 的，一律 Cat-2。

### H-3 — final-unseen 需要 quarantine / invalidate 机制与“失败后可学什么”的明确定义

- 现状：final fail = reject/defer；final 结果不可用于调参重跑。对，但缺：
  1. **实现 bug 导致的 final failure**：需要 void 机制——若 final 失败可证明为实现 bug（规格一致修复），结果标记 `FINAL_RESULT_VOID_IMPLEMENTATION_DEFECT`，family 不得重跑同一窗口（窗口已暴露），但可等待新的 unseen cohort（Shadow/Forward）再考。
  2. **失败后可学什么**：可学到“该预注册假设未在该窗口存活”——这是考试本身的目的；但任何受 final 失败启发的新假设都是新 family/lineage，且该 final 窗口对它永不再 unseen。协议应把“final 后生成的新假设只能靠 Shadow/Forward 获得新鲜证据”写成显式规则。
  3. **单次 final 窗口的 false rejection 风险**：6 个月、强相关产品的单次 final 是一次抽样；应把 final 结果解读为“该窗口的一次考试”，不承诺终身有效，也不把单次通过当作永真。

### H-4 — lineage 检测缺少“区分性机制签名”规则（换名/相似洗白）

- 现状：协议禁止改名重置暴露、teacher/student 默认非独立。但：
  1. “trader A 学了 B 但不承认”无法靠自报检测；需按**材料证据**（非通用结构、独特词汇指纹、引用、时序）判定，而非靠承认。
  2. 多本书共同源自更早经典技术分析——若把“共同祖先”当血统，则所有技术分析都塌缩成一个 family、毫无独立性。需要区分**通用语言**（趋势线、支撑阻力，不算血统）与**区分性机制签名**（特定非平凡规则构造，算血统）。
  3. “两个表面不同 setup 底层信息相同”（如 20-bar 新高突破 vs 加成交量过滤）应按信息相关性判为同一 family 的变体，而非两个独立确认；相关性检查应在信息层，不只是 PnL 相关。
- 要求：family/lineage 绑定使用**机制签名哈希**而非名称；相似度超过阈值即继承暴露。

### H-5 — observability surrogate 缺少“来源论证而非回测选择”规则

- 现状：决策块 E 允许 surrogate 作为新的 INFERRED 解释，但“如何判断 surrogate 保持意义”未定义。
- 要求：
  1. surrogate 必须由**来源所述观察面**论证（交易者说他看的是什么），并证明可从 point-in-time 可得数据因果重建；不允许“试一堆 proxy 留最佳”（那是 feature mining）。
  2. 每个 surrogate = 一个 branch，计入 search freedom。
  3. 过度保守的代价是很多人类知识永远不可测——这是可接受的诚实结果，但协议应统计“因不可观测而被搁置的 playbook 比例”，让成本可见。

### H-6 — search-freedom 计数缺少“先枚举、哈希、全数计入”的可审计规则

- 现状：schema 有 branch_id，但计数规则未锁定。
- 要求：
  1. 所有分支在**任何回测前**一次性枚举，操作化哈希后锁定（不可事后增删）。
  2. 人工“合并解释”发生在计数之后，不减少预注册分支数。
  3. prompt 改变 = 搜索自由度变化：枚举必须在钉死的 prompt/规格下进行。
  4. 多重检验校正基于**总分支数 × 总测试组合数**，而非胜者。

---

## 4. MEDIUM（可进入后续实施阶段再解决）

- **M-1 — 12/6/6、10/8/6、rolling 的季节/regime 浓度**：任意半年窗口都会捕获特定季节性（中国商品季节性明显）与单一宏观 regime（2024 贵金属单边 vs 2025 分化）。应在冻结协议时把各窗口的 regime 描述（波动率、趋势强度、产品相关性）写成证据，供解读结果。
- **M-2 — exposure 状态词表在 split 冻结前保持占位**：`FINAL_UNSEEN_LOCKED/EXPOSED` 等 6 值目前是 placeholder；split 冻结时应一并定义精确语义，避免两套词表。
- **M-3 — 中国 derivative 来源的暴露继承**：王少多/张亚楠等 derivative 访谈若提升，其暴露 = 原始 QHRB 内容日期 + 七禾网整理日期；需在提升前完成。
- **M-4 — source-example 日期识别工具**：图表日期 OCR / 视频帧日期提取 / 文字日期抽取目前均未验证为项目能力；应在需要审计首批 high-risk 来源前验证最小能力。
- **M-5 — INSUFFICIENT_EVIDENCE 的“退出路径”**：判为 INSUFFICIENT_EVIDENCE 后，family 是等待 Shadow/Forward、还是封存、还是允许换产品/周期重试（重试即新 search freedom）？需要后续定义。

---

## 5. OVER_GOVERNANCE（可能复杂过头、应删减）

- **5.1 过度精确的字段**：
  - schema 中 `source_context_before_after` + `source_excerpt_short` + `source_paraphrase` 三者全填对每个 EXPLICIT claim 过重；建议 EXPLICIT 只需 anchor + 短摘 + 释义之一 + 上下文标记。
  - 每个 claim 都填满 ~35 字段是假精确；应允许惰性填写（只填相关的，其余 `UNKNOWN`）。
- **5.2 逐 claim 的 exposure 全矩阵**：对每个 claim 记录 6 值 exposure 状态过重；建议 exposure 在 family 级记录 + 例外日期清单，claim 级只继承引用。
- **5.3 概念桶过多**：决策块 A–J 可压缩为 5 个概念桶：①来源/claim；②解释/搜索；③暴露/血统；④观测性；⑤验收/考试（validation+final）。更少的概念桶减少流程摩擦，不降低安全性。
- **5.4 “3+2+1” 已正确降级**：保留为启发式，不入冻结协议（这是对的，别退回）。
- **5.5 简化且不降安全的项**：source 数值评分（已拒绝，保持拒绝）；per-field claim_status 全量标注（只对核心字段）；过多 exposure 枚举细分（split 冻结前保留占位即可）。
- 注意：过度删减会重新打开 C-1/C-2 的洞。**可删的是表单负担，不可删的是 PRIMARY 规则、公共验收契约、枚举锁定。**

---

## 6. SPLIT_REVIEW（独立评价，不替 Owner 决定）

### G1 — 12/6/6（dev=2024, val=2025H1, final=2025H2）
- 优点：简单、可审计、暴露记账容易。
- 弱点：
  - 6 个月 validation/final 对稀疏 playbook 统计能力很弱；
  - 半年窗口集中季节性 + 单一 regime；
  - H2-2025 作为 final：如果 2025H2 是贵金属/工业金属的同向行情，一次 final 通过的意义有限，一次失败也可能是 false rejection；
  - 任何 2025-07 后发布的来源都可能污染 H2-2025（见 C-3 出版日期规则）。

### G2 — 10/8/6（dev=10mo, val=8mo, final=6mo）
- 优点：validation 历史多 2 个月（相对 G1 多 33%），对中等频率 playbook 有实际意义；final 仍保持 6 个月。
- 弱点：
  - dev 只有 10 个月，对上下文型/低频 playbook 的开发数据更少；
  - 日历边界不直观（11 月、8 月这种中途切点）；
  - final 仍是 6 个月，季节/regime 浓度问题不变。

### G3 — rolling/blocked validation
- 优点：validation 内稳定性诊断更丰富。
- 弱点（在 24 个月、强相关产品下尤其明显）：
  - 反复滚动 = 同一段历史被多次“看”，本身就是搜索自由度放大；
  - 极易把 validation 变成 development（滚动调参）；
  - 24 个月太短，滚不出有意义的多个独立块（有效块数 ~2–3）。
- 独立判断：**G3 在当前数据量下风险大于收益**，不建议作为主方案；若 Owner 选择 G3，必须预注册块数、块切点、聚合规则，并把每次滚动视为一次 look。

### 独立评价（不给结论，给约束）
- 三者都无法解决根本问题：24 个月、有效独立样本少、单 regime 覆盖。**split 是二阶问题，一阶问题是“事件数/有效样本是否足够”与 INSUFFICIENT_EVIDENCE 的操作化。**
- 无论选哪个，都必须：① 按有效独立样本（产品相关性修正后）设预注册最小事件数；② final 结果按“单窗口一次考试”解读；③ 把 Shadow/Forward 作为修订与最终确认的主路径写入协议。

---

## 7. SOURCE_EXPOSURE_REVIEW（source-example leakage 的可执行方案）

提出可执行的替代设计（替代当前“plausibly covers → fail closed”的主观规则）：

1. **出版日期硬上限**：`publication/upload date < 2024-01-01` → 结构上不可能包含窗口内图表 → 免审计、默认干净。这是唯一完全客观的边界。
2. **出版日期在窗口内或之后** → 必须生成**示例日期清单**：
   - 图表：可识别的坐标轴日期；
   - 文字：日期提及；
   - 视频：画面日期 / 口述日期。
   - 清单 = family 暴露日期集合的组成部分。
3. **口述结果即暴露**：不展示图表只讲“某日大行情”同样记录为该日期 exposure。
4. **日期未知**：fail closed 仅针对该示例可能覆盖的窗口，不株连来源的其他示例。
5. **derivative/repost**：暴露 = 原内容日期 ∪ 新增内容日期。
6. **血统继承**：family 暴露 = 其血统内所有材料暴露日期的并集（与现有暴露继承一致）。
7. **过度保守的对策**：出版日期规则让大多数 pre-2024 来源自动干净；只有出版日期 ≥ window_start 的来源需要做日期清单，从而避免“整族全部污染”。

---

## 8. SEARCH_FREEDOM_REVIEW（AI interpretation branch 的可审计规则）

1. **Branch = machine operationalization 的哈希**：两个解释若哈希相同则同一 branch（措辞不同、操作化相同 → 不新增）；哈希不同则不同 branch（措辞看似小改、操作化不同 → 新增）。这消除了“改个形容词算不算”的主观性。
2. **主解释优先**：回测前声明唯一主解释；验收只看主解释。
3. **先枚举后锁定**：所有分支在任何回测前一次性枚举并哈希；事后增删即新 lineage/继承暴露。
4. **合并不减少计数**：人工“合并解释”发生在计数之后，多重检验校正基于预注册分支总数。
5. **prompt 变化 = 搜索变化**：枚举必须在钉死 prompt/规格下进行；改 prompt = 新枚举事件。
6. **检测“先看结果再选解释”**：唯一防御是 pre-registration + 哈希 + 时间戳；任何不在预注册集合中的解释自动视为已暴露后代。
7. **多重检验校正基于总数**：`总分支数 × 产品/周期/环境组合数`，而非胜者单个。

---

## 9. VALIDATION_FINAL_REVIEW（validation/final 污染修订建议）

### validation 侧
- 采纳 fail-safe 分类（H-2）：Cat-1 实现 bug 修复（规格一致、限次重跑同一 validation）；Cat-2 逻辑修改/消歧（新后代、继承暴露、同一 validation 不再 fresh）；Cat-3 规格歧义 → 一律 Cat-2。无法分类者默认 Cat-2。
- 明确代价：24 个月数据下，**一个 family 每个数据 epoch 实质上只有一次干净的 validation 考试机会**；开发期必须把调试做足，protocol 应把这一事实写进风险声明。

### final 侧
- 状态机：`FINAL_UNSEEN_LOCKED → FINAL_EXPOSED → FINAL_ACCEPTED | FINAL_REJECTED | FINAL_VOID_IMPLEMENTATION_DEFECT（→ 等待新 unseen cohort）`。
- 窗口暴露不可逆：一旦查看，该窗口对该 family 及后代永不再 unseen；void 只改变结论（reject → inconclusive/defect），不撤销暴露。
- 禁止“看了 final 调一调再跑同一窗口”——协议已禁止，本审查确认并强化：受 final 启发的新假设只能通过 Shadow/Forward 获得新鲜证据。

---

## 10. MINIMUM_REQUIRED_CHANGES（最少改哪些即可进入 Owner freeze package）

1. **加入 PRIMARY_BRANCH 规则**（C-1）：预注册唯一主解释 + 验收只看主解释 + 分支以操作化哈希定义 + 回测前锁定枚举。这是把“人类经验验证”与“伪装挖掘”区分开的**最关键**一条。
2. **把 family 数值门槛换成公共验收契约**（C-2）：固定指标菜单 + 全局统一门槛规则 + 全局最小样本量；诊断指标不计入验收。
3. **引入出版日期硬上限 + 示例日期清单的暴露机制**（C-3）：替代“plausibly covers → fail closed”。
4. **INSUFFICIENT_EVIDENCE 操作化**（H-1）：按有效独立样本设预注册最小事件数，不达标自动判 INSUFFICIENT_EVIDENCE；在冻结协议中承认 6 产品并非 6 独立样本。
5. **validation/final fail-safe 分类 + final 状态机**（H-2/H-3）：Cat-1 限次 bug 修复、Cat-2 默认；final void/invalidate 机制。
6. **lineage 机制签名规则**（H-4）：family 绑定按机制签名哈希，通用语言不算血统，信息层相关性检查。
7. **surrogate 来源论证规则 + search-freedom 枚举锁定**（H-5/H-6）。

这 7 条可以在不重写架构、不推翻现有来源层/claim schema 的前提下，作为输入包 v0.2 的修订内容进入 Owner freeze package。

---

## 11. STRONGEST_ARGUMENT_AGAINST_HUMAN_PLAYBOOK_FIRST

> 你能想象到的最强反方论证：

在 24 个月、6 个强相关产品、单一宏观 regime 的数据上，Human Playbook First 的“忠实验证人类经验”目标在统计上很可能**做不到**：要么诚实地得到大量 `INSUFFICIENT_EVIDENCE`（因为有效独立样本太少、稀疏 playbook 事件数不足、单次 6 个月 final 只是一次抽样），要么为了产出“验收过的 playbook”而系统性地滑向“挑一个能过的解释/能过的指标/能过的窗口”——即**换皮的指标挖掘**。

更糟的是：本书/课程来源几乎都是事后出版、面向美国市场的解释性材料，其“人类经验”本身混杂了幸存者偏差、营销激励与事后叙述（source dossier 已承认这一点）。把一个本来就可能不存在的“经验”用 24 个月数据去“验证”，得到“经验有效”的结论，其可信度上限就是那 24 个月 + 那 6 个产品；而这个上限远不足以支撑“验证了人类经验”这种高姿态结论。换句话说：**这个范式在数据规模上承诺了它无法兑现的证据强度，而协议设计上的每个防挖掘补丁都在对抗这个根本性的样本不足。**

---

## 12. STRONGEST_ARGUMENT_FOR_HUMAN_PLAYBOOK_FIRST

> 在当前架构约束下它仍然值得做的最强理由：

本项目的替代默认路线（大范围指标/规则/参数挖掘并按历史 PnL 排序）在 `ARCHITECTURE_BASELINE.md` / `RESEARCH_DIRECTION.md` 中已被明确禁止，而且它在 24 个月数据上只会更糟（搜索空间无限、多重检验灾难）。Human Playbook First 的价值不在于“用 24 个月证明某个打法定能盈利”，而在于：

1. **把无界搜索变成有界假设检验**：每个 playbook 是一个有来源、可归因、可证伪的预注册假设；总测试负担 = playbook 数量 × 有限分支，而不是组合规则空间。这让多重检验校正第一次变得可行。
2. **产出可累积的负证据与基础设施**：即使大部分 playbook 判为 `INSUFFICIENT_EVIDENCE` 或 rejected，协议也会产出“该来源的该打法定量上未能存活”的诚实结论 + 一套可复用的 来源/解释/暴露/验收 流水线。这套流水线是后续 Shadow/Forward 数据成熟时真正研究价值的主要载体。
3. **符合产品的真实约束**：clean-room、可归因人类经验、live 关键路径不依赖 LLM、验收门槛必须防过拟合——Human Playbook First 是唯一能把这些约束同时满足的路线；在数据不足时它正确地选择“不做结论”而非“造假结论”。
4. **成长路径清晰**：24 个月只是第一个 epoch；Shadow/Forward 会给修订与再确认提供真正 unseen 的证据，这正是本协议反复强调的。

一句话：**在“必须可归因、必须防挖掘、数据暂时不够”这三重约束下，Human Playbook First 是唯一同时诚实且可积累的路线——前提是修掉 C-1/C-2/C-3。**

---

## 附：技术债/限制的阻截阶段（对应第四节）

- **TD-001**（session/trading-day 双重责任）：在协议冻结阶段不是 blocker；在**首次 confirmatory validation 的时序/事件定义开始承载 PnL 证据时**成为 blocker。
- **TD-002**（部分平仓未实现 PnL 简化）：在**首份依赖 PnL 的 confirmatory 验收证据**成为 blocker。
- **LIMIT-001**（历史涨跌停元数据）：在**任一 playbook 声称涉及涨跌停非成交真实性**（如 rb、以及可能触及涨跌停的品种）时成为 blocker。
- 结论：三者都应在**首批 playbook 进入 confirmatory 验收**阶段前解决，而**不是**在协议/日期冻结阶段。当前阶段无需工程大改，这与本审查的“不要提前要求无关大改”约束一致。

## 附：审查边界确认

- 本审查只新增 review evidence，未修改 `RESEARCH_DIRECTION.md`、`ARCHITECTURE_BASELINE.md`、`CURRENT_STATE.md`、protocol input package、claim schema、source dossier 的语义。
- 未冻结任何协议/split；未抽取具体交易打法；未回测；未触碰 final-unseen。
- 未提交任何“accepted/frozen”状态。
