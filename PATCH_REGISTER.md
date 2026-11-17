# 隔离补丁登记

固定提交上新增或修改15个文件，完整diff及hash在 `patches/p0-offline.patch` 和 `SOURCE_LOCK.json`。补丁在G0冻结源码上 `git apply --check` 退出0。未提交或推送。

| 文件组 | 目的和验证 | 升级与撤回 |
|---|---|---|
| lib constants、providers/index、mention-judge/analyze、新p0-policy.test | 离线开关只允许stub Provider/judge，3条回归测试 | 上游registry/judge工厂变更后需重审入口，保留OS deny-egress |
| Worker index、handlers、process-prompt | 并发1，关闭cron/历史重判/启动catch-up/后继采样，取消遗留排队维护 | 上游新增队列时需逐项审阅，撤回后先停止Worker，防止周期恢复 |
| Web opportunities、MCP tools及其测试 | 离线读空缓存无生成，MCP移除写工具，1条回归测试 | 上游新增有副作用的read工具需重审 |
| Web __root | 显著UPSTREAM_STUB横幅 | 仅在固定VITE_TUC_P0_MODE的build中生效 |
| config env-registry、Web env.d.ts、turbo.json | 登记两个隔离环境变量和缓存输入 | env registry测试和完整build通过 |
| www sitemap probe | 本地自检绑定127.0.0.1 | 仅影响构建自检监听，完整构建通过 |

本轮选择在独立工作副本添加显式离线开关，并保留上游默认路径供原版单测验证。所有运行入口都叠加OS出站拒绝。完整费用控制仍需独立设计并贯穿每个请求入口。

实际回退前先核对 `patch-files-final.json` 并保留本项目后续变更。可用 `git apply --reverse --check` 检查撤回条件，按本补丁逐文件处理。禁止使用会丢弃其他修改的全仓reset或clean。
