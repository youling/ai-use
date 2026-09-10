# 50_TEMPLATES

可复用模板层。

需要生成 Human/Agent interface artifact 时优先复用这里的现成模板，不为同一语义另造一套格式。

模板索引：

| 模板 | 分层 | 场景 |
| --- | --- | --- |
| [`DISPATCH_PAIR.md`](DISPATCH_PAIR.md) | Human / Agent 层 | 双词派单：人类派发卡 + Agent 种子词；含网页端、云端电脑、本地、本地+设备四类运行位置 |
| [`HUMAN_WORKSPACE_BOOTSTRAP.md`](HUMAN_WORKSPACE_BOOTSTRAP.md) | Human 层 | 新用户首次搭建 workspace |
| [`bootstrap_check_request.md`](bootstrap_check_request.md) | Human 层 | Human 请求 Agent 执行初始化状态检查（触发 `BOOTSTRAP_CHECK`） |
| [`capability_self_check.md`](capability_self_check.md) | Agent 层 | 节点 / 设备切换、派发前的能力盘点（触发 `CAPABILITY_SELF_CHECK`） |
| [`architect_handoff_check.md`](architect_handoff_check.md) | Agent 层 | 总架构师交接的接收侧验收（触发 `ARCHITECT_HANDOFF_CHECK`） |
| [`architect_handoff_transaction.md`](architect_handoff_transaction.md) | Human / Agent 层 | 总架构师交接事务对：`ARCHITECT_HANDOFF_REQUEST` 发起 + `ARCHITECT_HANDOFF_ACCEPTED` 接任确认 |
| [`pointer_response.md`](pointer_response.md) | Agent 层 | 指向 durable source 的回应；pointer 一律独立代码块 |

双词的 canonical interface 语义见 [`../docs/AGENT_INTERFACE.md`](../docs/AGENT_INTERFACE.md)；**可复制格式只在 `DISPATCH_PAIR.md` 维护**，避免“规范一套、架构师各写一套”。

Workspace 初始化规范源见 `../10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md`。
