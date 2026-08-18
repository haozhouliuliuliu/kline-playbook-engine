# HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_DELTA_ADVERSARIAL_REVIEW_V0_1

> Date: 2026-08-19
> Status: INDEPENDENT_TARGETED_DELTA_ADVERSARIAL_REVIEW / ADVISORY_ONLY / NOT_FROZEN
> Reviewer role: independent adversarial reviewer. This review attacks ONLY the three new pre-freeze gaps identified by the Owner final recap, plus their cross-gap interaction. It does NOT reopen Skeleton v1.0 or the Human Playbook First direction. It does NOT freeze any protocol, does NOT select a concrete playbook/split, does NOT backtest, does NOT access final-holdout, and does NOT modify live AI semantics.
> Reviewed gap authority: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_FINAL_PREFREEZE_GAP_REVIEW_V0_1.md`
> Reviewed freeze candidate: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_2.md`
> Prior independent review: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADVERSARIAL_REVIEW_V0_1.md`
> Prior adjudication: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADJUDICATION_V0_1.md`
> Owner decision package (HOLD pending this review): `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_DECISION_PACKAGE_V0_1.md`
> Claim schema: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V0_1.md`
> Supporting authorities read: `AGENTS.md`, `00_READ_FIRST.md`, `OWNER_COLLABORATION_CONTRACT.md`, `CROSS_PROJECT_OPERATING_CONTRACT.md` (v3.1), `ARCHITECTURE_BASELINE.md` (Skeleton v1.0), `RESEARCH_DIRECTION.md`, `CURRENT_STATE.md`, `TOOL_REGISTRY.md`, `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`, source-layer close-out, source material inventory.

---

## 执行摘要（中文）

审查结论：**GO_WITH_REQUIRED_CHANGES**。

三个新增 gap 的方向全部正确，且组合后 **Human Playbook First 仍然实际可运行**，未发现新的 CRITICAL 致命缺陷，不需要重开 Skeleton v1.0，也不需要推翻 Human Playbook First。

- **GAP A（历史 holdout vs 真正 unseen）**：正确且必须采纳。历史锁仓的学术价值不是"认知纯净"，而是"程序完整性"（防止项目内部迭代/调参污染）。"先验知道 2025 行情"会**削弱声明的强度**，但不会**消灭 holdout 的效用**。正确做法是：把声明收窄为 PROJECT_GOVERNED_HISTORICAL_HOLDOUT，把 latent memory 作为"披露的背景风险"，把真正的前瞻 unseen 留给 Shadow/Forward，并把"需要最强 unseen 证据才放行"的路径指向前瞻数据。
- **GAP B（整波多重检验）**：正确且必须显式写入冻结协议。Skeleton v1.0 只提供了"记账原语"（strategy × params × ... 计数），没有提供"决策规则"（被测试集的分母如何影响晋升/验收）。100 个 playbook 测完只报 5 个赢家确实是严重选择偏差。关键是最小 wave 记录 = **不可变的计数清单**（测试集 + 分母），而不是重型表格。
- **GAP C（统计画像冻结时点）**：正确且比替代方案更简单。在第一个 outcome-bearing 回测前冻结"原则 + 数值过程"完全可行，**并不需要先看 development PnL 才能设计**——事件数下限可以用非 outcome 的"信号触发频率"估算，而不是用 PnL。若项目坚持用 PnL 校准，则必须烧掉一个结构上隔离的 calibration cohort。
- **交叉冲突**：四约束（AI 可能见过 2025 / 历史 final 只能是被锁 holdout / 画像必须在 outcome 回测前锁 / wave 必须先知道）组合后**不冲突**，因为它们的触发条件全部收敛到同一个门："**第一个 outcome-bearing performance backtest 之前**，profile（原则+数值）与 wave（测试集+分母）必须同时锁定"。按此门即可得到最小可行生命周期。

**本审查未冻结任何内容。** 未选择 split，未抽取打法，未回测，未触碰 final-holdout，未修改 live AI semantics。本文件只新增 review evidence。

---

## 1. REVIEW_VERDICT

**`GO_WITH_REQUIRED_CHANGES`**

理由：

- 三个 gap 的语义修正方向均成立，且相互一致；组合后研究流程仍然可运行（见 §4 CROSS_GAP_CONFLICTS 与 §7 RECOMMENDED_MINIMAL_LIFECYCLE）。
- 但每个 gap 都带有一组**必须写入冻结协议/决策包**的收窄与细化（见 §6 MINIMUM_REQUIRED_CHANGES）。若不写入，会留下三个可被钻空子的洞：
  - GAP A：只"记录"retrieval 状态而不"技术性禁止"受保护行情检索（策略与执行两层分离）；
  - GAP B：wave 记录成为可选形式，或"追加家族后再挑赢家"未被封死；
  - GAP C："engine sanity 回测"可能被伪装成候选 outcome 回测来绕过画像锁。
- 这些都是**协议规则层面的细化**，可以在冻结前补齐；不构成架构/范式层面的致命矛盾。

**本审查未发现新的 CRITICAL（致命）缺陷。**

---

## 2. GAP_A_VERDICT

**`GO`**（语义修正成立；需要收窄声明、强制执行、记录研究者暴露、把前瞻证据作为升级路径）

### 2.1 逐项攻击

**A1 — 人类/AI 可能已知道 2025 行情，是否真的破坏历史 holdout 的研究意义？**

不会整体破坏，只削弱"最强 unseen 声明"。区分两个价值：

- **程序完整性价值（主要价值）**：历史 holdout 防止的是项目**内部**的迭代调参污染——研究者/AI 在同一个数据上反复"看结果→改分支/参数"，这是研究管线里最大的过拟合向量。锁定 + 单次考试 + 不可逆暴露，直接封死这条路径。这个价值与"研究者是否记得 2025 行情"无关。
- **认知纯净价值（次要且被高估）**："所有人都完全不知道这个窗口"几乎无法证明。但注意：先验知识是**分散、低分辨率**的信息（"2025H2 贵金属走强"），远比**迭代、高分辨率**的结果信息（"我的精确策略在这个精确窗口产生了 X PnL"）弱。把这两者混为一谈是错误。

额外事实：项目当前已接纳的来源绝大多数是 2024 年之前的出版物（Brandt 2011、Brooks 2012、Dalton 等），effective-content-date 规则已经排除了"来源内容含 2025 示例"这条污染路径；剩余的先验向量只有研究者/模型的自身记忆。这不是可忽略的，但它是**有界**的。

真正的残留风险不是"破坏意义"，而是**候选池选择偏差**：记得 2025H2 是单边的研究者可能优先选趋势类来源/打法。这会偏置候选池，但不会绕开统计机制——被选中池里的每个 family 仍然要过同一套锁定考试。因此应记录为限制，而非否决。

**A2 — 把 2025H2 定义为"项目受保护的历史 holdout"而不声称 epistemically unseen，是否足够严谨？**

足够，前提是满足两条：

1. **声明与事实匹配**：只声称锁能保证的东西——(a) 无项目数据访问；(b) 无项目内部迭代/调参；(c) 已接纳来源经 effective-content-date 规则无窗口内示例；(d) 解释过程为 SOURCE_ONLY 且模型/prompt/tool/输入 bundle 被记录。**不**声称"对所有人/所有模型认知上未见"。
2. **威胁模型显式**：把"外生先验知识"列为**不可消除的背景风险**，明确它降低推断强度但不使程序失效。

严谨性来自"声明 = 实际控制范围"，而不是"声明最大"。`PROJECT_GOVERNED_HISTORICAL_HOLDOUT != PROSPECTIVE_GENUINELY_UNSEEN_DATA` 这个区分正是把声明收窄到可验证范围，方向正确。

**A3 — 是否只有未来 Shadow/Forward 才能称为真正 prospective unseen？**

是，且这是正确默认。理由：

- 对模型：训练数据截止之前无法包含"未来"，因此未来数据在 parametric memory 意义上**强于**任何历史窗口（前提：无 retrieval，且数据晚于模型训练截止）。
- 对研究者：没有人知道未来，因此未来数据对研究者同样是真 unseen。

但要防止过度声明：**"真 unseen" ≠ "统计充分"**。Shadow/Forward 样本积累慢、可能 regime 不同、有实盘/成本暴露。它解决的是**污染问题**，不是**样本量问题**。协议应把 Shadow/Forward 定位为"最强认知地位 + 后续升级路径"，而不是"证据充足性的解药"。

**A4 — SOURCE_ONLY AI interpretation 是否足够？**

四条建议（禁止查询受保护期 outcome、禁止为解释打法而浏览未来行情、锁 prompt/spec、记录模型/版本/tool/retrieval/bundle hash）是**必要**的，且作为"项目可控污染"的对策基本足够。但有一条关键强化：

> **禁止必须是"技术性执行"，不是"策略性请求"。** 仅要求模型"不要浏览"是不够的；解释环境的 tool/retrieval 层应像 Selection Firewall 的 technical denial 一样，**结构上使受保护窗口不可访问**，并记录该环境确已如此配置（`retrieval_or_tool_access_mode=DENIED_BY_ENVIRONMENT`）。"记录 access mode"与"强制 access mode"是两层；只记录不强制是可钻的。

其余（记录模型/版本、锁 prompt/spec、记录 bundle hash）是必要记录，但对"模型 latent memory"只能作为 context，不能作为证明——这与 gap review 里"provider-reported cutoff 只是 context，不是 proof"一致。补充一个较难治理但必须写明的点：SOURCE_ONLY 还应禁止**以 outcome 知识伪装的类比推理**（例如"这个形态很像 2025H2 黄金那一波"）；唯一可执行的控制是既有的"任何显式引用/提及受保护期 outcome → 该 family 标记 exposed"。

**A5 — latent/parametric memory 无法证明不存在，如何诚实治理？**

不要试图证明否定项。五个可执行步骤：

1. **收窄声明**：历史 holdout 只声明"项目程序层面未见/未迭代"，不声明"认知层面未见"。
2. **控制环境**：SOURCE_ONLY + 技术性禁止检索受保护 outcome（见 A4）。
3. **记录风险**：按 gap review 的 schema 字段记录 `exogenous_market_knowledge_risk` 等；模型版本/cutoff 只作 context。
4. **披露为固定背景风险**：latent memory 风险对所有历史研究**均匀存在**，无法消除 → 应"披露并限定"，而不是"解决"。
5. **用正要求替代无法证明的负断言**：任何将放行到**真实资金/不可逆部署**的 final acceptance，应把"历史 holdout 通过"视为必要不充分，把**前瞻 cohort（Shadow/Forward）**设为放行前置。这把"无法证明没见过"变成一个**可满足的正向要求**（去拿未来证据），而不是一个不可验证的断言。

**A6 — 人类研究者的市场记忆如何记录？哪些是明确 exposure，哪些是不可消除背景风险？**

- **明确 exposure（可记录、必须记录）**：研究者自述记得特定 2025H2 结果（如"2025 年 9 月铜见顶"）；研究者为设计/选择 claim 而检索或引用了受保护期 outcome；研究者 2024-2025 期间在该市场有职业/交易活动。按 family 记入 `RESEARCHER_EXOGENOUS_EXPOSURE=EXPLICIT`。
- **背景风险（不可消除）**：对 2024-2025 市场总体特征的日常熟悉（来自新闻/生活经历），无具体可检索记忆。记 `POSSIBLE` 或 `UNKNOWN`，不假装消除。

最小机制：一次性研究者声明 + 每 family 一条 exposure 注记 + "不得为设计/选择 claim 而查阅受保护期 outcome"规则。**不要**建一套重型档案——一个轻量字段即可。

**A7 — 是否需要修改 FINAL_UNSEEN 名称/语义？**

保留架构名称，修正语义声明（这是最简单且不churn的做法）：

- Skeleton v1.0 已用 `final-unseen` 表示"项目锁定、无项目访问/迭代"，这是**程序语义**，保留。
- 冻结协议中显式定义：`FINAL_UNSEEN := PROJECT_GOVERNED_HISTORICAL_HOLDOUT`，附一段 threat model："该窗口对项目流程 unseen，不对所有人/模型 provably unseen"。
- 状态机沿用 v0.2（`FINAL_UNSEEN_LOCKED -> FINAL_EXPOSED -> ...`），但文档解释必须用限定语义。
- 若日后某处代码/文案使用 `FINAL_UNSEEN` 表示"认知上完全未知"，属误用，应改为限定表述。

结论：保留名称、明确威胁模型即可；不重命名，避免为无安全收益的文字而增加 churn。

### 2.2 GAP A 小结

语义修正是对的、可执行的，且不假装绝对纯净。必须补入冻结协议的最小项：收窄声明 + 技术性禁止检索（而非仅记录）+ 研究者暴露注记 + 把前瞻证据作为放行路径。

---

## 3. GAP_B_VERDICT

**`GO`**（wave 预注册方向正确；需要显式 claim 计数语义 + 先测后锁规则 + 分母永久保留 + 计数单元与单调性规则）

### 3.1 逐项攻击

**B1 — 忠实测试 100 个不同人类 playbook 再只报 5 个赢家，是否构成严重 multiple testing？**

是，这是经典的 winner's-curse / 选择偏差。若零假设为真（playbook 无真实 edge），100 次独立检验在 5% 水平下期望约 5 个假阳性；只报这 5 个"赢家"而不保留 100 这个分母，就是严重选择偏差。gap review 对 v0.2 的批评成立：v0.2 的 search-freedom 治理是**分支级**（family 内部），family/claim 级的多重性没有被显式治理。

对抗性细化——严重性取决于**研究问题形态**：

- 若目标是"在多个候选里**挑选**哪些 playbook 有效" → 必须做多重性校正，分母必须保留。
- 若目标是"**逐一确认**每个预注册 family 的假设"（每个 family 是一次独立 confirmatory 考试，families 不互相竞争）→ 每个 family 的确认在单 family 层面成立，但**跨 family 的"我们的打法成功率高"这类元结论**仍然需要整波分母；且一旦存在**晋升子集**（从 N 个里选 k 个去 final/live），选择偏差就回来了。

协议必须先在语义上定死：**这是"逐一确认的 library 构建"，还是"整波筛选后的晋升"**。reviewer 不替项目选，但必须指出：只要存在"从被测试集里挑选晋升子集"或"报告成功率/胜者"的环节，分母语义就是必须的。最小安全语义：**wave 里每个做过 outcome-bearing 测试的 family 都是该波搜索空间的一部分；wave 分母必须保留；任何对子集的晋升必须承认它是从被测试集中选出来的。**

**B2 — Skeleton 的 strategy × parameters × instruments × timeframe × context 是否已隐含覆盖，还是必须显式写出？**

Skeleton v1.0 提供了**记账原语**（"total search freedom records strategy × ..."），但不是**决策规则**。必须显式写出，原因有三：

1. "strategy" ≠ "playbook family"——一个 family 可含多个 strategy/分支（Skeleton 的 strategy 计数不覆盖 family 层级）。
2. 本 gap 的核心是**晋升/选择**（被测试集的分母如何影响验收与晋升），这是协议级决策，不是数据结构特性。
3. 记账只有喂给显式规则（"被测试数如何影响验收解释"）才有意义，否则只是填表。

结论：Skeleton 提供计数原语，冻结协议必须显式定义 family/claim 级多重性语义——**什么算一次测试、分母是什么、测试数如何影响验收**。

**B3 — claim 数量怎么算？一本书 100 句话是 100 个 hypothesis 吗？**

不是。claim ≠ 句子。**可独立测试的 claim** 定义：

> 一个来源可归因、可分别证伪的断言，且有自己独立的确定性 operationalization。

计数语义：

- 同一 setup 的多句话 = 1 个 claim。
- 一个复合断言（入场+出场+失效）——若各部分可分别证伪且分别来源可归因，可拆成多个 claim；若它们构成一条完整交易逻辑，则 1 个 claim。
- 判定测试：**"一方的真假是否在逻辑上决定另一方？"** 以及 **"能否各自独立操作化为不同 artifact？"** 共享同一 operationalization hash → 同一 claim（与既有 operationalization-identity 规则一致）。
- 共享 outcome-affecting 逻辑 → 同一 family 变体，不是独立确认。

**何时多个 claim 归入同一 playbook family？** 满足任一强信号即归族：同一来源血统；同一机制签名（共享 outcome-affecting 逻辑/输入/context）；同一底层市场判读（信息层相关，见 H-4）；互为复述/变体。**复述不得计数为独立确认。**

多重性校正的计数单元**不使用"句子数"**，而使用"真正作为独立假设被 outcome-tested 的 claim 数"。

**B4 — RESEARCH_WAVE 是否会过度治理？一个合理最小 wave 记录多简单？**

过度治理风险真实存在（重型预注册表格会窒息流程）。最小 wave 记录应当是**计数清单，不是表格**：

```
wave_id
protocol/profile 版本
日期
被测试 family 列表（每个含：预注册 PRIMARY branch hash、scope、claim 数）
instrument/timeframe/context 范围
parameter/search 范围（或 "none"）
分母语义一句话（哪些计为一次测试）
```

关键性质是**不可变 + 测试集先注册**，不是**内容丰富**。不需要预写结果、预测、冗长理由。凡给 wave 加重型 review gate、完整 rationale、预测要求，都可删——那是过度治理。

**B5 — source discovery 持续开放，performance testing 按 wave 锁定，边界是否合理？**

合理，且是正确边界——与既有"source discovery broad; outcome-bearing testing wave-registered"一致。发现不是统计检验；outcome-bearing 回测才是。开放发现不会膨胀被测试集，只是喂给未来 wave。

一个必须封死的细节：**"discovery"不得偷偷包含 outcome 检视**（例如浏览 2025 行情来决定下一个测哪个 family）。因此"发现开放"必须限定为**来源级发现**（读来源、做 provenance），不得是"看行情挑候选"。这直接与 GAP A 的 SOURCE_ONLY 规则衔接。

**B6 — 新增 family 后：新 wave / append / 如何避免不断追加然后只挑赢家？**

最干净的规则是**双时点**：

1. **锁定前（第一个 outcome-bearing 测试运行前）**：可以在当前 wave 追加——因为仍是预注册，分母在测试前被重声明即可。
2. **锁定后（第一个 outcome-bearing 测试运行后）**：追加 = **新 wave / 后代搜索事件**，继承已见信息，不得并入旧 wave。

这同时封死"不断追加然后挑赢家"：一旦看过本波任何 outcome，再追加 family 就是带着信息的新搜索事件。跨波"成功率"报告必须按波分别报告分母，或用累积真实分母——**永不**用"滚动挑选后的子集"做计数。

**B7 — multiple-testing correction 应基于 family / claim / branch / 组合数，还是 effective hypothesis count？**

Reviewer 不替项目选公式，但给出安全计数语义：

- **计数单元** = 每个 (family, 预注册 primary-branch operationalization hash, 实际运行过的 instrument/timeframe/context 组合, 实际测试过的参数集) 中**确实做了 outcome-bearing 测试且参与任何决策**（晋升/验收/保留）的项。
- 从未 outcome-tested 的 family / 从未测试的 alternative branch **不计入测试分母**（但若报告"发现→晋升漏斗"，发现数单独报告）。
- 两条安全不变量：
  1. **分母 = 该 wave 全部 outcome-tested 项，永久保留，永不裁剪到赢家**；
  2. **校正规则对测试数单调**——测试越多，绝不允许让验收更容易。
- 计数单元的**选择**必须在 wave 运行前（与 profile 同时）预注册。

协议只需冻结"计数单元 + 分母 + 单调性"这三样语义；具体校正方法属于 GAP C 的 profile 实现细节（profile 本身在第一个 outcome-bearing 测试前锁定）。

### 3.2 GAP B 小结

wave 预注册是最小正确机制。必须补入冻结协议：claim 计数语义（可证伪操作化身份，非句子）、测试集先锁后测、锁定后追加=新 wave、分母永久保留、计数单元+单调性预注册。最小 wave = 不可变计数清单。

---

## 4. GAP_C_VERDICT

**`GO`**（冻结时点正确且比替代更简单；需要"原则/数值"分层 + 非 outcome 工作放行 + engine-sanity 例外定义 + calibration 烧毁规则）

### 4.1 逐项攻击

**C1 — 先看 development PnL 再决定 confidence method / min event count / dependence handling / acceptance thresholds，是否构成 protocol-level metric/threshold shopping？**

是——这是**协议层的指标/门槛挑选**，只是上移了一层。即便 profile 是"项目全局统一"，**在看到哪些候选强之后**再选置信方法/门槛，等于让被观察到的候选来引导验收机制。gap review 的修正（第一个 outcome-bearing 回测前锁死）方向正确。

对抗性细化：并非所有 development PnL 观察都同样危险。**用于调试实现**（代码是否按规格跑）的 PnL 观察是合法的，且只要 profile 已先锁，它不会影响 profile 选择。危险的是**用 development outcome 校准验收机制**。所以"第一个 outcome-bearing performance backtest 前锁定"是干净、安全的分界线。

**C2 — 是否真的必须在第一笔 performance backtest 前全部冻结？**

对"决策相关数值元素"——是：验收指标（来自固定菜单）、置信/精度方法、最小事件数过程、相关性处理、多重性计数单元。它们全部喂给验收决策，必须在任何 outcome-bearing 证据出现前固定。

关键反驳"需要先看 PnL 才能设计 profile"：**不需要。** 一个确定性过程（如"扣除成本后的平均净期望的下置信界 > 0 + 预注册事件数下限，用相关性感知聚类计算"）可以在**不看任何候选 PnL** 的情况下完整写出。事件数下限可以用**非 outcome 的信号触发频率**（这个 setup 在 development 数据上触发多少次——这是信号计数，不是盈亏）来估计。因此 profile 的全部要素都可以在零 outcome 信息下设计。"必须先看 development PnL 才能设计 profile"主要是挑选的合理化措辞。

**C3 — 如果太严格，是否可以分层？**

可以，且分层正是正确结构。分层如下（profile 锁之前可自由进行）：

- source/claim extraction：可进行（SOURCE_ONLY）。
- operationalization（写确定性 artifact、哈希）：可进行。
- non-outcome tests（单元/集成/数据质量/执行语义，凡不揭示候选绩效）：可进行。
- 信号触发频率估计（非 PnL）：可进行，用于设计事件数下限。
- **任何揭示候选 outcome 绩效的测试（PnL/expectancy/Sharpe/win-rate/equity）**：profile 锁之前禁止。

关键分界：**凡揭示候选 outcome 绩效，即 outcome-bearing，需要已锁 profile。** 其余一切自由运行。这个分层避免全停，且安全。

**C4 — 若项目确实需要 development outcomes 设计 statistical profile，如何不污染随后验证的 family？**

唯一安全路径，且应尽量不用：

1. **声明 calibration-only cohort**：指定一个明确子集（families/数据）专门用于 profile 设计。
2. **烧毁**：该 cohort 的 outcome 只用于设计 profile；这些 family/窗口被永久标记为 calibration-exposed，**同一协议版本下永不能再作为干净证据**。
3. **其余 family 干净**：它们在 profile 锁后测试，天然干净。
4. **最便宜的 decisive 路线（推荐）**：先检查能否用"统计原则 + 非 outcome 量（信号触发频率、相关性诊断）"设计 profile。能，则根本不需要 PnL 校准、不需要烧毁。这符合 operating contract 的"先做最便宜的决定性检查"。

结论：几乎不需要 PnL 校准；若坚持，必须烧毁结构上隔离的 cohort。

**C5 — 最简单、安全的冻结时点是什么？**

**COMMON_STATISTICAL_PROFILE_V1（原则 + 数值过程）在第一个 outcome-bearing performance backtest 之前锁定**，非 outcome 工作放行。这个时点是一个**程序触发器**（"任何 outcome-bearing 回测运行之前"），不是日期，因此无需猜测第一次回测何时发生，天然可审计。它比任何基于日期的规则更简单、更安全。

**C6 — 需要独立 review 的是统计原则、exact numerical profile、还是两者？**

分两层：

- **统计原则**（固定指标菜单、公共验收契约、uncertainty-explicit、dependence-aware、分母保留、单调性、禁止 metric shopping、锁定时机）：这是**语义**，属于冻结协议 → 需要独立 review + **Owner gate**。
- **exact numerical implementation**（具体置信方法、具体事件数下限、具体聚合）：这是**实现 profile**，版本化 + 独立 review + 在第一个 outcome-bearing 回测前锁定。它**不需要 Owner gate**——因为一旦锁定纪律（先锁后测、不可事后改）由协议强制，具体数字就是确定性技术过程。任何"锁定后改数字"都要求新协议版本（既有规则）。

所以：**锁定时机与原则 = Owner 冻结决定；exact 数字 = 独立 review 的实现细节（但必须在第一个 outcome-bearing 测试前锁定）。**

**C7 — 补：engine-sanity 回测例外（新发现，防绕过）**

必须定义一个例外，否则会被绕过：**"引擎健全性回测"**——用于验证回测引擎本身是否按规格工作（例如用随机/哑信号或与候选 family 无关的 sanity 数据集），且其结果**明确不用于任何候选决策或 profile 校准**——属于**非 outcome 工具测试**，允许在 profile 锁前运行，但必须记录并声明"非候选 outcome"。这封死"跑个快速 sanity 回测"伪装成工具测试、实际是候选 outcome 的漏洞。

### 4.2 GAP C 小结

冻结时点正确。必须补入冻结协议：原则/数值分层、非 outcome 工作 + 信号频率放行、engine-sanity 例外、PnL 校准需烧毁 cohort、锁定时机为程序触发器。

---

## 5. CROSS_GAP_CONFLICTS

### 5.1 四约束组合后是否可运行？

四约束：AI 不能证明没见过 2025（A）；历史 final 只能是被锁 holdout（A）；profile 必须在 outcome 回测前锁（C）；wave 必须先知道（B）。

**组合后 Human Playbook First 仍然可运行。** 关键观察：四个约束的触发条件全部收敛到**同一个门**：

```text
BEFORE THE FIRST OUTCOME-BEARING PERFORMANCE BACKTEST:
  COMMON_STATISTICAL_PROFILE_V1  (原则 + 数值) 已锁定
  RESEARCH_WAVE 测试集 + 分母 已锁定
  SOURCE_ONLY 解释过程 已生效（技术性禁止检索受保护 outcome）
```

- GAP A 的 SOURCE_ONLY 从 claim 提取开始生效，与 B/C 无冲突——它约束的是"解释阶段不看受保护行情"，development 阶段看 development 数据本来就是允许的。
- GAP B 的 wave 锁与 GAP C 的 profile 锁共享同一个触发事件（第一个 outcome-bearing 回测），因此没有先后矛盾。唯一需要的小顺序：**计数单元语义（profile 原则的一部分）必须早于 wave 清单**，因为 wave 要按该单元记录计数；数值方法（Bonferroni vs BH 之类）不改变 wave 记录什么，可在任一时刻锁定，只要在第一个 outcome-bearing 测试前。
- 结论：**不是矛盾，是收敛**。

### 5.2 交叉带来的声明削弱（必须承认）

组合的真实代价是**声明强度**而非**可运行性**：

- 历史 final holdout 通过 = "通过了一次程序锁定的历史考试"，**不是** "该打法在 unseen 数据上有效"。
- 因此协议必须把 final-holdout 通过表述为"历史 epoch 内晋升的必要条件；对强 unseen 声明/真实部署不充分，需要前瞻确认"。这是 A 的语义修正直接要求的，B/C 不与它冲突。

### 5.3 最强反方论证（已检验）

> "因为 AI 的 latent knowledge 可能在 SOURCE_ONLY 阶段悄悄引导 PRIMARY_BRANCH/family 选择，'盲目'预注册并不盲；被选出的 family 随后在 2024 dev 上'开发'、在 2025 holdout 上'确认'，产生一个流程上干净、认识上污染的假确认。"

回应：这不是致命缺陷，因为——程序机制（锁 wave、锁 profile、单次 holdout 考试）**仍然界定了选择**：即便 latent knowledge 引导了候选选择，每个 family 仍要过一次预注册考试 + 固定 profile，family 数量被 wave 界定。残留污染正是 GAP A 要求披露的"背景风险"；它削弱声明强度，但不使程序失效。诚实的声明已经被收窄："这些 playbook 通过了程序锁定的历史考试；不能排除 2025 先验知识影响了候选选择；因此超出该历史 epoch 的晋升需要前瞻确认。"这正是 GAP A 修正的全部要点。**不致命。**

### 5.4 潜在小冲突与解决

- **wave 锁定 vs 渐进式 claim 提取**：不必等所有来源提取完才能测。wave 在"准备开始 outcome-bearing 测试"时锁定；该 wave 内的 family 必须在第一个 outcome-bearing 测试前盲提取完；未入波 family 归未来 wave。这是排程问题，不是逻辑矛盾。
- **profile 锁 vs engine 验证**：见 C7——engine-sanity 回测定义为非 outcome 工具测试，允许先跑。
- **12/6/6 与 A**：12/6/6 作为治理选择不因 A 而弱化，只弱化"final 通过"的声明强度（见 §8）。

---

## 6. OVER_GOVERNANCE_RISKS

把三 gap + v0.2 全部叠加后，真实风险是**过程官僚化**。安全关键不变量其实很小，其余都是轻量日志：

- **不可删（安全关键）**：
  1. 分母保留 + 计数单元预注册（B）；
  2. profile（原则+数值）在第一个 outcome-bearing 回测前锁定（C）；
  3. SOURCE_ONLY：技术性禁止检索受保护 outcome（A）；
  4. 暴露不可逆（既有）。

- **可轻量（避免过度治理）**：
  1. wave = 不可变计数清单，不加 review gate / 预测 / 冗长 rationale；
  2. GAP A 日志 = 每次解释会话一条记录，不是每个 claim 一份清单；模型版本/cutoff 只作 context；
  3. 研究者暴露 = 一次性声明 + 每 family 一条注记，不是重型档案；
  4. profile 锁 = 确定性过程（procedure），不是追求完美数字；锁定后修改走新协议版本；
  5. 每 wave 大小是项目选择——小 wave 合法且声明成本低，不要为避免多重性而强制超大 wave，也不要为"显得严谨"而做每 family 一个 wave 的极端。

过度治理的反例：若对每个 claim 强制填满 schema 全部字段、对每个 wave 强制独立 review 门、对每个解释会话强制多模型复核，会在 24 个月数据上把研究进度拖死且无安全收益。**可删的是表单负担，不可删的是分母、锁定时机、技术性禁止、暴露不可逆。**

---

## 7. RECOMMENDED_MINIMAL_LIFECYCLE

下面顺序**不是**默认接受任务示例顺序，而是从依赖关系推导的（见 §5.1）：

```text
SOURCE DISCOVERY                 （开放；仅来源级；不浏览受保护行情）
-> BLIND CLAIM EXTRACTION        （SOURCE_ONLY：无受保护 outcome 检索；模型/prompt/tool/bundle 记录；研究者暴露注记）
-> STAT PROFILE PRINCIPLES + 计数单元 LOCK   （协议冻结的一部分，Owner-gated）
-> RESEARCH WAVE LOCK            （被测试 family/claim/branch/scope/range；分母固定）※ 须在计数单元之后
-> STAT PROFILE NUMERICAL LOCK   （独立 review + 版本化）※ 可与 wave 锁互换先后，但必须在第一个 outcome-bearing 测试前
   ── 以上全部完成于第一个 outcome-bearing performance backtest 之前 ──
-> DEVELOPMENT                   （非 outcome 测试 + 在已锁 profile/wave 下的 outcome-bearing development）
-> VALIDATION                    （CAT1/CAT2/CAT3；artifact 锁定）
-> HISTORICAL PROJECT-GOVERNED FINAL HOLDOUT   （单次程序锁定考试；不声称认知 unseen）
-> PROSPECTIVE SHADOW/FORWARD    （真正 unseen；对强声明/真实部署的前置）
```

与任务示例顺序的两处有意修正：

1. **计数单元语义须在 wave 锁之前**（wave 按该单元记录计数）；
2. profile 锁不是固定阶段，而是"第一个 outcome-bearing 回测前"的**门**——数值锁与 wave 锁可互换先后，只要都在门前。

---

## 8. 是否仍支持 12/6/6 作为 historical protected holdout

**是，仍支持 12/6/6 作为 leading historical protected-holdout 候选**，前提是采纳 GAP A 的语义修正：

```text
DEVELOPMENT      2024-01-01 .. 2024-12-31
VALIDATION       2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT
                 2025-07-01 .. 2025-12-31
PROSPECTIVE_GENUINELY_UNSEEN  future Shadow/Forward cohorts
```

理由：12/6/6 作为**治理选择**（日历/审计简单、全年 dev、对等 val/final）不因 GAP A/B/C 而失效；它不解决样本量与相关性问题——那些由 `INSUFFICIENT_EVIDENCE` 处理，而不是改日期。GAP A 只改变**附着在 final 通过上的声明强度**（"程序锁定考试"而非"认知 unseen 证明"），不改变 split 的治理合理性。`10/8/6` 仍为合法替代；rolling 不推荐（24 个月滚不出足够独立块）。无 split 被冻结。

---

## 9. 必须进入 Owner freeze decision 的内容

以下为**语义/规则**，属于 Owner gate（冻结研究语义）：

1. **GAP A 语义修正**：`PROJECT_GOVERNED_HISTORICAL_HOLDOUT != PROSPECTIVE_GENUINELY_UNSEEN_DATA`；`FINAL_UNSEEN` 保留名称但定义为程序锁定、威胁模型显式；SOURCE_ONLY 解释过程（技术性禁止检索受保护 outcome，非仅记录）；研究者/模型外生知识暴露记录；latent memory 为披露的背景风险；需最强 unseen 证据的部署路径指向前瞻数据。
2. **GAP B 语义**：RESEARCH_WAVE 预注册要求（第一个 outcome-bearing 回测前锁测试集+分母）；claim 计数语义（可证伪操作化身份，非句子）；锁定后追加 = 新 wave；分母永久保留；计数单元 + 单调性预注册。
3. **GAP C 语义**：profile **原则**（固定指标菜单、公共验收契约、uncertainty-explicit、dependence-aware、分母保留、单调性、禁止 shopping）+ **锁定时机**（原则与数值均须在第一个 outcome-bearing performance backtest 前锁定）；非 outcome 工作与信号频率估计放行；engine-sanity 回测为非 outcome 工具测试的例外定义；PnL 校准须烧毁结构隔离 cohort。
4. **交叉门**：单一门——"第一个 outcome-bearing performance backtest 之前，profile（原则+数值）与 wave（测试集+分母）必须同时锁定；计数单元先于 wave 清单"。

这些进入 Owner decision package 后，Owner 的"按推荐冻结"即可覆盖；否则 decision package 需要补充这些语义。

## 10. 哪些只是后续普通 implementation detail

以下为**实现细节**，一旦上述语义冻结，可由项目正常实施流程处理（不另需 Owner gate）：

- exact 数值 profile（具体置信方法、事件数下限、聚合/相关性处理）——独立 review + 版本化 + 先锁后测，但无需 Owner gate；
- wave manifest 的具体字段（计数清单 schema）；
- 研究者暴露注记的字段格式；
- 解释会话日志的字段格式（model/version/tool/bundle hash 等）；
- 具体多重性校正方法（在 profile 内，随 profile 锁定）；
- source-only 环境的工程配置（如何做 technical denial）与相应测试。

---

## 11. 冻结状态

```text
REVIEW_VERDICT=GO_WITH_REQUIRED_CHANGES
NEW_CRITICAL_FOUND=NO
RESEARCH_PROTOCOL_FREEZE_STATUS=NOT_EXECUTED
STRATEGY_RESEARCH_STARTED=NO
NEXT_ACTION=PROJECT_BRAIN_ADJUDICATE_DELTA_REVIEW_THEN_REVISE_DECISION_PACKAGE
```

本审查只新增 review evidence，未修改 `RESEARCH_DIRECTION.md`、`ARCHITECTURE_BASELINE.md`、`CURRENT_STATE.md`、protocol candidate、Owner decision package 的语义。未冻结协议/split，未抽取打法，未回测，未触碰 final-holdout，未修改 live AI semantics。
