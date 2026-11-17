# G0 Provider 接入矩阵

静态基线为 `15c2d5f1b56682ce98e6c6ed76e254eec124e15e`，日期为 2026-11-17。下表描述本次源代码审阅结果。Mock 合约、真实请求、判读质量、账号免费资格均保留独立状态。

## 接入路线

| 路线 | 静态核对结果 | 协议与配置 | Mock 合约 | 真实采样 | 合格非模拟判读 | 账号/额度 | G0 判定 |
|---|---|---|---|---|---|---|---|
| 上游 stub | registry 有 `stub`，judge 有规则替身 | `stub:stub`、`ONBOARDING_LLM_TARGET=stub:stub`、`TYPESAFE_API_KEY=stub` | NOT_RUN | NOT_RUN | NOT_RUN | NOT_CHECKED | 可用于后续 L1 流程验证 |
| OpenAI 原生 | registry 有 `openai-api`，使用 `provider.responses(model)` | `chatgpt:openai-api:<approved-model-id>`，Key 为 OPENAI_API_KEY | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 原生接入代码存在，A1 缺失 |
| Gemini 原生 API | registry 没有专用 Google adapter | 后续必要时实现独立协议适配 | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 需要适配评估 |
| Gemini OpenAI 兼容 | 官方有 Chat Completions 兼容说明，Elmo 没有对应 adapter | 官方示例 host 为 `generativelanguage.googleapis.com`，精确版本/模型待选 | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 需独立合约，Responses 兼容性未经证明 |
| Gemini 经 OpenRouter | 已有通用 OpenRouter adapter，STATUS_TARGETS 包含 Gemini | `gemini:openrouter:<approved-google-model-slug>`，使用 gateway Key | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 属于 gateway 路线，模型当前可用性待核验 |
| Qwen 经 OpenRouter | 通用 adapter 存在，STATUS_TARGETS 包含 Qwen | `qwen:openrouter:<approved-qwen-model-slug>`，使用 gateway Key | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 已有接入抽象，免费资格待核验 |
| Qwen / DashScope 直连 | registry 没有专用 DashScope adapter | 地域/workspace 对应的 OpenAI compatible Chat 端点，实际值待账户确认 | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 需要适配评估 |
| 本地模型 | 所审 registry 没有专用本地 adapter | 模型、权重许可、硬件与 endpoint 均未选 | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 如需使用应先做范围决定 |
| 第三方采样商 | registry 有六种采样商实现，部分支持 Gemini 等目标 | SearchAPI、Olostep、Bright Data、Oxylabs、Cloro、DataForSEO | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 有独立凭据与潜在费用，当前停用规划 |

以上目标格式仅用于计划。`<approved-…>` 需要实际批准值。registry 对未知 provider 抛错，目标 parser 可解析版本字符串，但源码没有完整的账号授权模型白名单。P0 需在请求守卫中固定模型、host、地区、角色和凭据别名。[registry](upstream/elmo/packages/lib/src/providers/index.ts) [目标 parser](upstream/elmo/packages/config/src/scrape-targets.ts)

## OpenAI 和研究路径

采样中 `options.version` 决定实际请求模型，缺省会使用 adapter 默认研究模型。采样搜索开关为显式 true，最大输出 8,000。所审调用未设置统一 maxRetries、取消 signal 和总超时。结果仅返回 rawOutput、webQueries、modelVersion。[OpenAI adapter](upstream/elmo/packages/lib/src/providers/registry/openai-api.ts)

结构化研究采用独立默认模型，并且 `webSearch=true` 为默认值。`ONBOARDING_LLM_TARGET` 只使用 provider 段，模型段会被研究实现忽略。Opportunities 则通过 completion wrapper 明确设置 `webSearch:false`，仍然会消耗模型请求。[研究选择](upstream/elmo/packages/lib/src/onboarding/llm.ts) [结构化生成](upstream/elmo/packages/lib/src/providers/registry/ai-sdk.ts)

OpenAI raw response 缺失时 adapter 会重建正文与引用结构。此时原始搜索调用项可能丢失，模型实际回报值、usage、请求 ID、结束原因与截断状态需在 TUC 证据侧车补齐。adapter 对截断仅告警，后续不能直接将其纳入正常完成的分母。[返回结构](upstream/elmo/packages/lib/src/providers/types.ts) [输出上限](upstream/elmo/packages/lib/src/providers/config.ts)

Google 官方兼容示例使用 Chat Completions，Alibaba 文档要求 Key 与地区 endpoint 相匹配。实际适配需要验证请求字段、usage、取消、输出/推理 Token 上限、引用及错误语义。[Google 兼容说明](https://ai.google.dev/gemini-api/docs/openai) [Alibaba 兼容说明](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)

## Jev 与判读选择

| 条件 | 固定源码行为 | 当前核验状态 |
|---|---|---|
| TypeSafe Key 为 `stub` | `jevAnalyzer(stubTransport, 8, "stub")`，按 cue words 产生结果 | 静态已读，JUD-01 为 NOT_RUN |
| TypeSafe Key 非空 | 选择 TypeSafe transport，模型 `jev-1.13.0` | 通道代码已读，额度 UNKNOWN |
| TypeSafe 缺失，OpenRouter Key 非空 | 选择 OpenRouter systemone，模型 `typesafe/jev-1.13` | 通道代码已读，额度 UNKNOWN |
| 两者缺失 | 抛出明确配置错误 | 静态已读，JUD-02 为 NOT_RUN |
| 所选通道故障 | 工厂保持所选网关，429 可在池内重试 | COST-05/08 为 NOT_RUN |
| DB 解密失败或无 overlay | 通用 `getCredential` 允许读环境值 | COST-08、SEC-07 为 NOT_RUN |

Worker 的 TypeSafe Key 默认直接来自 `process.env.TYPESAFE_API_KEY`。OpenRouter Key 来自回调 `getCredential`，可动态刷新。两条来源应分别记录，不能把全部 judge 凭据概括为 DB overlay。[Worker 判读入口](upstream/elmo/apps/worker/src/mention-judge/index.ts)

Jev 请求可能批量包含多个实体的 verdict 与 evidence 问题。TooLarge 会导致实体拆分或回答截短后再请求。adaptivePool 默认并发上限 64，429 重试最多六次，报告判读外层最多三次尝试，derive 队列另可重投。[判读工厂与拆分](upstream/elmo/packages/lib/src/mention-judge/analyze.ts) [transport 和重试池](upstream/elmo/packages/lib/src/mention-judge/jev.ts)

当前没有 Jev 免费额度或硬停止证明。可选下一步为合格的免费 Jev、一个获批的替代 MentionAnalyzer，或只验证规则可证明的有限指标。替代判读器需要独立 judgeVersion、人工复核标签和 holdout 质量证据。判读准确率、precision、macro-F1 和引文一致性全部为 `NOT_RUN`。

## API / MCP 能力边界

源码已发现 `/api/v1/brands`、`/api/v1/prompts/{promptId}/runs`、`/api/v1/prompts/{promptId}/runs/{runId}`、分析、引用和报告路由。MCP registry 有 17 个工具，包含创建和修改 prompts。所有接口运行发现与鉴权验证均为 `NOT_RUN`。[MCP registry](upstream/elmo/apps/web/src/lib/mcp/tools/index.ts)

`get_opportunities` 标为 readOnly，代码会调用 `publishedOpportunities → resolveOpportunities`。缓存过期或缺失且摘要足够时生成新报告并写库。初始只读白名单应排除此调用路径。`get_run` 返回规范化正文和引用，raw、judgeVersion fingerprint 和 passage offsets 保持内部字段，完整可审计导出仍有缺口。[MCP analytics](upstream/elmo/apps/web/src/lib/mcp/tools/analytics.ts) [Run 返回映射](upstream/elmo/apps/web/src/server/runs-core.ts)

## 下一阶段路线建议

优先执行原版 stub 基线和已有 OpenAI/OpenRouter 抽象的离线合约。负责人确认已有零新增费用的账号与 judge 条件后，再选择一个真实主路线。Gemini/DashScope 直连的实现取决于该选择，避免同时维护多套未使用适配器。G0 当前没有选定真实模型或 endpoint。
