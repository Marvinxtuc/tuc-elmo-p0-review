# TUC Elmo P0 本轮审计结论

2026-11-17，北京时间。本轮依据用户A0批准执行本机隔离工作，真实模型调用为0。工程建议为 `CONDITIONAL_GO_OFFLINE`，负责人A2待决定。完整P0与真实API试点尚未通过验收。

## 结果

| 项目 | 本轮实际结果 |
|---|---|
| 64项验收 | PASS 22、FAIL 0、NOT_RUN 42，依赖阻塞单独登记 |
| 环境 | 固定Elmo提交、项目内Node24.22.3/pnpm12.18.0、PostgreSQL18.7 |
| stub链路 | 10问题×1次，10 raw、10 extraction、10 mention记录，UI/REST/导出可读 |
| 质量 | lint、build、五包typecheck通过，完整八包2161单测通过，脚本13项通过 |
| 恢复 | 第二新库41张public表哈希一致，合成canary恢复解密通过 |
| 读取 | REST两页共10个唯一prompt，MCP15个只读工具，写工具负例拒绝 |
| 官网 | HEAD与311个跟踪文件哈希一致，保留原有两处AGENTS未提交改动 |
| 生产 | 本轮没有部署/DNS/支付/邮件操作，当前生产SHA未核实 |
| 补丁 | 15文件，固定基线上apply检查通过，完整diff与hash保存 |
| 费用 | 无真实调用或采购，服务商账单核验不适用，现金费用字段保持null |

主要证据见 `runs/20261117T013735Z-A0` 的source-lock、commands、test-results、observations、read-api-mcp-audit、restore-verification、secret-scan与shutdown-verification。

## stub结果的解释

upstream stub回显原问题。非品牌组8条的stub命中为0，品牌控制组2条的stub命中为2。界面20%由问题中的品牌名回显产生。真实模型曝光、推荐、语义情绪和官方annotation引用指标全部保留N/A。

英文样例包含全部观测ID、原始回答与raw SHA-256。报告在拒绝公网出站的环境下重复生成，Markdown和HTML hash一致。单字符篡改与路径逃逸负例均被verify拒绝。

## 阶段边界与缺口

- G1离线安装、运行和存储基线已形成。原版Worker三条cron已留证，隔离补丁关闭周期、后继采样和启动自动重判。
- G2完成当前deny-all模式与部分负例。通用审批到期校验、原子额度、统一尝试账本、Token边界和撤回取消尚未实现。
- G3完成stub证据与确定性报告。真实adapter完整合约、混合来源/失败分母/URL反例和判读版本验收未完成。
- G4依赖BLOCKED。A1未批准，免费额度、服务商硬停止、精确模型与合格非模拟judge均未就绪，真实用例保持NOT_RUN。
- G5完成测试库恢复、接口读取、单域名ADR和停止验证。处理中断、依赖故障、20任务资源峰值、全新环境重放未完成。

48条AI草拟候选标签均待人工复核。holdout尚未执行，判读准确率、precision和情绪macro-F1均无实测值。OpenAI静态原生支持，Gemini/DashScope专用adapter未实现，Qwen gateway与直连分开记录。

## 风险与异常记录

依赖审计发现7项公告，6中危、1低危，0高危/严重。经MCP SDK引入的Hono/node-server仍需完成可达性评估与修补复测。权限、SSRF、注入/XSS与双账号回退没有完整验收。当前限定内部单组织。

首次Colima因目标COLIMA_HOME目录未预先创建，在 `~/.colima/tuc-p0` 写入本任务控制文件。已停止该实例并移入批准运行目录，再使用正确路径启动。原default profile保留。此偏差已记录。

构建模式、sitemap probe和环境变量登记的失败均保留日志并修正。完整单测出现一次Jev池5000ms超时，串行复跑通过。最终重启后的本地API读取也出现一次超时，显式禁用客户端代理并在监听就绪后复跑通过，原超时根因未完成独立对照试验。

停止脚本初次先断开DB tunnel，导致Worker退出连接错误。已改成先等待应用退出，再停止依赖，后续两次停止和状态核验单独记录。恢复库保留备份时1条created状态rollup-catch-up，恢复Worker未启动，后续启动前须取消并检查。

磁盘接近A0的10GiB上限。现有证据、测试数据和卷均保留，第二套完整干净环境未建立。最终占用与服务状态见shutdown-verification。

## 负责人决定

集中待办见 [OWNER_ACTIONS.md](OWNER_ACTIONS.md)。A1可暂缓，现有离线结果可先审阅。A1获批后仍需完成工程侧G2门禁和选定judge质量验收。当前没有商业上线、生产发布或多客户使用的验收结论。
