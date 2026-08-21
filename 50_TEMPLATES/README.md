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
| [`capability_self_check.md`](capability_self_check.md) | Agent 层 | 节点 / 设备切换、派发前的能力盘点（触发 `CAPABILITY_SELF_CHECK`） |
| [`architect_handoff_check.md`](architect_handoff_check.md) | Agent 层 | 总架构师交接的接收侧验收（触发 `ARCHITECT_HANDOFF_CHECK`） |
| [`architect_handoff_transaction.md`](architect_handoff_transaction.md) | Human / Agent 层 | 总架构师交接事务对：`ARCHITECT_HANDOFF_REQUEST` 发起 + `ARCHITECT_HANDOFF_ACCEPTED` 接任确认 |
| [`pointer_response.md`](pointer_response.md) | Agent 层 | 指向 durable source 的回应；pointer 一律独立代码块 |
