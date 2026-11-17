# Provider 验证矩阵

| 路线 | 固定源码 | 本轮离线证据 | 真实实测 | 依赖与结论 |
|---|---|---|---|---|
| upstream stub | 原生 | 10次采样、stub判读、DB、REST/MCP和英文报告 | 不适用 | L1 管线可用，输出回显问题 |
| OpenAI 原生 | `openai-api`，Responses | 原版相关单测已随全套执行，完整P0合约矩阵未验收 | NOT_RUN | A1、API资格、精确模型、免费额度和硬停止缺失 |
| Gemini 原生 | 无专用 adapter | NOT_RUN | NOT_RUN | 待选路线后评估，原生Key不能直接确认可用 |
| Gemini 兼容接口 | 通用兼容协议不能直接覆盖 Responses | NOT_RUN | NOT_RUN | 需要独立适配与mock，不自动新增 |
| Qwen/OpenRouter | 有 gateway adapter | 原版目标解析/adapter单测已执行，P0配额与异常矩阵未完成 | NOT_RUN | gateway Key、模型可用性、免费条件和禁止回退待核实 |
| Qwen/DashScope | 无专用 adapter | NOT_RUN | NOT_RUN | 地域、workspace、endpoint、Key与免费硬停止待核实 |
| Jev/TypeSafe | 原生 judge 路线 | 使用stub，原版mock单测执行 | NOT_RUN | 独立费用与额度证据缺失 |
| Jev/OpenRouter | 原生 fallback 路线 | 离线策略拒绝真实judge和fallback选择 | NOT_RUN | 仅在明确选定并批准后可用 |
| 替代语义判读器 | 未实现 | 48条候选fixture，全部待人工复核 | NOT_RUN | 24 development、24 holdout，holdout候选14正10负，不能报告准确率 |

真实模型调用数为0。所有服务商权限、免费额度与商业数据权利保持待核实。A1 未批准前不注入真实 Key。G2 的通用预算守卫也必须先完成，当前离线模式只允许 stub。
