# TUC GEO — Elmo 技术验证任务（P0）
## 可执行、可测试、可审计的 Codex 交付方案

| 文档项 | 内容 |
|---|---|
| 文档编号 | TUC-GEO-ELMO-P0-001 |
| 版本 | 1.0 |
| 编制日期 | 2026-11-17；运行记录统一保存 UTC，面向 project owner 的摘要使用北京时间 |
| 业务负责人 | project owner |
| 执行者 | Codex；必要时由获授权人员提供账号权限和复核标签 |
| 唯一公网业务域名 | `www.techunityconnect.com` |
| 首选开源项目 | `elmohq/elmo` |
| 研究基线提交 | `15c2d5f1b56682ce98e6c6ed76e254eec124e15e` |
| 当前交付状态 | 执行方案；已做指定文件的静态核查，尚未执行部署、测试或真实模型调用 |
| 执行结果初值 | 全部 `NOT_RUN`，不得预填通过 |
| 默认现金支出授权 | 新增软件、采样、模型 API、Token 和云资源支出均为 0 |

> **交付原则：先证明 Elmo 能在既定费用和安全边界内形成可复核的监测闭环，再决定是否进入产品开发。界面能打开、模型能回复、开源许可允许使用，都不等于闭环验证通过。**
>
> 本文中的 `p0ctl`、`p0-policy.yaml`、`tuc-*` 适配器和测试输出，是交付给 Codex 的待实现规格，不是 Elmo 已有功能。标为“上游命令”的内容才是已核对的现有命令。本文不包含真实密钥，不代表授权部署生产。

## 阅读与执行导航

- 负责人先读第 1、3、7、12、18、21 节。
- Codex 开工先读第 2、4、5、6、13 节及最后的启动指令。
- 测试负责人使用第 9—11、14—17 节。
- 所有外部事实引用见第 22 节；`[Sxx]` 是源代码或官方文档，设计阈值和测试要求是本项目规定，不是上游保证。

---

## 1. P0 的目标、交付边界和成功定义

### 1.1 必须回答的六个问题

1. Elmo 开源版能否在隔离环境从固定版本安装、启动、备份和恢复？
2. OpenAI、Gemini、Qwen 分别属于原生支持、间接接入、需要适配，还是暂时不可用？
3. 除回答生成外，品牌初始化、提及判读、情绪、机会报告、历史重处理等环节是否还会调用其他收费服务？
4. 在不新增现金支出的条件下，能否完成至少一个已批准 Provider 的真实 API 采样、非模拟判读、证据持久化和报告导出？
5. 能否证明没有偷偷使用另一个账号、备用 Key、付费搜索工具、采样供应商或无人知晓的重试？
6. 在不改动现有官网、不新增公网域名的前提下，Elmo 是否值得保留为内部引擎？下一阶段只需补哪些最小能力？

### 1.2 本阶段做什么

固定源码与依赖；审计外部调用；隔离部署；原版 stub 基线；接口与费用门禁；一个最小真实 API 闭环；API/MCP 能力核查；原始证据和英文报告；备份恢复；Go / No-Go 决策。

### 1.3 本阶段不做什么

不做完整 SaaS、支付、营销邮件、自动销售、客户门户、多客户商业运营、生产 DNS、生产反向代理或主站上线。不抓取登录后的 AI 消费端，不破解限制，不购买采样服务，不以“先试一次”为由触发未知费用。不为统一前端框架而重写 Elmo。

### 1.4 三层验收，不能互相替代

| 层级 | 检验对象 | 能证明什么 | 不能证明什么 |
|---|---|---|---|
| L1：原版模拟基线 | Elmo 原生 stub、固定测试输入 | 安装、页面、任务、存储、导出管道可用 | 品牌在任何真实 AI 平台出现 |
| L2：真实 Provider API | 已批准免费额度／明确零新增费用的接口 | 指定模型 API 在指定配置下的回答 | ChatGPT/Gemini 消费端实际推荐或排名 |
| L3：完整证据闭环 | L2 + 非模拟且合格的判读 + 指标 + 可复核报告 | 受控内部 API 监测试点可运行 | 已具备对外销售、生产 SLA 或多租户安全 |

L1 通过但缺少可用免费 API，不得写“完整 P0 通过”；可以交付 `CONDITIONAL_GO_OFFLINE` 和具体阻塞项。一个真实 Provider 跑通即可验证核心链路；第二、第三家未完成时必须单独标注，不得写“三家均支持”。

---

## 2. 不可变约束与权限

| ID | 约束 | 执行要求 |
|---|---|---|
| C01 | 单一公网业务域名 | 仅 `www.techunityconnect.com`；`.net` 不启用，不新增公网子域 |
| C02 | Elmo 为首选 | 优先复用，不因部分依赖受限而直接推倒重建；但不得掩盖不满足条件的事实 |
| C03 | 开源版优先 | 核验源码、许可证、依赖、模型权重许可；不购买 Cloud/白标套餐 |
| C04 | 新增费用为 0 | 有 Key 不等于有预算；付费余额也不自动等于可使用的免费额度 |
| C05 | 生产零改动 | 不修改官网仓库、生产数据、域名、证书、原表单、真实支付或发布配置 |
| C06 | 最小权限 | 测试凭据、测试数据库、测试网络；不继承生产 `.env` 或个人浏览器会话 |
| C07 | 数据真实 | 模拟、回放、本地模型、真实 API、消费端数据分别标注 |
| C08 | 缺失即阻断 | 无权限、无额度证据、无原始回答、无必要审批时标 `BLOCKED`，不伪造通过 |
| C09 | 可重现 | 固定 commit、lockfile、镜像摘要、配置哈希、问题集和判读版本 |
| C10 | 最少人工但不可越权 | 批量收集待批准事项；审批缺失时继续独立安全任务，不自动批准 |
| C11 | 凭据不外泄 | 不写入 Git、报告、截图、提示词、命令行参数和公网链接 |
| C12 | 不无限扩展范围 | 不新增付费替代品，不顺带开发销售系统，不自动开通云资源 |

**费用解释：** 可以使用已持有的账号与 API Key，前提是本批次有可核实的免费额度或其他明确的零新增费用依据。消费已购买的 API 余额仍是付费资源消耗，本阶段默认不授权。既有电脑、电力、网络和 Codex 权益的机会成本另记，不宣称整个项目“没有成本”。

**权限优先级：** 用户最新明确决策 → 当前工作区有效 `AGENTS.md` 与批准文件 → 本文执行细则 → 上游一般示例。冲突记入 `CONFLICTS.md`。本文不擅自覆盖官网的既有范围；上游要求显式授权的数据库迁移，必须取得“仅新建隔离测试库”的授权后执行。

---

## 3. 已核实的技术事实与尚未验证的事项

### 3.1 固定研究基线

本次读取的 `main` 对应提交：

```text
repository: https://github.com/elmohq/elmo
commit:     15c2d5f1b56682ce98e6c6ed76e254eec124e15e
commit UTC: 2026-11-16T17:25:25Z
```

这是研究快照，不宣称它是已通过本项目测试的稳定发行版。执行时可以检查更新和安全公告，但不得静默换成 `latest`；换版本须保留原基线、变更理由并重跑适用测试。[S01]

| 编号 | 已核实事实 | 对本项目的影响 |
|---|---|---|
| F01 | 根 `LICENSE.md` 为 MIT；版权声明需保留。[S02] | 核心源码可按许可复用；不能据此推导第三方 API、商标或数据权利免费 |
| F02 | 固定提交的 `package.json` 指定 Node `24.x`、`pnpm@12.18.0`。[S03] | 以包声明为准，不套用旧 Node 22，也不改主站全局运行环境 |
| F03 | Elmo 是 pnpm/Turborepo 单仓；产品 Web 为 TanStack Start，后台使用 pg-boss/PostgreSQL。[S04] | 不要求改成 Next.js，不额外引入 Redis/BullMQ 来替换已有队列 |
| F04 | UI 开发支持 `SCRAPE_TARGETS=stub:stub`、`ONBOARDING_LLM_TARGET=stub:stub`、`TYPESAFE_API_KEY=stub`。[S04][S06] | 原版零模型费用基线可以先测；仍要实证无意外外联 |
| F05 | 判读工厂明确把 `TYPESAFE_API_KEY=stub` 作为开发替身；有 TypeSafe Key 则优先使用，否则可选 OpenRouter；无二者会报错。[S07] | stub 判读不可宣传为真实 Jev；Key 的优先级与账户回退必须测试 |
| F06 | 品牌初始化和 Opportunities 需要直接 LLM；OpenAI 的结构化研究路径默认可开启搜索。[S05][S09] | 不能只控制采样入口，必须覆盖初始化、建议生成和搜索工具 |
| F07 | `RUNS_PER_PROMPT` 默认 5；旧任务的调度不会因只改延迟变量而自动更新。[S05] | P0 显式设为 1，关闭自动调度；不把大延迟当成关闭 |
| F08 | 修改判读版本或品牌信息可能触发历史重判。[S05] | 升级、改别名、增竞品都要纳入调用预算和阻断测试 |
| F09 | 当前 Provider registry 有 OpenAI、Anthropic、Mistral、OpenRouter、采样商及 stub；未列出独立 Gemini API 或 DashScope adapter。[S08] | 不能声称 Gemini/Qwen 原生 Key 直接填入就可用 |
| F10 | 当前 OpenAI adapter 使用 Responses 路径，不能从“兼容 OpenAI”推导其他服务完整兼容该路径。[S09] | Gemini/Qwen 的 Chat Completions 或原生协议应独立验证 |
| F11 | 官方要求 Elmo 位于其域名根路径，不支持直接用子路径部署。[S05] | P0 保持内部引擎；不把原版 UI 直接代理到官网 `/geo` |
| F12 | `DEPLOYMENT_MODE=local` 被定义为 single-org。[S05] | 不能把品牌分组当成租户隔离；本阶段只用内部测试数据 |
| F13 | 当前 TUC `AGENTS.md` 限制主站不引入数据库、CRM、认证、dashboard 或门户，生产发布需另行批准。[S10] | 本项目与主站隔离；单域名并不意味着同一仓库、进程或数据库 |
| F14 | 根目录清单未包含 `.env.example`，虽然开发文档仍给出复制示例。[S06][S19] | 不盲目执行 `cp .env.example .env`；按代码验证器生成隔离配置并记录文档差异 |

### 3.2 必须由实际测试确认

安装是否成功、Docker/主机架构兼容性、数据库初始化、原生 API/MCP 可用范围、认证与对象隔离、真实接口响应、免费额度、成本硬阻断、报告完整性、资源占用、备份恢复，均未因上述静态核查而自动通过。

---

## 4. P0 架构：不动官网，先验证内部引擎

```text
现有 www.techunityconnect.com
    └─ 本阶段保持原状；最多做获准的低频公开页面读取

Codex 隔离项目目录
    ├─ 固定提交的 Elmo 源码
    ├─ 测试控制器 p0ctl（待实现）
    ├─ 费用与出站策略（待实现）
    ├─ 固定测试数据／API 响应回放
    └─ runs/<run_id>/ 审计证据

隔离运行环境
    ├─ Elmo Web：仅本机或明确批准的私网地址
    ├─ Elmo Worker：pg-boss，默认不自动调度
    ├─ PostgreSQL：独立实例／独立数据库与账号
    ├─ 判读：原生 stub 或获准的非模拟判读器
    └─ Provider：仅精确白名单；默认没有公网 API 出站权限
```

**首选集成路径：** Elmo 保持独立内部服务，后续 TUC 的服务端适配层读取必要数据，再由主站批准的功能呈现。当前只验证接口和撰写 ADR，不实现公网集成。

不得以 iframe、全量字符串替换、把 `APP_URL` 改成 `/geo`、宽松 CORS 等方式假装已经解决原版 UI 子路径问题。若坚持完整复用原 UI，须另立路由、静态资源、认证回调、Cookie、API 和升级兼容改造项目；不属于 P0。

**推荐运行位置：** 已有、明确授权且具备资源的设备或测试主机。先记录 CPU 架构、内存、磁盘、Docker/Node/pnpm 状态；不假设已有 Mac 或云主机当前一定在线、空闲或获得授权。不安装全局服务，不修改全局 shell 或防火墙。容器端口仅绑定 loopback；数据库不公开。不能证明网络隔离时，不注入真实 Key。

---

## 5. 逐环节依赖与隐藏费用审计

Codex 必须生成 `DEPENDENCY_REGISTER.md`，每行记录：触发动作、源码路径与符号、服务域名、凭据来源、费用类型、默认是否启用、取消／重试语义、P0 处理办法、测试 ID 和证据。

| 环节 | 必查内容 | P0 默认处理 |
|---|---|---|
| 回答采样 | Provider SDK、模型、搜索工具、最大输出、隐式重试 | stub；真实调用须通过 A1 |
| 品牌初始化 | 自动网页研究、品牌摘要、竞品建议 | 人工／固定种子；自动研究关闭或回放 |
| 提及和情绪判读 | Jev 的 TypeSafe/OpenRouter 路由；原生 stub | stub 仅用于 L1；L3 必须是合格非模拟判读 |
| Opportunities／推荐内容 | 独立 LLM、隐藏联网、结构化重试 | 关闭；P0 用确定性模板生成报告 |
| 历史重判 | 改别名、加竞品、升级、开启禁用品牌 | 禁止未经批准自动执行 |
| 定时采样和补偿任务 | pg-boss cron、过期任务、catch-up | 本阶段只手动触发有限批次 |
| 来源元信息 | 引用页面抓取、标题、favicon、缩略图 | 禁止任意联网；需要时仅批准的公开站点 |
| 可观测性／遥测 | 匿名遥测、错误上报、远程日志、云计费事件 | 关闭，验证关闭效果 |
| MCP／CLI | 表面读取是否触发后台任务或重判 | 初始只读能力白名单 |
| SDK／队列内部重试 | SDK maxRetries、429、超时、递归拆分 | 真实批次初始为 0 自动重试，所有请求统一计数 |
| 凭据解析 | 环境变量与加密数据库凭据的覆盖顺序 | 清洁测试环境；禁用未知账号回退 |
| 构建／安装 | 安装脚本、镜像拉取、远程构建缓存 | 下载阶段与运行阶段分离；不启用付费构建 |

不能通过“删掉收费字段”就认定消除了收费依赖；必须在请求边界观察到阻断。仅写 `MAX_COST=0` 但无人读取该变量不构成控制措施。

---

## 6. Provider 接入验证与最小适配

### 6.1 候选接入矩阵

| 路线 | 静态状态 | 需要验证／实现 | 不允许的推断 |
|---|---|---|---|
| OpenAI 原生 API | registry 有 `openai-api` | Responses 请求、模型权限、usage、搜索开关、费用准入 | 不是 ChatGPT 消费端，ChatGPT 登录态不是 API Key |
| Gemini 原生 API | 固定 registry 未含专用实现 | 先检查是否已有可复用抽象，再做独立 adapter 的 mock 合约测试 | 不能把采样商支持 Gemini 当作支持 Google 原生 Key |
| Gemini OpenAI 兼容接口 | Google 官方提供兼容接口说明 [S13] | 明确使用的 API 协议、base URL、响应和 usage 差异 | Chat Completions 兼容不保证 Responses、搜索工具和全部参数兼容 |
| Qwen 通过 OpenRouter | 上游有 OpenRouter 路线 [S11] | 当前可用模型、gateway Key、免费资格和不回退规则 | DashScope Key 不能作为 OpenRouter Key 使用 |
| Qwen／DashScope 直连 | 固定 registry 未含专用实现 | 独立兼容接口 adapter；地域、workspace、Key 与模型一致 [S14] | 不硬编码过时的 endpoint，不把兼容接口当成即插即用 |
| 本地模型 | 不认定原版已原生支持 | 确有必要且获准时适配；核验模型许可和硬件 | 本地模型不代表 ChatGPT、Gemini 或 Qwen 消费端 |

优先顺序：**先跑通原版 stub；再选择用户确实拥有且符合零费用准入的一个真实接口；无需为了凑三家接口申请账号或充值。**

### 6.2 配置样式与命名边界

下面是上游支持的格式，`<approved-model-id>` 必须替换成已确认存在且具备权限的实际模型 ID，不可原样运行：

```text
chatgpt:openai-api:<approved-model-id>
qwen:openrouter:<approved-openrouter-model-id>
```

初始不附加 `:online`。不代表结构化研究路径也已禁止搜索，后者必须独立验证。

`gemini:tuc-gemini-api:<model>`、`qwen:tuc-dashscope-api:<model>` 仅是建议的新增适配器命名，原版不具备这些 ID。真正实现并加入解析器、密钥校验、Provider registry、usage 与测试之前，必须拒绝这些配置。

### 6.3 每个适配器的最小合约

必须支持或明确标记不支持：请求超时、取消、输出上限、模型和 endpoint 固定、无搜索模式、原始回答保存、usage 的缺失语义、Provider 请求 ID、结束原因、错误分类、数据来源类型。

同一真实调用返回的数据至少映射到：

```text
provider_id / endpoint_id / credential_ref / model_requested / model_reported
request_id / started_at / completed_at / latency_ms / finish_reason
raw_response_ref / answer_text / source_annotations / usage
observation_mode / web_search_requested / web_search_observed / status
```

不能把返回的普通 URL 自动提升为“搜索引用”；无引用功能的模型应标记 `citations_capability=unsupported`。不能为通过解析而默默丢弃拒绝、截断、工具错误或非 JSON 内容。

### 6.4 Jev 的处置决策

按以下顺序选择，不同时开发多套替代品：

1. 有可核实的免费 Jev 通道且能够阻断超额：原生 Jev，单独批准其调用额度。
2. 没有免费 Jev，但有获准的本地模型或免费模型接口：实现独立 `MentionAnalyzer` 适配器；保留独立 `judgeVersion`，通过第 10 节的人工标注集验证。
3. 只有确定性规则：仅输出规则能够证明的词面命中、域名匹配和证据片段；不输出未经验证的语义情绪、推荐意图和同名实体判断。该路线默认只形成有限能力结果。
4. 以上条件均不满足：保持原版 stub 的离线验证；真实判读标 `BLOCKED`，不谎称 L3 完成。

原版 `stubTransport` 属于测试替身，不能改个名称就充当免费生产判读器。新判读器不得伪装成 Jev，不直接改写历史判读；先保存候选结果，版本化比较后再决策。[S07]

---

## 7. 零新增费用的准入、限额与熔断

### 7.1 API Key、订阅和额度是三个不同问题

OpenAI 官方仍区分 ChatGPT 与 API 账单；当前官方也说明部分符合条件的 Pro/Business 订阅可能获得 API credits，但需要符合资格、激活并确认到账。不能因为用户有 Pro 就假定已经领取，或自动替其激活、绑定组织或充值。[S15][S16]

Gemini 必须核实实际项目的 free tier、模型与功能范围，不能只看 API Key 已生成。[S17] Qwen 官方文档说明免费额度存在地域／模型等边界，且免费额度耗尽后可能自动转按量计费；适用账号必须核实并开启 `Free Quota Only`，不得为了消除报错关闭它。[S18]

这些政策可能变化。执行前以实际账号、官方规则和当次截图／导出的元数据重新确认。本文不预设你的余额、权限或领取状态。

### 7.2 A1：真实调用批准单

只有以下字段齐全且费用路径可硬限制，才允许进入 G4：

```yaml
approval_id: null                 # 由负责人批准后填写，不能由模型自签
approved_by: null
approved_at: null
expires_at: null
provider_id: null
endpoint_id: null                 # 精确 host / path / region，不用通配符
model_id: null
credential_ref: null              # 密钥管理别名，不是密钥
usage_purpose: elmo-p0
billing_basis: null               # free_tier / granted_credits / verified_no_charge
quota_evidence_ref: null
quota_checked_at: null
quota_expires_at: null
provider_hard_stop_evidence_ref: null
paid_fallback_disabled: false
approved_cash_charge_usd: 0
max_http_requests_all_roles: 0
max_input_tokens_per_request: 0
max_output_tokens_per_request: 0
max_total_tokens: 0
allowed_roles: []                 # 如 answer / judge；初始化和研究必须另列
allowed_tools: []                 # 默认无搜索、无工具
approved: false
```

余额截图需脱敏，只证明额度信息，不复制账号隐私。额度被其他程序共享、付费回退状态不明、账单控制只是提醒而非硬阻断，均视为费用路径未证明，不做真实调用。

### 7.3 批次建议上限

负责人可批准一个有限批次：1 次连接冒烟 + 10 个固定问题各采样 1 次 + 最多 10 次独立判读，**全部角色 HTTP 请求合计不超过 24 次**。批次并发 1，自动重试 0，不启动周期任务，不追加搜索。达到上限即停止，不能为了完成数量偷偷扩大。

24 是建议的调用次数上限，不是对实际 Token 或现金费用的承诺。拆分判读、多次结构化生成、SDK 重试均消耗同一请求计数。候选判读器的标注集测试另设批次；除非使用本地推理，否则也必须另有免费额度和批准，不挤进未说明的预算。

每次请求需有可验证的输入／输出／推理 Token 上界，参数不支持或无法约束时不放行。真实返回 usage 缺失时记录 unknown 并暂停后续请求，不填 0。

### 7.4 默认策略文件（待实现，不是 Elmo 原生配置）

```yaml
schema_version: 1
project: tuc-geo-elmo-p0
mode: stub
cash_budget_usd: 0
live_requests_enabled: false
allowed_public_business_hosts:
  - www.techunityconnect.com
outbound:
  default: deny
  provider_allowlist: []
  web_fetch_allowlist: []
  follow_redirects: false
execution:
  max_concurrency: 1
  live_auto_retries: 0
  scheduled_runs_enabled: false
  historical_rejudge_enabled: false
  onboarding_research_enabled: false
  opportunities_enabled: false
  search_tools_enabled: false
  real_batch_request_cap: 0
  kill_switch_default: true
credentials:
  inherit_shell_credentials: false
  production_credentials_allowed: false
  unknown_fallback_allowed: false
approval:
  live_approval_required: true
  sandbox_migration_approval_required: true
  production_deploy_allowed: false
```

### 7.5 控制必须形成两层防线

**业务层：** 每个请求先检查 mode、角色、endpoint、模型、凭据别名、审批有效期和剩余额度，再原子预留额度。请求成功后结算；超时／取消但可能已到达服务商时记 `UNKNOWN_CHARGE`，不得简单释放额度或自动重试。

**网络层：** stub／回放阶段拒绝公网 API 出站；真实阶段只开放批准路由，禁止绕过控制器的 SDK 直连、其他域名和重定向外传。仅设置 `HTTP_PROXY` 不算完成，必须实测 SDK 是否会绕行。无法验证网络约束时，真实调用保持关闭。

费用凭证、额度、请求计数、供应商 usage 不一致时停止。只有供应商自身也能阻止转付费，才能据此接受“零新增费用”试验；本地估算和告警不能提供绝对账单保证。

---
## 8. 环境、目录、版本和配置管理

### 8.1 建议目录

所有内容在新的隔离目录，**不得建在现有官网的工作树中**。以下目录由 Codex 在获准后创建：

```text
tuc-geo-elmo-p0/
├── PLAN.md                         # 本文的固定副本
├── upstream/elmo/                  # 上游固定提交；改动单独留 patch
├── harness/                        # 测试控制器、合约、策略和安全检查
├── fixtures/                       # 明确标记的人工测试数据
├── config/
│   ├── policy.stub.yaml
│   ├── policy.live.example.yaml    # 不含真实凭据，不默认启用
│   └── dependency-lock.json
├── secrets/                        # 本地权限 0700；不进 Git / 普通证据包
├── approvals/                      # 仅保存授权元数据，执行账号无权伪造批准
├── runs/<run_id>/                   # 每次执行独立、不可覆盖
├── reports/                        # 脱敏审计、决策与报告
├── patches/                        # 最小改造与对应测试
└── p0ctl                           # 需 Codex 实现的唯一测试入口
```

`upstream/elmo` 保留上游 Git 历史。不要向原作者仓库提交 TUC 私有域名、经营数据或凭据；不创建远程仓库／PR，除非用户另有授权。外层文档目录避免被误提交到公开 upstream。

### 8.2 环境清单

记录 OS、CPU 架构、可用内存／磁盘、Node、pnpm、容器引擎、数据库、浏览器和证书信任情况。Node 与 pnpm 按固定提交要求在项目隔离环境准备，不改变主站运行版本。Docker Desktop、云 VM 等授权或费用资格需检查，不把所有运行环境都默认当成免费软件。

如果某环境缺 Docker、无法联网下载依赖、不能绑定端口或没有足够资源，记录具体 blocker，继续完成源码与策略审计。不得编造启动成功。本文编制时也未完成容器部署或运行性能测试。

### 8.3 原生 stub 配置

下面仅列出已核对的关键上游变量，**不是可直接完整启动的 `.env`**；Codex 必须按当前 env validator 补齐必要字段，并将秘密写入安全位置：

```dotenv
DEPLOYMENT_MODE=local
DISABLE_TELEMETRY=1
SCRAPE_TARGETS=stub:stub
ONBOARDING_LLM_TARGET=stub:stub
TYPESAFE_API_KEY=stub
RUNS_PER_PROMPT=1
APP_URL=http://127.0.0.1:3000
VITE_APP_URL=http://127.0.0.1:3000
```

这里的 `stub` 是上游明示的开发值，不是真实 Key。`DATABASE_URL`、`BETTER_AUTH_SECRET`、`ELMO_ENCRYPTION_KEY` 另行生成；只允许隔离数据库。若选定启动方式读取根目录及 `apps/web/.env`，两处配置需一致且权限受限。[S04]

默认不把 shell 已有的任何真实 Provider Key 传给进程；不把原有全局 `~/.elmo` 配置带入。数据库也必须全新，避免已有加密 Key 覆盖测试配置。启动前只报告“某凭据已设置／未设置”，不要输出原值。

**设置 `RUNS_PER_PROMPT=1` 不等于关闭调度。** 需要核对并禁止新建周期计划、现有计划、重试队列和历史重判。不能用 `DEFAULT_DELAY_HOURS=0` 或不合法值尝试关闭，必须通过实际代码和测试明确开关行为。

### 8.4 版本冻结

必须保存上游 commit、lockfile 的 SHA-256、`AGENTS.md` 哈希、镜像 tag 与 digest、应用构建哈希、PostgreSQL 大版本、迁移版本和测试补丁哈希。拉取依赖只在准备阶段开放批准的源；运行阶段关闭下载。

遵守上游 pnpm 的供应链设置，不使用 npm/yarn/npx 绕过，不移除安全 overrides，不为安装成功而放松 `allowBuilds` 等控制。[S04] 安装失败可报告原始原因，不得把依赖安全检查关掉。

---

## 9. 统一数据合约与可审计证据

### 9.1 数据必须标明来源

使用以下互斥的 `observation_mode`：

```text
UPSTREAM_STUB       上游占位数据
FIXTURE_REPLAY      人工固定输入或已脱敏录制响应的离线回放
DIRECT_MODEL_API    本次真实调用供应商模型 API
LOCAL_MODEL         本地推理；不代表任何消费端
CONSUMER_UI         获得合法来源的消费端观察；本 P0 默认不启用
```

`judge_mode` 单独保存，如 `UPSTREAM_STUB`、`JEV_TYPESAFE`、`JEV_OPENROUTER`、`LOCAL_VALIDATED`、`API_VALIDATED`、`RULES_LIMITED`。真实采样 + stub 判读是混合状态，不能贴成完整实测。页面、导出文件和报告抬头都必须显示这两个标签。

### 9.2 建议的观测记录

以下是 TUC 导出合约，不要求逐字改造上游数据表。优先从既有 schema 映射，不够的字段放在证据侧车文件中：

```typescript
type ObservationMode =
  | "UPSTREAM_STUB" | "FIXTURE_REPLAY" | "DIRECT_MODEL_API"
  | "LOCAL_MODEL" | "CONSUMER_UI";

type ObservationStatus =
  | "SUCCEEDED" | "FAILED" | "BLOCKED" | "CANCELLED" | "TRUNCATED";

interface AuditObservation {
  schemaVersion: "1.0";
  runId: string;
  observationId: string;
  brandId: string;
  promptId: string;
  promptSetVersion: string;
  promptGroup: "non_brand" | "brand_control";
  promptTextSha256: string;
  observationMode: ObservationMode;
  providerId: string;
  endpointId: string;
  credentialRef: string; // 仅安全别名；不得放 Key
  modelRequested: string;
  modelReported: string | null;
  collectionRegion: string | null; // 未控制则 null，不能假称“美国用户实测”
  language: string;
  searchRequested: boolean;
  searchObserved: boolean | null;
  startedAt: string;
  completedAt: string | null;
  providerRequestId: string | null;
  status: ObservationStatus;
  errorCode: string | null;
  rawResponseRef: string | null;
  rawResponseSha256: string | null;
  answerTextRef: string | null;
  finishReason: string | null;
  citationCapability: "supported" | "unsupported" | "unknown";
  citations: Array<{
    url: string;
    sourceKind: "provider_annotation" | "answer_link";
    title: string | null;
    evidenceRef: string;
  }>;
  judgeMode: string;
  judgeVersion: string | null;
  judgeStatus: "SUCCEEDED" | "BLOCKED" | "FAILED" | "NOT_RUN";
  judgeInputSha256: string | null;
  mentions: Array<{
    entityId: string;
    mentioned: boolean | null;
    recommended: boolean | null;
    sentiment: "positive" | "neutral" | "negative" | "mixed" | "unknown";
    evidenceQuote: string | null;
    evidenceStart: number | null;
    evidenceEnd: number | null;
    offsetEncoding: "utf16" | "unicode_codepoint" | null;
  }>;
  usage: {
    inputTokens: number | null;
    outputTokens: number | null;
    reasoningTokens: number | null;
    toolCalls: number | null;
  };
  costStatus: "NOT_APPLICABLE" | "VERIFIED_ZERO_CASH" | "UNKNOWN";
  approvalId: string | null;
  upstreamCommit: string;
  implementationSha256: string;
}
```

实际 schema 必须校验跨字段条件：`DIRECT_MODEL_API` 要有批准及原始响应；失败不允许冒充成功；判读成功需要版本和原文证据；mock 不允许 `VERIFIED_ZERO_CASH` 表述为真实账号账单核验。未判读使用 null，不偷填 false。

### 9.3 原始数据与不可变性

原始响应保存在访问受控的证据目录，先剔除认证头、Set-Cookie、URL 中的 secret 等不应保存的传输秘密。保留回答正文与必要响应字段；对安全清理后的原始证据计算哈希，记录清理规则。

分析结果与原始响应分开；重跑判读产生新版本，不覆盖旧结果。报告里的每个事实结论均指向 observation ID 和可定位片段。证据哈希只能证明与既定基线一致，不能独自证明作者没有同时改写文件和清单；交付时将清单哈希另存给负责人或批准的只读位置。

---

## 10. 测试数据、人工金标准与英文问题集

### 10.1 固定数据集

建立 48 条人工构造或合法脱敏的回答样本，明确 `FIXTURE_REPLAY`，绝不称为市场实测。六组各 8 条：

| 组 | 覆盖内容 |
|---|---|
| A | 明确品牌提及、正面推荐、仅事实说明 |
| B | 全称／空格／大小写／合法别名／官方域名 |
| C | 同名企业、普通词义、缩写歧义、品牌名子串误匹配 |
| D | 不推荐、批评、混合评价、“没有足够信息”、无品牌 |
| E | 正确引用、回答普通链接、重复 URL、伪装官网、无引用能力 |
| F | 长文本截断、中文和 emoji 偏移、提示注入、空／格式错误 |

每条保存人工标签、理由、原文证据和审核人。24 条用于开发，24 条冻结为 holdout；开发完成后才能运行 holdout。holdout 至少包含 10 个应提及、10 个不应提及的判定；情绪子集应有多个类别。

不能让同一个模型生成答案、标签，再自己宣布标签全对。负责人或获授权 QA 需一次性核对人工标签。无人核对时标 `LABEL_REVIEW_PENDING`，不报告判读准确率已通过。

### 10.2 判读质量门槛

以下是本项目的小样本验收阈值，不是统计意义上的生产准确率承诺：

- holdout 品牌提及准确率及 precision 均至少 95%，同时公开分子、分母与混淆矩阵；零预测正例时 precision 未定义，不能填 100%。
- 声称支持情绪时，计算 macro-F1，目标至少 0.80，并公开各类样本数；样本不足或不支持时不作此声明。
- 每一条被引用的证据必须确实存在于对应原文；证据一致性为 100%。
- 所有同名实体／伪域名／注入等关键安全反例必须通过，不能被平均分掩盖。
- 原生 stub 仅检验流程，不纳入候选真实判读器质量验收。

“提及”和“推荐”分开。`We do not recommend Example Alpha` 是提及，但不是推荐。上游对 `no_info` 的处理可能与普通词面命中定义不同，必须在 `METRIC_MAPPING.md` 中解释，不悄悄改结果迎合预期。[S07]

### 10.3 真实采样的品牌配置

内部品牌：`TechUnity Connect`。主域：`techunityconnect.com`，允许的官网 host 明确列出 `www.techunityconnect.com` 和已核实必要 host。`TUC` 单独出现存在歧义，不默认视为确定提及；需上下文或域名佐证。

最多 2 个竞品，仅使用公开且核实的名称／官网；没有核实就不填。不能捏造 TUC 的客户、认证、案例、收入或业务能力。

### 10.4 10 个英文种子问题

这是一组待冻结的接口试验问题，不是用户搜索量研究。真实运行前只允许一次相关性审核，然后保存版本和哈希；不能为了让 TUC 出现反复挑选问题。

| ID | 分组 | 问题 |
|---|---|---|
| Q01 | non_brand | Which providers help B2B software companies integrate AI into existing production workflows? |
| Q02 | non_brand | How should a small enterprise evaluate an external AI integration partner? |
| Q03 | non_brand | Which engineering partners can help a company move an AI proof of concept into production? |
| Q04 | non_brand | What should a company look for when choosing an AI integration consultancy for a security-sensitive workflow? |
| Q05 | non_brand | Which service providers offer forward-deployed engineering support for enterprise AI projects? |
| Q06 | non_brand | How can a B2B company compare vendors for AI workflow integration and ongoing reliability? |
| Q07 | non_brand | What evidence should a buyer request from a provider that builds enterprise AI applications? |
| Q08 | non_brand | Which providers can support API integration, evaluation and observability for enterprise AI workflows? |
| Q09 | brand_control | What can you verify about TechUnity Connect and the services described on its official website? |
| Q10 | brand_control | What information is available about TechUnity Connect, and what remains uncertain? |

Q09 的官网读取若需要付费搜索则不得自动开启。无搜索情况下模型答“不知道”也是合格观察。真实数据不要求 TUC 被提及；系统正确呈现零提及才是验收目标。

---

## 11. 指标定义与报告口径

所有指标按 `observation_mode + provider + endpoint/model + search配置 + promptSetVersion + judgeVersion` 分组。不能把 stub、API、本地模型和消费端结果混算；品牌组与非品牌组分开。

设计划观测数为 N，成功取得有效回答数为 S，完成合格判读数为 J：

```text
采样完成率 = S / N                         N=0 时 N/A
判读完成率 = J / S                         S=0 时 N/A
非品牌提及率 = 非品牌组的确认提及数 / 非品牌组已完成合格判读数
明确推荐率 = 非品牌组的确认推荐数 / 非品牌组已完成合格推荐判读数
官方来源引用率 = 具有官方来源 annotation 的观测数 / 具备该引用能力的有效观测数
```

必须显示每项分母及被排除原因。超时、429、空响应、被阻断不能算“没有提及”；没有引用能力不是引用率为 0，而是 N/A。普通回答中的超链接与 Provider 返回的引用 annotation 分开统计。

同一个逻辑观测的重试只算一次，但请求次数／成本按每次实际请求累计。不得将 10 个问题的结果称为 AI 全市场份额。问题内首次出现位置只称为“该回答中的首次提及位置”，不是搜索引擎排名。

P0 小样本报告不做显著性改善、增长归因、收入归因或胜过竞品的结论。零提及不是技术失败；假证据、错分母和混入 mock 才是失败。

---

## 12. 执行阶段、门禁与人工批准

### 12.1 阶段总表

| 阶段 | 工作 | 交付 | 退出条件 |
|---|---|---|---|
| G0：只读核查 | 工作区、AGENTS、源码快照、许可、外部依赖、环境 | `M0_READINESS.md`、依赖表、冲突表、测试计划 | 范围和阻塞明确；尚未调用真实 Provider |
| G1：隔离基线 | 依赖安装、测试库、迁移、stub Web/Worker | 版本清单、启动与上游测试结果、出站记录 | 原版 stub 闭环、无付费外联 |
| G2：费用与安全门禁 | 请求守卫、额度预留、凭据边界、异常注入 | 费用与权限测试、断路器证据 | 关键阻断用例通过 |
| G3：最小适配与离线验证 | 必要 Provider adapter、判读合约、回放、报告 | 适配状态矩阵、补丁、金标准结果 | 候选真实路线明确且 mock 合约可复现 |
| G4：受控真实批次 | 仅已批准 Provider／judge，有限手动调用 | 原始响应、usage、额度核验、英文样例 | 至少一个候选真实链路验证；否则 BLOCKED |
| G5：恢复和决策 | 备份还原、接口读取、复算、证据校验 | 完整审计包、ADR、Go/No-Go | 结论逐项关联证据，无未披露失败 |

### 12.2 最小人工批准点

**A0：隔离执行授权。** 确认新目录、测试机器、仅新建测试库迁移、容器资源范围。第 21 节给出可一次批准的文字。未批准时只做 G0，不启动服务或迁移。

**A1：真实调用授权。** 一次批准一个明确的 Provider／judge 组合与批次。Key 通过安全渠道注入，不在聊天粘贴。审批是“使用已有零新增费用额度”，不是“允许付费”。缺少条件时继续完成 G1—G3、可离线执行的 G5，不循环催问。

**A2：采纳决策。** 查看证据摘要后决定是否进入下一阶段。A2 不包含公网发布、生产数据库、支付或对外客户开通。

Codex 不能自行生成签名伪装为负责人授权。若使用审批文件，执行进程不能写批准字段；若使用聊天批准，保存消息引用、范围和确认时间，由负责人核对。

### 12.3 立即停止真实调用的情况

发现未知费用／账户回退、越出白名单、密钥泄露、证据被覆盖、重复无限请求、生产资源被连接、用户撤回授权，或无法确认取消后的计费状态。停止网络出口和任务领取，保存证据、隔离凭据，继续做不需要真实调用的分析。

---

## 13. 命令、执行器与重放规范

### 13.1 固定源码示例：只下载和读取，不运行服务

以下 Bash 示例假设 `P0_HOME` 已被设为**官网目录之外的全新绝对路径**。不得在已存在目录中执行删除或覆盖来“重试”：

```bash
set -euo pipefail
: "${P0_HOME:?Set an approved, new absolute sandbox path outside the website repository}"
case "$P0_HOME" in /*) ;; *) printf '%s\n' 'P0_HOME must be absolute' >&2; exit 2;; esac
[ ! -e "$P0_HOME" ] || { printf '%s\n' 'Path exists; review instead of overwriting' >&2; exit 2; }
umask 077
mkdir -p "$P0_HOME/upstream" "$P0_HOME/reports"
git clone --no-checkout https://github.com/elmohq/elmo.git "$P0_HOME/upstream/elmo"
git -C "$P0_HOME/upstream/elmo" checkout --detach 15c2d5f1b56682ce98e6c6ed76e254eec124e15e
git -C "$P0_HOME/upstream/elmo" rev-parse HEAD
# Read AGENTS.md and the policy before installation or any runtime command.
```

下载失败就记录错误，不改用未核实镜像，不宣称已经拉取。若改为本地已有副本，仍验证 remote、commit、工作树差异及来源。

### 13.2 已核实存在的上游命令

必须先审查命令实际脚本、网络行为与数据库目标。下表不是“一次全部运行”的脚本。[S03][S06]

| 命令 | 作用／前提 |
|---|---|
| `pnpm install --frozen-lockfile` | 用锁定 pnpm；遵守供应链限制；下载阶段才能运行 |
| `pnpm lint` | Biome 检查；记录退出码 |
| `pnpm test` | 上游单测；先检查测试是否可能外联 |
| `pnpm build` | 构建；准备好所需 stub 配置，禁止云凭据 |
| `pnpm test:scripts` | 脚本测试 |
| `pnpm license-check` | 上游许可检查；仍需保存依赖许可清单 |
| `pnpm test:e2e` | 浏览器已准备、隔离应用已启动后执行 |
| `pnpm test:api` | 按该版本测试配置启动，禁止指向生产 |
| `pnpm validate:spec` | 核查 API spec；按实际前置条件执行 |
| `pnpm --filter @workspace/web dev` | 只启动 Web；不要误用全栈 dev 启动未受控 Worker |
| `pnpm --filter @workspace/lib exec drizzle-kit migrate` | 仅 A0 明确批准的新建测试库；上游禁止未经授权迁移 |

根脚本未声明通用 `pnpm typecheck`，不要编造。Codex 应检查各 package 的类型检查命令与 tsconfig，生成准确的 `QUALITY_COMMANDS.md`；必须覆盖发生改动的包。也不要直接运行未经审查的 `test:e2e-local`，因为自动环境脚本可能包含迁移、启动或清理动作。

### 13.3 待实现的统一执行器 `p0ctl`

可使用项目已具备的 Node/TypeScript 和 pnpm，不为控制器再引入一套 SaaS。建议的命令契约：

```text
./p0ctl inspect                 只读环境与源码审计
./p0ctl bootstrap --approval A0 准备隔离运行环境与测试库
./p0ctl test --suite offline    跑 stub/回放及费用安全负例
./p0ctl test --case COST-03     单例复现
./p0ctl live --approval A1      只跑获准的固定批次
./p0ctl report --run <run_id>   只从已有证据生成报告，不隐式联网
./p0ctl verify --run <run_id>   哈希、分母、模式标签与证据关系核验
./p0ctl stop --run <run_id>     停止本次任务；不删除证据或卷
```

这些命令必须先由 Codex 实现并测试，不能在不存在时假报执行结果。每条命令应校验政策、支持明确错误和幂等执行；`--dry-run` 可展示操作但不能算测试通过。

**退出码：** 0=该命令要求的测试已通过；1=断言失败；2=前置条件／审批阻塞；3=配置或证据完整性错误。`NOT_APPLICABLE` 是用例状态，不能作为掩盖失败的总退出成功。

**审计日志：** 保存命令的脱敏表示、cwd、源码版本、配置哈希、起止时间、退出码、stdout/stderr 文件引用。通过 `tee` 保存日志时必须保留原命令退出码；不使用 `|| true` 掩盖失败。不要把完整环境变量、数据库 DSN、Provider Key 或带签名 URL 写进日志。

### 13.4 CI 原则

先本地跑；不得默认消耗 GitHub Actions 的付费额度或连接生产 secrets。获得许可后，CI 只运行 stub／回放、schema、静态检查和安全负例。真实模型测试不放到每次 push、PR、定时构建里。基线和补丁必须分别测试，结果分开保存。

---
## 14. 测试矩阵：64 项可复核用例

所有用例默认 `NOT_RUN`。以下是**测试规格，不是测试结果**。每项由 Codex 落实为可执行测试或明确的人工审计步骤，保存实际输出。

适用性：`BASE` 为内部基线必测；`LIVE` 是取得 A1 后才执行的真实闭环门槛；`COND` 是声称具备相应非模拟判读能力时必测；`OPT` 为未选中的额外路线可暂缓，但如选作主路线即升级为必测。没有 Key 的 LIVE 项记 BLOCKED，不能记 PASS 或偷偷改成不适用。

每项结果保存 `test_id / requirement_ids / suite / applicability / status / expected / actual / evidence_refs / started_at / ended_at / exit_code / reviewer`。同一用例复跑追加记录，不抹去失败历史。

### 14.1 源码与供应链（G0 / G1）

| ID | 适用性 | 测试及操作 | 预期结果 | 最低证据 |
|---|---|---|---|---|
| SRC-01 | BASE | **固定版本**：核对 remote、HEAD、lockfile 与工作树；记录镜像 digest。 | 与批准基线一致；任何差异均列入补丁清单。 | source-lock.json；git diff |
| SRC-02 | BASE | **许可范围**：读取 LICENSE.md；列依赖、模型、服务许可；运行可用许可检查。 | 保留 MIT 声明；未核实依赖标出，不把 API 服务说成免费。 | license-inventory.json；检查日志 |
| SRC-03 | BASE | **工具链**：在隔离环境核对 Node、pnpm 与 packageManager；检查未修改主站配置。 | 满足固定提交要求；不全局替换用户工具链。 | environment.json；官网前后摘要 |
| SRC-04 | BASE | **仓库指令**：读取有效 AGENTS 与批准文件，比较本文权限和数据库迁移要求。 | 冲突有明确处理；没有生产修改或越权迁移。 | CONFLICTS.md；审批引用 |
| SRC-05 | BASE | **供应链门禁**：安装使用冻结 lockfile；检查安全配置和 install scripts；运行可用漏洞检查。 | 未绕过控制；高风险可达问题单列，未解决不放行真实密钥。 | 安装日志；SBOM；风险表 |

### 14.2 环境与原版基线（G1）

| ID | 适用性 | 测试及操作 | 预期结果 | 最低证据 |
|---|---|---|---|---|
| ENV-01 | BASE | **环境隔离**：以凭据白名单启动；检查挂载、监听、DB 标识、HOME 与现有环境差异。 | 不继承真实 Key；不连生产库；无公网端口。 | 脱敏配置；进程/端口/挂载清单 |
| ENV-02 | BASE | **原版 stub 闭环**：用 upstream stub 新建测试品牌、问题，手动跑任务并刷新页面。 | Web、Worker、持久化可用；页面和导出标明模拟。 | 日志；截图；观测 JSON |
| ENV-03 | BASE | **迁移限定**：无 A0 时尝试迁移；有 A0 后只迁移新测试库，并复跑。 | 无批准拒绝；已批准的测试迁移可重现，无生产目标。 | 审批引用；迁移版本；目标指纹 |
| ENV-04 | BASE | **上游质量基线**：按已核实命令跑 lint、unit、build、相关类型检查和适用 E2E/API。 | 保存每项实际结果；上游既有失败与补丁新增失败分开。 | 原始测试结果；退出码 |
| ENV-05 | BASE | **调度不会偷跑**：禁用周期触发；检查新旧任务、重启后计划与补偿任务。 | 除显式批次外无新模型任务；不能只靠大间隔。 | 队列表；计时／假时钟测试 |
| ENV-06 | BASE | **遥测与外联**：关闭 telemetry；浏览器和 Worker 完成 stub 流程并采集出站日志。 | 无公网模型、遥测或其他未批准请求；字体/图片外联也列出。 | egress.jsonl；浏览器请求日志 |

### 14.3 费用保护与异常回退（G2 / G4）

| ID | 适用性 | 测试及操作 | 预期结果 | 最低证据 |
|---|---|---|---|---|
| COST-01 | BASE | **未授权真调用**：注入合成凭据，未设置 A1，请求真实目标。 | 在 HTTP 发出前阻断；外部请求数为 0。 | 拒绝事件；传输层 spy |
| COST-02 | BASE | **过期或未知额度**：构造过期审批、过期额度、缺余额证据、共享余额无法确认。 | 全部拒绝；不能以 Key 可用为理由放行。 | 准入断言 JSON |
| COST-03 | BASE | **并发原子限额**：用本地假服务模拟 20 个并发请求争夺剩余 1 次额度。 | 最多 1 次到达假服务，其余在发送前被阻断。 | 事务日志；假服务计数 |
| COST-04 | BASE | **Token 与工具边界**：提交过长输入、超输出配置、无限思考参数及带搜索工具请求。 | 不支持约束即阻断；不会仅靠事后估算。 | 参数校验；请求截获 |
| COST-05 | BASE | **重试与未知计费**：假服务返回 429、5xx、超时和断连；开启 SDK 默认重试做反例。 | 控制器识别每次尝试；真实配置无自动重试；未知计费不释放为可用。 | 请求序列；额度账本 |
| COST-06 | BASE | **旁路生成任务**：触发 onboarding、Opportunities、CLI 研究与结构化格式重试。 | 未单独批准时不外联；报告生成保持离线。 | 调用图；egress；拒绝原因 |
| COST-07 | BASE | **历史重判**：修改测试别名、竞品、judgeVersion 并重启或重新启用品牌。 | 历史任务不绕过策略；需要批准而非自动追赶。 | 队列变化；出站计数 |
| COST-08 | BASE | **Key/账户回退**：使用两个合成账号，模拟 DB Key 解密失败、主 Key 401、缺 Key。 | 不转用另一环境 Key 或 Provider；明确报错。 | credential_ref 流转；mock transport |
| COST-09 | BASE | **急停和审批撤回**：运行假慢请求时撤回批准／触发 kill switch，再入队。 | 立即拒绝后续请求；在途请求尝试取消并标记是否未知计费。 | 停止时间线；请求日志 |
| COST-10 | LIVE | **真实额度核验**：比对真实批次前后的免费额度／usage、所有角色请求和本地账本。 | 无新增现金费用的证据完整；滞后或不明标 BLOCKED，不填写 0。 | 脱敏服务商记录；对账表 |

### 14.4 Provider 合约与实测（G3 / G4）

| ID | 适用性 | 测试及操作 | 预期结果 | 最低证据 |
|---|---|---|---|---|
| PRV-01 | BASE | **目标解析**：测试合法 ID、未知 provider、未知 model、错误配置及空配置。 | 未知目标拒绝；不会静默选默认收费模型。 | parser 测试；配置摘要 |
| PRV-02 | BASE | **OpenAI adapter 合约**：以记录格式的合成 Responses 数据测试文本、usage、注解、拒绝和截断。 | 映射正确；不将其等同 ChatGPT UI；没有假成功。 | adapter 测试；映射快照 |
| PRV-03 | OPT | **Gemini adapter**：实现需要的协议适配，先用 mock 测 endpoint、请求字段和响应。 | 直连支持与 gateway 支持分别说明；未实现不填支持。 | GEMINI_STATUS.md；合约测试 |
| PRV-04 | OPT | **Qwen adapter**：分开测试 OpenRouter 与 DashScope；确认模型和请求协议。 | 不会混用 Key；直连与转接各有清晰状态。 | QWEN_STATUS.md；合约测试 |
| PRV-05 | BASE | **Key 地域/目标错配**：在本地 transport 模拟不同 endpoint、region、workspace 和凭据错误。 | 401/403 明确；不换账号、不自行申请新 Key。 | 错误分类测试 |
| PRV-06 | BASE | **搜索默认关闭**：检查采样与研究请求、API tools、providerOptions 及真实返回工具记录。 | 未批准搜索不发送；上游默认值无法覆盖策略。 | 请求快照；搜索能力表 |
| PRV-07 | BASE | **异常响应**：测试空文本、缺 usage、非 JSON、未知模型、超大响应和 finish_reason。 | 返回 FAILED/TRUNCATED/unknown 等准确状态；不捏造引用或零成本。 | 异常 fixtures；解析结果 |
| PRV-08 | BASE | **额度耗尽**：用假服务模拟免费额度不足、限流、账单限制等错误。 | 停止该批次；无付费降级、换模型或账号轮询。 | 拒绝记录；调用次数 |
| PRV-09 | LIVE | **真实主路线**：A1 通过后运行一次连接试验和固定问题批次；请求总数含判读。 | 至少一个真实 API 路线有完整证据；未调用的其他路线如实列出。 | raw；observations；usage；批准单 |

### 14.5 判读质量与可解释性（G3 / G4）

| ID | 适用性 | 测试及操作 | 预期结果 | 最低证据 |
|---|---|---|---|---|
| JUD-01 | BASE | **stub 标记**：运行 TYPESAFE_API_KEY=stub，并导出页面、API 和报告。 | 每个出口保持 stub 标签；不被归入真实质量结果。 | UI 截图；导出模式标签 |
| JUD-02 | BASE | **无 judge 拒绝**：移除判读凭据且不选本地有效 adapter，触发判读。 | 明确 BLOCKED/FAILED；不把未判读设为未提及。 | 错误事件；观测状态 |
| JUD-03 | COND | **人工金标准**：对候选非模拟判读器运行冻结 holdout，不修改答案或标签。 | 满足第 10 节阈值；公开分母、混淆矩阵和人工标签来源。 | golden-manifest；scores.json |
| JUD-04 | BASE | **词义与否定**：测试相同名字、TUC 缩写、子串、负面推荐及 no_info。 | 词面命中/语义提及/推荐分开；差异有方法说明。 | 案例结果；METRIC_MAPPING.md |
| JUD-05 | BASE | **原文片段**：对中英混合、emoji、HTML 清理、换行与截断计算证据偏移。 | 引用片段可回定位；偏移编码明确；无编造引文。 | span assertions；原文哈希 |
| JUD-06 | BASE | **判读版本**：以两个 judgeVersion 分析同一 raw，并重跑相同版本。 | 结果版本隔离，旧证据不覆盖；缓存键含输入与版本。 | 两版分析导出；缓存测试 |
| JUD-07 | LIVE | **真实非模拟判读**：对真实回答用已批准且质量合格的 judge；检查其请求和原文引用。 | L3 不含占位情绪；无私自 Jev/OpenRouter 路由切换。 | judge 证据；调用账本 |

### 14.6 数据、指标与报告（G3 / G5）

| ID | 适用性 | 测试及操作 | 预期结果 | 最低证据 |
|---|---|---|---|---|
| DATA-01 | BASE | **原始证据**：保存经过秘密字段清理的原始响应、问题、时间、模型和请求 ID。 | 响应与分析分开；每条成功结果能追溯证据。 | observations.jsonl；原始文件哈希 |
| DATA-02 | BASE | **来源隔离**：向同一测试品牌导入 stub、回放、API 标签和不同 judgeVersion。 | 界面、查询、导出不混算；筛选条件保留。 | 聚合测试；导出快照 |
| DATA-03 | BASE | **分母复算**：用含成功、失败、未判读、品牌问题、重试的 fixtures 独立复算。 | 与第 11 节一致；分母 0 为 N/A；失败不当作零提及。 | metrics-recompute.json |
| DATA-04 | BASE | **域名和引用**：测试官网、官网后缀伪装、userinfo、重复 URL、普通文本链接。 | 正确按 host 校验；annotation 与 answer_link 分开；无能力为 N/A。 | URL fixtures；归一化结果 |
| DATA-05 | BASE | **拒绝和截断**：导入安全拒绝、输出被截断、空内容和错误页。 | 单独标注，不隐去失败、捏造补全或充当正常答案。 | 状态断言 |
| DATA-06 | BASE | **重复与重放**：重复投递相同 job/observation，制造并发入库，再离线回放。 | 逻辑观测不重复；每次真实请求仍保留独立账本。 | 去重约束；计数对比 |
| DATA-07 | BASE | **API 可读性**：从当前 OpenAPI/schema 发现真实读取路径；授权读取样本及分页。 | 导出字段可用或缺口被披露；不猜接口不存在却报成功。 | API_COVERAGE.md；响应证据 |
| DATA-08 | BASE | **离线报告复现**：断开公网，用同一证据和模板生成英文 Markdown/HTML 两次。 | 去除生成时间等明确可变字段后内容一致；每结论有证据 ID。 | 报告；规范化 diff；离线日志 |

### 14.7 安全与权限（G2 / G5）

| ID | 适用性 | 测试及操作 | 预期结果 | 最低证据 |
|---|---|---|---|---|
| SEC-01 | BASE | **密钥泄露**：用可识别合成 canary 检查日志、Git、HTML、错误堆栈、提示词和打包内容。 | 除授权 secret 存储外均不可见；不得用真实 Key 做泄露试验。 | secret-scan.json；敏感文件排除清单 |
| SEC-02 | BASE | **认证边界**：未登录、过期 session、无效 token 请求私有 API 与报告。 | 拒绝访问；后台地址不能替代鉴权。 | 认证用例；HTTP 结果 |
| SEC-03 | BASE | **单组织限制**：检查 local 模式权限，测试低权限账号与对象 ID；记录是否支持独立组织。 | 不能证明多租户即标 SINGLE_ORG_ONLY，不允许多客户共享开放。 | ACCESS_BOUNDARY.md；对象访问测试 |
| SEC-04 | BASE | **MCP 权限**：发现实际 tools，白名单只读；请求创建/删除/执行采样类操作做负例。 | 未批准变更不可执行；缺只读粒度则不向 Codex 开放宽权限 MCP。 | MCP 能力清单；拒绝日志 |
| SEC-05 | BASE | **提示注入与 XSS**：在回答/网页放要求泄露 Key、执行命令、改评分及脚本 HTML 的 fixture。 | 仅当数据解析；无额外工具操作；HTML 安全渲染。 | sandbox 日志；浏览器断言 |
| SEC-06 | BASE | **SSRF**：在本地模拟私网、metadata、loopback、IPv6、重定向和 DNS 重绑定目标。 | 拒绝非批准获取目标；不访问真实内网敏感端点。 | 本地恶意服务计数；拒绝原因 |
| SEC-07 | BASE | **凭据加密恢复**：使用合成 Provider Key 测保存、正确密钥解密、错误密钥和恢复。 | 存储不明文；错误密钥不得降级使用未知环境账号。 | 加密检查；恢复测试 |
| SEC-08 | BASE | **出站绕过**：测试 SDK 直连、不同 host、IPv6、代理 bypass、跨域重定向。 | 网络层拒绝未批准路由；仅有 HTTP_PROXY 不算通过。 | 网络策略；egress 负例 |
| SEC-09 | BASE | **发布前安全评估**：汇总可达漏洞、依赖许可、默认账户、公开端口与敏感挂载。 | 无未处理的关键风险带入真实 Key；生产风险不隐藏。 | SECURITY_REVIEW.md |

### 14.8 任务可靠性与恢复（G5）

| ID | 适用性 | 测试及操作 | 预期结果 | 最低证据 |
|---|---|---|---|---|
| OPS-01 | BASE | **Worker 重启**：在本地假任务处理中停止并重启 Worker。 | 任务状态可解释；不重复计算，不丢失原始证据。 | 重启时间线；任务状态 |
| OPS-02 | BASE | **DB/依赖不可用**：用隔离环境中断数据库或假 Provider。 | 失败受控；无忙循环或无限请求；错误可诊断。 | 故障日志；请求计数 |
| OPS-03 | BASE | **备份与恢复**：备份测试 DB、必要加密密钥和版本信息；恢复到另一个新测试库。 | 观测、配置、用户权限和 canary 凭据一致；不恢复到生产。 | 恢复日志；前后记录/哈希核对 |
| OPS-04 | BASE | **资源与稳定性**：固定本机配置，连续跑 20 个本地 fixture 任务并记录 CPU/内存/延迟。 | 给出实测峰值和失败数，不伪称生产吞吐或 SLA。 | resource-profile.json；任务日志 |
| OPS-05 | BASE | **停止与清理**：执行 stop 两次，检查当前 run 的进程、队列和网络；清理另需范围校验。 | 幂等停止；不删除证据或其他 Docker 卷。 | stop.log；资源清单 |
| OPS-06 | BASE | **人工事项汇总**：模拟缺 Key、需标签审核、服务故障和到期审批。 | 生成单份待办摘要；不循环催问、不自动批准或自动充值。 | OWNER_ACTIONS.md |

### 14.9 单域名约束与复现（G5）

| ID | 适用性 | 测试及操作 | 预期结果 | 最低证据 |
|---|---|---|---|---|
| INT-01 | BASE | **主站零改动**：比较 P0 前后官网仓库状态与部署操作记录。 | 没有修改官网代码、DNS、支付、认证、表单或生产配置。 | 网站工作树快照；操作审计 |
| INT-02 | BASE | **根路径限制**：检查上游 root-path 要求；评估未来内部 API 方式。 | ADR 不声称原版 UI 可直接挂 /geo；不推荐新增域名来绕过决定。 | ADR-SINGLE-DOMAIN.md |
| INT-03 | BASE | **内部接口演示**：本地服务端适配器只读已生成报告；不把 Elmo 管理 token 给浏览器。 | 可映射必要数据；无公网发布；单组织限制明确。 | 本地请求/响应；权限检查 |
| INT-04 | BASE | **复现交接**：在干净隔离配置中按 Runbook 重放最小离线流程，校验报告和证据清单。 | 无需口头补充隐藏步骤；失败准确标注，源码和环境版本一致。 | REPRODUCTION.md；重放日志 |

---

## 15. 审计证据、结果格式与交付完整性

### 15.1 每次运行的证据目录

```text
runs/<run_id>/
├── run-manifest.json
├── approvals.redacted.json
├── source-lock.json
├── environment.redacted.json
├── policy.redacted.yaml
├── commands.jsonl
├── test-results.jsonl
├── egress.jsonl
├── quota-ledger.jsonl
├── fixtures-manifest.json
├── raw/                         # 访问受控，禁止带认证头或敏感会话
├── observations.jsonl
├── analyses/<judge_version>/
├── metrics-recompute.json
├── screenshots/                 # 预先确认无密钥和客户隐私
├── logs/
├── reports/
├── evidence-manifest.json       # 文件路径、大小、SHA-256、敏感级别
└── SHA256SUMS                   # 不将自己递归计入哈希
```

禁止 `runs/latest` 作为唯一证据位置。每次运行有独立 UTC ID；重跑不能覆盖原始记录。敏感证据目录设最小权限；与可公开的报告分离。API Key、数据库口令和加密主密钥不进入普通审计包；恢复所需秘密单独保管，不与备份同处公开目录。

### 15.2 运行清单模板

下方是未执行的模板；空值必须由实际运行填写，不得随意补成成功：

```json
{
  "schema_version": "1.0",
  "run_id": null,
  "plan_id": "TUC-GEO-ELMO-P0-001",
  "plan_version": "1.0",
  "plan_sha256": null,
  "upstream_commit": "15c2d5f1b56682ce98e6c6ed76e254eec124e15e",
  "patch_sha256": null,
  "lockfile_sha256": null,
  "runtime_versions": {},
  "container_digests": [],
  "database_schema_version": null,
  "policy_sha256": null,
  "prompt_set_sha256": null,
  "golden_set_sha256": null,
  "approval_refs": [],
  "started_at_utc": null,
  "completed_at_utc": null,
  "live_request_count": null,
  "external_cash_charge_usd": null,
  "billing_verified": false,
  "test_counts": {},
  "decision": "NOT_RUN",
  "limitations": []
}
```

`external_cash_charge_usd=null` 表示没有核实，不等于 0。若全程离线或 stub，填无真实调用的证明，并将真实账号账单核验标成不适用；不要伪造服务商账单。

### 15.3 单用例结果模板

```json
{
  "test_id": "COST-03",
  "requirement_ids": ["C04", "C08", "C09"],
  "suite": "offline",
  "applicability": "BASE",
  "status": "NOT_RUN",
  "expected": "20 concurrent local attempts with 1 reserved slot yield at most 1 outgoing request",
  "actual": null,
  "evidence_refs": [],
  "started_at": null,
  "ended_at": null,
  "exit_code": null,
  "reviewer": null
}
```

允许的结果状态：`NOT_RUN / PASS / FAIL / BLOCKED / NOT_APPLICABLE`。任何 `PASS` 必须同时存在实际输出和可读取证据；任何 `NOT_APPLICABLE` 需具体理由及批准的范围。HTML 绿勾或模型文字“看起来正确”不构成测试证据。

### 15.4 哈希与复核

Codex 实现跨平台 SHA-256 清单生成器：使用相对路径稳定排序，包含字节数，拒绝逃逸路径／不受控符号链接；不把秘密目录和清单自身打包进公开证据。

验收者应能：任选一条结论 → 找到 observation → 找到原始回答 → 校验哈希 → 复算相关指标。修改一字后的证据应使 `p0ctl verify` 失败。将最终清单摘要交给负责人保留；仅在同一可写目录放一个哈希文件，不称为防篡改审计系统。

### 15.5 保留与删除

P0 的建议保留期为 30 天，属于内部方案而非法定要求。由负责人确定最终留存期限；关键审计摘要可更长，原始响应按供应商规则和必要性管理。删除必须限定到本 run 的目录、测试记录和卷；先导出批准保留的证据。未得到删除授权时，只停止服务，不 `docker compose down -v` 或清空目录。

---

## 16. 安全、恢复和最少人工操作手册

### 16.1 安全基线

- 只使用 TUC 公开信息与人工测试数据，不向免费模型提交客户机密、个人联系方式、密钥或内部架构。
- 实际服务条款、数据使用方式与账号地域单独核验；开源许可不覆盖 API 服务和第三方数据。
- Web、Worker、数据库、文件存储分开最小权限。非必要不挂载宿主 Docker socket、SSH agent 或主目录。
- 管理界面只本机／批准私网可达；若必须在远端主机操作，先确认访问方式与权限，不自动开公网端口。
- P0 只用一个内部组织。对外客户级隔离、生产审计日志、SLA 和备援均是下一阶段能力，不得通过修改文案抹掉。
- 公开网页读取仅限获准 host 的低频 GET；不运行渗透扫描、不提交表单、不登录客户系统。

### 16.2 备份恢复演练

1. 停止领取新任务，记录队列状态和待处理 observation。
2. 备份测试数据库；单独安全备份加密密钥及必要配置，绝不写进普通日志。
3. 创建另一套空白测试数据库／卷，使用相同数据库大版本和已锁定迁移版本恢复。
4. 检查品牌、问题、原始证据索引、判读版本、账号权限、队列状态和合成凭据可解密性。
5. 不运行自动补偿采样或历史重判；先在 deny-egress 状态验证。
6. 记录恢复用时与缺失数据，不称为生产 RTO/RPO 保证。

上游提醒数据库备份必须配套保留凭据加密密钥；错误密钥可能触发环境凭据回退。[S05] 本项目要求恢复失败时停住，不能转用未知账号。

### 16.3 故障处理

| 情况 | 自动动作 | 人工处理 |
|---|---|---|
| 免费额度不足／到期 | 停止对应真实请求，其他离线任务继续 | 更新合法额度证据；不得自动充值 |
| Provider 429／不稳定 | 保存失败，真实批次不自动重试 | 决定是否批准新批次 |
| Jev 不可用 | 标记判读未完成，不回退 stub 冒充成功 | 评估获准替代判读器 |
| API Key 泄露疑似 | 停止任务并隔离受影响证据 | 负责人处置／撤销测试 Key，检查传播范围 |
| 数据库不可用 | 暂停任务领取，不忙循环 | 修复测试服务或恢复备份 |
| 网络策略无法证明 | 不注入真实 Key、不调用接口 | 调整测试环境，不降低安全条件 |
| 生产资源误连接 | 立即停止写入与相关进程，保留日志 | 通知负责人；不得擅自清理生产“痕迹” |

### 16.4 负责人只看一页摘要

每个阶段结束后由现有运行生成摘要，不默认开设后台自动任务：

```text
阶段 / 当前决策 / 本次执行范围
测试：PASS x，FAIL x，BLOCKED x，NOT_RUN x，N/A x
真实接口：Provider、模型、调用数、search 开关、判读方式
费用：已核实零新增 / 未核实 / 异常；证据引用
官网和生产：未修改 / 发现异常
新增补丁：数量、目的、上游维护影响
需负责人处理：最多集中列出 3 项，注明缺什么及影响
下一步：仅在已有授权范围内的工作
```

不要求负责人每天看日志。仍需一次性确认标签和额度，以及最终作出采纳决定；这些不能用“AI 已自评通过”替代。

---

## 17. 报告模板与交付内容

### 17.1 对负责人交付的审计结论

`P0_AUDIT_REPORT.md` 至少包含：版本与范围、环境、原版基线、补丁、Provider 支持矩阵、判读结果、调用路径和费用、权限边界、64 项用例结果、失败原因、单域名集成 ADR、备份恢复、资源记录、Go/No-Go。

不要把整体结果写成“支持 OpenAI/Gemini/Qwen”，应按下表逐格填写：

| 路线 | 静态已确认 | Mock 合约通过 | 真实调用通过 | 非模拟判读通过 | 额度证明 | 本次可用范围 |
|---|---|---|---|---|---|---|
| OpenAI 原生 | 待执行者核对 | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 未实测 |
| Gemini 直连 | 需适配评估 | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 未实测 |
| Qwen/DashScope 直连 | 需适配评估 | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 未实测 |
| Qwen/OpenRouter | 需核对具体模型 | NOT_RUN | NOT_RUN | NOT_RUN | UNKNOWN | 未实测 |

### 17.2 英文样例报告骨架

样例仅用于内部验收；禁止自动发布到官网或作为客户案例。

```markdown
# TechUnity Connect — AI API Visibility Pilot

Status: INTERNAL TEST — NOT A CONSUMER-UI RANKING REPORT
Observation mode: <actual mode>
Judge mode and version: <actual judge>
Collection window: <actual UTC timestamps>
Providers / models / search configuration: <actual values>
Question-set version: <hash or version>

## Scope and limitations
Explain which APIs were tested, which were not, and whether search was enabled.
Separate branded controls from non-brand discovery questions.
State that API outputs are not consumer ChatGPT/Gemini interface rankings.

## Collection and analysis completeness
Planned observations / successful answers / valid judgements / blocked or failed.

## Findings
Each finding must include observation IDs and exact supporting passages.
Report no mention as a valid result; do not invent reasons for non-appearance.

## Citation evidence
Distinguish provider annotations from ordinary answer links.
Use N/A when the selected method does not expose citations.

## Suggested next actions
Tie each action to an observed issue; label hypotheses as hypotheses.
No promised ranking, traffic or revenue outcomes.

## Evidence index and method
Include reproducible IDs, versions and hashes, not secrets.
```

### 17.3 报告生成规则

首版采用确定性 Markdown/HTML 模板，数值由代码计算，不再调用收费模型写报告。已有合格的本地模型可作为可选文案润色层，但不得改数字、证据或方法标签。PDF 不是 P0 必需交付；不为格式增加第三方服务或不必要依赖。

UI、API、CSV/JSON、Markdown、HTML 必须保持相同分母和来源标签。报告不解释“为什么某 AI 不推荐 TUC”，除非原回答提供了可引用的理由；否则标成待验证假设。

---

## 18. Go / No-Go 决策与不可降级门槛

### 18.1 决策类型

| 决策 | 条件 | 允许做什么 |
|---|---|---|
| `GO_API_PILOT` | 所有适用 BASE 通过；确不适用项须逐项说明并经复核，硬门槛不可豁免；所选路线的 LIVE/COND 全部通过；完整证据与费用证明 | 进入另行批准的内部 API 试点设计；仍不授权商业上线 |
| `CONDITIONAL_GO_OFFLINE` | 安装、stub、回放可用，真实接口／判读／额度存在未完成项 | 继续有限离线开发与架构评估；不宣称真实闭环完成 |
| `NO_GO_CURRENT_CONSTRAINTS` | 零费用、许可、关键安全、证据或单域名约束无法满足且最小改造不合理 | 停止扩展本路线，保留审计结果；不擅自买服务绕过 |
| `BLOCKED` | 网络、设备、Key、权限、免费额度或批准缺失，无法作出充分判断 | 交付已完成结果和精确 blocker，不误判项目永远不可行 |

“上游不支持某个选项”和“已测试发现漏洞”是不同性质；前者可以是范围限制，后者必须记录风险。未测试不能写“不存在问题”。

### 18.2 不可用平均分抵消的硬门槛

任何真实路线出现以下情况，都不能获得 `GO_API_PILOT`：未经批准费用、账号回退、生产变更、Key 泄露、模拟数据冒充真实、证据无法回溯、失败算零提及、关键权限越界、无硬限制的付费风险，或所选判读器没有通过必要质量验证。

对于多租户能力，P0 可以明确限定为 `INTERNAL_SINGLE_ORG_ONLY`，但不能因此宣称已适合多个客户共用。如果后续要售卖，客户隔离将是新增的生产前硬门槛。

### 18.3 哪些开发工作值得保留

优先保留上游品牌／问题管理、已有队列与数据模型、证据提取、API、基础 UI。TUC 新增工作限制在：

1. **费用与请求边界**：策略、批准、配额预留、熔断、可审计账本。
2. **确有必要的一个适配器或判读替代**：先 mock、再有限实测，独立版本。
3. **证据导出和报告**：模式标签、原始引用、指标复算、确定性模板。

每个补丁记下修改文件、原因、替代方案、测试 ID、上游升级影响和撤回方法。不能为了省一点接口改造而重做 UI、权限、计费或组织系统。

如果必须广泛改写 router/auth、核心数据库、调度和多个 Provider 才能达到最小目标，先提交改造评估，暂停扩展；不要借 P0 名义交付一个失去上游可升级性的 fork。

---

## 19. 完整交付清单与可追踪任务

### 19.1 必交文件

| 文件 | 内容 | 验收方式 |
|---|---|---|
| `README_P0.md` | 一页使用方法、版本、授权与状态 | 新执行者可定位入口 |
| `M0_READINESS.md` | 工作区、工具链、现有约束、依赖与阻塞 | 所有未知项明确 |
| `SOURCE_LOCK.json` | commit、lockfile、镜像、配置哈希 | 可复核版本 |
| `DEPENDENCY_REGISTER.md` | 所有外联及潜在费用环节 | 映射源码和测试 |
| `PROVIDER_MATRIX.md` | 四条路线分层支持状态 | 静态／mock／live 不混淆 |
| `COST_AND_EGRESS_AUDIT.md` | 免费额度、批准、出站、账本和回退 | 证明请求没有越界 |
| `TEST_PLAN.md` + `test-results.jsonl` | 64 项适用性和实际结果 | 全部有状态，PASS 有证据 |
| `QUALITY_COMMANDS.md` | 本版本真实可用的质量命令 | 命令、前置与退出码准确 |
| `METRIC_MAPPING.md` | 上游与 TUC 指标定义差异 | 可独立复算 |
| `SECURITY_REVIEW.md` | 关键风险和内部使用边界 | 不隐藏生产缺口 |
| `ADR-SINGLE-DOMAIN.md` | 内部 Elmo 与未来主站接口方案 | 不引入其他公网域名 |
| `RESTORE_RUNBOOK.md` | 测试库备份、恢复、停止与受控清理 | 至少一次恢复实证 |
| `SAMPLE_REPORT_EN.md` | 实际数据模式对应的英文样例 | 明确来源与限制 |
| `P0_AUDIT_REPORT.md` | 核心结论、阻塞、成本、Go/No-Go | 每项结论指向证据 |
| `OWNER_ACTIONS.md` | 最少人工待办 | 可一次性处理 |
| `runs/<run_id>/` | 第 15 节完整证据 | 哈希和关联校验通过 |
| `patches/` + 测试代码 | 实际最小改造；无改动则写明 | diff 可重放，未混入 secrets |

没有真实调用条件时，`SAMPLE_REPORT_EN.md` 必须显著标为 stub／replay，`P0_AUDIT_REPORT.md` 写 `CONDITIONAL_GO_OFFLINE` 或 `BLOCKED`，不能把文件齐全等同 P0 通过。

### 19.2 建议任务拆分

| 任务 | 内容 | 依赖 | 验收关联 |
|---|---|---|---|
| T01 | 范围、仓库指令和版本冻结 | 无 | SRC-01～05 |
| T02 | 调用图、凭据解析与费用清单 | T01 | COST-06～08 |
| T03 | 新环境、迁移与原版 stub | A0、T01 | ENV-01～06 |
| T04 | 请求守卫、预算、出站与急停 | T02、T03 | COST-01～09、SEC-08 |
| T05 | Provider 合约与必要单一适配器 | T04 | PRV-01～08 |
| T06 | 判读质量、金标准和模式标签 | T03、标签复核 | JUD-01～06 |
| T07 | 证据数据模型、指标和报告 | T05、T06 | DATA-01～08 |
| T08 | 真接口限量验证 | A1、T04～07 | PRV-09、JUD-07、COST-10 |
| T09 | 安全、恢复和单域名 ADR | T03～07；真实结果可后补 | SEC、OPS、INT |
| T10 | 审计交付与采纳决策 | 所有已执行结果 | 第 18 节决策 |

依赖被阻塞时执行独立任务，不自动跨审批边界。不要用任务数量或代码行数衡量完成，依据是证据和验收。

---

## 20. 验收人复核清单

交付前逐项填写，不得预先打勾：

- [ ] 单域名决定保留，`.net` 和新公网子域未启用。
- [ ] 原官网、生产 DNS、生产数据库、表单和支付未修改。
- [ ] 上游 commit、依赖、镜像和补丁已锁定。
- [ ] 开源、模型、依赖与服务条款分别核验；未知项未隐藏。
- [ ] stub、回放、真实 API、本地模型和判读方式均明确。
- [ ] OpenAI／Gemini／Qwen 的静态、合约和实测状态分开。
- [ ] 若调用真实 API，所有角色均有有效批准、免费额度证明和账本。
- [ ] 定时采样、历史重判、搜索、研究和 Key 回退没有绕过限制。
- [ ] 人工标签被复核；候选判读器不是把原生 stub 改名。
- [ ] 失败、不支持、未判读不会转换成虚假的零提及或零费用。
- [ ] 至少能从一个报告结论追溯到原始回答并复算。
- [ ] 64 项测试都有真实状态；未做的仍是 NOT_RUN/BLOCKED。
- [ ] 完成隔离测试库备份恢复与停止演练。
- [ ] 单组织限制、未测试能力、生产缺口在决策中显著呈现。
- [ ] 审计包脱敏并通过秘密扫描；哈希清单已另交负责人。
- [ ] 最终结论是明确的 Go/Conditional/No-Go/Blocked，不是笼统“基本完成”。

---

## 21. 可直接交给 Codex 的启动指令

### 21.1 第一条指令：只执行 G0

```text
你是 TUC GEO 项目的工程执行与验证 Agent。

请完整阅读本文件 TUC_GEO_Elmo_P0_Test_Audit_Plan.md，把它作为 P0 执行规格。
当前只执行 G0 只读核查，不开始部署、不迁移数据库、不调用真实 AI Provider。

已确认约束：
1. 唯一公网业务域名 www.techunityconnect.com；不启用 .net，不新增公网子域。
2. Elmo 为第一优先开源引擎；先验证，再决定最小改造。
3. 新增软件、Token、模型 API、采样、云资源费用均未获批准。
4. 允许使用已有 Provider Key 不代表授权产生费用；不得读取无关秘密或把 Key 放入输出。
5. 不修改现有官网、原表单、生产 DNS、生产数据库、支付或上线配置。
6. 遵守当前工作区和上游 AGENTS.md。Elmo 固定研究提交为
   15c2d5f1b56682ce98e6c6ed76e254eec124e15e；不要静默升级。

先确认当前工作区与授权范围，读取指令和源码；可以在独立审计目录写报告，
不修改现有业务代码，不运行会触发应用、安装脚本或数据库写入的命令。

输出：
- M0_READINESS.md
- SOURCE_LOCK.json（仅记录已实际核验的内容）
- DEPENDENCY_REGISTER.md
- PROVIDER_MATRIX.md
- CONFLICTS.md
- 拟定的 G1—G5 执行清单、隔离目录与需要的一次性批准

重点核验：OpenAI Responses 路径、Gemini/Qwen 直连支持、Jev 依赖与 stub、
初始化和机会报告的隐藏模型调用、默认五次采样、历史重判、凭据回退、
原版 UI 根路径限制、local 模式 single-org。

所有测试默认 NOT_RUN。没有运行、没有凭据、没有额度证据，就如实写出。
不要为缺少真实 Key 停止可以独立完成的静态工作。
完成 G0 后停止在门禁处，汇总最多三项需要负责人决定的事项。
```

### 21.2 G0 通过后的隔离执行授权模板

以下文字需由负责人实际发出才构成 A0，不因出现在文档里自动生效：

```text
批准你按方案执行 G1—G3 和 G5 中不依赖真实 API 的部分。
仅允许在你已报告、我批准的新隔离目录和测试机器内工作。
明确授权创建新的测试数据库，并只对该新测试库执行所需上游迁移。
允许在隔离环境安装已审计并锁定版本的开源依赖、启动本地服务和运行测试。
不授权任何生产变更、真实模型调用、新增付费服务、公开部署或对外发信。
不得清理或覆盖其他项目数据，不得修改全局配置。
完成后提交测试证据、最小补丁和真实调用批准单；缺少批准的 G4 保持 BLOCKED。
```

### 21.3 真实批次授权必须具体

负责人依据第 7 节批准单确认 Provider、model、endpoint、judge、免费额度、硬停止及调用次数。不要使用“你自行决定费用”“有 Key 就全部跑”“一直运行直到完成”等无限制指令。G4 完成后关闭实时调用开关，交付证据，不自动进入长期采样。

---

## 22. 来源、核查范围与版本说明

### 22.1 固定源码来源

下面链接用于核查本文中的静态事实。执行时保存实际下载内容及哈希；`main` 链接需要另行记录当次 commit。链接可访问不等于该功能已运行通过。

- **[S01] 上游研究提交**：https://github.com/elmohq/elmo/commit/15c2d5f1b56682ce98e6c6ed76e254eec124e15e
- **[S02] MIT 许可证**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/LICENSE.md
- **[S03] package.json／真实命令**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/package.json
- **[S04] 上游 AGENTS.md**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/AGENTS.md
- **[S05] 配置、判读、调度和域名限制**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/packages/docs/content/docs/developer-guide/configuration.mdx
- **[S06] 开发环境文档**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/packages/docs/content/docs/developer-guide/development-setup.mdx
- **[S07] 判读实现及 stub 分支**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/packages/lib/src/mention-judge/analyze.ts
- **[S08] Provider registry**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/packages/lib/src/providers/index.ts
- **[S09] OpenAI adapter 实现**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/packages/lib/src/providers/registry/openai-api.ts
- **[S10] TUC 官网既有约束**：https://github.com/Marvinxtuc/TechUnityConnect/blob/main/AGENTS.md 。本次读取的 blob SHA：`826f1ddd4e85f5e70074d4baf69e0bd48c3271a0`。该链接可要求用户仓库权限，不复制其他私有内容。
- **[S11] 上游 Providers 文档**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/packages/docs/content/docs/user-guide/providers.mdx
- **[S12] Worker 判读入口**：https://github.com/elmohq/elmo/blob/15c2d5f1b56682ce98e6c6ed76e254eec124e15e/apps/worker/src/mention-judge/index.ts
- **[S19] 固定提交的根目录清单**：https://api.github.com/repos/elmohq/elmo/contents/?ref=15c2d5f1b56682ce98e6c6ed76e254eec124e15e

### 22.2 官方 Provider 文档

这些页面会更新；免费政策、模型和 endpoint 必须在执行时复核，不把本文中的存在性说明当成账号承诺。

- **[S13] Gemini OpenAI compatibility**：https://ai.google.dev/gemini-api/docs/openai
- **[S14] Qwen / Model Studio OpenAI compatible API**：https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope
- **[S15] OpenAI：ChatGPT 与 API 的账单管理**：https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform
- **[S16] OpenAI：符合条件订阅的 API credits benefit**：https://help.openai.com/en/articles/20001626-api-credits-benefit-for-eligible-chatgpt-subscriptions
- **[S17] Gemini API billing**：https://ai.google.dev/gemini-api/docs/billing
- **[S18] Model Studio 免费额度与 Free Quota Only**：https://www.alibabacloud.com/help/en/model-studio/new-free-quota

### 22.3 当前核查的局限

本文基于指定上游文件、TUC 仓库指令和官方文档的静态核查，不是完整源码安全审计，也不是安装评测。当前没有验证用户机器、账号余额、原生 API/MCP 运行、Docker 启动或真实费用。编制环境未成功通过 Git 下载并运行整个项目；没有以此虚构任何测试结果。

本文提出的运行上限、质量阈值、目录、测试控制器和人工审批均为工程规格。Codex 必须在真实环境中实施并留证；不能引用本文自身作为“已经测过”的依据。

---

## 最终验收原则

**首选 Elmo，但不预设 Elmo 一定通过。允许已有 API Key，但不预设它免费。复用上游功能，但不把 stub、文档和真实运行混为一谈。保持单域名与现有官网不变，先把证据闭环、费用边界和最小改造验证清楚。**
