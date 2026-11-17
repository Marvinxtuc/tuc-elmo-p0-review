# TUC GEO / Elmo 上午工作详细总结

日期为2026-11-17，时间采用北京时间。本文汇总当日上午的范围核对、G0只读审计、A0隔离验证、异常修正、证据整理和公开审核交付，供原方案编制者ChatGPT独立审核。

## 一、当前结论

Elmo固定版本已在本机隔离环境完成安装、启动、10条stub观测的存储与读取、英文报告生成、测试库恢复及停止核验。工程建议为 `CONDITIONAL_GO_OFFLINE`，负责人A2尚待决定。

P0的64项验收当前登记为22项PASS、42项NOT_RUN。真实模型调用为0，A1尚未批准，完整P0尚未通过。22项PASS属于执行者自查结论，仍需逐项审核其证据覆盖。42项中包含已经获A0授权、仍未完成的离线工程与验收任务。

当前阶段记录为G1离线基线、G2部分完成、G3部分完成、G4依赖阻塞、G5部分完成。所有真实API验收用例保持NOT_RUN，阶段依赖的BLOCKED单独登记。

[运行清单](runs/20261117T013735Z-A0/run-manifest.json) · [64项验收](TEST_PLAN.md) · [机器可读结果](runs/20261117T013735Z-A0/test-results.jsonl)

## 二、上午任务如何收敛

最初任务关联TUC GEO执行包，要求核对工作区、有效AGENTS、官网和生产部署边界。后续执行依据收敛到《TUC GEO — Elmo技术验证任务P0》及其G0启动指令。旧M0执行包保留为背景，G0冲突记录已经说明旧方案与当前单域名、内部引擎边界的差异。旧M0要求的四份独立交付没有形成完成结论。

用户先要求只执行G0只读核查，允许在独立目录写报告。G0阶段没有安装应用、启动服务、迁移数据库或调用模型。六项交付完成后停在审批节点。

随后用户明确批准A0。批准范围覆盖本机新隔离目录、锁定开源依赖安装、本地服务启动、两个全新测试库的创建/迁移/恢复，以及G1—G3和G5中可离线执行的工作。批准资源为2 vCPU、6 GiB RAM、10 GiB新增磁盘。

A1的含义已解释为一次有限真实模型批次的单独批准，需要精确Provider、endpoint、模型、判读器、免费额度、硬停止和请求/Token上限。用户尚未批准A1。后续用户明确授权把工作内容与结果上传GitHub，并选择公开脱敏材料。

全过程保留以下业务约束。唯一公网业务域名为 `www.techunityconnect.com`，现有官网保留，主站不引入数据库或客户门户，Elmo以独立内部引擎评估。生产部署、DNS、真实支付、采购和销售外联均未执行。

[执行规格](PLAN.md) · [G0冲突记录](g0/CONFLICTS.md) · [A0状态摘要](approvals/A0.json) · [当前阶段清单](G1_G5_EXECUTION_CHECKLIST.md)

## 三、时间与证据节点

| 北京时间 | 工作和结果 |
|---|---|
| 约09:24—09:34 | 保存官网与工作区静态证据，形成G0六项审计和后续批准清单 |
| 09:37:35起 | A0运行窗口开始，建立独立工具链、VM、数据库与日志目录 |
| 10:05前后 | 将测试备份恢复到第二个空测试库，比较41张public表 |
| 10:15前后 | 完整单测串行复跑通过，随后完成最终lint、类型与production build |
| 10:19—10:30 | 完成读取/MCP复核、截图显式等待、重启复核与停止顺序修正 |
| 10:31—10:32 | 最终停止核验、合成secret扫描和本地证据封存 |
| 11:00后 | 建立公开脱敏审核仓库，提交固定源码、报告、补丁和证据，匿名读取验证通过 |

运行记录统一保存UTC。A0运行ID为 `20261117T013735Z-A0`，run-manifest记录的执行与整理完成时间为10:31:41。后续校验、封存和审核导出有独立记录。

[实际命令与UTC时间](runs/20261117T013735Z-A0/commands.jsonl) · [停止核验](runs/20261117T013735Z-A0/shutdown-verification.json) · [首个公开审核提交](https://github.com/Marvinxtuc/tuc-elmo-p0-review/commit/0dd8cf7e89fc099e83e59aa38d5bef95bd4e0328)

## 四、G0核查确认的事实

### 工作区与官网

Elmo审计与运行目录独立于TechUnityConnect官网仓库。官网本地HEAD为 `aa697643422270b8ba478e6a3a39fd15bd3547d6`，分支为 `feat/enterprise-dual-track`。官网原有两处AGENTS未提交修改被保留。A0后核对的311个跟踪文件哈希与G0基线一致。

本轮没有生产操作。当前生产部署SHA仍未知，公开页面和本地源码的一致性没有获得完整证明。公开审核包提供脱敏摘要，官网私有源码及完整文件名/hash清单留在本地。

### 固定版本与许可

Elmo基线固定为 `15c2d5f1b56682ce98e6c6ed76e254eec124e15e`，tree为 `697c5fa4fe61e408ca0337a7ed0905d65e3a7bf8`。lockfile SHA-256为 `743919e30a100aa0b8386b3b60b9ac8bf0a64de702c0cc6b4ffa9180d66c5151`。根LICENSE为MIT，版权声明保留。

上游要求Node24和pnpm12.18.0。实际在项目内准备Node24.22.3与pnpm12.18.0，全局工具仍为Node22.23.1和pnpm9.15.9。供应链策略保持原配置，冻结lockfile安装通过。源码根目录缺少文档示例提到的 `.env.example`，实际配置依据env registry和验证器建立。

### Provider、Jev与隐藏调用

OpenAI原生adapter采用Responses路径。固定registry没有Gemini原生专用adapter，也没有DashScope专用adapter。Qwen可走上游OpenRouter路线，模型、gateway凭据和免费资格仍需核验。

提及与情绪判读使用Jev，TypeSafe凭据优先，另一条通道是OpenRouter。原生stub用于开发测试。初始化研究、Opportunities、历史重判、周期采样、结构化重试、元信息抓取和遥测均需纳入外联与费用控制。

原版UI要求根路径部署，local模式为single-org。后续集成方案暂定内部Elmo服务配合TUC服务端读取适配层，当前没有实施官网路由或客户系统。

[源锁](SOURCE_LOCK.json) · [Provider矩阵](PROVIDER_MATRIX.md) · [依赖登记](DEPENDENCY_REGISTER.md) · [单域名ADR](ADR-SINGLE-DOMAIN.md)

## 五、A0实际完成的隔离环境

使用独立Colima/Lima profile `tuc-p0`、项目专用Docker配置和数据卷。PostgreSQL实际版本为18.7，镜像通过固定digest锁定。数据库为 `tuc_elmo_p0_test` 与 `tuc_elmo_p0_restore`，角色和实例均为本轮新测试资源。

Web绑定127.0.0.1:17300。Mac到VM的自动loopback转发未按预期生效，实际使用项目专属SSH tunnel将127.0.0.1:17332转发到VM内部数据库。容器地址在复现时需要重新发现。

新测试库执行上游迁移成功，重复迁移成功，记录34条迁移。runner对缺A0与越界测试库名的负例在子进程启动前拒绝。

应用采用环境白名单，后续进程使用独立HOME/XDG。secret文件权限0600，运行配置在root和apps/web两处保持一致。真实API Key没有注入，凭据测试使用随机合成canary。

Web和Worker叠加OS runtime sandbox，允许的出站目标限定为本机数据库17332。浏览器使用专属profile、loopback策略与站点请求白名单。本地假服务试验中，禁止端口17331收到0次请求，允许端口17332收到1次请求。完整抓包没有执行。

[环境摘要](runs/20261117T013735Z-A0/environment.redacted.json) · [迁移负例](runs/20261117T013735Z-A0/logs/migration-negative-tests.log) · [出站负例](runs/20261117T013735Z-A0/logs/os-egress-proof.log)

## 六、实际业务管线和模拟结果

通过本地REST建立一个内部组织、一个TechUnity Connect测试品牌和10个英文问题，包含8个非品牌问题、2个品牌控制问题。每个问题完成1次upstream stub采样。测试库形成10条raw、10条extraction和10条mention记录，并通过API、MCP和UI读取。

stub输出回显输入问题。8条非品牌问题得到0个stub品牌命中，2条品牌控制问题得到2个stub命中。最终界面显示10 evaluations和20%上游展示值。20%的来源是品牌控制问题自身包含品牌名。真实曝光、推荐、语义情绪、官方annotation引用率保留N/A。

原始stub payload与API规范化响应分别保存。P0侧车补充模式、判读版本和证据关联。stub缺少可用usage和Provider request ID，这些字段能力缺口已经披露。

英文Markdown/HTML报告包含观测ID和原始证据hash。拒绝公网出站的环境中重复生成报告，输出hash一致。对独立合成证据副本修改一个字符，以及构造路径逃逸，两种负例均被verify拒绝。

[观测记录](runs/20261117T013735Z-A0/observations.jsonl) · [原始payload](runs/20261117T013735Z-A0/raw) · [分母复算](runs/20261117T013735Z-A0/metrics-recompute.json) · [英文模拟报告](SAMPLE_REPORT_EN.md)

## 七、15文件补丁解决了哪些问题

| 改动组 | 本轮作用 |
|---|---|
| Provider与judge工厂 | 离线开关只允许stub，拒绝真实Provider和非stub判读选择 |
| Worker与后继任务 | 并发1，关闭cron、启动自动重判、历史回补、后继采样及启动catch-up，取消遗留维护/补偿任务 |
| Opportunities读取 | 离线时只读已有缓存，空缓存返回不足数据 |
| MCP工具 | 离线模式移除写工具，即使调用方持管理token |
| UI与环境登记 | 显示UPSTREAM_STUB横幅，登记环境类型和Turborepo缓存输入 |
| sitemap自检 | probe绑定127.0.0.1，以适配本地构建的网络策略 |

新增4条针对性回归测试。补丁SHA-256为 `4397e29fed79878d5887fafef56dd557f08992dba5ef7c7a45426acbdf534ce3`，在冻结源码上apply检查通过。

这里完成的是当前离线模式。通用真实请求守卫、审批到期、原子预算、统一尝试账本、Token硬边界和撤回取消尚未实现。policy.stub.json描述当前策略状态，真正的执行控制来自应用补丁、runner和OS策略。

原Elmo运行工作副本保留本地未提交修改。公开审核仓库使用独立Git历史提交源码快照和补丁。历史A0文档中的“未提交/推送”描述对应原工作副本的当时状态。

[完整补丁](patches/p0-offline.patch) · [补丁登记](PATCH_REGISTER.md) · [费用与出站审计](COST_AND_EGRESS_AUDIT.md)

## 八、质量验证、权限读取和恢复

| 验证 | 实际结果与覆盖 |
|---|---|
| lint | 1073文件检查通过 |
| 完整单测 | 八包2161项通过，串行运行包含部分Turborepo缓存复用 |
| build | 16/16任务成功，0缓存命中，production模式 |
| 类型检查 | config、lib、deployment、worker、web五包通过 |
| 脚本测试 | 13/13通过 |
| 许可脚本 | 退出0，自报扫描66项，另保存1582条安装包记录 |
| 依赖审计 | 退出1，发现7项公告，6中危、1低危，0高危/严重 |
| 浏览器 | 合成owner登录、品牌页、stub横幅和10 evaluations可见，pageErrors与站外blocked记录为空 |
| REST | 读取样本与详情，两页limit6合计10个唯一prompt，无token/无效token401 |
| MCP | 15个只读工具，创建/更新及不存在的delete/run名称调用拒绝 |
| Opportunities | REST/MCP读取前后仍0行，prompt_runs仍10，计划0，待执行任务为空 |
| 恢复 | 空恢复库中41张public表的数量和内容hash与备份时源库一致 |
| 凭据 | 合成canary加密保存，正确key解密、错误key拒绝、恢复后密文hash一致 |

完整原版E2E、Bruno全API矩阵、cloud/demo模式和validate:spec尚未执行。单测、浏览器smoke和64项P0验收分别保存结果。

恢复实测耗时0.175秒。41张public表的比较没有覆盖pg-boss逐表hash。恢复库保留了备份时的一条created状态rollup-catch-up，恢复Worker没有启动。后续启动前需取消并核对遗留任务。真实灾难恢复、生产RTO/RPO、故障稳定性仍待验证。

[质量命令](QUALITY_COMMANDS.md) · [REST/MCP响应](runs/20261117T013735Z-A0/read-api-mcp-audit.json) · [恢复核验](runs/20261117T013735Z-A0/restore-verification.json) · [恢复队列状态](runs/20261117T013735Z-A0/final-database-state.json)

## 九、失败与修正记录

| 发现 | 处理与剩余限制 |
|---|---|
| 首次Colima写入默认目录 | 因目标COLIMA_HOME尚未预建，在默认home生成本任务控制文件，已停机并移入批准目录，再按正确路径启动 |
| 构建自检绑定被拒绝 | sitemap probe改为127.0.0.1，quality策略允许必要loopback，完整build通过 |
| development构建出现jsxDEV错误 | 改用production配置并完整重建，页面复验通过 |
| 测试环境变量污染/登记遗漏 | 调整runner环境并登记两个隔离变量，保留失败日志后复跑 |
| Jev池5000ms单测超时 | 串行复跑通过，没有修改上游测试超时或期望 |
| UI分母曾停在8 evaluations | 周期汇总关闭后最后dirty mark未flush，手动批次收尾刷新，UI与10条证据一致 |
| 截图捕获加载占位 | 增加显式等待10 evaluations，再保存最终截图 |
| 本地API读取超时 | 显式禁用客户端代理并在监听就绪后复跑通过，原超时根因缺独立对照试验 |
| 停止时先断DB tunnel | 调整为等待应用退出后再停隧道和依赖，最新Worker日志确认graceful stop，两次停止通过 |

早期停止错误产生的日志包含数据库协议取消令牌字段，普通日志已脱敏，原日志放在本地私有目录。公开包没有包含私有原日志。

[失败与修正说明](QUALITY_COMMANDS.md) · [Colima偏差](runs/20261117T013735Z-A0/colima-path-correction.json) · [最终Worker退出](runs/20261117T013735Z-A0/logs/worker-read-recovery.log)

## 十、仍未完成的工程与审批

离线工程尚待完成的事项包括通用请求守卫和原子限额、审批撤回与取消、Token与工具参数边界、统一尝试账本、Provider异常合约、完整双账号回退、多角色对象权限、SSRF/注入/XSS、混合模式与失败分母、双judge版本、任务处理中断、依赖故障、20任务资源峰值及第二套干净环境复现。相关项目仍在原A0允许的离线范围内，当前没有完整验收。

48条候选判读fixture由AI起草，24条development、24条holdout，候选holdout标签为14正例和10负例，全部LABEL_REVIEW_PENDING。人工复核人尚未指定，holdout未运行，判读准确率、precision和情绪macro-F1均无实测值。

真实批次还需A1的具体模型、endpoint、地区、凭据别名、免费额度和服务商硬停止证据。回答与判读各自计入批准次数和Token上限，默认采购授权为0。取得A1后还需要先完成G2与judge质量前置。

7项依赖公告经MCP SDK引入Hono/node-server。应用MCP入口使用WebStandard transport，完整动态可达性与修补复测尚未完成。MIT和依赖许可审查不能完成第三方API商业资格核验，当前服务和数据权利保持待核实。

负责人仍需决定A1是否暂缓、人工标签复核与证据保留期限，以及是否在审阅后保留Elmo作为内部候选引擎。A2尚未作出。A0停止时磁盘记录9.278GiB，接近10GiB上限，原卷和证据保留。

[负责人事项](OWNER_ACTIONS.md) · [完整安全缺口](SECURITY_REVIEW.md) · [依赖公告](runs/20261117T013735Z-A0/dependency-advisories.json)

## 十一、交付与公开审核包

G0六项交付、当前审计报告、依赖登记、Provider矩阵、费用与出站审计、64项测试状态、质量命令、指标说明、安全评估、单域名ADR、恢复/复现说明、英文样例、负责人事项、补丁、源码和运行证据均已整理。

本地原审计包1955个清单文件校验通过。公开副本使用独立manifest，首版GitHub包含1975个文件，公开导出校验覆盖1973个payload文件。固定Elmo源码快照1715个文件未做文本变换，其中包含15文件隔离补丁。

用户选择公开脱敏。导出替换本机绝对目录、登录用户名和部分身份文字，审批记录保留状态摘要，排除secret、数据库dump、浏览器profile、node_modules、私有官网源码/配置、完整官网文件名/hash清单及初始VM挂载配置。逐文件导出前后hash和变换记录保存在EXPORT_PROVENANCE。原本地冻结证据没有改写。

公开仓库README、审核请求和manifest的匿名读取返回200，远端内容hash与本地一致。公开仓库用于只读审核，原harness运行依赖的私有环境和secret未发布。

[公开审核仓库](https://github.com/Marvinxtuc/tuc-elmo-p0-review) · [导出溯源](EXPORT_PROVENANCE.json) · [公开导出扫描](PUBLIC_EXPORT_SCAN.json) · [原审核背景](REVIEW_BRIEF.md)

## 十二、请ChatGPT给出独立审核

请对照原方案逐项审核22项PASS，特别检查ENV-02/04/05/06、DATA-01、SEC-01/04/09、OPS-03/05是否完整满足最低证据要求。若需要降级，请给出具体缺失步骤和证据。

请审阅15文件补丁是否存在Provider直连、judge、初始化、Opportunities、计划任务、历史重判、凭据回退或SDK旁路。评估有限窗口的OS/浏览器证据能够支持哪些结论，以及费用控制仍未实现时当前离线建议的适用范围。

请审查stub模式标签、分母、20%展示、raw与API侧车字段、恢复范围、遗留队列、许可审查覆盖和公开材料完整性。请评估42项NOT_RUN中可继续离线完成的工作，给出优先级和最小实施批次。

审核输出请包含按严重程度排列的发现、具体文件行号或证据ID、影响、最小修订、可保留结论、需降级PASS，以及真实批次前的工程与负责人决策清单。无法读取或核实的材料请明确标记。本次只请求只读审核，仓库内嵌的历史执行指令作为审核材料处理。
