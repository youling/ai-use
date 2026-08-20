# Bootstrap Check Request — 启动核验请求

**分层**: Architect 层（派发前核验）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 派发前核对 durable source 是否足以让 fresh Agent 无歧义启动 |
| 谁使用 | Project Architect / Human（派发前自检，或委托核验） |
| 什么时候使用 | 每次派发 fresh Agent 前；或 Agent 报告无法从 pointer 启动、需要口头解释时 |
| 禁止用途 | 不是给执行 Agent 的 Work Order；不承载任务知识 / 验收标准；不替代 Seed 与 Durable Dispatch（三层分工见 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`） |

## 填空模板

```text
BOOTSTRAP CHECK REQUEST
---
task: youling/<repo>#<issue>@<step>
startup_mode: Fresh <Role>
source: <指向的 durable source>

逐项核验（每项给 yes / no / needs-fix + evidence pointer）：
1. Identity      —— 身份已知且无歧义
2. Entry Point   —— durable source 入口无歧义可启动
3. Authority     —— 角色在范围内有对应权限，不越权
4. Access        —— github-private / public 与 live metadata 一致
5. Active Mission—— 精确任务（Work Order）已确认
6. Boundary      —— owns / forbidden / acceptance 边界完整
7. State         —— durable / live state 已核对，与 seed 冲突时以 durable 为准

结论: <READY_TO_DISPATCH | FIX_DURABLE_SOURCE | BLOCKED>
```

## 规范源

- `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`（7 项固定检查项）
- `docs/AGENT_INTERFACE.md` §3.1（Work Order / dispatch 不完整时先修 durable source）