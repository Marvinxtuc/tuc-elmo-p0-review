# G0 冲突与处置记录

日期为 2026-11-17。下表的处置适用于本次只读核查，后续实施均以负责人实际批准范围为准。风险为静态代码发现，相关运行测试全部为 `NOT_RUN`。

| ID | 冲突或差异 | 依据 | 本次处理与后续要求 |
|---|---|---|---|
| C01 | 前一 GEO 执行包提出 `geo.techunityconnect.com` 与独立产品平台，新计划 C01 采用唯一公网业务域名 | 旧包 `docs/01_EXECUTION_PLAN_ZH.md` §4，新附件 §2、§4 | 新请求仅推进 Elmo 内部核查。新增子域、支付、客户门户与完整 SaaS 留在本次范围外，后续如需采纳旧方案应重新提案 |
| C02 | 官网范围排除 DB/认证/门户，Elmo 自带 PostgreSQL、认证和后台 | 官网当前 `AGENTS.md`，上游 `AGENTS.md` | 采用官网目录之外的审计与拟议测试目录，后续内部 Elmo 的数据库和权限单独隔离 |
| C03 | 官网存在两个未提交规则修改，附件引用的是 HEAD 中的 AGENTS blob | `SOURCE_LOCK.json` 的 website 字段 | 记录 HEAD、工作树 blob 和 SHA-256，以当前工作树文件约束审阅，原改动保留 |
| C04 | 上游要求交接前 lint，用户限定 G0 且禁止安装与服务 | 上游 `AGENTS.md` 的 Commands，最新请求 | 当前 lint 为 `NOT_RUN`。G0 报告存于上游目录外，后续实际代码交付遵守相应质量门禁 |
| C05 | 附件 A0 模板与完整阶段命令可执行，当前批准范围仅 G0 | 附件 §12、§13、§21 | 模板保存为待批准规格，A0/A1 均记 `NOT_GRANTED` |
| C06 | 当前 PATH 为 Node 22.23.1 / pnpm 9.15.9，上游要求 Node 24 / pnpm 12.18.0 | 环境证据、上游 `package.json` | 后续采用项目隔离工具链，准备动作等待 A0 |
| C07 | 开发文档要求 `cp .env.example .env`，固定源码根目录缺失该文件 | `development-setup.mdx`，固定 tree 清单 | 后续依据 env registry 与 validator 构造新测试配置，逐项核对 root 和 apps/web 两处文件 |
| C08 | 上游原 UI 要求 root-path，业务域名受单域名约束 | `configuration.mdx:128` | P0 以 loopback 内部根路径运行。未来服务端读取方案留待 ADR，不承诺原 UI 可直接挂 `/geo` |
| C09 | local 是 single-org，但源码存在组织字段、scope 和跨组织测试 | `configuration.mdx:13`，`deployment.ts:14` | 限定内部单组织。实际认证及对象授权保留 SEC-02/03 测试，多客户商业适用性待单独评审 |
| C10 | OpenAI 兼容接口说明以 Chat Completions 为主，Elmo OpenAI 路线使用 Responses | `openai-api.ts:26`，Google/Alibaba 官方兼容文档 | Gemini/DashScope 直连标记为需适配。精确 endpoint、地区、model、usage 与工具能力待 G3 合约验证 |
| C11 | 判读工厂明确不跨网关故障回退，通用凭据解析却允许 DB overlay 缺失时取 env | `analyze.ts:276`，`secrets/store.ts:21`、`refresh.ts:22` | 分别描述网关选择与凭据来源。后续合成双账号、解密失败及 401 负例必须覆盖，当前记录为可达风险 |
| C12 | P0 要求全部角色并发 1、自动重试 0，上游有多层重试与并行 | `jev.ts:111`、`:119`，`analyze.ts:184`，`report-worker.ts:168`，`derive-runs.ts:38` | 请求守卫需覆盖池、递归拆分、SDK、队列和报告尝试。配置值必须由真实请求边界读取并验证 |
| C13 | 原版 GET / MCP opportunities 标注 read，缺缓存时存在模型调用与 DB insert | `routes/api/v1/brands/$brandId/opportunities.ts:14`，`mcp/tools/analytics.ts:127`，`server/opportunities.ts:542` | 从初始纯读取白名单中排除此能力，后续仅允许纯读取已存报告或显式批准生成。相关 COST-06、SEC-04、DATA-07 为 `NOT_RUN` |
| C14 | `DISABLE_TELEMETRY` 可关闭 PostHog，Sentry 另按 DSN 启用 | `worker/src/telemetry.ts:8`，`worker/src/instrument.ts:11`，`web/src/router.tsx:30` | 后续清洁配置移除 Sentry、Plausible、Clarity 等变量并捕获浏览器/Worker 出站。单个开关效果留待 ENV-06 |
| C15 | Compose 模板发布 `5432:5432` 与 `${port}:3000`，并带依赖迁移容器 | `apps/cli/src/compose.ts:95`、`:118`、`:168` | 后续采用经审阅的测试 Compose，Web 仅 loopback，DB 不暴露宿主，迁移只在 A0 目标库执行。原版快速启动命令待审阅后使用 |
| C16 | 采样默认五次，Worker 有启动重判和继任调度，P0 只允许有限手动批次 | `constants.ts:1`，`worker/index.ts:124`，`jobs/process-prompt.ts:43`、`:398` | `RUNS_PER_PROMPT=1` 只约束倍数。后续分别阻断新增计划、待执行队列、重判、补偿和周期后继 |
| C17 | 配置文档称旧任务保留原节奏，当前任务代码会读取当前 plan 并在周期后调度下一次 | `configuration.mdx:56`，`jobs/process-prompt.ts:88`、`:398`，`web/lib/job-scheduler.ts:47` | 标记文档与实现差异。ENV-05 需检查排队中 startAfter 与下一周期，保持显式调度门禁 |
| C18 | 原始 API 记录与 TUC 完整证据合约存在字段缺口 | `providers/types.ts:7`，`openai-api.ts:80`，`server/runs-core.ts:25`、`:103` | 上游公共 API 返回规范化正文，隐藏 raw、判读 fingerprint 与 passage offsets。后续采用内部授权导出和侧车证据，并保留模型实际回报值、usage、请求 ID 与 hash |
| C19 | 上游 CLI link 脚本调用 npm 全局操作，AGENTS 规定只用 pnpm | 根 `package.json` 的 `cli:link` / `cli:unlink` | P0 不需要全局链接，可使用批准环境中的项目命令。列入后续命令审阅清单 |
| C20 | 根 MIT 声明与第三方 API、依赖、数据、模型权重许可属于不同材料 | `LICENSE.md`，`scripts/check-licenses.mjs`，附件 §2、§16 | 保存 MIT 声明，逐项许可和服务权利仍待核验。G0 保持内部静态研究状态 |
| C21 | 本地官网 HEAD 与历史发布记录存在 SHA 差异，当前公开页面未暴露生产 commit | 官网发布文档、`website-public-en.json` | 当前源码/生产一致性记 `UNKNOWN`，记录 HTTP 200 与 Netlify 头，不推断部署版本 |

## 对既有执行包的适用解释

前一执行包中的预算、报价、真实支付、销售外联和远程仓库模板不构成本次批准。此前被中断的 M0 静态读取没有产生该执行包要求的四份报告，本次交付依据为用户最新提出的 Elmo G0 六项输出。

审计过程没有调用上游应用脚本。环境的广泛文件权限仅描述工具能力，实际行动范围仍按本次 G0 请求执行。

## 可复核来源

固定上游路径均相对 `upstream/elmo/`。源锁保存关键文件哈希，全量文件摘要见 `evidence/source-file-hashes.json`。本表描述的行号对应冻结提交。[源锁](SOURCE_LOCK.json)

Google 兼容文档使用 `/v1beta/openai/chat/completions`。Alibaba 兼容文档要求 Key 与 endpoint 地域匹配，该页地域表与迁移说明中的北京 host 写法存在差异，后续应按实际账户与正式 endpoint 元数据核对。选定真实批次前继续保持 endpoint 空值。[Google 兼容说明](https://ai.google.dev/gemini-api/docs/openai) [Alibaba 兼容说明](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)
