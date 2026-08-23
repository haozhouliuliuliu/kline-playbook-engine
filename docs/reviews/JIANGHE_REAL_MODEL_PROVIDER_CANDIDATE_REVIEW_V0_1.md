# 江河真实模型 Provider 候选审查 V0.1

```text
REVIEW_STATUS=CANDIDATE_IMPLEMENTATION_READY_FOR_LIVE_PROBE
REVIEW_DATE=2026-08-23
RESEARCH_SCOPE=OFFICIAL_PROVIDER_DOCUMENTATION_ONLY
LIVE_CALLS=0
PAID_SPEND=0
NETWORK_CALLS_FROM_TESTS=0
ADOPTED_PROVIDER=NONE
ADOPTED_MODEL=NONE
```

## 1. 边界与结论

本审查只为未来的非结果 Jianghe Fidelity 探针准备受治理的调用合同；不选择
赢家，不采纳 Provider，不发出真实 API 请求，也不读取任何 API 凭证。

桌面工具或 WorkBuddy UI 中“可选择模型”只表示交互层可能可用，**不构成**项目
可编程 API、图像输入、版本绑定、原始回复审计或可控成本的证据。本审查没有用
它们作为依据。

新增的 `src/jianghe_model_provider.py` 是 Provider 中立合同，默认且强制禁止真实
调用：它仅能构造待转换的请求载荷和解析测试提供的模拟回复。没有 HTTP、socket、
第三方 SDK 或环境变量读取代码。

## 2. 状态词的严格区别

| 状态 | 含义 | 本分支可达到吗 |
| --- | --- | --- |
| `CANDIDATE` | 官方资料显示可能有相关 API 能力，但尚未用项目批准的账号、模型、样本和成本上限做真实探针。 | 可以 |
| `VERIFIED` | 在 Owner 批准的受限真实探针中，已保存请求/回复/版本/费用/延迟证据，并逐条通过五个 Fidelity tracks；仍不是项目默认选择。 | 不可以 |
| `ADOPTED` | Owner 在比较证据后批准一个 Provider + 明确模型/版本进入受治理研究对象，并完成相应身份、漂移、成本与复现规则。 | 不可以 |

因此本分支的上限固定为：

```text
CANDIDATE_IMPLEMENTATION_READY_FOR_LIVE_PROBE
```

## 3. 所有候选都必须满足的合同

`ProviderIdentity`、`ModelIdentity`、`InvocationConfig`、`JiangheModelRequest`、
`JiangheModelResponse`、`InvocationTiming`、`CapabilityDeclaration` 共同绑定：

```text
provider + model + version/snapshot（要求时）
+ system/decision prompt identity + inference configuration
+ observation identity + visual artifact identity + structured input identity
+ request/response/normalized-decision timestamps
+ raw response SHA-256 + normalized response + usage metadata + latency
```

时间线在构造时 fail-closed：

```text
observation_available_at
<= model_request_at
<= model_response_at
<= normalized_decision_at
```

这只产生“何时可用决定”的审计事实，不产生订单、成交、PnL、未来价格或其他
candidate-outcome 字段。Provider 延迟不能把意图或成交倒填进过去。

`InvocationConfig` 只能记录环境变量**名称**（例如未来采用的密钥机制），从不读取
环境变量；`live_calls_enabled=True` 目前会直接报错。响应中的原始 HTTP/JSON 内容
将在未来 adapter 内由项目本地捕获并哈希，不依赖 Provider 帮项目保存审计副本。

## 4. 官方资料侦察（不等于项目验证）

下表的“是”只表示官方文档描述了该 API 能力；“本地”表示由本项目合同在调用
边界记录；“待真实探针”表示官方资料不足以证明该**具体账号 + 具体模型**在本
项目场景中可用。没有一项因 UI 可选而被标记。

| 候选 Provider / API | 图像输入 | 结构化 JSON 输出 | 响应模型/用量 | 时间、原始回复与延迟 | 重复性与漂移 | 当前判定 |
| --- | --- | --- | --- | --- | --- | --- |
| OpenAI Responses API | 是，文档说明文本/图像输入；也支持 base64 图像。 | 是，`json_schema`/严格结构化输出。拒绝或不完整回复仍须 fail-closed。 | API 资料描述模型、响应状态和 usage；项目仍须保存实际返回的模型字段。 | `request_at`/`response_at`/延迟由本地时钟记录；原始 body 本地捕获哈希。 | 文档给出 `temperature`、`top_p` 等采样控制；不把“较低随机性”误说成完全确定。具体模型的版本/别名漂移须首次探针确认。 | `CANDIDATE` |
| Anthropic Messages API | 是，API 可发送 base64、URL 或 `file_id` 图像。 | 是，`output_config.format` 的 JSON Schema 输出。 | 文档示例返回 message id、model 与 input/output token usage。 | 本地记录时间和原始 body；公开消息示例不替代本项目时间链。 | 官方版本文档说明固定 model ID 与可漂移 alias 的区别；同时明确即使温度为 0 也不完全确定，且新模型对采样参数有限制。 | `CANDIDATE` |
| Google Gemini API | 是，Interations API 支持 URL、内联数据或 Files API 图像。 | 是，`application/json` + JSON Schema 子集。 | 模型目录和 API 参考可用于请求模型/参数；具体响应模型字段、usage 字段与账号可用性须探针保存。 | 本地记录时间、原始 body、SHA-256 与延迟。 | 官方 API 参考有 `temperature`、`topP`、`seed`，但 Gemini 3.x 文档建议使用默认采样；模型弃用/变动语义须在探针时固定。 | `CANDIDATE` |
| DeepSeek Chat Completions API | **未在本轮官方资料中确立。** 不得把它列为视觉通过。 | 是，官方 JSON Output；文档提示可能有空内容，必须 fail-closed。 | 官方 API 参考说明 `usage`；模型名会升级/弃用。 | 本地可捕获时间、原始 body、SHA-256 与延迟；不把此项误当成已做真实网络验证。 | 官方资料有 `temperature`、`top_p`；没有把它作为确定性保证。版本别名已出现升级/弃用，必须按 drift 处理。 | 仅 `SEMANTIC/STRUCTURED/OPERATIONAL_PROVIDER` 候选；`VISUAL/DUAL_INPUT` 未满足 |

说明：`OPERATIONAL_PROVIDER` 轨道的“可审计性”既包含 Provider 返回的可见字段，也
包含项目自己必须记录的本地时间、请求身份、响应原文哈希与延迟。因此“Provider
有 API 文档”本身不足以使该轨道通过。

## 5. 官方来源清单

以下均为 Provider 官方资料。本分支没有使用第三方博客、模型聚合页或 UI 截图。

### OpenAI

- [Responses 创建接口：文本/图像输入、JSON 输出、状态、temperature/top_p](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)
- [图像与视觉：URL、base64、文件 ID 图像输入](https://developers.openai.com/api/docs/guides/images-vision)
- [结构化输出：JSON Schema 与 refusal/incomplete 处理](https://developers.openai.com/api/docs/guides/structured-outputs)
- [模型目录：模型 ID 与 API 可用性](https://developers.openai.com/api/docs/models)

### Anthropic

- [Vision：图像 content block、base64/URL/file_id](https://platform.claude.com/docs/en/build-with-claude/vision)
- [Structured outputs：JSON Schema、拒绝与截断边界](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Messages API 使用：response id/model/usage、系统提示和采样参数限制](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)
- [模型 ID 与版本：固定 ID、alias 漂移与服务基础设施差异](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)

### Google Gemini

- [图像理解：URL、内联数据、Files API 与多图输入](https://ai.google.dev/gemini-api/docs/image-understanding)
- [结构化输出：JSON Schema 子集和应用层校验要求](https://ai.google.dev/gemini-api/docs/structured-output)
- [模型目录与弃用信息](https://ai.google.dev/gemini-api/docs/models)
- [生成参数：temperature、topP、seed](https://ai.google.dev/api/generate-content)
- [Gemini 3.x 参数建议](https://ai.google.dev/gemini-api/docs/generate-content/whats-new-gemini-3.5)

### DeepSeek

- [创建 Chat Completion：JSON 输出、usage、temperature/top_p](https://api-docs.deepseek.com/api/create-chat-completion)
- [JSON Output：空内容风险与处理要求](https://api-docs.deepseek.com/guides/json_mode/)
- [模型版本/弃用更新](https://api-docs.deepseek.com/updates)

## 6. 第一次真实 Fidelity probe 前的 Owner 门

现在**不要求**提交任何 credential。第一次探针需要 Owner 另行明确批准并提供：

1. 允许的 Provider/account；
2. API credential mechanism（例如由 Owner 管理的环境变量或其他受批准机制，而不是把密钥写入仓库）；
3. 最大允许支出及超过上限的停机规则；
4. 允许测试的具体模型 ID 与版本/快照或 alias 漂移处理方式；
5. 是否允许向 Provider 发送标准化 K 线图片、结构化点时数据，或两者；
6. 单次/重复调用次数、采样参数/seed（若该模型支持）、模型漂移记录与 raw response 保存范围；
7. 明确仍只使用无结果 Fidelity fixtures，禁止发送 candidate outcome、未来价格、PnL 或真实下单信息。

在上述门全部满足前，任何 adapter 都必须维持：

```text
LIVE_CALLS=0
PAID_SPEND=0
NETWORK_CALLS_FROM_TESTS=0
```

## 7. 本包的可复核测试范围

`tests/test_jianghe_model_provider.py` 使用纯内存模拟回复，覆盖：

- 默认禁网与 `invoke()` 失败闭合；
- 候选能力声明及五轨道关系；
- model/version identity；
- 图像、结构化、双输入请求封装；
- 时间单调性与延迟；
- raw response SHA-256 与 usage metadata；
- 畸形回复和缺失版本的 fail-closed；
- 合同公开字段、结构化输入、规范化回复均不允许 outcome 字段。

这些测试没有也不能证明某个 Provider 真实可用、收费、图像理解质量或 Jianghe 忠实度；
它们只证明未来真实探针不会缺少必要的项目治理边界。
