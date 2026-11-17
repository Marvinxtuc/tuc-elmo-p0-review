# G0 依赖与潜在费用登记

日期为 2026-11-17，基线为 `15c2d5f1b56682ce98e6c6ed76e254eec124e15e`。表内凭据均为变量名，用户账号、Key 和额度未读取。费用默认新增授权为 USD 0，付费余额消耗同样需要明确授权。所有关联测试状态为 `NOT_RUN`。

本表覆盖已审阅的采样、初始化、判读、报告、调度、凭据、可观测性及安装路径。SDK 下载内容、运行期 DNS、传递依赖许可和网络绕行仍需后续证据。源码路径相对 `upstream/elmo/`，完整源文件及哈希随审计目录保存。

## 运行与供应链

| ID | 动作与源码符号 | 服务或资源 | 凭据来源 | 费用与默认条件 | 重试或取消语义 | P0 处理与关联测试 |
|---|---|---|---|---|---|---|
| D01 | 安装与构建，根 `package.json`、`pnpm-workspace.yaml`、`docker/Dockerfile:5` | Node 24、pnpm 12.18.0、包注册源、容器 registry、Alpine 软件源 | 不应继承 cloud / registry 私有凭据 | 下载、磁盘、构建资源和可能的云缓存费用。G0 未安装 | 安装失败须保留原始原因，供应链拒绝需处理 | A0 后用隔离工具链与冻结 lockfile，保留 `minimumReleaseAge:5760`、`trustPolicy:no-downgrade`、`blockExoticSubdeps:true` 及 allowBuilds/overrides。SRC-03/05、ENV-04 |
| D02 | 安装脚本，`apps/www/package.json` 的 postinstall，workspace allowBuilds | fumadocs-mdx、原生构建、浏览器与 Sentry CLI 二进制 | Sentry 凭据不得注入准备阶段 | 允许的 install scripts 可下载资源，Puppeteer / Sentry 等列为 allowBuilds=true | 安装与运行分阶段审计 | G1 审阅实际下载来源与脚本日志。SRC-05、ENV-06 |
| D03 | DB 与队列，`apps/cli/src/compose.ts:95`、`worker/src/boss.ts` | PostgreSQL / pg-boss。Compose 提议 `postgres:18-alpine` | 新测试 DATABASE_URL、独立账号 | 存储和备份成本，G0 无运行实例 | 队列可重投，DB 断连恢复待测试 | A0 指定两个全新测试库供迁移与恢复，实际版本和 digest 待锁定。ENV-01/03、OPS-02/03 |
| D04 | 许可检查，`LICENSE.md`、`scripts/check-licenses.mjs` | 源码 MIT、第三方依赖、字体、工具及服务 | 无 | 根 MIT 已读取，脚本包含 FSL/OFL 等例外 | 检查脚本读取已安装依赖元数据 | 第三方逐项许可、SBOM、漏洞状态保持待核验。模型权重本次未选。SRC-02/05、SEC-09 |
| D05 | Docker / 本机资源 | arm64 测试机器、daemon、Compose、磁盘 | 运行环境授权 A0 | 已有 CLI 不证明引擎可用或软件许可满足，Docker Desktop 商业资格待核验 | 停止须限定本 run，清理卷另需批准 | 建议 Web loopback、DB 不发布宿主端口，资源上限见执行清单。ENV-01、OPS-04/05 |

## 模型、判读及旁路调用

| ID | 触发动作、源码路径与符号 | 外联与凭据来源 | 费用类型与默认条件 | 重试、取消与证据限制 | P0 处理与关联测试 |
|---|---|---|---|---|---|
| D06 | 采样 `providers/registry/openai-api.ts:26` `getOpenAIResponsesModel` / `runOpenAI` | OpenAI SDK Responses，常规 API host `api.openai.com`。`getCredential(OPENAI_API_KEY)`，缺省可走 SDK 环境解析 | Token 与可选搜索费用。采样 webSearch 仅在显式 true 时开启，输出上限 8,000 | 调用处未显式设置 maxRetries、总超时或取消 signal，SDK 最终行为待锁定验证。返回结构没有单独 usage 字段，raw 可回退重建 | G2 补统一请求边界，模型/host/Key 别名白名单。PRV-02/05/06/07、COST-01/04/05 |
| D07 | 采样与研究 `providers/registry/openrouter.ts:100` / `:64` | `openrouter.ai/api/v1/chat/completions`，`getCredential(OPENROUTER_API_KEY)` | Qwen/Gemini 可通过 gateway 配置，实际模型资格未知。研究默认独立模型 `anthropic/claude-sonnet-5.5`，默认可带 native search | raw fetch 调用没有统一超时/取消 signal。结构化研究未显式设置输出上限，模型提供商回退条款需进一步核验 | 默认关闭，A1 逐角色批准。PRV-04/05/06/08、COST-06/08 |
| D08 | 其他直接 LLM，`registry/anthropic-api.ts`、`mistral-api.ts` | Anthropic SDK / `api.anthropic.com`、`api.mistral.ai`，相应环境或 DB overlay Key | Token、Anthropic 搜索等潜在费用。研究自动选择顺序可到达这些 Provider | Anthropic 搜索错误有额外重试，SDK 行为需实测 | 非候选角色保持关闭。COST-05/06/08、PRV-06 |
| D09 | 第三方采样，`providers/index.ts` 及各 `registry/*.ts` | SearchAPI `www.searchapi.io`、Bright Data `api.brightdata.com`、Oxylabs `data.oxylabs.io`、Cloro `api.cloro.dev`、DataForSEO `api.dataforseo.com`、Olostep SDK host 待核验。相应 registry credential 名称 | 采样、异步任务、轮询、搜索或订阅费用，需目标配置与 Key | `retryTransient` 共三次尝试，Olostep SDK `maxRetries:3`，异步受理后的取消/计费待核验 | 不配置采样商 Key。本 P0 使用 stub 或另批原生 API。COST-01/05、PRV-01/08 |
| D10 | 品牌初始化与问题建议，`onboarding/analyze.ts:178`、`suggest-prompts.ts:60`、`llm.ts:23` | `runStructuredResearchPrompt` → 研究 Provider。显式 target 只选择 provider 段，研究模型由 provider 内部决定 | 有独立研究费用。无显式配置时按 OpenAI→OpenRouter→Anthropic→Mistral 选第一个已配置服务 | `analyze-brand` 与 `suggest-prompts` 队列各 `retryLimit:1`，结构化 SDK 重试待核验 | G1 仅固定种子与 stub。G2 禁止未批准研究，禁止 target 中模型名被忽略而绕过白名单。COST-06/08、PRV-06 |
| D11 | 官网摘要抓取，`website-excerpt.ts:16` `getWebsiteExcerpt` | 默认先 `r.jina.ai/<url>`，可选 `process.env.JINA_API_KEY`。失败后直接读取输入 URL | 匿名配额与带 Key 请求资格未知，可能产生第三方内容传输和费用 | Jina 30s、直抓 15s，响应限 2MiB。fetch 默认重定向，所审函数未实现逐跳 IP/DNS 审查 | G1 回放摘要或固定文本，G2 捕获 Jina 和直抓两条出站。COST-06、SEC-06/08 |
| D12 | TypeSafe Jev 判读，`mention-judge/jev.ts:53`、`analyze.ts:276` | `api.typesafe.ai/v1/systemone`，`jev-1.13.0`。Worker 默认直接取 `process.env.TYPESAFE_API_KEY` | 独立判读 Token 费用，非空 TypeSafe Key 优先。原生 stub 分支使用规则 | transport 30s。adaptivePool 并发最高 64，429 默认六次重试。`askFitting` 可拆分实体或截短回答后再请求 | A1 单独批准 judge，G2 统一计数，G3 质量验证。JUD-01/02/03/07、COST-04/05 |
| D13 | OpenRouter Jev 判读，`jev.ts:58` / `createMentionAnalyzer` | `openrouter.ai/api/v1/systemone`，模型 `typesafe/jev-1.13`，`getCredential(OPENROUTER_API_KEY)` | 无 TypeSafe Key 时可选。相同 gateway Key 可同时承担采样和判读费用 | 网关选择在工厂初始化时确定，所选网关失败时不会自动切换另一网关。其 Key 每次解析，仍受 DB/env 变化影响 | 记录 answer/judge 各自 credential_ref 和请求数量。当前免费与硬停止未知。JUD-07、COST-08/10 |
| D14 | 原生 stub，`registry/stub.ts`、`jev.ts:197` | 无模型 API，`TYPESAFE_API_KEY=stub` / 两个 stub target | 仅规则和预置回答，运行仍使用本机资源 | stub 之外的网页摘要、图标和遥测路径仍可能联网 | 输出显著标 `UPSTREAM_STUB`。ENV-02/06、JUD-01、DATA-02 |
| D15 | Opportunities，`server/opportunities.ts:527` / `resolveOpportunities` | `runStructuredCompletionPrompt` 采用研究 Provider，但明确 `webSearch:false` | 无新鲜缓存且数据足够时产生独立模型调用，local `reportGeneration:true` | 最多三次生成尝试，成功写 `brandOpportunities`。GET 与 `get_opportunities` 也可触发 | 初始纯读取白名单排除该路由，报告采用确定性离线模板。COST-06、SEC-04、DATA-07/08 |
| D16 | 报告链判读，`worker/src/report-worker.ts:168` `judgeWithRetries` | 当前 MentionAnalyzer，可能落到 D12/D13 | 每回答判读最多三次外层尝试，可叠加 transport 内重试 | 尝试间等待 5s×attempt，无法用报告 queue retryLimit=0 推断零额外判读 | G2 所有传输经过统一计数与批准。COST-05、JUD-07 |

## 后台、权限、网络与可观测性

| ID | 触发与源码 | 域名 / 凭据 | 默认与费用影响 | 重试及取消 | P0 处理与关联测试 |
|---|---|---|---|---|---|
| D17 | 凭据加载，`secrets/store.ts:21`、`:47`、`refresh.ts:22` | DB secrets overlay → `process.env`，由 `ELMO_ENCRYPTION_KEY` / retired keys 解密 | overlay 不含某 Key 时可回落环境值。首次加载失败继续，后续每 60s 刷新 | 刷新失败可保留旧 overlay，坏密文行跳过。未知账号回退风险为静态可达 | 清洁 HOME/env、新测试库、单一合成 credential_ref。真实模式应失败关闭。COST-08、SEC-07 |
| D18 | 历史重判 / Worker 启动，`worker/index.ts:124`、`:158`、`jobs/reprocess.ts` | pg-boss / 当前 judge | 启动补判最近 30 天、定期 reprocess，REPROCESS_DAYS 默认 90，名字/竞品/judgeVersion 变更可触发 | derive 队列 retryLimit=5，reprocess=2。重启和启用旧品牌可放大费用 | G1 从空库与 deny-egress 开始，G2 隔离启动回补并测试撤回。ENV-05、COST-07 |
| D19 | 周期采样，`constants.ts:1`、`web/lib/job-scheduler.ts:52`、`jobs/process-prompt.ts:398` | 配置的全部目标与相应 Key | 默认五次采样、默认 24 小时，处理完成后安排下一周期 | process-prompt queue retryLimit=0，但周期失败可退避后重调度 | 显式倍数 1，并单独禁止继任任务、新旧计划、补偿与手动旁路。ENV-05、COST-05/09 |
| D20 | MCP / API，`mcp/tools/index.ts`、`tools/prompts.ts`、`routes/api/v1/*` | 内部 API Key / session / OAuth scope | 目录有 17 个工具，含 create/update prompts，后者可触发队列。read scopes 也包含 D15 | HTTP 方法和 readOnly 标注无法覆盖全部副作用，后台作业继续独立运行 | 初始仅允许已审阅纯读取工具。发现及鉴权实测 `NOT_RUN`。SEC-02/03/04、DATA-07 |
| D21 | Telemetry / 错误上报，`worker/telemetry.ts`、`cli/telemetry.ts`、`web/server/config.ts`、`worker/instrument.ts`、`web/router.tsx` | `us.i.posthog.com`，Sentry DSN 决定 host，浏览器 Plausible/Clarity 变量，Crisp 为 cloud/demo | PostHog 可有内置公共项目标识。DISABLE_TELEMETRY 控制 PostHog，Sentry 独立按 DSN 启用，监测服务潜在费用及隐私影响 | flush 与 SDK 后台发送独立于模型任务，关闭效果待捕获 | 清洁配置移除全部非必要监测变量，后续捕获浏览器、Web 与 Worker 出站。ENV-06、SEC-01/08 |
| D22 | 图标与远程资源，`routes/api/site-icon/index.ts:32`、`lib/site-icon.ts`、`routes/api/og/index.ts:49` | `t1.gstatic.com/faviconV2`，以及配置的远程 icon URL | 无模型调用，但可有额外公网读取、数据传输和 SSRF 路径 | site icon 超时 5s、OG icon 3s，最终重定向行为待验证 | stub 浏览器请求也需记录，优先本地资源。ENV-06、SEC-06/08 |
| D23 | Cloud / white-label，`deployment/src/auth-hooks/cloud.ts`、`billing/plugin.ts`、`email.ts`、`auth-hooks/whitelabel.ts` | Stripe、Resend、Auth0，相关环境变量 | local billing=false、teamInvites=false。cloud 的账单/邮件与 white-label 的 SSO 是其他模式路径 | 第三方副作用需分别处理，当前未执行 | 固定 local、清洁配置、限制模式切换，真实支付与发信留在当前范围外。ENV-01、SEC-01/09 |
| D24 | 网站就绪扫描，`packages/site-audit/src/audit.ts`、`fetcher.ts` | 提交的公开网页和 robots/sitemap | 已有开源扫描逻辑，但仍消耗网络和资源，P0 未执行扫描 | 请求、重定向、私网控制按实际 scanner 代码待专项审阅 | G0 只做一次官网 GET。需使用扫描能力时另审范围及 SSRF 合约。SEC-06、ENV-06 |

## 账号、额度和商业授权

| 对象 | 当前状态 | 后续必须核实的材料 |
|---|---|---|
| OpenAI answer | `UNKNOWN` | API organization、model 权限、已到账有效 credits、禁止超额付费的硬控制、精确 endpoint 与用途 |
| Gemini answer | `UNKNOWN` | 实际项目 tier、模型免费资格、地区、限额、数据使用条款、付费回退状态 |
| Qwen / DashScope answer | `UNKNOWN` | 地区/workspace/模型一致、有效免费额度、Free Quota Only 的实际状态和适用性 |
| OpenRouter answer | `UNKNOWN` | 所选模型可用性、免费资格、提供商路由与回退、账单硬停止 |
| TypeSafe / OpenRouter Jev | `UNKNOWN` | 独立 judge 免费额度、Jev 版本、systemone 许可与硬停止，不能从 answer 免费推导 judge 免费 |
| 数据 / 报告商业使用 | `UNVERIFIED` | API 数据保存、报告分享、模型输出用途、再分发和处理条款，当前仅规划内部验证 |
| Docker 运行环境 | `UNVERIFIED` | 实际容器引擎、既有设备授权与适用软件许可 |

OpenAI 官方区分 ChatGPT 与 API 账单，符合条件的订阅仍需激活并确认实际到账的 credits。本次账号状态未核实。[账单说明](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform) [Credits 资格说明](https://help.openai.com/en/articles/20001626-api-credits-benefit-for-eligible-chatgpt-subscriptions)

Gemini 官方说明 Free tier 限定可用模型和额度。Alibaba 当前文档将新用户免费额度限定到指定地区/部署范围，额度耗尽或过期可转按量计费，Free Quota Only 需要核实实际开关。此次均只读取公开说明。[Gemini 计费说明](https://ai.google.dev/gemini-api/docs/billing) [Model Studio 免费额度](https://www.alibabacloud.com/help/en/model-studio/new-free-quota)

## 费用结论

G0 的新增购买和授权支出为 0，本次没有执行真实模型请求。服务商实际账单核验状态保持 `NOT_RUN`，金额为 `null`。已有设备、网络、电力及 Codex 权益的机会成本未经核算。

G1—G3 与离线 G5 的采购预算建议继续为 0，前提是既有测试环境与开源依赖满足许可和资源要求。出现付费前置条件即记录具体 blocker。G4 的账号费用、Token 上限、所有角色请求合计和硬停止证明需要 A1 单独批准。
