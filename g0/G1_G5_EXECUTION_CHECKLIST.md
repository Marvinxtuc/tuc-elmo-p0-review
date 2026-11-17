# G1—G5 执行清单与批准要求

日期为 2026-11-17。本文为 G0 的拟议后续计划，所有执行项当前为 `NOT_RUN`。A0、A1 和 A2 均待负责人实际决定。G0 结束后停在此审批节点。

## 拟议隔离范围

运行目录建议为 `<AUDIT_ROOT>`，G0 尚未创建。测试机器建议使用已盘点的本机 Mac mini，实际使用等待 A0。当前静态审计目录保留冻结源码和证据，运行工作副本从相同 commit 创建，补丁另存并记录 hash。

建议初始资源上限为 2 vCPU、6 GiB 内存、10 GiB 新增磁盘，均为待批准值。Web 拟绑定 `127.0.0.1:17300`，端口可用性待 G1 检查。DB 只在隔离内部网络可达。卷、容器、数据库和进程采用本项目独立名称，避免共享其他项目资源。

建议逻辑测试库名为 `tuc_elmo_p0_test` 与 `tuc_elmo_p0_restore`，两者都在新建测试实例中创建。库名仅为规划，实际目标指纹在 A0 后写入证据。原版默认数据库账号密码及公开端口需在测试配置中收紧。

准备阶段只开放已审阅依赖源和镜像源，运行阶段使用默认拒绝的 API 出站策略。stub、合成 Key、固定 TUC 公开信息与人工 fixture 构成首轮数据。secret 存储、批准元数据和普通报告分开保存，运行进程不得自行写入批准字段。

## G1 隔离基线

进入条件为 A0 明确批准目录、机器、资源、依赖安装、启动服务以及两个新测试库的创建、迁移和恢复。预计新增采购支出为 0，已有设备与软件许可的资格待核验。

| 步骤 | 拟执行工作 | 验收及证据 | 对应测试 | 当前状态 |
|---|---|---|---|---|
| G1.1 | 检查磁盘、Docker daemon/Compose 与许可资格，隔离准备 Node 24、pnpm 12.18.0 | 保存 environment 与明确版本，既有全局工具链及官网摘要对照 | SRC-03、ENV-01 | NOT_RUN |
| G1.2 | 从冻结 commit 准备运行工作副本，锁镜像 digest、包源、lockfile 与脚本 | 运行 SOURCE_LOCK、镜像 manifest、依赖许可清单、供应链拒绝日志、可用漏洞核查 | SRC-01/02/05 | NOT_RUN |
| G1.3 | 生成新测试配置，root 与 apps/web 配置一致，凭据白名单、专属 HOME、loopback 端口 | 脱敏配置 hash、挂载/端口清单、配置缺失错误，secret 文件权限 | ENV-01、SEC-01 | NOT_RUN |
| G1.4 | 只创建和迁移 A0 指定的新测试库，数据库指纹前置核验 | 迁移日志及 journal 实际版本，缺 A0 拒绝记录，可重复迁移行为 | ENV-03 | NOT_RUN |
| G1.5 | 先部署拒绝模型 API 出站的边界，再启动 Web 与受控 stub Worker | 出站日志，固定种子手动一批，页面/导出显著 UPSTREAM_STUB | ENV-02/06、JUD-01 | NOT_RUN |
| G1.6 | 查明并控制启动回补、维护 cron、重判、后继采样、待执行队列 | 任务前后清单，重启观察，固定时钟测试，所有旁路计数 | ENV-05、COST-07 | NOT_RUN |
| G1.7 | 按实际脚本执行适用质量命令，原版与后续补丁结果分开 | 完整命令、输入、时间、退出码与日志，未经执行项保持 NOT_RUN | ENV-04 | NOT_RUN |

G1 退出要求为原版 stub 从任务到存储和读取可复现，外联受控，测试库迁移目标明确，所有失败和基线缺陷有可复核记录。若原版 Worker 需要最小补丁才能停止周期路径，先保存原版观察，再由 A0 授权范围中的隔离最小改造落实，并分别报告结果。

## G2 费用与安全门禁

进入条件为 A0 与 G1 隔离环境。使用合成凭据、本地假服务和异常 fixtures。预计新增采购支出为 0。

| 步骤 | 拟执行工作 | 验收及证据 | 对应测试 | 当前状态 |
|---|---|---|---|---|
| G2.1 | 实现最小请求守卫，校验 mode、角色、精确 host/path/model、批准期限、额度与 Token 上界 | 缺批准、过期额度、非法工具/模型、长输入在发送前拒绝 | COST-01/02/04、PRV-05/06 | NOT_RUN |
| G2.2 | 统一请求账本与原子预留，将 SDK、Jev pool、拆分、队列、报告尝试纳入计数 | 本地 20 并发争夺一个槽位，最多一次到达假服务。未知计费不释放为新额度 | COST-03/05 | NOT_RUN |
| G2.3 | 禁止未批准研究、Opportunities、历史回补与凭据回退 | 合成双账号、DB 解密失败、401、缺 Key 均失败关闭，GET / MCP 不触发隐含生成 | COST-06/07/08、SEC-04/07 | NOT_RUN |
| G2.4 | 急停、审批撤回、取消在途请求及网络层 deny-egress | 记录拒绝新任务、取消时间线，未知在途请求保留 UNKNOWN_CHARGE | COST-09、SEC-08 | NOT_RUN |
| G2.5 | 合成 canary、认证、对象范围、注入、XSS、SSRF 和安全汇总 | 无凭据外泄，非法对象被拒绝，恶意网页仅作为数据，绕过出站被阻断 | SEC-01/02/03/05/06/09 | NOT_RUN |

G2 退出要求为费用保护负例在传输层得到证据，默认无真实 Key，read scope 所含生成副作用已受控，API 出站绕过测试通过。真实模型的费用硬停止还需要服务商侧材料和 A1，留待 G4 准入。

## G3 最小适配与离线验证

进入条件为 A0、已通过的隔离/费用边界和已选定的候选路线。先覆盖已有 adapter，新增 Gemini/DashScope 或替代 judge 只选择确有必要的一条。预计新增采购支出为 0。人工标签审核另需指定负责人。

| 步骤 | 拟执行工作 | 验收及证据 | 对应测试 | 当前状态 |
|---|---|---|---|---|
| G3.1 | parser、OpenAI Responses 与选定 gateway 的合约 | 明确文本、usage、annotation、普通链接、拒绝、截断、错误与缺 usage 的映射 | PRV-01/02/05/06/07/08 | NOT_RUN |
| G3.2 | 如主路线需要，单独适配 Gemini 或 DashScope | 新 ID、model/Key/endpoint、限额与超时、错误分类有 mock 测试，非候选路线保持 NOT_RUN | PRV-03/04 | NOT_RUN |
| G3.3 | 生成并由授权人员复核 48 条 fixtures，24 开发、24 冻结 holdout | 标签理由、审阅人、数据与分割 hash。holdout 至少 10 应提及与 10 不应提及 | JUD-03 | NOT_RUN |
| G3.4 | 选定 judge 合约和版本，检查歧义、否定、no_info、偏移、版本缓存 | 准确率与 precision ≥95%，情绪声明须 macro-F1 ≥0.80，引文一致性100%，关键反例全部符合。无足够能力则输出相应限制 | JUD-01/02/03/04/05/06 | NOT_RUN |
| G3.5 | 完整证据侧车、哈希、模式标签、原始与分析版本隔离 | DIRECT_MODEL_API 必须有 A1 与 raw，fixture 明确标识，未判读/null 和失败状态保留 | DATA-01/02/05/06 | NOT_RUN |
| G3.6 | 指标复算、引用域名验证、品牌/非品牌分组、确定性英文 Markdown/HTML | 分母为0给N/A，失败排除原因明确，两次离线报告规范化一致，每条结论指向 evidence | DATA-03/04/08 | NOT_RUN |

G3 判读质量如要调用免费远程模型，也必须具备对应 A1，单独批准质量评估批次。缺少该批准时继续本地回放与其他离线任务，实际判读质量结果保持 `NOT_RUN`，阶段依赖记 `BLOCKED`。

## G4 受控真实批次

G4 进入条件为负责人实际批准 A1、G2 门禁与选定路线的离线合约通过、真实 judge 质量合格、服务商免费额度和硬停止可核验。本阶段新增现金支出上限拟维持 0，任何非零消耗需另立范围决定。

| 步骤 | 拟执行工作 | 验收及证据 | 对应测试 | 当前状态 |
|---|---|---|---|---|
| G4.1 | 核对 answer 与 judge 各自的账号安全别名、地区、模型、免费额度、到期、条款、付费回退与硬停止 | 填写 A1 所有字段，quota 与 provider-side hard-stop 证据可读取。共享余额不明即 BLOCKED | COST-01/02/08/10 | NOT_RUN |
| G4.2 | 一次性有限批次，建议1次连接、10问题×1采样、最多10次独立判读 | 总 HTTP 次数含所有角色与拆分，建议合计≤24，并发1、自动重试0、无搜索/周期。Token 上界另行批准 | PRV-09、JUD-07 | NOT_RUN |
| G4.3 | 原始回答、usage、请求ID、endpoint/model与报告证据保存 | usage 缺失暂停，拒绝/截断/失败不作零提及，账号或网关变化停止 | DATA-01/03/05、COST-05/10 | NOT_RUN |
| G4.4 | 前后额度与账本对账，生成明确模式标签的内部英文报告，关闭实时开关 | 对账、A1、证据关系完整。零提及结果可合格，实时窗口结束可复核 | COST-10、PRV-09、JUD-07 | NOT_RUN |

A1 当前缺失，G4 进入依赖为 `BLOCKED`，所有 G4 用例状态继续为 `NOT_RUN`。本次没有访问账户或领取任何 credits。建议上限24次属于待批准规格，实际 Token、模型价格和免费资格仍需明确证据。

## G5 恢复、接口读取与采纳

G5 的离线工作依赖 A0 和前述隔离成果，可以在缺 A1 时继续。真实闭环结论依赖 G4。预计新增采购支出为 0。

| 步骤 | 拟执行工作 | 验收及证据 | 对应测试 | 当前状态 |
|---|---|---|---|---|
| G5.1 | Web/Worker 停止和重启、DB 故障、20个本地任务资源记录 | 无无限重投，逻辑观测去重，记录峰值、失败数和退出状态 | OPS-01/02/04/05 | NOT_RUN |
| G5.2 | 将测试 DB 恢复到第二个全新测试库，合成凭据解密及队列检查 | 数据数量、hash、版本、权限可对照，恢复后 deny-egress，不自动补判 | OPS-03、SEC-07 | NOT_RUN |
| G5.3 | 发现真实 API/MCP，只读已生成数据，验证权限、分页和证据字段 | API_COVERAGE、MCP 白名单及拒绝记录，Opportunities 副作用已隔离，管理 token 仅服务端 | DATA-07、SEC-02/03/04、INT-03 | NOT_RUN |
| G5.4 | 完成单域名 ADR 和官网前后比对 | 官网 SHA/工作树/文件摘要，Elmo 内部服务边界，root-path 与 single-org 限制写明 | INT-01/02 | NOT_RUN |
| G5.5 | 在干净隔离配置重放，校验 hash、分母与双版本证据 | REPRODUCTION、确定性报告、独立证据清单，修改一个字会使校验失败 | DATA-08、INT-04 | NOT_RUN |
| G5.6 | 汇总64项真实状态、费用、源锁、许可与安全缺口，提交最多三组人工待办 | P0_AUDIT_REPORT、OWNER_ACTIONS、稳定证据目录、负责人保留的独立清单摘要 | OPS-06、SRC-01/02/04、SEC-09 | NOT_RUN |

A2 由负责人依据结果决定采纳。当前 G0 尚未安装或跑 stub，因此完整 P0 判定保留 `BLOCKED`。后续只有 L1/离线结果成立时才可考虑 `CONDITIONAL_GO_OFFLINE`，真实 API、合格判读与所有硬门槛满足后才可考虑 `GO_API_PILOT`。

## 质量命令的已核对存在性

下列命令仅完成根及 package 脚本的静态核对。执行状态均为 `NOT_RUN`，具体前置配置与网络/数据库副作用须在 A0 后审阅。

| 命令 | 用途与前置 |
|---|---|
| `pnpm install --frozen-lockfile` | 指定 pnpm 与 Node、依赖源/下载窗口、保留供应链门禁 |
| `pnpm lint` | 根 Biome check，保存退出码 |
| `pnpm test` | Turborepo 单测，先核对测试是否会外联 |
| `pnpm build` | 跨包构建，清洁凭据、stub 配置和构建遥测审查 |
| `pnpm test:scripts` | 根 Node 脚本测试 |
| `pnpm license-check` | 基于安装元数据的依赖许可检查 |
| `pnpm --filter @workspace/web check-types` | Web `tsc --noEmit` |
| `pnpm --filter @workspace/worker check-types` | Worker `tsc --noEmit` |
| `pnpm --filter @workspace/lib check-types` | lib `tsc --noEmit`，config、deployment 等受影响包另覆盖 |
| `pnpm test:e2e` / `pnpm test:api` | 需要批准测试服务与浏览器/Bruno，审阅目标和种子行为 |
| `pnpm validate:spec` | 当前脚本读取 local/cloud/demo 三组 API 结果，缺项准确记录，禁止为生成结果连接真实 cloud |
| `pnpm --filter @workspace/lib exec drizzle-kit migrate` | 仅对 A0 的新测试库执行，先核对目标指纹 |

根脚本没有通用 `typecheck`。`test:e2e-local` 含自动环境脚本，需逐项审阅后才可执行。G1 将据实际可用命令生成正式 QUALITY_COMMANDS 与执行日志。[脚本声明证据](evidence/package-manifests.json)

## 64 项用例的当前状态

`evidence/test-results.jsonl` 逐条保存全部规格及初值。当前计数为 PASS 0、FAIL 0、BLOCKED 0、NOT_APPLICABLE 0、NOT_RUN 64。上文的阶段依赖 blocker 与测试实际执行状态分别记录，缺 A0/A1 不会把未执行用例写成已测。

| 组 | 数量 | 当前结果 |
|---|---|---|
| SRC-01—05 | 5 | NOT_RUN |
| ENV-01—06 | 6 | NOT_RUN |
| COST-01—10 | 10 | NOT_RUN |
| PRV-01—09 | 9 | NOT_RUN |
| JUD-01—07 | 7 | NOT_RUN |
| DATA-01—08 | 8 | NOT_RUN |
| SEC-01—09 | 9 | NOT_RUN |
| OPS-01—06 | 6 | NOT_RUN |
| INT-01—04 | 4 | NOT_RUN |

## 负责人集中决定的三组事项

1. **A0 隔离执行范围**。决定是否批准在上述本机和新运行目录执行 G1—G3 及离线 G5，批准安装锁定开源依赖、启动 loopback 服务，以及仅对两个全新测试库迁移与恢复。确认或调整2 vCPU、6 GiB、10 GiB资源上限。执行前仍需核验引擎许可与资源。验收后只停止本 run，删除或清卷另行批准。
2. **A1 候选路线与免费凭据条件**。选择一个已有账号可证明零新增费用的 answer/judge 组合，提供脱敏额度与硬停止元数据并确定批次。密钥后续通过安全渠道注入。当前可以暂缓 A1，A0 获批后的离线任务仍可推进。
3. **人工复核与最终采纳责任**。指定一次性标签/holdout复核人，确认原始证据建议30天的保留期，并在 G5 审阅结果后作出 A2。对外销售、商业数据权利与生产集成需要后续独立范围批准。

需要阶段批准的依据来自用户本次“完成 G0 后停止在审批节点”的要求，以及附件 §12 的 A0/A1/A2 门禁。此清单提供具体可审批对象，当前审批字段均保持空缺。
