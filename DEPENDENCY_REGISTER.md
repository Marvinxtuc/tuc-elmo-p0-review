# 依赖与潜在费用登记

本轮未选择真实 Provider。以下路径相对固定 Elmo 工作副本。G0 的详细静态调用图保留在原审计包同名文件。表中的费用为潜在计费方式，当前实例使用 stub 和拒绝公网出站策略。

| 触发动作 | 源码与依赖 | 服务及凭据 | 潜在费用与重试 | 当前处理及证据 |
|---|---|---|---|---|
| 回答采样 | `packages/lib/src/providers` registry、OpenAI/OpenRouter 等 adapter | OpenAI、OpenRouter、Anthropic、Mistral 与采样商各自 Key | token、搜索、采样请求，SDK 和队列可能重试 | 仅 stub，真实 factory 拒绝，lib p0-policy 单测 |
| OpenAI 采样 | OpenAI adapter 的 Responses 路径 | `api.openai.com`，OPENAI_API_KEY | 输出和工具计费 | 未调用，PRV-02 全合约未验收 |
| 品牌研究 | `packages/lib/src/onboarding` | 对应直接 LLM Key | 结构化重试，部分研究默认支持搜索 | 固定品牌种子，ONBOARDING_LLM_TARGET=stub:stub，OS deny-egress |
| 提及和情绪判读 | `packages/lib/src/mention-judge`、`apps/worker/src/mention-judge` | TypeSafe Key 优先，否则 OpenRouter 的 Jev 路线 | Jev pool 可重试和拆分，账号费用独立 | TYPESAFE_API_KEY=stub，真实 judge 拒绝，Jev 质量 NOT_RUN |
| Opportunities | `apps/web/src/server/opportunities.ts` | 直接 LLM Key | 首次读取/过期可触发生成 | 离线补丁仅读缓存，空缓存返回不足数据，HTTP/MCP 读前后0行 |
| 历史重判 | worker `jobs/reprocess`、`jobs/derive-runs` | 同上 judge | 品牌变化、版本变化、重启可补判 | 离线启动跳过历史请求，完整变更矩阵 NOT_RUN |
| 周期采样 | worker `index.ts`、`jobs/process-prompt.ts` | 已配置 Provider 和 judge | 默认 RUNS_PER_PROMPT=5，后继队列和 cron | 显式1，关闭周期与后继采样，最终队列空 |
| 汇总刷新 | worker rollups 与 startup | PostgreSQL | 本地计算，启动 catch-up 和分钟 cron | 手动批次 flush，取消遗留排队 catch-up |
| 来源抓取 | `packages/lib/src/website-excerpt.ts`、citation 相关逻辑 | 任意来源 URL 与第三方来源 | 网络、远程元信息，SSRF 风险 | OS 拒绝公网，完整重定向/DNS负例 NOT_RUN |
| MCP | web MCP tools 和 SDK | 本项目合成管理 token，仅本地服务器使用 | 原版含写工具和有副作用的读取 | 15个只读工具，4类写/未知工具负例，API/MCP日志 |
| 遥测 | Web/Worker instrumentation、telemetry | 可选 Sentry/遥测服务 | 上报和日志存储 | DISABLE_TELEMETRY=1，无真实 DSN，浏览器无站外请求，OS出站拒绝 |
| 凭据解析 | `packages/lib/src/secrets` | DB加密值与环境变量 | 原版存在错误密钥或缺值回退风险 | 仅合成值，正确/错误密钥和恢复测试通过，双账号回退全矩阵 NOT_RUN |
| 安装和构建 | pnpm、Turborepo、Node 官方发行 | 公开包源和镜像源 | 下载流量、本地磁盘，潜在远程缓存 | frozen lockfile，项目内runtime，未启用远程付费构建 |
| PostgreSQL | 独立开源镜像与 pg-boss | 新测试账号和卷 | 本机 CPU/RAM/存储 | 镜像 digest、迁移34条、恢复41表证据 |
| 运行引擎 | 已有 Colima/Lima、Docker CLI | 本地项目profile | 本机资源机会成本 | 新采购支出未发生，未启动 Docker Desktop |

依赖许可脚本退出0，自报扫描66项。额外安装包清单含1582条记录，json-query 2.2.2 的 LICENSE 已核对为 MIT。该脚本覆盖范围和 API 商业授权分别记录。

`pnpm audit --json` 退出1，记录7项公告，6中危、1低危，0高危/严重。依赖经 MCP SDK 引入 Hono 与 node-server。应用 MCP 使用 WebStandard transport，静态入口未发现 Hono 路由辅助函数或 node-server 导入。完整运行可达性与修补复测尚未完成，真实 Key 准入继续关闭。公告详情见 `runs/20261117T013735Z-A0/dependency-advisories.json`。
