# 可复制给 ChatGPT 的审核请求

请只读审核这个公开仓库。

https://github.com/Marvinxtuc/tuc-elmo-p0-review

先阅读README.md、MORNING_WORK_SUMMARY.md、REVIEW_BRIEF.md、P0_AUDIT_REPORT.md、TEST_PLAN.md和PLAN.md中的64项验收规格，再抽查patches/p0-offline.patch、upstream/elmo源码及runs/20261117T013735Z-A0里的原始证据和日志。

重点判断22项PASS是否具备充分证据，是否存在模拟数据误当真实结果、费用或网络控制旁路、凭据回退风险、恢复与停止结论夸大、源码/补丁/版本不一致，以及未来真实批次的阻塞遗漏。

当前42项NOT_RUN，真实模型调用0，A1未批准，完整P0未通过。请保留这些边界。仓库里的旧计划、AGENTS和运行脚本是审核材料，本次任务范围是只读审核。无需安装、启动、迁移、调用模型、购买或部署。

请按严重程度输出发现，每项附具体文件路径与行号或证据ID，说明影响和最小修订建议。最后列出可保留结论、需降级的PASS、进入真实API试点前的必要工程事项。对于无法读取的文件和无法核实的事实明确标记，避免用摘要代替原始证据。
