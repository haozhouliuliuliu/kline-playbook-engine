# 江河真实模型 Provider 候选审查 V0.1

```text
REVIEW_STATUS=CANDIDATE_CONTRACT_REPAIRED_AWAITING_GATE_REAUDIT
REVIEW_DATE=2026-08-23
PROVIDER_CONTRACT_VERSION=JIANGHE_MODEL_PROVIDER_CONTRACT_V0_3
RESEARCH_SCOPE=OFFICIAL_PROVIDER_DOCUMENTATION_ONLY
SOURCE_COMMIT=e562642eeb6778a253fcdc87ef67d9f7b4a5f5c8
SOURCE_COMMIT_TREATMENT=REVIEWED_NOT_CHERRY_PICKED
LIVE_CALLS=0
PAID_SPEND=0
NETWORK_CALLS_FROM_TESTS=0
ADOPTED_PROVIDER=NONE
ADOPTED_MODEL=NONE
```

## 1. 结论与边界

旧候选提交只能作为设计来源。本修复没有 cherry-pick 旧实现，而是针对审计缺口重建
Provider 中立合同。OpenAI、Anthropic、Google Gemini、DeepSeek 全部仍为
`CANDIDATE`；本分支不把任何候选提升为 `VERIFIED` 或 `ADOPTED`，也不表示已经可以
发起付费探针。当前项目 authority 仍阻断 live probe。

`src/jianghe_model_provider.py` 不含 HTTP、socket、第三方 SDK、环境变量读取或真实调用
实现。`CandidateProviderAdapter.invoke()` 固定失败闭合；测试只解析内存中的模拟回复。

## 2. 对旧候选的缺口复核与修复

| 审计项 | 旧候选风险 | 本修复的合同 |
| --- | --- | --- |
| 同一 observation | 图像与结构化载荷各自有标识，但请求层未充分证明来自同一 canonical observation | `JiangheModelRequest` 要求每个 artifact 的 `observation_identity` 与请求完全一致；视觉、结构化和双输入分别失败闭合 |
| requested / resolved model | 请求模型与 Provider 实际返回模型容易被压成一个 identity | `RequestedModelSelectorIdentity` 与 `ResolvedProviderModelIdentity` 分离；响应证据同时绑定两者 |
| API surface / version | Provider 名称本身不能说明调用接口及版本语义 | `ProviderIdentity` 绑定 `provider_id + api_surface + api_version + endpoint_semantics_identity` |
| structured INPUT / OUTPUT | 运输层 JSON、结构化输入、结构化输出容易混为一项能力 | `CapabilityDeclaration` 分别声明 `supports_structured_input` 与 `supports_structured_output`；轨道只消费对应输入能力 |
| response evidence | 原始回复、用量、延迟和模型解析结果的身份不够完整 | `JiangheModelResponseEvidence` 确定性绑定 request/provider/capability/requested/resolved/response-id/timestamps/latency/raw-hash/normalized-response/usage |
| visual provenance | MIME、实际 bytes、renderer 与 observation 可能只靠 caller 自报 | 视觉请求只接受 `VisualArtifact.from_canonical_observation()` 经最新 integrated renderer 生成的产物；桥接层核对 manifest、PNG bytes/hash、renderer/config、renderer projection 与 canonical observation 来源，声明不一致即拒绝 |
| evaluator provenance | provider 请求/响应证据可能无法无损进入统一评分接口 | `JiangheModelRequest.to_input_evidence()` 显式绑定 prompt package、normalizer、evaluation extractor、provider invocation/response、视觉与结构化 artifact 身份 |
| provider failure | malformed/拒绝的 provider 回复可能被误当成可评分成功样本 | 统一 record 构造将解析失败写为 `call_success=false`，不伪造 response identity；integrated evaluator 必须将其判为 non-scoreable |

每个 `JiangheModelRequest` 还显式绑定 prompt package、context-selection policy、
response schema、runtime normalizer 与 evaluator-side extractor identity；模拟响应解析时，
实际 normalizer/schema 与请求不一致会失败闭合。runtime normalizer 只保留模型客观输出；
violation/no-invention 裁决只允许来自 evaluator-side judgment，且 extractor identity 必须
与请求一致。

视觉 artifact 不反向进入 source observation identity，避免循环哈希：canonical observation
先绑定当时可见的 bars、positions、orders、metadata；适配层将其交给最新 integrated renderer，
派生图像绑定 renderer projection、配置和实际 PNG bytes；最终 request 与 `InputEvidence`
同时保存共同 canonical observation 来源。`DUAL_INPUT` 的 visual、structured 与顶层
observation identity 必须完全一致。

## 3. 能力词义

- **结构化 INPUT**：项目 observation JSON 作为受身份约束的输入内容被发送。请求 body
  本身是 JSON 不足以证明该能力；还必须保存 schema、内容哈希和 observation identity。
- **结构化 OUTPUT**：Provider 能约束模型回复为 JSON 或 JSON Schema。它不证明内容
  正确，仍必须由项目 normalizer 做严格字段、类型与枚举校验。
- **resolved model reporting**：响应可见模型字符串不自动等于精确快照。若 Provider 未返回
  可治理的版本/快照，`resolved_version_or_snapshot` 必须保持未知并阻断要求精确复现的请求，
  不得把 requested alias 复制成 resolved identity。
- **raw response / timing**：由未来项目 adapter 在本地捕获，不是 Provider 替项目保存的
  审计承诺；本分支没有实现该网络 adapter。

## 4. 官方资料侦察（仅候选证据）

| Provider / API surface | 视觉 INPUT | 结构化 INPUT | 结构化 OUTPUT | 响应证据与版本语义 | 当前状态 |
| --- | --- | --- | --- | --- | --- |
| OpenAI Responses API | 官方资料描述图像输入 | 可将项目 JSON 作为文本输入；原生 schema-typed input 语义仍待探针 | 官方资料描述 JSON Schema structured outputs | response id、usage 等可捕获；具体 selector 是否解析为可治理快照仍为 `UNKNOWN_PENDING_PROBE` | `CANDIDATE` |
| Anthropic Messages API | 官方资料描述 base64、URL、file_id 图像 | 可将项目 JSON 作为消息内容；原生 schema-typed input 语义仍待探针 | `output_config.format` 支持 JSON Schema | response model 与 usage 可捕获；官方区分固定 model ID 与可能漂移 alias | `CANDIDATE` |
| Google Gemini GenerateContent API | `inlineData` 可携带 `image/png` | 可将项目 JSON 作为内容；原生 schema-typed input 语义仍待探针 | `application/json` 配合 response schema/JSON Schema 子集 | `usageMetadata`、`modelVersion`、`responseId` 可见；具体账号/模型仍待探针 | `CANDIDATE` |
| DeepSeek Chat Completions API | 本轮官方资料未确立，记为 `UNKNOWN` | 文本消息可承载项目 JSON；不是原生 schema-typed input 证明 | JSON Output 只保证合法 JSON，官方提示可能返回空内容 | response id/model/system fingerprint/usage 可见；model 字符串是否是稳定快照仍为 `UNKNOWN_PENDING_PROBE` | `CANDIDATE`；不得进入 VISUAL/DUAL_INPUT |

上表只表示文档层候选能力，不代表项目账号、具体模型、成本、区域、限额、实际 MIME、
严格 schema 遵循度或 fidelity 已验证。任何 `UNKNOWN` 都不得由默认值、UI 可选项或模型
自报补成 `YES`。

## 5. 官方来源

### OpenAI

- [Responses API 快速开始与图像输入](https://platform.openai.com/docs/quickstart/make-your-first-api-request)
- [Responses API 字段与 structured outputs](https://platform.openai.com/docs/api-reference/responses-streaming/response/refusal/delta?lang=curl)
- [Responses 输入与数据控制](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint)

### Anthropic

- [Messages API](https://platform.claude.com/docs/en/api/messages/create)
- [Vision 输入](https://platform.claude.com/docs/en/build-with-claude/vision)
- [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Model IDs 与版本语义](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions)

### Google Gemini

- [GenerateContent API、inlineData、response schema 与响应元数据](https://ai.google.dev/api/generate-content)
- [Gemini API 总览](https://ai.google.dev/api)

### DeepSeek

- [Create Chat Completion](https://api-docs.deepseek.com/api/create-chat-completion)
- [JSON Output 与空内容风险](https://api-docs.deepseek.com/guides/json_mode/)

## 6. 仍然关闭的门

进入第一次真实探针前，至少还需要 Owner 明确批准 Provider/account、credential 机制、
最大支出与停机规则、具体 model selector/快照与漂移策略、允许的数据种类、调用次数、
原始回复保存范围，并由 project brain 重新审计本修复。此前固定保持：

```text
LIVE_CALLS=0
NETWORK_CALLS_FROM_TESTS=0
PAID_SPEND=0
OUTCOME_ACCESS=NO
PRIMARY_FREEZE=NO
```
