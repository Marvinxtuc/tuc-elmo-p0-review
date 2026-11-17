# Elmo G0 就绪核查

核查日期为北京时间 2026-11-17。机器可读证据使用 UTC。本次执行依据为用户最新的 G0 请求，附件作为审计规格使用。附件中的 A0、A1 和后续阶段命令仍是待批准内容。

## 结论与阶段状态

G0 静态核查已完成，可提交隔离执行方案审批。P0 整体采纳结论为 `BLOCKED`，等待 A0 及后续运行证据。L1、L2、L3 均未运行。当前证据尚不足以作出 `CONDITIONAL_GO_OFFLINE` 或 `GO_API_PILOT` 决策。

本次实际完成计划全文读取、校验文件比对、固定源码下载、代码与配置审阅、主机只读盘点、官网公开页面一次 GET，以及本目录报告和证据保存。64 项测试全部保持 `NOT_RUN`，静态发现另行记录。具体依赖和审批分别见 [依赖表](DEPENDENCY_REGISTER.md)、[Provider 矩阵](PROVIDER_MATRIX.md)、[冲突表](CONFLICTS.md) 与 [后续执行清单](G1_G5_EXECUTION_CHECKLIST.md)。

## 工作区与指令

| 对象 | 实际核对结果 |
|---|---|
| 当前 cwd | `<USER_HOME>/Desktop`，这是工作区容器目录 |
| 独立审计目录 | `<G0_AUDIT_ROOT>`，本次新建，目录权限 0700 |
| 官网页面仓库 | `<USER_HOME>/Desktop/TechUnityConnect`，origin 为 `https://github.com/Marvinxtuc/TechUnityConnect.git` |
| 官网页面分支与 HEAD | `feat/enterprise-dual-track`，`aa697643422270b8ba478e6a3a39fd15bd3547d6` |
| 官网原有本地改动 | `AGENTS.md` 与 `docs/codex/AGENTS.md` 均已有未提交修改 |
| 上层磁盘规则 | `/AGENTS.md`、`/Users/AGENTS.md`、`<USER_HOME>/AGENTS.md`、`<USER_HOME>/Desktop/AGENTS.md` 均不存在 |
| 会话规则 | 用户提供的全局 AGENTS 指令及最新 G0 请求适用 |
| 官网有效磁盘规则 | 已读取当前工作树 `AGENTS.md` 和 `docs/codex/AGENTS.md`，审计按各自路径作用域使用 |
| Elmo 磁盘规则 | 固定提交只有根 `AGENTS.md`，已读取全文 |

官网工作树规则的 Git blob 为 `37f5a0ac1ce58f0952a7a4102b9ea3aa5125c7bf`。附件 S10 的 `826f1ddd4e85f5e70074d4baf69e0bd48c3271a0` 与本地 HEAD 中的版本一致。当前有效文件另有本地修改，已保存工作树哈希。附件中的远程 `main` 当前值未经本次核对。审批记录和源锁中保留这一差异。[源锁](SOURCE_LOCK.json)

上游要求交接前运行 lint，并要求使用 pnpm、保留供应链控制、迁移须显式批准、公开仓库保护私有资料。G0 只读限制优先适用，lint、安装、构建、迁移和提交均留待相应阶段。审计报告位于上游工作树之外。[上游规则](upstream/elmo/AGENTS.md)

## 固定源码与许可

| 项目 | 已核验值 |
|---|---|
| 上游 origin | `https://github.com/elmohq/elmo.git` |
| 本地位置 | `upstream/elmo`，完整 Git clone，保留历史 |
| 实际 HEAD | `15c2d5f1b56682ce98e6c6ed76e254eec124e15e` |
| 实际 tree | `697c5fa4fe61e408ca0337a7ed0905d65e3a7bf8` |
| 提交时间 | `2026-11-16T17:25:25Z` |
| checkout 状态 | detached HEAD，工作树干净，非 shallow |
| 跟踪文件 | 1,714 个，已逐文件保存字节数与 SHA-256 |
| 根源码许可 | MIT，版权人为 Blue Whale Software, LLC，2026，复用需保留声明 |
| 工具链声明 | Node `24.x`，`pnpm@12.18.0` |
| lockfile SHA-256 | `743919e30a100aa0b8386b3b60b9ac8bf0a64de702c0cc6b4ffa9180d66c5151` |
| 根 AGENTS SHA-256 | `a43b814a9923b0d26dd4765781b118a979640818c8f3733650ef5d3e5b0c93cf` |
| 迁移文件最后 journal 条目 | `0033_copilot_picks_to_bing_ai_mode`，idx 33。实际数据库迁移版本为空 |

计划原文件 SHA-256 为 `d31a54c561a2d218e16c68dbbba7fb49333f5150aaf9f8ec7e9dc93d2a1fbc73`，与用户提供的 sidecar 一致。原文和校验文件副本位于 `evidence/`。[计划副本](evidence/TUC_GEO_Elmo_P0_Test_Audit_Plan.md)

已核验根 MIT 许可及 workspace 包声明，第三方依赖逐项许可、安全公告、模型权重和服务条款仍待核验。许可脚本列有 Sentry FSL、字体 OFL 等例外，需要安装后审阅实际依赖清单。镜像 digest、应用构建哈希、运行配置哈希及实际数据库版本均为空，源锁明确记录未执行状态。[许可检查脚本](upstream/elmo/scripts/check-licenses.mjs)

## 主机与环境

| 项目 | 只读盘点结果 | 后续含义 |
|---|---|---|
| OS / CPU | macOS 26.5.1，arm64 | 容器及原生依赖的 arm64 兼容性待运行核验 |
| 物理内存 | 32 GiB | 当次 `memory_pressure -Q` 显示 66% system-wide free，该值属于即时指标 |
| 可用磁盘 | 约 31.8 GiB，Data 卷使用率 85% | 安装、镜像与备份前重新核算空间 |
| PATH Node | `v22.23.1` | 与上游 Node 24 要求不匹配 |
| PATH pnpm | 安装包元数据为 `9.15.9` | 与上游 pnpm 12.18.0 不匹配，未运行其包装器 |
| Corepack | 安装包元数据为 `0.34.6` | 后续需隔离准备指定工具链 |
| Docker CLI | `29.4.1` | daemon、Compose、虚拟机、许可资格和资源配置待核验 |
| PostgreSQL 客户端 | `psql` / `pg_dump` 均未在 PATH 找到 | 后续可在批准容器内提供 |
| 浏览器 / 证书 | 运行验证 `NOT_RUN` | 留待 G1 浏览器和 localhost 检查 |

工具链版本核查仅执行 Node、Docker CLI、Git 的版本查询，pnpm 和 Corepack 读取其现有安装包元数据。没有执行依赖下载、应用入口或数据库命令。[环境证据](evidence/environment-static.json)

## 官网与生产边界

官网当前规则约束为六个顶级页面、首页五模块、中英文、企业 tech/biz 表单、独立 FDE 表单与可选分析。主站范围排除数据库、CRM、认证、dashboard 和客户门户。根 package 声明 Next.js `15.5.25` 与 Node `22.x`，部署配置使用 Netlify。[官网有效规则](<USER_HOME>/Desktop/TechUnityConnect/AGENTS.md)

2026-11-17T01:24:36Z 对 `/en` 的单次 GET 返回 HTTP 200，响应头为 `Server: Netlify`。当前生产 SHA 未得到可验证元数据，本地 HEAD 与当前生产是否一致为 `UNKNOWN`。仓库的 2026-09-13 发布记录记载应用提交 `8a20f357fd08c8a901a37bee5f80c9fac6a77624`，其适用范围为历史发布。运行中的邮件、分析投递及完整路由回归均为 `NOT_RUN`。[公开 GET 证据](evidence/website-public-en.json)

官网原有两个未提交规则文件已有快照，后续将按当前工作树继续保留。G0 的写入范围集中在独立审计目录。前后状态及文件哈希比较见 `evidence/website-after.json`。回退本次审计只涉及新建审计目录，需按用户删除审批规则单独处理，官网无需恢复操作。

## 静态发现与阻塞

1. OpenAI 采用 Responses adapter。Gemini 和 DashScope 原生直连需要适配，OpenRouter 已有 Gemini/Qwen 路由格式。实际模型可用性、账号及免费额度均为未知。[Provider 矩阵](PROVIDER_MATRIX.md)
2. Jev 固定为 `jev-1.13.0`，OpenRouter 使用 `typesafe/jev-1.13`。TypeSafe 优先选择、网关故障保持所选通道、DB→env 凭据解析和研究 Provider 自动选择具有不同语义，需要分别验证。[依赖表](DEPENDENCY_REGISTER.md)
3. Opportunities 的 GET 和 MCP `get_opportunities` 在缺少新鲜缓存且摘要足够时可触发模型生成与写库。生成最多尝试三次。这是后续只读能力白名单的重点限制。[机会报告生成](upstream/elmo/apps/web/src/server/opportunities.ts)
4. 默认每问题五次采样，Worker 启动即注册维护、历史重判及聚合任务，并尝试补判。原版配置片段无法单独实现 P0 的一次性批次限制。[Worker 启动路径](upstream/elmo/apps/worker/src/index.ts)
5. Jev 限流池默认并发上限 64、429 重试六次，超长判读还可递归拆分。报告判读和队列另有重试层。G2 必须统一计数及约束。[Jev transport](upstream/elmo/packages/lib/src/mention-judge/jev.ts)
6. 原版 UI 要求域名根路径，local 为 single-org。单域名下的后续方案采用内部服务及受控服务端数据读取，具体公网呈现需另批。[配置说明](upstream/elmo/packages/docs/content/docs/developer-guide/configuration.mdx)

| 阻塞项 | 影响范围 | 解锁材料 |
|---|---|---|
| A0 未提供 | G1、G2、G3 与需要运行环境的 G5 | 测试机器、隔离路径、资源、安装与新测试库迁移授权 |
| 工具链与运行环境未准备 | G1 | 隔离 Node 24 / pnpm 12.18.0、daemon 可用性及软件许可核验 |
| 凭据、免费额度、硬停止及 A1 缺失 | G4 | answer 与 judge 各自的有效额度、服务条款、精确批次批准 |
| 第三方依赖与服务许可仍有未核实项 | G1 供应链门禁及所选真实路线 | 实际依赖许可清单、容器引擎资格、API 数据处理与报告用途条款 |
| 人工标签审核人未指定 | 合格非模拟判读的 JUD-03 | 48 条样本及冻结 holdout 的人工复核 |
| 费用与出站守卫待实现 | G2 退出、G4 准入 | 传输层计数、失败关闭、禁止旁路、急停证据 |
| 当前生产 SHA 未核对 | 仅限制本次对生产版本的结论 | 后续经授权的部署元数据读取，独立内部试验可继续规划 |

本次没有打开凭据文件、读取现有 Provider Key 或查询账号账单。所有真实接口、免费资格和商业授权均保持未知。下一阶段需要负责人处理的三组事项集中列在执行清单末尾。
