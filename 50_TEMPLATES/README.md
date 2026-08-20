# 50_TEMPLATES

可复用模板层。

启动 / 交接 / 报告模板见 [`../docs/SESSION_LIFECYCLE.md`](../docs/SESSION_LIFECYCLE.md) §3–§6，
及 [`../docs/AGENT_INTERFACE.md`](../docs/AGENT_INTERFACE.md) 的 Card / Seed / Completion 结构。

Workspace 初始化模板：`HUMAN_WORKSPACE_BOOTSTRAP.md`（首次搭建清单，规范源 `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`）。

模板索引：

| 模板 | 分层 | 场景 |
| --- | --- | --- |
| [`HUMAN_WORKSPACE_BOOTSTRAP.md`](HUMAN_WORKSPACE_BOOTSTRAP.md) | Human 层 | 新用户首次搭建 workspace |
| [`bootstrap_check_request.md`](bootstrap_check_request.md) | Human 层 | Human 请求 Agent 执行初始化状态检查（触发 `BOOTSTRAP_CHECK`） |
| [`pointer_response.md`](pointer_response.md) | Agent 层 | 指向 durable source 的回应；pointer 一律独立代码块 |
