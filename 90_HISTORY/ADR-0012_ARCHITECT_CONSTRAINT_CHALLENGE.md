# ADR-0012 — Architect Constraint Challenge：反盲从但不扩 authority

- **Status:** Accepted direction / materialization in #106
- **Issue:** `youling/ai-use#106`
- **Decision level:** L2
- **Canonical mechanics owner:** `docs/AGENT_INTERFACE.md`

## Context

`CONTINUE_WITHIN_AUTHORITY` 解决了 Architect 不应把 Human prompt 当 scheduling clock，但真实执行仍出现另一类失败：历史 AI recommendation、临时 workaround、无 evidence hard cap、普通 repair->Human Gate 等 lower-layer constraint 被后续 Agent 机械继承，导致治理从“保护能力”变成“抑制能力”。

同时，允许 Architect 质疑规则又不能变成“我不喜欢规则所以自行绕过”。必须保留 Human/higher authority、security、secret、destructive、deploy、verification 等边界。

## Decision

Architect 负有 material constraint-quality duty：

```text
Detect
 -> identify constraint owner/currentness
 -> Amend | Challenge | Supersede
 -> continue unaffected authorized work
```

按 owner 分三类：

1. **Architect-owned / lower-layer AI-generated**：在 current authority 内、且不改变 Human goal/acceptance/material scope/safety boundary时直接 amend，durable 记录理由；
2. **Human / higher authority / global governance**：只能 challenge，不得绕过；受争议动作 fail-closed，其它 authorized work 继续；
3. **stale / superseded lower authority**：若 hierarchy 已证明 newer ruling supersede，采用 current rule并标记旧 gate stale，不重新制造 Human Gate。

Builder/Foreman 可以识别并 durable 报告 bad constraint，但默认不获得 governance override authority。

## Currentness-before-wait

进入 `HUMAN_REQUIRED / AWAITING_DECISION` 前必须 live-reconcile exact Work 最新 durable Human/Architect ruling。历史 gate 不能仅因旧文本还在就继续生效。

## No new lifecycle

`Constraint Challenge Packet` 只是 durable finding shape，不是 Work state、审批状态或新 scheduler。使用现有 Issue/Work/checkpoint/Review surface。

## Constitution / Interface split

`CONSTITUTION.md` 只保留稳定 invariant：Architect 不得静默盲从 material bad constraint；Challenge != Override；higher authority still wins。完整 trigger、owner classification、Builder boundary、finding shape 与 waiting/currentness mechanics 只由 Agent Interface 拥有。

## L0 decision

不修改 `AGENTS.md`。L0 已拥有 Human sovereignty、authority hierarchy、current durable truth、fail-closed 与 continuation 根不变量；缺少 Challenge mechanics 不会让 Agent 丧失识别 lower-layer authority/truth fault 的基础能力，因此不满足 Kernel residency test。

## Compatibility

本决策不改变 Human final authority、merge/deploy/destructive/security/secret/verification gate，不授予 Builder self-governance，不改变 Work/executor lifecycle。Historical constraints 仍保留 provenance；只有 current hierarchy/evidence 决定其是否继续适用。

## Counterexample

旧 Work Order 写 `360s timeout -> HUMAN_REQUIRED`。真实任务需要 20 分钟，且 current Architect拥有该 project-local Work rule；没有 Human requirement/provider hard limit/security理由。

正确处理：Architect 以 live evidence 直接把 arbitrary timeout 改为动态/任务级控制，durable 写明理由，继续 Work。若 `360s` 是 Human 当前明确要求，则只能 challenge，不能绕过。

## Consequences

收益：减少历史 AI 约束惯性、假 Human Gate 与无证据 hard cap；让 Architect 自治包含 constraint-quality responsibility，同时保持 higher authority。

代价：Architect 必须判断 materiality 与 owner；错误的 challenge 可能增加治理噪音，因此普通偏好/轻微低效不触发该机制。
