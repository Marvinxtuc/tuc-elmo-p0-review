# 测试库恢复与停止

## 已完成演练

源库为 `tuc_elmo_p0_test`，目标库为同一新测试实例中的 `tuc_elmo_p0_restore`。目标初始0张public表，使用PostgreSQL18.7的pg_dump/pg_restore。恢复实测0.175秒，41张public表的数量与内容哈希一致，包含10条prompt_runs、1个organization及测试账号权限。

合成Provider canary在源库和恢复库均能使用正确密钥解密，错误密钥被拒绝，两侧密文哈希一致。详情保存在 `restore-verification.json`、`credentials-before-backup.json` 与 `credentials-after-restore.json`。

恢复时间只描述本次小型测试数据。pg-boss队列没有纳入41表的逐表哈希比较，恢复库未启动Worker。恢复库保留了备份时的一条created状态rollup-catch-up任务，定时计划为0。该恢复库尚未启动Worker，后续启动前必须通过离线补丁取消遗留补偿任务并复核。真实灾难恢复和生产RTO/RPO保持待验证。

## 再次恢复的前置

1. 仅使用A0明确的新测试库，核实实例、role、数据库名和目标无业务表。
2. 停止本run领取任务，记录队列。应用必须保持OS deny-egress和stub配置。
3. 单独保管 `secrets/app.env` 的加密主密钥，备份和secret不能混入普通公开报告。
4. 本轮restore库已有数据，`harness/restore-check.py` 会拒绝覆盖。第三个目标库或清空现库需要新的具体授权。
5. 对空目标恢复后比较业务表、权限、schema版本和canary，先检查队列再决定是否启动Worker。

本轮备份位于run目录的 `test-database.dump`，权限0600。它已被普通manifest排除。

## 停止与回退

在项目目录执行 `python3 p0ctl stop`，再次执行应保持幂等。该入口只处理当前run记录的进程、固定compose项目和`tuc-p0` profile，保留卷和文件。停止顺序为应用退出、DB tunnel关闭、容器停止、VM停止。停止结果需以PID、端口和VM状态复核。

本次源码补丁位于 `patches/p0-offline.patch`。撤回时先停止本项目服务并核对当前文件哈希，再将新工作副本与冻结源码比较。`git apply --reverse --check` 可作只读前置，实际撤回应逐文件处理本补丁。官网与其他项目不属于回退对象。
