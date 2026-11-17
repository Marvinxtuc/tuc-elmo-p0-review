该文件保存经原生通道自动读取的完整可见审核正文，线程标识已脱敏。审核针对代码提交 `2d21db26ed809d1884846106f50f4021c0b84b30`。文末 sandbox 附件尚未单独下载，正文已完整接收。

# TUC GEO — B1 独立只读审核结果

**request_id：`TUC-GEO-B1-REVIEW-20261117-01`**  
**origin_codex_thread_id：`[PRIVATE_CODEX_THREAD]`**

**审核结论：`B1_PARTIAL_REQUIRES_FIXES`。本轮整改成果可以保留，但新增 14 项不宜全部认定为 PASS；建议先完成 B1 补修，不进入 B2/B3，更不放行 A1。**

本次已通过 GitHub 读取 Issue #1、PR #2 元数据，以及固定提交中的关键实现和测试记录。PR 的 base/head 与请求一致：

| 项目 | 核对结果 |
|---|---|
| 固定审核基线 | `b287610a2576531a52fe6fe90bccf0fa70d80648` |
| 本次审核提交 | `2d21db26ed809d1884846106f50f4021c0b84b30` |
| PR #2 | Draft、未合并 |
| 本次执行依据 | 用户采用的 Issue #1 |
| 审核方式 | 静态源码审查＋已提交执行证据核对；没有重新运行仓库测试或启动服务 |

以上版本关系来自实际读取的 PR 元数据，不只是请求中的摘要。

## 一、验收计数裁决

**新增 14 项的建议改为：12 项有限范围 PASS、2 项 PARTIAL。**

需要退回补修或补证的是 **`COST-02`、`COST-09`**。

| 台账 | PASS | PARTIAL | NOT_RUN |
|---|---:|---:|---:|
| Issue #1 历史审核底账 | 17 | 5 | 42 |
| 执行者本次拟议 overlay | 31 | 5 | 28 |
| **本次独立审核建议 overlay** | **29** | **7** | **28** |

这次按照用户采用的 **Issue #1 底账**计算。原 A0 的 22/42、Issue 历史 17/5/42，以及本对话此前其他审核版本分别保留，**不回写、不覆盖，也不据此宣布此前意见已被撤销**。Issue 和本次 overlay 均明确采用独立复核层，而不是修改历史运行记录。

真实 Provider 请求继续保留**本轮记录为 0**的边界。守卫日志中的 **14 次本地 HTTP 命中是模拟服务请求**，不能算成真实模型请求；同时，这也不是服务商账单审计。**A1 仍为 `NOT_GRANTED`，真实批次准入仍为 `NO_GO`。**

---

## 二、按严重程度排列的发现

下文行号指固定提交中的源码行号。

### B1-R01｜高：急停没有持久化的全局停止状态，COST-09 不能完整通过

**文件：**

- `harness/request-guard.cjs:90–119`
- `harness/request-guard.cjs:171–204`
- `harness/request-guard.test.cjs:149–167`

当前 `emergencyStop()` 的实现是：查询**已经存在**的批准单，然后逐个调用 `halt()`。没有单独保存全局急停状态；新批准单注册和额度预留也没有检查这种状态。现有撤回／急停测试只验证**同一批准单**停止后，再换一个角色请求会被拒绝。

因此，从源码可以推导出以下缺口：

```text
登记批准单 A
→ emergencyStop()
→ 登记一个新 ID 的合法模拟批准单 B
→ B 仍可通过批准检查和额度预留
```

**这是静态推导，本次没有执行该反例。** 它不表示已经发生真实调用，而是说明当前实现更接近“停止现有批准单”，还不是完整的、持续生效的全局急停。

**影响：** 新批准 ID、新进程或重新初始化控制器，不能被默认视为解除急停。否则，急停后的后续任务仍存在被接纳的路径。

**最小修订：** 在 SQLite 中增加持久化的全局停止状态或停止版本号；注册批准、原子预留和发送前均检查。解除急停必须是明确的独立动作，留下批准依据和审计记录。补测同实例新批准 ID、新实例、另一个进程及并发登记，急停后假服务的新增命中必须为 **0**。

**裁决：`COST-09 → PARTIAL`。** 已有同批准单撤回、在途取消和 `UNKNOWN_CHARGE` 证据保留。

---

### B1-R02｜高：新停止脚本的进程归属检查退化，可能影响其他项目

**文件：`harness/b1-stop.py:12–23`**

当前脚本读取记录中的 PID，查询进程命令，只要命令包含以下任意通用字符串，就调用 `os.killpg(pid, SIGTERM)`：

```text
pnpm
src/index.ts
.output/server/index.mjs
```

没有同时核对精确工作区、进程启动时间、PGID 与本 run 的身份。

**影响：** 当原 PID 已结束并被复用时，另一个项目的 `pnpm` 进程可能满足匹配条件。这里没有证据表明本轮已经误杀进程，但该脚本不满足“只停止本项目资源”的可靠边界。

**最小修订：** 启动记录应绑定 PID、进程启动身份、规范化工作目录、可执行文件、PGID 和 run ID。停止前全部匹配；身份未知或不匹配时非零退出，不发送信号。用 mock／spy 测试 PID 复用、其他工作区、PGID 不一致和残留子进程，**不要实际终止无关进程来验证**。

最终停止记录显示五个端口无监听、无活动已登记进程，这个本轮结果可以保留；但它不能消除脚本的潜在归属风险，也不应因此追改 A0 的历史 OPS-05。

**裁决：新增的 B1 补修阻塞项，不另行改写历史测试计数。**

---

### B1-R03｜中：COST-02 的“共享额度”负例没有实际执行证据

**文件：**

- `harness/request-guard.test.cjs:75–87`
- `harness/request-guard.cjs:90–109`

该测试名称包含 `shared quota`，但测试体实际覆盖的是：缺少证据引用或凭据摘要、批准过期、额度过期、重复批准 ID。没有构造 `quota_scope` 为共享、未知或缺失的情况。

实现本身确实要求 `quota_scope === 'FIXTURE_EXCLUSIVE'`，所以**这里不是认定代码允许共享额度，而是验收证据没有覆盖宣称的分支**。

**最小修订：** 增加缺失、`SHARED`、`UNKNOWN` 三类本地 fixture，逐项断言明确拒绝、HTTP 命中增量为 0、attempt 预留数为 0。

**裁决：`COST-02 → PARTIAL`。** 原有过期、缺证据和重复 ID 子测试的通过结果保留。

另需继续区分：模拟批准单中的非空 `quota_evidence_ref`，不等于真实服务商的免费资格已经核验。

---

### B1-R04｜中：资源预算与官网全树核验仍是下一轮运行前置

**文件：`B1_GO_NO_GO.md`，“待复核与阻塞”部分。**

官网全树比对仍受 `docs/CODEX_MASTER_PROMPT_V2.md` 读取停滞影响；物理磁盘新增占用也没有完成归因。这两项保持 **PARTIAL** 是正确的。

三个 `du` 数值简单相加约为 **10.245 GiB**，但包含 APFS COW 共享块，**既不能据此判定物理新增已超限，也不能据此证明仍在 10 GiB 内**。

**最小修订：** 先明确已批准预算的计量口径，并完成可核验的占用归因；官网受阻文件则采用获准、可停止的读取方式补核。不能自动扩容、删除证据或清空卷来得到“通过”。

本次没有发现生产修改证据，但也不会把“未实施生产操作”的说明升级为“本轮全树一致性已重新证明”。

---

## 三、F-01—F-04 的整改评价

| Finding | 审核判断 | 可保留成果及限制 |
|---|---|---|
| **F-01** | **指定启动路径可有限接受** | 默认离线、完整 runtime 配置检查、强制预加载器和 OS 沙箱均已补上。八项启动检查实际包含一个正例和七个拒绝负例，不是八个负例。 |
| **F-02** | **PARTIAL** | 目标绑定、SQLite 原子预留、错误停批、进程失联保留额度已有代码和执行证据；全局急停及共享额度负例仍未闭合。 |
| **F-03** | **已测试离线路径可有限接受** | Web 前置写入拒绝、MCP 调用层防护、直接 Provider／研究包装，以及受限 Worker 都有对应实现。不能扩大成完整多主体权限通过。 |
| **F-04** | **指定恢复实例可有限接受** | 旧任务在注册 handler 前被隔离，pg-boss 自动迁移、监督和调度被关闭；恢复启动有实际隔离日志。但完整备份恢复验收仍不成立。 |

上述判断来自启动器、启动负例、Web／MCP 入口、Provider 包装和 Worker 队列控制的实际源码，不只是主报告描述。

还有两点需要特别保留：

**第一，之前 quality 阶段默认连接 5432 的问题已经有针对性整改。** 新补丁把质量阶段出口收紧到 17440，schema 生成改为核验冻结文件，不再走该阶段的数据库初始化。这项修正可以认可，但并不自动补齐全部 ENV-01／ENV-06 场景。

**第二，当前 runtime 只注册本批次的汇总处理器。** 这证明的是冻结实例的受控读取、任务隔离和模拟守卫能力，**不是证明完整的新建品牌、登录、新采样和真实 Provider 监测流程已经恢复可用**。不要为了恢复这些功能而直接切到 quality 模式。

---

## 四、新增 14 项的逐项裁决

| 用例 | 本次裁决 | 有限范围 |
|---|---|---|
| COST-01 | LIMITED_PASS | 未批准、真实目标和未受控入口的拒绝 |
| **COST-02** | **PARTIAL** | 补共享／未知／缺失额度范围负例 |
| COST-03 | LIMITED_PASS | 20 个独立进程、一份本地 SQLite、一个请求名额 |
| COST-04 | LIMITED_PASS | 当前 mock 协议的输入、输出和工具限制；不是实际模型 tokenizer 证明 |
| COST-05 | LIMITED_PASS | 本地故障、未知计费保留、重试反例及进程失联 |
| COST-06 | LIMITED_PASS | 已测试 Web、MCP、CLI、Provider、研究和 job 路径 |
| COST-07 | LIMITED_PASS | 合成配置变更、旧任务及当前恢复实例重启 |
| COST-08 | LIMITED_PASS | 合成账号绑定、401 停批、不可解密／读取失败不回退 |
| **COST-09** | **PARTIAL** | 同批准单停止成立，全局持续急停不完整 |
| PRV-01 | LIMITED_PASS | mock／offline 固定目标和配置准入 |
| PRV-05 | LIMITED_PASS | 本地 endpoint、region、workspace、凭据错配及 401／403 |
| PRV-06 | LIMITED_PASS | mock 禁用搜索／工具，真实路线当前拒绝 |
| SEC-07 | LIMITED_PASS | 合成凭据及 resolver 测试，结合 A0 恢复证据；不代表独立密钥灾备完成 |
| SEC-08 | LIMITED_PASS | 已记录的有限 IPv4、IPv6、代理、子进程、DNS 和重定向检查 |

并发证据确实记录了 **1 次成功、19 次 `REQUEST_LIMIT`、假服务实收 1 次**，不是仅根据日志标题认定。

凭据回退也确实增加了“不可读取”的状态及对应测试，不能再沿用上午“完全没有修复”的结论。不过，真实账号、真实 transport 和服务商费用限制仍未验证。

Issue 底账中的 **SRC-05、ENV-04、ENV-05、ENV-06、OPS-03** 五项 PARTIAL 继续保留；不能因为 B1 新增这些日志就自动升级。

---

## 五、测试与恢复证据的准确解释

我核到了 `lib-verified.log` 的 863 项通过摘要、`worker-complete.log` 的 17 项、`web-contract-1.log` 的 261 项及守卫日志的 9 项。**这些是提交中的执行记录，不是我重新运行后的结果。**

几个不能扩大解释的地方：

- **API 拒绝：** 六个实际 Web 请求记录为 403；这支持前置写入阻断，不等于所有业务 handler、所有身份和对象权限都经过完整验收。
- **出站：** 活跃 IPv4／IPv6 监听器的对照命中为 2，沙箱负例命中为 0，比上午的证据更强，但仍是有限矩阵，不是全量网络取证。
- **恢复：** Worker 日志可见 created、retry、active 合成任务被隔离，以及正常停止；不能把数据库中人工设置的 active 状态，等同于“真实执行中的任务被安全抢停”。后者仍属于处理中断测试。

恢复库保留合成竞品、测试任务和获准汇总变化，已经披露；**不要为追求“与原库完全一致”擅自删除它们**。同样，原始 10 条观测保持不变的核验记录，不等于完整密钥恢复、干净环境恢复或生产 RTO／RPO 已通过。

对于失败修正，空 `pnpm` 执行标记为 `INVALID_EXECUTION`、保留重建导致的 500 及后续重测，是正确的记录方式。不过，最终 Web 合约日志仍有 mock 环境中的 Better Auth `db.insert is not a function` 错误文本，需要明确分类；**“测试汇总通过”不能写成“日志没有错误”**，也不应反向把这条 mock 初始化错误直接认定为生产故障。

---

## 六、下一步最小补修与负责人待决定事项

**本审核是整改建议，不是新的实施授权。保持阶段停止状态和 Draft PR。**

| 顺序 | 最小工作 | 需要的决定或验收 |
|---|---|---|
| 1 | 核实资源计量口径与物理占用；处理受阻官网文件 | 负责人确认可用范围，不自动扩容或删证据 |
| 2 | 补全全局急停、修正停止进程身份检查、补 COST-02 负例 | 确认仅限 B1 补修；全部使用本地模拟，不扩展到 B2/B3 |
| 3 | 新 run 重测并追加证据 | 新批准 ID／新进程急停后零命中；无关进程零信号；共享额度零预留 |
| 4 | 回传新的固定提交、逐项结果及 overlay | 原 A0、原 B1 日志和失败记录不覆盖 |
| 5 | 再决定是否批准 B2/B3 | 不将本次局部通过视为下一阶段批准 |

负责人还需确认合成竞品和测试 job 的保留／清理安排；默认继续保留。人工金标准、F-07 完整扫描、依赖漏洞可达性和商业权利不因本次 B1 通过部分检查而豁免。

**A1 仍需真实 Provider 集成审查、准确的模型与 endpoint／region／凭据标识、免费额度和硬停止证据、实际 Token 边界、合格非模拟 judge，以及单独批准。不能仅把当前 `MOCK_FIXTURE` 改成真实 URL。**

---

## 七、实际读取范围与限制

本次重点读取了：

| 类别 | 文件或记录 |
|---|---|
| 依据与交付 | Issue #1、PR #2 元数据、`B1_GO_NO_GO.md`、`B1_TEST_RESULTS.json`、`B1_SOURCE_LOCK.json`、`B1_REVIEW_OVERLAY.md` |
| 守卫与启动 | `b1-runner.py`、`offline-preload.cjs`、`request-guard.cjs`、`request-guard.test.cjs`、`p0-startup-negative.py`、`b1-stop.py` |
| 应用控制 | constants、Provider 包装、OpenAI／结构化研究选段、凭据 store 及测试、Web/MCP server、Worker index／handlers／boss／p0-jobs |
| 运行证据 | 守卫日志、并发原始记录、启动结果、API/MCP 结果、出站监听证据、恢复核验与重启日志、停止记录及部分数据库快照 |

`patches/b1-offline.patch` 读取了前 190 行，并结合当前文件内容审查核心实现；**不是对 PR 全部 193 个变更文件的逐行全覆盖**。

整包快照获取未成功，因此**没有独立重算全部 manifest 和文件哈希**。数据库 before/after 的所有表与队列也未逐项独立复算。私有配置、实际 SQLite／数据库／dump、COW 依赖副本、Mac／VM／APFS 状态、官网受阻文件和生产控制面不在本次直接核验范围。`B1_SOURCE_LOCK.json` 中的摘要是已读取的声明，不冒充已全部重新计算。

补充交付：

**:chatgpt-content-reference{index="36"}[完整审核报告（MD）](sandbox:/mnt/data/TUC_GEO_B1_Independent_Review_2d21db2.md)**  
**:chatgpt-content-reference{index="37"}[机器可读裁决（JSON）](sandbox:/mnt/data/TUC_GEO_B1_Independent_Review_2d21db2.json)**

以下核心结果同时保留在正文，供原生通道直接收取，不依赖附件下载：

```json
{
  "request_id": "TUC-GEO-B1-REVIEW-20261117-01",
  "origin_codex_thread_id": "[PRIVATE_CODEX_THREAD]",
  "baseline_commit": "b287610a2576531a52fe6fe90bccf0fa70d80648",
  "reviewed_commit": "2d21db26ed809d1884846106f50f4021c0b84b30",
  "review_basis": "USER_ADOPTED_ISSUE_1",
  "decision": "B1_PARTIAL_REQUIRES_FIXES",
  "new_limited_pass_tests": [
    "COST-01",
    "COST-03",
    "COST-04",
    "COST-05",
    "COST-06",
    "COST-07",
    "COST-08",
    "PRV-01",
    "PRV-05",
    "PRV-06",
    "SEC-07",
    "SEC-08"
  ],
  "new_partial_tests": [
    "COST-02",
    "COST-09"
  ],
  "issue_1_based_overlay": {
    "PASS": 29,
    "PARTIAL": 7,
    "NOT_RUN": 28
  },
  "additional_blocker": "B1-R02_STOP_PROCESS_IDENTITY",
  "real_provider_calls": 0,
  "real_provider_calls_basis": "RECORDED_FINITE_OFFLINE_RUN_NOT_BILLING_AUDIT",
  "A1": "NOT_GRANTED",
  "A1_gate": "NO_GO",
  "B2_B3_authorized_by_this_review": false,
  "repository_tests_executed_by_reviewer": false,
  "repository_modified_by_reviewer": false,
  "full_repository_manifest_rehashed": false,
  "historical_records_preserved": true,
  "handoff_status": "REPLIED_AWAITING_CODEX_ACK"
}
```
