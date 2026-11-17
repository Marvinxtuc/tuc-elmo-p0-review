# 指标映射与分母

本轮10条观测的 observation_mode 与 judge_mode 都为 UPSTREAM_STUB。判读版本为 stub+request-1。原始stub回显每条问题，8条非品牌问题得到0个stub命中，2条品牌控制问题得到2个stub命中。

| 项目 | 本轮口径 |
|---|---|
| 计划 / 保存 | 10 /10 |
| stub处理 / 保存 | 10 /10 |
| 合格真实判读数 J | 0，尚无非模拟判读器验收 |
| 非品牌词面stub命中 | 0 /8，仅fixture计数 |
| 品牌控制词面stub命中 | 2 /2，品牌名来自问题回显 |
| 实际API曝光、明确推荐、语义情绪 | N/A |
| 官方annotation引用率 | N/A，stub未提供该能力 |

上游界面在所有10条上显示AI Visibility 20%、Share of Voice 100%、Sentiment 50、Position 1.0。这些是stub数据上的上游展示值。英文报告显著标注来源，并把真实业务指标保留为N/A。

关闭自动刷新曾导致UI暂时显示8 evaluations和13%。批次完成后显式发送一次本地refresh-rollups，最终截图和REST记录均为10 evaluations。旧截图及其JSON另存，用于保留分母问题的历史。

未来真实指标必须按模式、Provider、endpoint/model、search配置、问题集和judge版本分组。采样完成率为S/N，合格判读完成率为J/S，分母0时N/A。失败、截断、被拒绝和未判读分别列明排除原因。官方annotation与普通文本URL分别保存。

本轮复算覆盖10条stub固定输入。含失败、未判读、重试、混合来源、恶意URL与双judge版本的完整验收仍为NOT_RUN。
