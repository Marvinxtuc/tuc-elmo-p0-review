# P0 验收执行记录

本轮只使用A0允许的本机隔离范围。当前PASS 22、FAIL 0、NOT_RUN 42，共64项。历史失败日志保留，当前PASS采用后续已通过结果。

NOT_RUN表示该验收用例尚未完整执行，部分已有子检查证据另行说明。A1和人工标签等依赖的BLOCKED记录在dependency字段，未执行的真实测试继续为NOT_RUN。

| 阶段 | 本轮状态 |
|---|---|
| G1 | 离线基线成立，完整干净安装复现与故障矩阵未完成 |
| G2 | PARTIAL，deny-all离线边界有效，通用费用控制未完成 |
| G3 | PARTIAL，stub证据与报告可用，真实adapter合约和judge质量未完成 |
| G4 | BLOCKED，A1未批准，真实测试NOT_RUN |
| G5 | PARTIAL，恢复/读取/停止/ADR完成，故障和全新环境重放未完成 |

## 64项状态

| ID | 状态 | 实际范围或缺口 |
|---|---|---|
| SRC-01 | PASS | commit/tree/lockfile和镜像固定，15文件补丁保存并在冻结源码上apply检查通过 |
| SRC-02 | PASS | 根MIT许可保留，许可脚本退出0，安装包清单1582条，服务/模型权利未知项登记 |
| SRC-03 | PASS | 项目Node24.22.3/pnpm12.18.0，全局版本保持22.23.1/9.15.9，官网311文件一致 |
| SRC-04 | PASS | 有效规则与A0核对，迁移仅新测试库，冲突和路径纠正已登记 |
| SRC-05 | PASS | 冻结安装通过，供应链策略保留，audit发现7项中低危公告，真实Key准入关闭 |
| ENV-01 | PASS | 项目独立实例/卷/账号，loopback监听，环境白名单，最终进程独立HOME，secret0600 |
| ENV-02 | PASS | upstream stub复用，10条任务持久化和读取，页面与报告标明模拟，附隔离补丁 |
| ENV-03 | PASS | 两新库范围内迁移及重复执行成功，缺A0/越界库名负例子进程0次 |
| ENV-04 | PASS | lint/unit/build/五包typecheck/script通过，本地浏览器与API smoke通过，完整原版E2E未执行并披露 |
| ENV-05 | PASS | 最新离线Worker多次重启，最终源库10条观测、0计划、0待执行任务，取消遗留catch-up，验证为本轮有限窗口 |
| ENV-06 | PASS | 浏览器无站外请求，Web/Worker在OS层仅DB出站，模型和遥测无法公网发送 |
| COST-01 | NOT_RUN | 离线factory拒绝真实Provider与judge，OS端口拒绝已测。尚无完整审批/传输spy矩阵。 |
| COST-02 | NOT_RUN | 本项验收未执行。 |
| COST-03 | NOT_RUN | 本项验收未执行。 |
| COST-04 | NOT_RUN | 本项验收未执行。 |
| COST-05 | NOT_RUN | 本项验收未执行。 |
| COST-06 | NOT_RUN | Opportunities空缓存读取无写入已测，onboarding/CLI全部旁路负例尚未完成。 |
| COST-07 | NOT_RUN | 已关闭启动重判与周期任务，品牌别名/竞品/judge版本变更负例未执行。 |
| COST-08 | NOT_RUN | 只使用合成canary，真实双账号401/解密失败回退矩阵未完成。 |
| COST-09 | NOT_RUN | 本项验收未执行。 |
| COST-10 | NOT_RUN | 本项验收未执行。 |
| PRV-01 | NOT_RUN | 原版parser单测执行，P0未知model与收费默认完整矩阵未验收。 |
| PRV-02 | NOT_RUN | 原版OpenAI相关mock单测执行，P0完整Responses合约矩阵未验收。 |
| PRV-03 | NOT_RUN | 本项验收未执行。 |
| PRV-04 | NOT_RUN | 本项验收未执行。 |
| PRV-05 | NOT_RUN | 本项验收未执行。 |
| PRV-06 | NOT_RUN | 本项验收未执行。 |
| PRV-07 | NOT_RUN | 本项验收未执行。 |
| PRV-08 | NOT_RUN | 本项验收未执行。 |
| PRV-09 | NOT_RUN | 本项验收未执行。 |
| JUD-01 | PASS | provider和judge均UPSTREAM_STUB，页面横幅、API provider和导出/报告来源明确 |
| JUD-02 | NOT_RUN | 本项验收未执行。 |
| JUD-03 | NOT_RUN | 48条候选标签全部LABEL_REVIEW_PENDING，人工复核与合格判读器缺失。 |
| JUD-04 | NOT_RUN | 本项验收未执行。 |
| JUD-05 | NOT_RUN | 本项验收未执行。 |
| JUD-06 | NOT_RUN | 本项验收未执行。 |
| JUD-07 | NOT_RUN | 本项验收未执行。 |
| DATA-01 | PASS | 10条raw和规范化API响应分开保存，ID/时间/问题/模型可追溯，stub缺usage与请求ID如实标识 |
| DATA-02 | NOT_RUN | 本轮只有stub来源，混合模式和双judge版本未导入测试。 |
| DATA-03 | NOT_RUN | 10条stub已复算，失败/未判读/重试的完整分母fixture未验收。 |
| DATA-04 | NOT_RUN | 本项验收未执行。 |
| DATA-05 | NOT_RUN | 本项验收未执行。 |
| DATA-06 | NOT_RUN | 本项验收未执行。 |
| DATA-07 | PASS | 实际REST运行/详情读取、两页prompt和MCP读取通过，字段缺口披露 |
| DATA-08 | PASS | deny-egress下报告重复生成hash一致，含raw hash和观测ID，单字符修改检出 |
| SEC-01 | PASS | 随机合成secret精确值扫描覆盖日志/报告/提示/patch/build，未发现泄露，私有存储排除 |
| SEC-02 | NOT_RUN | 无token和无效token401已测，过期session负例未执行。 |
| SEC-03 | NOT_RUN | 仅内部single-org，低权限与对象ID矩阵未验收。 |
| SEC-04 | PASS | 实际MCP开放15只读工具，create/update和未知delete/run拒绝，数据不变 |
| SEC-05 | NOT_RUN | 本项验收未执行。 |
| SEC-06 | NOT_RUN | 本项验收未执行。 |
| SEC-07 | NOT_RUN | canary加密/正确错误密钥/恢复已测，错key的credential resolver环境回退负例未完成。 |
| SEC-08 | NOT_RUN | OS默认拒绝和两个loopback端口负例已测，IPv6/代理/重定向完整矩阵未执行。 |
| SEC-09 | PASS | 内部边界、7项依赖公告、宽测试role、权限/SSRF/费用缺口均已评估登记，真实Key仍关闭 |
| OPS-01 | NOT_RUN | 空闲Worker多次重启，处理中任务中断与去重未执行。 |
| OPS-02 | NOT_RUN | 本项验收未执行。 |
| OPS-03 | PASS | 空restore库恢复41张public表一致，canary正确/错误密钥与恢复验证，恢复队列遗留1条catch-up已披露，未启恢复Worker |
| OPS-04 | NOT_RUN | 本项验收未执行。 |
| OPS-05 | PASS | 本run应用、DB和VM两次幂等停止，端口/PID复核，文件和卷保留 |
| OPS-06 | NOT_RUN | OWNER_ACTIONS汇总已交付，四类情景自动生成的完整负例尚未执行。 |
| INT-01 | PASS | 官网311跟踪文件摘要、HEAD与原有dirty状态一致，本轮无生产操作，生产SHA未知 |
| INT-02 | PASS | root-path与single-org约束确认，内部服务端读取ADR已交付，无公网集成 |
| INT-03 | NOT_RUN | REST/MCP内部读取已示范，TUC服务端适配器未实现。 |
| INT-04 | NOT_RUN | 同环境报告重放和patch apply检查通过，第二套干净安装未执行。 |

逐项机器记录含证据引用，见 [test-results.jsonl](runs/20261117T013735Z-A0/test-results.jsonl)。

通过条目只覆盖登记的有限输入与观察窗口。完整原版E2E、多角色权限、SSRF/注入、预算竞态与真实API均有独立未完成项。
