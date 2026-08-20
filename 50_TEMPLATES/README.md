# 50_TEMPLATES

可复用交互模板层（Agent ↔ Human）。

模板默认属于 **L2 Targeted Reference**：仅在派发 / 启动 / 完成 / 对齐 / 授权场景按需取用，
不进入 Agent 默认启动上下文。模板是**填空格式**，规则以规范源为准，不重复制定协议。

## 模板索引

| 模板 | 分层 | 谁使用 | 场景 | 规范源 |
| --- | --- | --- | --- | --- |
| [`agent_seed.md`](agent_seed.md) | 派发者 → Agent | Human / Architect 填写；Agent 启动 | 派发执行 | `docs/AGENT_INTERFACE.md` §3 |
| [`bootstrap_check_request.md`](bootstrap_check_request.md) | Architect 层 | Architect / Human | 派发前核验 | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` |
| [`bootstrap_check_report.md`](bootstrap_check_report.md) | Agent 层 | 执行 Agent | 启动后回写 | `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` |
| [`human_dispatch_card.md`](human_dispatch_card.md) | Human 层 | Architect 填写；Human 决策 | 派发决策 | `docs/AGENT_INTERFACE.md` §2 |
| [`durable_dispatch.md`](durable_dispatch.md) | Architect 层 | Project Architect | 每次执行派发 | `docs/AGENT_INTERFACE.md` §1.1 |
| [`completion_report.md`](completion_report.md) | Agent 层 | Builder / Verifier / Research / Repair | 任务完成 | `docs/AGENT_INTERFACE.md` §4 |
| [`pointer_response.md`](pointer_response.md) | Agent 层 | 执行 Agent | 聊天携带应 durable 化的知识 | `docs/AGENT_INTERFACE.md` §3.1 |
| [`alignment_request.md`](alignment_request.md) | 双方协作 | Agent / Architect 请求；Human 确认 | 执行前对齐 | `CONSTITUTION.md` §1 |
| [`implementation_authorization.md`](implementation_authorization.md) | Human 层 | Human 授权 | 重大动作前 | `CONSTITUTION.md` §1 |

## 分工速查

- **Seed 只负责寻址**（`agent_seed`），不承载任务知识。
- **Durable Dispatch 承载任务知识**（`durable_dispatch`），seed 不复制。
- **Bootstrap Check 负责启动状态验证**（`bootstrap_check_request` / `bootstrap_check_report`）。
- **Human 拥有最终主权**：调度（`human_dispatch_card`）、对齐（`alignment_request`）、
  授权（`implementation_authorization`）都在 Human 层止步。

完整协议 / 历史模板见 `docs/AGENT_INTERFACE.md` 与 `docs/SESSION_LIFECYCLE.md` §3–§6。