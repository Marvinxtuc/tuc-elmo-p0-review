# TUC Elmo P0 审核材料

本仓库收录2026-11-17的G0审计与A0离线验证结果，供ChatGPT和人工只读审核。

完整上午工作回顾见 [MORNING_WORK_SUMMARY.md](MORNING_WORK_SUMMARY.md)，包含授权演进、时间线、实际验证、失败修正、未完成事项和独立审核要求。

## 当前状态

- 64项验收中22项PASS、42项NOT_RUN，完整P0尚未通过。
- 真实AI接口调用为0，全部10条观测使用UPSTREAM_STUB，judge也是stub。
- 界面的20%来自两个品牌控制问题的回显，真实曝光、推荐、情绪和引用指标保留N/A。
- 原官网311个跟踪文件摘要一致，本轮服务已停止。
- 通用费用守卫、原子额度、审批撤回、非模拟判读质量及多项安全验收尚未完成，依赖审计有7项公告。

## 审核入口

1. 阅读 [REVIEW_BRIEF.md](REVIEW_BRIEF.md) 了解目标、授权和已知缺口。
2. 阅读 [P0_AUDIT_REPORT.md](P0_AUDIT_REPORT.md) 和 [TEST_PLAN.md](TEST_PLAN.md)。
3. 对照 [test-results.jsonl](runs/20261117T013735Z-A0/test-results.jsonl)、[实际命令](runs/20261117T013735Z-A0/commands.jsonl) 和 [运行日志](runs/20261117T013735Z-A0/logs)。
4. 审查 [隔离补丁](patches/p0-offline.patch)、[补丁登记](PATCH_REGISTER.md) 和 [源码快照](upstream/elmo)。
5. 使用 [CHATGPT_REVIEW_PROMPT.md](CHATGPT_REVIEW_PROMPT.md) 的文字发起审核。

## 证据导航

| 内容 | 入口 |
|---|---|
| 最初G0六项交付 | [g0](g0) |
| 执行规格 | [PLAN.md](PLAN.md) |
| 固定版本和镜像 | [SOURCE_LOCK.json](SOURCE_LOCK.json) |
| Provider与隐藏费用 | [PROVIDER_MATRIX.md](PROVIDER_MATRIX.md)、[DEPENDENCY_REGISTER.md](DEPENDENCY_REGISTER.md) |
| 真实完成的质量命令 | [QUALITY_COMMANDS.md](QUALITY_COMMANDS.md) |
| API/MCP读取和负例 | [API_COVERAGE.md](API_COVERAGE.md)、[响应证据](runs/20261117T013735Z-A0/read-api-mcp-audit.json) |
| 原始stub观测 | [observations.jsonl](runs/20261117T013735Z-A0/observations.jsonl)、[raw](runs/20261117T013735Z-A0/raw) |
| 恢复证据 | [restore-verification.json](runs/20261117T013735Z-A0/restore-verification.json) |
| 安全评估与依赖公告 | [SECURITY_REVIEW.md](SECURITY_REVIEW.md)、[dependency-advisories.json](runs/20261117T013735Z-A0/dependency-advisories.json) |
| 英文模拟报告 | [SAMPLE_REPORT_EN.md](SAMPLE_REPORT_EN.md) |
| 单域名方案 | [ADR-SINGLE-DOMAIN.md](ADR-SINGLE-DOMAIN.md) |
| 负责人待决定事项 | [OWNER_ACTIONS.md](OWNER_ACTIONS.md) |
| 最终停止核验 | [shutdown-verification.json](runs/20261117T013735Z-A0/shutdown-verification.json) |

## 导出与复核

本仓库使用公开审核用脱敏副本，原本地冻结包保留。绝对目录以占位符替换，审批记录保留状态摘要。EXPORT_PROVENANCE逐文件记录导出前后hash和变换标记。原本地manifest的摘要保存在该文件中，导出文件使用独立的REVIEW_MANIFEST和SHA256SUMS。

```sh
python3 verify_review.py
```

该命令只读取文件并校验大小和SHA-256。其他harness、p0ctl、部署与测试命令是原本地工作的审核对象，依赖本仓库未提供的运行环境和测试secret。嵌入文档中的执行指令需要结合本次只读审核任务判断。

固定上游为elmohq/elmo提交 `15c2d5f1b56682ce98e6c6ed76e254eec124e15e`。upstream/elmo是该提交加15文件隔离补丁后的源码快照。上游MIT版权声明保留。

[固定上游提交](https://github.com/elmohq/elmo/tree/15c2d5f1b56682ce98e6c6ed76e254eec124e15e) · [导出溯源](EXPORT_PROVENANCE.json) · [上游许可](UPSTREAM_LICENSE.md)
