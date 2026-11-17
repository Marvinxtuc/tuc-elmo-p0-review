# 本地 API 与 MCP 覆盖

路径来自固定源码的routes、API schema及MCP定义，实际调用目标固定为127.0.0.1:17300。

| 路径或动作 | 实测 |
|---|---|
| GET `/api/v1/brands` | 管理token可读，无token/无效token401 |
| GET `/api/v1/prompts?brandId=...` | 两页limit6，合计10个唯一prompt |
| GET `/api/v1/prompts/{id}/runs` | 每问题1条stub，共10条 |
| GET `/api/v1/prompts/{id}/runs/{runId}` | 保存规范化文本、provider、model、assessments与citations |
| GET `/api/v1/brands/{id}/opportunities` | 空缓存返回不足数据，无token/无效token401 |
| POST `/api/mcp` initialize、tools/list | 成功，列出15个只读工具 |
| MCP list_brands、get_opportunities | 成功读取 |
| MCP create_prompts、update_prompt | 不在已开放工具集，调用拒绝 |
| MCP delete_brand、run_prompt | 原固定工具集无此名称，调用拒绝 |
| MCP 无token/无效token | 401 |

读取前后prompt_runs为10、prompts为10、brand_opportunities为0、schedule为0、queued/active任务为空。HTTP/MCP原始脱敏结果保存在 `read-api-mcp-audit.json`。

当前API导出的模式标签由P0侧车添加，原生响应通过provider=stub识别。usage和Provider request ID在stub中无可用值。完整raw payload从测试库另行导出，与API规范化结果分别保留。

当前没有实现TUC服务端适配器，INT-03保持NOT_RUN。过期session、低权限对象范围和完整API/MCP负例仍未验收。未将管理token交给浏览器或配置为外部Codex连接。
