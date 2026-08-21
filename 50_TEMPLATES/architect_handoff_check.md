# Architect Handoff Check — 总架构师交接验收

**分层**: Agent 层（新总架构师接任前的接收侧验收）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 新总架构师接替旧总架构师时，验收交接是否完整、能否安全接管调度权 |
| 谁使用 | 接任的新总架构师（Global Architect / Project Architect 同构适用） |
| 什么时候使用 | 旧架构师输出 `READY_FOR_ARCHITECT_HANDOFF` 之后、新架构师正式接任调度之前 |
| 触发文本 | `ARCHITECT_HANDOFF_CHECK` |
| 禁止用途 | 不重做全量历史扫描；不在验收通过前派发新 Work Order；不替代 Fast Restore / Convergence |

## 在交接流程中的位置

| 阶段 | 模板 | 职责 |
| --- | --- | --- |
| 交出方收敛 | `docs/SESSION_LIFECYCLE.md` §6 Architect Convergence | 清理 OPEN WO、收敛决策、输出 `READY_FOR_ARCHITECT_HANDOFF` |
| 接收方恢复 | `docs/SESSION_LIFECYCLE.md` §5 Architect Fast Restore | 从 durable source 恢复现状 / 活跃图 / 冻结边界 |
| 接收方验收 | 本文件 | 确认交接完整，输出 `ARCHITECT_HANDOFF_ACCEPTED` 后才接任调度 |

本检查不重复定义 §5 / §6 的步骤，只做接收侧验收。

## 固定检查项

按序确认以下 6 项：

1. **Handoff Artifact** —— 旧架构师已留下 `READY_FOR_ARCHITECT_HANDOFF` 及精确 durable pointer（snapshot / decision index / active WO 清单）。
2. **Restore Done** —— 新架构师已按 §5 完成 Fast Restore 并产出现状快照；未完成则先恢复再验收。
3. **Active Graph** —— 快照中的活跃任务图与 live Issue 状态一致；冲突时以 live state 为准并指出过期项（规则见 §5 PHASE C）。
4. **Frozen Boundaries** —— 冻结边界与 shared contracts 已确认，无未决冲突。
5. **Authority Transfer** —— 接任已获 Human 确认；Human 拥有重大治理方向最终权威（`CONSTITUTION.md` §1）。
6. **Single Primary** —— 旧架构师会话已停止调度，不存在并行双主责（`CONSTITUTION.md` §4）。

## 触发文本

```text
ARCHITECT_HANDOFF_CHECK
```

## 填空模板

```text
ARCHITECT_HANDOFF_CHECK
---
control_plane: <control_plane_repo>
outgoing_pointer: <READY_FOR_ARCHITECT_HANDOFF durable pointer>
restore_output: <Fast Restore 产物 pointer>
```

## 完成后

验收通过后，由新 Architect 按 [`architect_handoff_transaction.md`](architect_handoff_transaction.md) 的 `ARCHITECT_HANDOFF_ACCEPTED` 规范格式**回写 durable source**（当前 authority issue）；本检查的验收结论填入其 `验证.handoff_check` 字段。仅存在于聊天的"我接任了"不算数。

任一检查项无法确认时报告 `BLOCKED`，保持 STOP：不施工、不改仓库、不派新 Work Order，先把问题交 Human 确认。

## 规范源

- `docs/SESSION_LIFECYCLE.md` §5（Fast Restore）/ §6（Convergence → `READY_FOR_ARCHITECT_HANDOFF`）
- `CONSTITUTION.md` §1（Human sovereignty）/ §4（同一时刻一个 primary）
- `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（接任后的启动状态验证仍按其执行）
- `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`（只存在聊天的确认不算数）
- `architect_handoff_transaction.md`（`ARCHITECT_HANDOFF_ACCEPTED` 规范格式）
