# 前瞻 Shadow 统计档案决议 V0.2

## 正式结论

```text
PROSPECTIVE_SHADOW_STATISTICAL_PROFILE=NOT_LOCKABLE_UNDER_CURRENT_ASSUMPTION_AUTHORITY
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

冻结目标保持为 `theta = E[S_d] / E[C_d]`，其零假设为 `E[S_d] <= 0`，其中
`S_d` 是交易日净候选分数、`C_d` 是该日完成 round-trip 数。不得以中位数、截尾、
截断、符号检验或逐日等权替换它。

数学缺口是：若只假定无条件 `E[S_d] <= 0`，而不另行规定可在结果前治理的条件均值、
独立/可交换性、已知有界支撑、已知尾部矩或依赖上界，则不存在可直接构造的、对任意
停止仍有效的非平凡 mean e-process。一个对所有满足无条件均值零的过程均为非负超鞅的
赌注过程，必须能处理可由过去决定的任意正/负条件漂移；在没有额外条件限制时，这使
它不能提供所需的正向证据。因而“拒绝 `E[S_d|F_{d-1}]<=0`”也不能被写成证明无条件
事件权重均值为正。

## 方法逐项处置

| 方法族 | 目标是否保持 | 缺失/不可治理假设 | 处置 |
|---|---|---|---|
| 均值/比率 e-process、置信序列 | 可保持 | 需要条件均值、已知有界/矩或可验证尾部控制；当前均非 A/B 类可保证事实 | REJECT |
| 自归一化与渐近序列推断 | 可保持 | 需要弱依赖/FCLT；既有合成反证在强持续、左偏下反保守 | REJECT |
| martingale-difference 方法 | 只检验更强条件零假设 | `E[S_d|F_{d-1}]<=0` 不是冻结无条件零假设 | REJECT |
| mixing、m-dependence、再生过程 | 可保持 | 依赖上界/再生机制不是项目机制或可预先采集设计保证 | REJECT |
| block/bootstrap/subsampling | 大多保持 | block 长度/带宽为任意 knob；短样本 Holm 尾部解析度不足 | REJECT |
| fixed-horizon 聚类方法 | 可保持 | 聚类独立性与簇数保证缺失；不能自然覆盖重复观察 | REJECT |
| e-value + Holm/Bonferroni | 仅在单假设 e-value 有效时 | 多重校正不能修复无效单假设过程 | REJECT_AS_COMPLETE_PROFILE |

既有 `HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_REVIEW.md`
已经以非候选合成数据反证自归一化、wild/bootstrap、weekly/grouped 与 subsampling 在
相关尾部的 size；V0.2 不重做历史六个月画像，只检查其结论在前瞻顺序场景下是否可绕过。
结论是否定的。

## 多重检验与波次

M=1 不删除 future `M>1` 语义。若未来某一单假设产生真正 anytime-valid p/e process，
Holm/Bonferroni 才能在任意跨假设依赖下提供 strong-FWER；重复观察只能由该过程自身的
顺序有效性吸收。后续新增假设必须新建 Research Wave，不能追加入已锁 wave。

## 合成反证范围

V0.1 与前序审查的 non-candidate fixtures 已覆盖 IID 对称/左偏、稀有大损失、异方差、
AR 持续/强持续、状态簇、跨产品相关、稀疏与 count-score 相关、长时间无交易、零/负/小
正替代。模拟只能反证或发现实现故障，不能代替定理。

## 可解除的唯一方式

必须先有一项 A/B 类（项目机制或前瞻采集设计）可审计保证，唯一地给出：条件零假设与
无条件目标之间的蕴含、尾部/支撑或条件 mgf 界、依赖/簇机制、顺序统计量、阈值、强 FWER
和停止规则。外部市场经验（C 类）须有独立强证据；从 Shadow 结果诊断出的 D 类假设禁止
成为 PASS gate。没有这些前提，不创建伪造的 locked profile 或 locked wave。

## 主要原始资料

- Ramdas, Ruf, Larsson, Koolen (2021), *Testing exchangeability: fork-convexity,
  supermartingales, and e-processes*, arXiv:2102.00630：展示对很宽泛序列类的
  非负超鞅会退化，支持“需要受治理过程类”的边界。
- Shao (2010), JRSS-B 72(3):343–366：自归一化均值推断是弱依赖渐近结果，不是本项目
  一般有限样本顺序保证。
- Holm (1979), Scand. J. Statist. 6(2):65–70：强 FWER 校正以前提有效的单假设 p 值为条件。
