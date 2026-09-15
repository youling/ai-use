# 上下文模式种子词（Context Mode Seed）

**版本：0.1.0**

本文件是 Context Lifecycle v0.1 的 vendor-neutral 可复制 contract，可直接被 deployment / control-plane adapter 消费。规范语义的 canonical home 是 [`../docs/AGENT_INTERFACE.md`](../docs/AGENT_INTERFACE.md)（continuation / `PREMATURE_YIELD` / completion boundary）与 [`../docs/SESSION_LIFECYCLE.md`](../docs/SESSION_LIFECYCLE.md)（Work Context lifecycle / `durable-before-fragile` / fresh 触发）。若本模板与 canonical 冲突，以 canonical 为准并修本模板 drift。

`DISPATCH_PAIR.md` 仍是 Human Dispatch Card + Agent Seed 的唯一日常入口；本文件只在需要表达 mode / context / independence / delegation 时被 `DISPATCH_PAIR.md` 以 targeted pointer 引用，不替代工单地址与 affinity 行。

## 正交语义（machine seam）

Canonical core 只表达以下正交维度，不设扁平单枚举：

```text
context_policy:
  WARM_RESUME | FRESH_CONTEXT | COMPACT_SAME_CONTEXT | SIDE_CONTEXT | FORK_CONTEXT

mode:
  PLAN | BUILD | REPAIR | SELF_REVIEW | VERIFY | INVESTIGATE

continuation:
  TO_DURABLE_BOUNDARY | ONE_SHOT

independence:
  REQUIRED | NOT_REQUIRED

delegation:
  INLINE_PRIMARY | SUBAGENT

parallelism:
  NONE | READ_ONLY | ISOLATED_WRITE
```

`FRESH_VERIFY`、`普通修复`、`side research` 是 Human-facing convenience label，只是上述维度的组合示例，不是 machine 枚举：

```text
FRESH_VERIFY
= context_policy:FRESH_CONTEXT
+ mode:VERIFY
+ independence:REQUIRED

普通修复
= context_policy:WARM_RESUME
+ mode:REPAIR
+ continuation:TO_DURABLE_BOUNDARY

side research
= context_policy:SIDE_CONTEXT
+ mode:INVESTIGATE
```

可复制的最小机器缝合示例（字段名稳定，值取自上表；无值即省略）：

```text
context_policy: WARM_RESUME
mode: REPAIR
continuation: TO_DURABLE_BOUNDARY
independence: NOT_REQUIRED
delegation: INLINE_PRIMARY
parallelism: NONE
```

## Human-facing 位置

日常 Seed 仍按 `DISPATCH_PAIR.md` 写工单地址与 `节点 / 项目 / 情景 / 上下文参考`。只有当“为什么这次被唤醒 / 当前执行模式”无歧义需要时，才追加一行可选语义意图：

```text
执行意图：<mode/context intent>；按 current durable acceptance 持续到对应 boundary
```

它只说明唤醒原因与模式亲和，不得复制 tests、scope、权限、安全 gate、完成 stop 条件。没有歧义时整行省略。`上下文参考` 与本文件的 `context_policy` 都是 affinity hint，不产生 authority，不声明 currentness，不得覆盖 current GitHub durable truth。

```text
私仓工单：youling/<repo>#<issue>[/<dispatch-comment>]
项目：<project>
情景：<lineage / context intent>
上下文参考：<optional pointers>
执行意图：<optional; semantic intent only>
```

## 同 lineage 默认与 fresh 触发（可复制判据）

- 同一 implementation lineage 内默认 `WARM_RESUME`：`PLAN -> BUILD -> TEST -> REPAIR -> SELF_REVIEW -> REPAIR` 优先复用 current owned warm context；明确 review finding 回流后优先由原 executor 修。
- Fresh context 默认主要用于：independent verification、security / permission boundary review、high-risk final acceptance、adversarial review、context contamination / unrelated new work、true parallel work。
- 恢复路径同样是 fresh 触发：warm context missing / invalid（`CONTEXT_UNAVAILABLE`）时，从 durable checkpoint / current state 做 `FRESH_CONTEXT` 重建，不伪造 active session。
- 不得因 warm 方便取消 current contract 已要求的 fresh independent verification。
- `DEFAULT_SAME_LINEAGE = WARM_RESUME`

## PREMATURE_YIELD（可执行判据）

```text
acceptance_not_met
AND no_real_stop_gate
AND legal_next_action_exists
AND executor_yielded
=> PREMATURE_YIELD
```

至少包括以下 canonical classes（可扩展，但扩展 class 必须 fail-closed，且不得把 ordinary repair input 升格为 Human gate）：

`REAL_HUMAN_GATE | AUTHORITY_BLOCKED | SECURITY_OR_DESTRUCTIVE_GATE | DEPENDENCY_BLOCKED | UNRECOVERABLE_EXECUTOR_FAILURE`

普通 test / lint / typecheck / red CI、已知 review finding、可在当前 scope 内修复的代码错误属于 repair input，不是 Human interrupt。executor 自述 `done / completed` 只是 observation，不能覆盖 deterministic finish / review / evidence gates。

## Completion boundary（指针式）

不新造第二套 acceptance。本模板不复制 acceptance 正文；executor goal / stop predicate 必须从 current durable Work Order acceptance 编译：只有本任务 acceptance 要求的 deterministic checks / currentness / commit-push / exact-head / evidence 均满足，才可 `COMPLETION_REACHED`。不适用项不得凭模板被强制创造（例如无需 commit 的任务不因本模板而必须 commit）。

## Durable before fragile（检查点触发）

Warm context 是 working memory / cache，不是 truth。以下风险前必须优先建立 current durable checkpoint：context compaction、provider / backend handoff、session termination / replacement、workspace ownership transition、long-running executor crash 风险。

```text
Warm while useful; durable before fragile; fresh when independence matters.
```

## 安全与独立性冻结

- `FORK_CONTEXT != FRESH_CONTEXT`：fork 继承认知与上下文，不能满足 independence。
- `SELF_REVIEW != FRESH_VERIFY`。
- `COMPACT_SAME_CONTEXT` 前执行 durable-before-fragile checkpoint；压缩摘要不能覆盖 GitHub current truth。
- `SIDE_CONTEXT` / subagent 调研结果可回流，但不转移 Work ownership / authority。
- provider action 不能产生 authority；Work Coordinate + current durable dispatch 才重新锚定任务。
- provider 不支持目标动作时 fail closed，回退到可证明等价的 adapter 行为，不从命令名推导 capability。
- `PROVIDER_COMMAND_IS_AUTHORITY = NO`
- `SEED_SECOND_SSOT = NO`
- `FORK_COUNTS_AS_FRESH_VERIFY = NO`

## Delegation 缝合（subagent）

Subagent 是隔离与并行机制，不是 authority 来源，也不是默认 mode 切换方式：

```text
MAIN_CONTEXT_OWNS_WORK = YES
SUBAGENT_OWNS_WORK = NO（除非显式委托 isolated child work coordinate / workspace）
SUBAGENT_RESULT = evidence/summary/pointer（不是 canonical acceptance truth）
SUBAGENT_IS_FRESH_VERIFY_BY_DEFAULT = NO
MODE_CHANGE != SPAWN_SUBAGENT
SAME_LINEAGE_REPAIR = WARM_PRIMARY_BY_DEFAULT
NESTED_SUBAGENT_DEFAULT = DENY
PRIMARY_CONTEXT_REMAINS_ORCHESTRATOR = YES
```

优先委托：repo / code exploration、外部与上游文档调研、独立 test / log triage、有界 security / quality / race / flake 审计 lane、大证据分区、独立问题的并行只读验证。

不因以下原因 spawn：mode 由 `BUILD` 切到 `REPAIR / SELF_REVIEW`、已知 Architect finding 回流、单测变红且同一 executor 可合法修、Human 说“继续”。

父 / 子 contract：父（main）保持 orchestrator 与最终 synthesizer；每个子单元只带 `work pointer + narrow question + allowed tools/write scope + expected return shape + stop condition`；子返回有界结果与 durable pointer，不向父 context 倾倒原始 transcript / log；子写必须有隔离 branch / worktree / generation ownership 与 exact-head handoff 后再合成；两个子不得共享可变 workspace，除非有显式冲突安全机制；子失败不自动成为 Human gate。

并行策略：`READ_ONLY` 优先；`ISOLATED_WRITE` 才允许并行写，否则拒绝。`PARALLEL_WRITES = ISOLATED_WORKSPACE_OR_DENY`。

## Provider 适配示例（Informative / Non-normative / freshness-marked）

本节不是 canonical truth，只是 2026-09-15 复核的 provider 观察，机器映射由 deployment / control-plane adapter 持有并自行重验。治理不得依赖命令名。

- ChatGPT / Codex（2026-09-15 复核）：slash commands 确认存在 `/goal`、`/plan`、`/review`、`/compact`、`/fork`、`/side`、`/status`、`/task`；当时官方列表没有 `/new`。`/goal` 是 persistent objective，goal resume 走 goal progress UI。`/fork` 明确复制当前 local chat 到新 chat / worktree，因此不得映射为 independent fresh verification。
- OpenCode（2026-09-15 复核）：TUI 确认 `/new` 建 session；`/sessions` 别名 `/resume`、`/continue`；`/compact` 别名 `/summarize`。Build / Plan 是同 session 可切换的 primary agents；项目级 `.opencode/commands/` 可定义 custom command。当前 command 文档字段为 `subagent: true|false`；Plan 默认对 edits / bash 是 `ask` 权限，若 `SELF_REVIEW` contract 要求 no mutation，adapter 必须显式配置 permission / agent contract，不能只靠“切到 Plan”推导。
- Subagent（2026-09-15 复核，来源见下）：ChatGPT Work / Codex 支持把独立工作委托为 subagent，CLI 以 `/agent` 查看与切换 agent threads，官方建议从读多并行（exploration / testing / triage）起步，并行写需处理冲突成本，父合成子结果；OpenCode 区分 primary agents 与 subagents，subagent 跑在 child session，可自动或手动触发，`subagent_depth` 可配且当前默认单层，与 `NESTED_SUBAGENT_DEFAULT = DENY` 对齐。内置 agent 名在不同文档面有差异，不得进入 canonical。

来源（仅 subagent 机制观察，slash 命令面以当日复核为准，不固化 URL 为 truth）：

- `https://learn.chatgpt.com/docs/agent-configuration/subagents`
- `https://learn.chatgpt.com/guides/best-practices`
- `https://opencode.ai/docs/agents`
- `https://opencode.ai/v2/docs/agents`
- `https://opencode.ai/v2/docs/commands`
- `https://dev.opencode.ai/docs/config/`

## 使用边界

- 本模板不承载 scope / acceptance / stop 正文；那是 current durable Work Order / dispatch 的职责。
- `delegation: SUBAGENT` 不产生 authority，不免除 exact-head / currentness 重读与独立性举证。
- 不引入 scheduler、task DB、provider marketplace、Bot、session recorder、prompt registry 或新状态源。
- provider 不支持目标动作时 fail closed；不得从命令名推导 capability。
