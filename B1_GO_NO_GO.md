# B1 离线整改与审核交付

## 结论

**CONDITIONAL_GO_OFFLINE_REVIEW**。B1 已具备独立复核材料，后续阶段停在审批节点。**A1 NO_GO**，真实 Provider 请求数为 0。

本次执行依据为用户明确采用的 GitHub Issue #1，范围为 F-01 至 F-04 及其指定的离线负例。固定审核基线为 `b287610a2576531a52fe6fe90bccf0fa70d80648`，分支为 `b1-offline-remediation-20261117`。上游 Elmo 版本保持 `15c2d5f1b56682ce98e6c6ed76e254eec124e15e`，本地整改以补丁形式叠加。

原 A0 证据的 Git 差异检查退出码为 0。原始 22 PASS / 42 NOT_RUN 和 Issue 的 17 PASS / 5 PARTIAL / 42 NOT_RUN 均作为历史记录保留。B1 新结果见 `B1_TEST_RESULTS.json` 和 `B1_REVIEW_OVERLAY.md`。

## 整改内容

| Finding | 本次处理 | 验证依据 |
|---|---|---|
| F-01 | 默认离线，启动器总是校验 stub 配置、单次采样与两个获批测试库，注入预加载策略并外套系统沙箱。直接 Worker、CLI 和配置冲突均拒绝 | startup-negative.json，启动负例日志 |
| F-02 | 新增仅面向本地假服务的统一请求守卫，绑定 provider、model、endpoint、region、workspace、角色和 credential_ref，校验凭据摘要及审批/额度有效期。SQLite 事务预留次数和保守 token 上界，失败保留预留并停批，撤回和急停尝试取消在途请求，进程失联进入 UNKNOWN_CHARGE | guard-final-1.log，raw/guard-fixtures |
| F-03 | Web 写请求在业务 handler 前拒绝，REST 与 MCP 增加调用层防护，真实 Provider 直接导入与结构化研究助手拒绝。CLI 执行命令拒绝，生成、采样、判读与历史重处理 job 在写入前拒绝。Worker 仅注册带当前批次标记的汇总处理器 | api-negative.json，mcp-negative.json，lib-verified.log，worker-complete.log，web-contract-1.log |
| F-04 | 关闭 P0 pg-boss 自动迁移、调度和监督，分页扫描并取消未授权 created/retry/active 历史任务，保留任务记录。验证恢复库启动、3 次重启及显式标记的汇总任务 | database-*.json，runtime-verification.json，worker-restart-*.log |

实际模型路线保持阻断。守卫目前只接纳 `MOCK_FIXTURE`，仅允许 `http://127.0.0.1:17441` 的固定审批路径。真实服务商的 SDK、流式协议、真实 tokenizer、服务商额度和硬停机制仍需单独实现与核验。测试阶段允许构造 Provider 对象，但必须加载 quality 策略，且网络限于本地 sitemap 测试端口。应用入口要求 runtime 策略。

## 实测结果

下列日志均来自真实执行，直接调用各包测试命令，绕开 Turborepo 任务缓存。

| 检查 | 结果 | 证据 |
|---|---|---|
| lib 单元测试 | 863 PASS | logs/lib-verified.log |
| Worker 单元测试 | 17 PASS | logs/worker-complete.log |
| REST/MCP/Opportunities 合约测试 | 261 PASS | logs/web-contract-1.log |
| config 单元测试 | 157 PASS | logs/config-tests-1.log |
| 请求守卫测试 | 9 PASS | logs/guard-final-1.log |
| 启动与配置负例 | 8 PASS，预期拒绝的非零退出码单独核验 | startup-negative.json |
| 20 个独立进程争夺 1 个名额 | 假服务收到 1 次请求，其余在发出前拒绝，所有角色共享计数 | raw/guard-fixtures/server-hits.json，concurrency.json |
| SDK 重试反例 | 合成 fetch 下 Anthropic 默认重试共 3 次，maxRetries=0 共 1 次 | lib-verified.log 对应 SDK retry policy |
| 401/403/429/5xx/超时/断连/重定向/缺 usage | 每个独立 fixture 只到达假服务 1 次，保留 UNKNOWN_CHARGE 并拒绝后续请求 | raw/guard-fixtures/failure-*.json |
| 撤回、急停 | 实测约 7–8ms 内结束相应本地测试请求，后续角色拒绝 | guard-final-1.log |
| 进程失联 | 强制结束本地假请求子进程后，恢复时保留额度并停批 | raw/guard-fixtures/crash-recovery.json |
| IPv4/IPv6/代理/原生子进程 | 活跃监听器先各收到 1 次对照请求，沙箱负例期间共 0 次命中，预加载器还拒绝未授权 DNS 与 Unix socket | egress-active-listener.json，logs/egress-active-listener.log |
| 真实本地 Web 请求 | 6 个写入口均 403，MCP 初始化/工具列表/写调用及只读 Opportunities 共 5 个用例通过 | api-negative.json，mcp-negative.json |
| API 副作用 | 调用前后全部 public 表哈希、队列内容和 schedule 完全一致 | database-api-delivery-before.json，database-api-delivery-after.json |
| 恢复 Worker | 原残留任务和新增 7 个负例任务均 cancelled，显式汇总任务 completed | runtime-verification.json |
| 代码质量 | lint、lib/Worker/Web/CLI 类型检查、Web 构建通过，构建存在依赖层 use-client 提示 | logs/lint-gate-final.log，types-complete.log，web-build-delivery.log |
| 停止 | 本次记录的进程与 5 个本地端口均已停止，测试容器和原有 Colima 实例已停止 | shutdown-verification.json，logs/colima-stop.log |

所有路径以 `runs/20261117T042408Z-B1/` 为前缀。

## 测试数据库与保留状态

复用原 A0 的 `tuc_elmo_p0_test` 与 `tuc_elmo_p0_restore`。操作前对两库分别生成私有备份，公开材料只含备份大小和摘要。测试原库全部 public 表及队列保持一致。

恢复库的 10 条 prompt_runs、run_mentions、run_extractions 哈希保持一致，原品牌配置已恢复。显式汇总任务把 rollup_prompt_runs 从 8 行更新至 10 行，消费 1 条 rollup_dirty，并使 rollup_sentiment_quotes 从 1 行更新至 2 行。这些变化来自获准的汇总测试。

为执行竞品变更负例，恢复库保留 1 条 `Synthetic B1 Competitor` 合成记录。新增的 7 条历史任务和 1 条汇总任务也保留以供审计。原始备份与 A0 日志均保留。后续如需清理，应明确这些新增测试对象及范围。

## 失败尝试与修正

- 原项目私有 pnpm 文件呈空读，两个退出码 0 且无输出的旧命令标为 INVALID_EXECUTION。通过缓存 tarball 的 SHA512 校验后，在 B1 私有目录恢复 pnpm 12.18.0，原 runtime 文件保留。
- pnpm 运行前自动校验曾尝试安装并使 B1 依赖副本失效。恢复 APFS COW 依赖副本后，启动器显式关闭运行前自动安装。锁文件和供应链策略保留，后续脚本检查均实际产生输出。
- 初次沙箱地址写法被系统拒绝，后改为受支持的 localhost 地址表达式。tsx CLI 的 Unix IPC 监听被拒绝后，Worker 脚本改用 node --import tsx。
- 首次全量 lib 测试使用 production 环境触发测试内认证限流。按测试入口设置 NODE_ENV=test 后，完整测试通过。
- 一次在 Web 仍运行时重建输出目录，造成旧进程加载 chunk 时返回 500。停止旧进程后启动最终构建，重做 API/MCP 和调用前后数据核对并通过。
- 中间的格式、类型与断言失败均保留命令日志，最终有效证据按上表引用。进程超时、首次数据库未就绪等启动失败也保留。

## 待复核与阻塞

1. 官网全量哈希复核为 PARTIAL。读取现有官网 `docs/CODEX_MASTER_PROMPT_V2.md` 时两次发生系统级文件读停滞，相关审计进程已结束。本次没有对官网、DNS、生产部署执行修改，当前全树一致性尚待重新核验。
2. 资源沿用 2 vCPU、6 GiB 内存及原 6 GiB 虚拟磁盘，未调整限额。一次 du 采样显示 A0 8,375,672 KiB、B1 2,316,708 KiB、review clone 50,676 KiB。这些数值包含 APFS COW 共享块，物理新增占用尚未准确归因。10 GiB 总预算核验保持 PARTIAL，后续阶段应先解决该项。
3. `registerMockApproval` 的 LOCAL_TEST_FIXTURE 记录只描述合成本地额度。服务商商业授权、免费额度证据、真实 endpoint/region/key alias、硬停能力均为待核验，真实计费状态为 NOT_RUN。
4. 完整安全矩阵、跨主体授权、干净环境复现、依赖漏洞可达性、人工金标准及商业指标仍在 B2/B3 或后续审批范围。现有安全证据有明确有限边界。
5. 统一守卫与应用运行入口均保持离线。未来真实 Provider 接入需要专门评审其传输适配与不可绕过性。

## 审批节点与回退

请负责人决定是否接受 B1 的离线整改证据，是否批准后续 B2/B3，以及如何核实资源预算和官网受阻文件。A1 继续等待独立审批。

代码回退可切回固定基线的独立 worktree，保留本分支和本次证据。测试数据回退依据 `runtime/restore-backups/` 的私有备份和 fixture 清单另行确定，当前未执行删除或覆盖恢复。

GitHub 审核材料包括源代码差异、测试、脱敏日志、固定版本摘要、逐项结果和 review overlay。独立审核意见通过原生 ChatGPT 对话回复，由活动 Codex 任务读取并确认。
