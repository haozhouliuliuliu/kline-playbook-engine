# 江河 Live Fidelity Prompt Package V0.1

```text
STATUS=CANDIDATE_PRE_LIVE_NON_OUTCOME
ADOPTION_STATUS=NOT_ADOPTED_FOR_PAID_PROBE
LIVE_CALLS=0
PAID_SPEND=0
OUTCOME_ACCESS=NO
PRIMARY_FREEZE=NO
```

本包只冻结未来受限 fidelity probe 所需的候选提示词、严格 response schema、
context-selection policy、runtime normalizer 和 evaluator-side extractor（评估侧提取器）
身份。它不是 provider 采纳、付费调用授权或 PRIMARY semantic freeze。

## 硬边界

- 只接收同一 canonical observation identity 的 point-in-time 图表/结构化输入；
- 不包含 fixture 正确答案、未来价格、PnL、收益、胜率、Sharpe 或权益曲线；
- 不诱导必须做多或做空；UNKNOWN、矛盾和不熟悉状态允许 WAIT/NO_TRADE；
- family 允许 `A/B/C/D/NONE`；action 允许
  `WAIT/NO_TRADE/WATCH/CANDIDATE/ENTER/MANAGE/EXIT`；
- 模型只能陈述客观输出，不能自评 `violated_principles`、
  `invented_thresholds` 或 fidelity 分数；这些必须由 evaluator-side fixture
  constraints 生成。

## Canonical identities

精确 prompt 文本、schema、context policy 与身份值以同目录 JSON 为准。JSON 还显式
记录整个 prompt package identity 与 evaluator-side extractor identity。身份算法由
`src/jianghe_model_provider.py` 的 `PromptArtifact` 和
`src/jianghe_response_normalizer.py` 的版本常量定义；任何受绑定内容变化都会产生新身份。

runtime normalizer 只提取模型实际输出的客观字段；`violated_principles` 与
`invented_thresholds` 只能由带匹配 extractor identity 的 evaluator-side judgment
提供，二者不能互相替代。

本文件不选择 OpenAI、Anthropic、Google Gemini 或 DeepSeek；全部仍为
`CANDIDATE`。
