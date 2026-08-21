# Architect Handoff Transaction — 总架构师交接事务

**分层**: Human / Agent 层（交接发起与接任确认的事务对）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 定义总架构师交接的两个事务端点：`ARCHITECT_HANDOFF_REQUEST`（发起）与 `ARCHITECT_HANDOFF_ACCEPTED`（接任确认），使交接作为可回写、可恢复的事务记录存在 |
| 谁使用 | 发起方：Human 或旧 Architect；确认方：新 Architect |
| 什么时候使用 | 决定更换总架构师、旧 Architect 会话退役、或跨节点 / 跨设备转移架构调度权时 |
| 禁止用途 | 不表达所有权转移；不修改生命周期系统；不修改 Workspace Schema；不引入数据库 |

## 在 Handoff 流程中的位置

完整 Agent Handoff 流程见 `START_HERE.md`：

1. Capability Self Check —— `capability_self_check.md`
2. Handoff Request —— 本文件 `ARCHITECT_HANDOFF_REQUEST`
3. Handoff Check —— `architect_handoff_check.md`
4. Handoff Accepted —— 本文件 `ARCHITECT_HANDOFF_ACCEPTED`
5. Bootstrap Check —— `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`
6. Resume Work

REQUEST 与 ACCEPTED 必须成对回写 durable source；只有 REQUEST 而 ACCEPTED 未回写时，调度权不视为已转移。

## ARCHITECT_HANDOFF_REQUEST

用途：Human 或旧 Architect 发起交接。

```yaml
版本:

事件:
  类型: ARCHITECT_HANDOFF_REQUEST


发起方:
  身份:
  pointer:


接收方:
  身份:


交接范围:
  role:
  workspace:
  authority_scope:


依据:
  durable_sources:


生效条件:


备注:
```

要求：

- 不能表达："所有权转移"。
- 只表达："AI 工作角色调度权转移"。
- `authority_scope` 只描述 AI 工作角色调度范围，不描述 GitHub 权限、组织权限或商业决策权限。
- `依据.durable_sources` 必须引用可验证的 durable pointer（如 Human 确认评论、当前 authority issue），不以聊天记忆为依据。

## ARCHITECT_HANDOFF_ACCEPTED

定义：由新 Architect 输出，作为接任确认的 durable 记录。`验证` 字段只引用两项前置检查的报告 pointer，不在本文件重复执行或重定义检查。

```yaml
版本:

事件:
  类型: ARCHITECT_HANDOFF_ACCEPTED


接收方:


验证:


  capability_check:
  handoff_check:


恢复来源:


当前状态:


限制:


阻塞:


时间:
```

字段约束：

- `验证.capability_check` —— 指向 `CAPABILITY_SELF_CHECK_REPORT` 的 durable pointer；
- `验证.handoff_check` —— 指向 Handoff Check（`architect_handoff_check.md`）验收结论的 durable pointer；
- `恢复来源` —— Fast Restore 所用 durable source（`docs/SESSION_LIFECYCLE.md` §5）；
- 任一验证缺失时不得输出 ACCEPTED，报告 `BLOCKED`。

## Capability != Authority

能力发现与交接本身都不产生治理权（`AGENTS.md` Authority）；Human 拥有最终主权（`CONSTITUTION.md` §1）。

交接不会赋予：

- GitHub owner 权限
- 人类组织权限
- 商业决策权限

只赋予：

- AI 工作流架构协调职责。

## 回写要求

REQUEST 与 ACCEPTED 均必须回写 durable source（当前 authority issue / control plane）。仅存在于聊天的交接不算数（`30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`）。

## 规范源

- `50_TEMPLATES/capability_self_check.md`（流程步骤 1）
- `50_TEMPLATES/architect_handoff_check.md`（流程步骤 3）
- `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（流程步骤 5）
- `docs/SESSION_LIFECYCLE.md` §5 / §6（Fast Restore / Convergence）
- `CONSTITUTION.md` §1 / §4（Human sovereignty / 单一 primary）
