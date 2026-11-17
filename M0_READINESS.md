# A0 执行后的就绪状态

2026-11-17，北京时间。工作区为 `<USER_HOME>/Desktop`，运行目录为 `<AUDIT_ROOT>`。G0 审计包保持冻结。

有效规则来自用户本会话的全局 AGENTS 指令与 Elmo 根 `AGENTS.md`。运行目录及祖先路径未发现额外 AGENTS 文件。官网规则限定官网仓库，生产边界沿用用户的零改动要求。

| 对象 | 当前核验 |
|---|---|
| A0 | 已批准，引用 `approvals/A0.json` |
| A1 | NOT_GRANTED |
| Elmo | 固定提交与 lockfile 保持，隔离补丁另存 |
| 运行引擎 | 独立 Colima/Lima profile `tuc-p0`，使用已有开源工具 |
| 资源 | VM 2 vCPU、6 GiB RAM，新增磁盘上限 10 GiB，接近上限 |
| Node / pnpm | 项目内 24.22.3 / 12.18.0，全局仍为 22.23.1 / 9.15.9 |
| PostgreSQL | 18.7，固定镜像 digest，独立内部网络和数据卷 |
| 数据库 | `tuc_elmo_p0_test` 与 `tuc_elmo_p0_restore` |
| 应用 | loopback 17300，DB 专属 tunnel 为 loopback 17332 |
| 模式 | UPSTREAM_STUB / UPSTREAM_STUB |
| 官网 | HEAD `aa697643422270b8ba478e6a3a39fd15bd3547d6`，311 文件哈希一致 |
| 生产 | 本轮没有生产操作，当前生产部署 SHA 待核实 |

隔离运行已证明安装、stub 数据管线和测试库恢复可用。真实费用保护、判读质量和生产安全仍有缺口。完整 P0 和真实试点均未通过验收。

A0 中的资源、测试库迁移和本地启动范围已使用。官网数据库、门户、支付、生产 DNS 和公开部署继续受用户既有边界约束。后续真实模型调用必须具备具体 A1、额度与硬停止证据，并先完成 G2 工程缺口。

首次 Colima 启动时，目标 COLIMA_HOME 尚未创建，工具在 `~/.colima/tuc-p0` 建立了本任务控制文件。已停止该实例并把新文件移入批准目录，然后重新启动。现有 default profile 保留。完整记录见运行证据的 `colima-path-correction.json`，其中初次中转路径已迁入最终 profile 目录。
