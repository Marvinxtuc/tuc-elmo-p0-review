# 复现边界与操作

当前完成同一隔离环境下的离线报告重复生成，以及冻结源码上的补丁apply检查。第二套全新安装环境重放尚未执行，INT-04保持NOT_RUN。磁盘接近已批准10GiB上限，当前环境和证据全部保留。

## 可立即复核

在 `<AUDIT_ROOT>` 执行以下命令。

```sh
python3 p0ctl verify
python3 p0ctl report
python3 p0ctl verify
```

报告生成在runtime.sb下运行，输入为run目录的observations、raw文件及固定模板。首次/重复生成的hash记录于report-render日志。样例报告包含每条observation ID和raw SHA-256。修改报告一个字符的负例由独立tamper-probe验证，原始报告保留。

## 本地服务重启记录

工具链、VM目录、数据库镜像、配置与问题集的hash在SOURCE_LOCK中。服务启动命令在commands与processes中，命令使用run-command.py，后续进程采用独立HOME。恢复运行时须保留runtime.sb，不更换成quality/browser策略。

DB使用独立Colima profile和内部网络。Mac到VM的loopback自动转发未生效，因此本轮使用项目SSH配置建立loopback17332到VM容器地址的专属tunnel。容器地址可能变化，复现前需通过项目Docker socket只读获取地址。不得把本轮容器IP视为永久配置。

应用使用production构建，Web绑定127.0.0.1:17300，Worker通过node的tsx loader运行。tsx CLI自身的Unix IPC bind在runtime策略下被拒绝，node loader命令已实测。

## 批次收尾

禁用周期调度后，最后一个采样批次可能留下rollup dirty mark。在本轮测试库手动运行 `harness/flush-rollups.mjs` 一次，并等Worker完成，再核对UI、REST、观测导出和报告分母。现有10条样例已完成该步骤。

固定问题和品牌通过本地REST创建，采样只使用upstream stub。当前没有实现完整的prepare/seed/observe控制器，不能把以上记录视为无人值守的全新安装Runbook。完整原版E2E和干净环境复现仍需工程完成。
