# TUC Elmo P0 离线验证

本轮执行依据为 project owner 的 A0 批准。当前工程建议为 `CONDITIONAL_GO_OFFLINE`，负责人尚未作出 A2 采纳决定。真实路线依赖为 `BLOCKED`，A1 尚未批准。

固定 Elmo 提交为 `15c2d5f1b56682ce98e6c6ed76e254eec124e15e`。当前工作副本包含 15 个文件的隔离补丁。Node 24.22.3、pnpm 12.18.0、PostgreSQL 18.7 均限定在本项目运行环境中。

## 已有结果

- 10 个问题各完成一次 upstream stub 采样、持久化和读取，英文报告可离线重复生成。
- lint、完整单测、build、五个相关包的类型检查通过，脚本测试 13 项通过。
- 测试库恢复到第二个新库，41 张 public 表内容哈希一致，合成凭据恢复解密通过。
- 本地 REST 分页与 MCP 读取通过，MCP 写工具拒绝，读取前后数据数量一致。
- 官网 311 个跟踪文件与 G0 摘要一致，G0 冻结包校验通过。

真实模型调用为 0。界面中的 20% 来自两个品牌控制问题的回显。真实曝光、推荐、情绪和引用指标均保留 N/A。

## 阅读入口

1. 阅读 [P0_AUDIT_REPORT.md](P0_AUDIT_REPORT.md) 与 [OWNER_ACTIONS.md](OWNER_ACTIONS.md)。
2. 查看 [TEST_PLAN.md](TEST_PLAN.md) 中 64 项验收的实际状态。
3. 用 `python3 p0ctl verify` 校验普通证据。清单摘要需由负责人独立保留。
4. 用 `python3 p0ctl report` 离线重建英文样例。输入与模板固定时输出应一致。
5. 用 `python3 p0ctl stop` 停止本项目应用、数据库和 VM，保留证据与卷。

`p0ctl` 当前实现 verify、report、status、stop。安装、真实 observe、通用预算预留与自动恢复入口尚未实现。服务最终状态以 [shutdown-verification.json](runs/20261117T013735Z-A0/shutdown-verification.json) 为准。

本轮证据位于 `runs/20261117T013735Z-A0`。secret、数据库 dump、浏览器 profile 与普通证据清单分开管理。现有 G0 结论保留在 `<G0_AUDIT_ROOT>`。
