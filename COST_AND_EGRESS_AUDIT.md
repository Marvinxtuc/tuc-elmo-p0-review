# 费用与出站审计

真实模型调用数为0。没有采购、充值、credits领取、支付或真实账号账单查询。本轮使用已有设备及公开开源依赖，服务商账单核验状态为 NOT_APPLICABLE_OFFLINE。`external_cash_charge_usd` 保留 null。

## 已执行控制

- 命令使用环境白名单，后续运行已使用项目独立 HOME/XDG。真实 API Key 未加载，DB中保存的 OPENAI_API_KEY 是随机合成 canary。
- Web/Worker 由 `sandbox-exec` 的 runtime.sb 启动，网络只允许本机17332数据库，公网和其他端口默认拒绝。
- stub Provider 和 stub judge 在应用工厂层允许，真实 Provider 和非stub judge在离线模式拒绝。
- 无定时计划、无遗留待执行任务，RUNS_PER_PROMPT显式为1。关闭后继采样与启动历史重判，批次汇总手动刷新。
- 本地假服务验证禁用端口17331收到0请求，允许端口17332收到1请求。该试验发生在数据库tunnel占用端口前。
- 浏览器使用专属profile、OS loopback策略和页面路由白名单，已观察页面没有站外请求。

证据位于 `logs/os-egress-proof.log`、`read-api-mcp-audit.json`、`browser-brand.json`、`environment.redacted.json` 及进程启动记录。

## 未完成控制

通用真实请求的精确endpoint/model审批、到期校验、原子额度预留、统一尝试账本、Token硬边界、撤回后的在途取消、UNKNOWN_CHARGE处置尚未实现。`config/policy.stub.json` 是状态说明，执行控制来自应用补丁、runner和OS策略。

本轮没有真实批次，也没有伪造费用账本。`quota-ledger.jsonl` 只记录离线窗口的零真实请求结论，不能用于证明未来真实请求具备原子预算。

G4 准入需先完成 G2 工程验收，再取得 A1 的 Provider、模型、判读器、免费额度、服务商硬停止、请求和Token上限。付款余额、订阅权益与持有Key分别核实。
