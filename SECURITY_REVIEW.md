# 内部离线安全评估

当前适用边界为 `INTERNAL_SINGLE_ORG_ONLY`。本轮已验证本地管理token的REST/MCP路径和合成owner登录。多客户共享、低权限对象隔离、过期session、SSRF、注入/XSS与完整出站绕过矩阵尚未通过验收。

## 已有控制与证据

| 控制 | 实测范围 |
|---|---|
| 公网出站 | Web/Worker运行sandbox默认拒绝，单独假服务负例验证端口边界 |
| 监听 | Web和DB tunnel为127.0.0.1，容器DB在内部network |
| secret | 仅合成测试值，secret文件0600，普通manifest排除secret、dump、浏览器profile、env |
| 凭据加密 | JWE密文保存，正确key解密、错误key拒绝、恢复后canary相同 |
| API认证 | 无凭据和无效token访问brands/opportunities均401 |
| MCP | 15个只读工具，create/update及不存在的delete/run工具调用拒绝 |
| GET副作用 | REST/MCP读取Opportunities后该表仍0行，观测10条，排队任务为空 |
| 官网保护 | 311跟踪文件一致，G0清单完整复核 |

## 待处理风险

1. `pnpm audit` 有6中危、1低危公告，经MCP SDK引入Hono/node-server。应用入口使用WebStandard transport，尚未完成动态可达性评估和补丁复测。
2. 原版凭据解密失败存在环境回退路径。本轮只使用合成值和stub，真实双账号回退矩阵未验收。
3. 通用费用控制与审批撤回未实现。OS拒绝所有真实路线，当前没有真实Key准入条件。
4. 数据库测试role负责新实例初始化，权限较宽。后续若进入真实内部试点，需单独审阅运行/迁移role拆分。
5. 备份包含合成用户、会话和测试配置，权限0600，普通证据包排除。恢复密钥仍在原secret目录，独立安全备份尚待负责人安排。
6. 资源尚未做20任务峰值与故障稳定性验收。当前本机结果不形成生产SLA。

secret扫描结果以运行目录 `secret-scan.json` 为准。扫描使用随机合成canary和本轮测试secret，只报告路径与字段名。浏览器截图已经目视确认stub横幅和合成账号，页面没有真实客户资料。

发现的权限边界和漏洞不得由A1豁免。生产、公开端口和真实凭据继续等待适用验收与独立授权。
