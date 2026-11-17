# 实际质量命令

命令通过 `harness/run-command.py` 使用项目工具链和清洁环境执行。运行目录中的 commands.jsonl 保存 UTC 时间、完整 argv、退出码和日志。

| 命令 | 最新结果 | 日志 |
|---|---|---|
| `pnpm install --frozen-lockfile` | 0，供应链策略保留 | pnpm-install.log |
| `pnpm lint` | 0，1073文件 | final-lint-minimal.log |
| `pnpm test --concurrency=1` | 0，2161单测，部分Turborepo缓存复用 | full-unit-serial.log |
| `pnpm build --concurrency=1` | 0，16/16任务，0缓存命中 | final-build.log |
| config/lib/deployment/worker/web `check-types` | 0，五包通过 | final-types.log |
| `pnpm test:scripts` | 0，13/13 | script-tests.log |
| `pnpm license-check` | 0，自报扫描66项 | license-check.log |
| `pnpm audit --json` | 1，7项中低危公告 | dependency-audit.log |
| 新测试库 `drizzle-kit migrate`及重复执行 | 0，34迁移记录 | test-db-migrate-detached-tunnel.log、test-db-migrate-repeat.log |
| 缺A0及越界库名迁移负例 | 0，均拒绝，子进程0次 | migration-negative-tests.log |
| 本地浏览器smoke | 0，登录、品牌页和stub横幅，pageErrors为空 | browser-brand-refreshed.log |
| 本地REST/MCP读取和写工具负例 | 0 | read-proxyless-ready.log |
| 冻结源码上的 `git apply --check` | 0 | patch-apply-check.log |
| G0 `shasum -a 256 -c` | 0，所有列入项一致 | g0-hash-verification.log |

原版五个关键包单测为1925通过。当前同五包为1929通过，新增4条针对隔离策略的回归测试。当前完整八包单测合计2161通过。

保留的失败历史包括原始环境变量污染、完整测试的Jev池5000ms超时、env registry登记缺失、sitemap probe绑定、development构建的jsxDEV错误。串行复跑解决本次超时，未修改上游测试的超时时间或期望。production完整重建后页面复验通过。

原版全套 E2E、Bruno全API矩阵、cloud/demo模式与validate:spec尚未执行。所选本地smoke只证明已记录的路径。构建中的第三方 `use client` 指令警告保留在原日志。

最终重启后的一次本地API复核超时已保留。客户端改为显式禁用代理并等待服务监听后，完整读取与MCP负例复跑0.6秒通过。初次重试在服务开始监听前收到connection refused，随后就绪检查确认监听再执行。原超时根因未单独完成对照试验。

停止脚本曾先断开DB tunnel，引发Worker退出连接错误。已改为等待应用退出后再停止tunnel和DB，最新停止日志单独保存。浏览器截图加入显式等待10 evaluations，避免把加载占位当作最终数据。
