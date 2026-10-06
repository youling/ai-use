# Agent Interface — Canonical L2 Reference

**Classification: L2 Targeted Reference.** Read when dispatching/executing Agent work, choosing Architect execution mode, advancing an authorized program, or producing/reviewing Human/Agent interface artifacts.

**Protocol Version: 2.10.0**

本文是 **execution / dispatch / continuation interface** 的 canonical home。公共 `ai-use` 不绑定特定 owner/repo、私有 control-plane 名称或账号。[Recovery & Handoff](../30_PROTOCOLS/RECOVERY_HANDOFF.md) 拥有 recovery、Work Context、正交 context/mode 与 independence/delegation 语义；[CONTEXT_MODE_SEED](../50_TEMPLATES/CONTEXT_MODE_SEED.md) 只给形态。本文保留 continuation、`PREMATURE_YIELD` 与完成边界。

---

## 1. Execution & Dispatch

执行先区分 `DIRECT | DELEGATE`：

- `DIRECT`：Project/Global Architect 在 current durable authority、pre-existing scope/acceptance 与本节 eligibility 同时满足时自己施工；不为了角色仪式制造 Builder dispatch / Agent Seed。
- `DELEGATE`：由 durable Work Order + current Architect dispatch 启动可替换 executor。Human 可以手工 transport Seed，也可以使用 current durable authority 允许的 execution transport；Human copy/paste 不是普通 executor 的治理必经节点。

`DIRECT | DELEGATE` 是执行方式，不产生 authority，也不改变 merge / deploy / destructive / production / irreversible authority。

### 1.0 Common execution hygiene

以下规则适用于 **所有 mutation executor**，不只 DIRECT Architect：

- 先理解再修改，只处理 current authorized scope；发现额外问题时记录 Follow-up / debt，不顺手扩大 task 或做无明确收益的重构。
- 写任务使用**物理隔离的 mutable workspace**：worktree、independent clone、container 或独立目录均可；不同 branch 共享同一 working tree **不算隔离**。
- task-private temporary files 保持在 task workspace 内；形成 remote-recoverable durable state 后可按 current authority 清理该 task workspace。
- 发现疑似他人/用户未提交现场，不 `reset` / `clean` / `stash` / overwrite / delete；ownership 不清楚时停止并报告。
- workspace isolation 只是 execution safety，不产生 repository/governance authority。

L0 只保留“不越 scope、不破坏不明确 ownership”的 root invariant；上述 mechanics 只在本接口维护。

### 1.1 Durable Dispatch

每次 Agent-facing delegated execution **必须**有 current `ARCHITECT_*_DISPATCH`（或等价 current durable dispatch）。Durable Work Order + dispatch 携带任务知识；Minimal Seed / transport payload 只寻址。

字段按任务需要填写，不强制统一全集。常见结构：

```text
ARCHITECT_EXECUTOR_DISPATCH
---
work_coordinate: `<owner>/<repo>#<issue>@<step>`
role: `<Builder | Verifier | Research | Repair | Release>`
startup_mode: `<Fresh Builder | Warm Resume | Fresh Verifier | ...>`
access: `github-private | github-public`
status: `DISPATCHED`
```

具体机器 gate 由 deployment-local control-plane contract 定义。公共 contract 不假设 control plane 一定叫 `ai-hub`，也不指向上游维护者 private repo。

Delegated execution 在 `EXECUTION_ALLOWED` 后进入统一的 attempt lifecycle：

```text
DISPATCH -> AGENT_CLAIMED -> [PROGRESS_CHECKPOINT]* -> AGENT_TERMINAL_RESULT
```

事件的 durable shape 由 [Durable Trace Principle](../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md#delegated-execution-attempt-events) 拥有；本接口只拥有这些事件与 execution/completion 的关系。

### 1.2 Bootstrap relationship

Seed 只提供 address。执行前按 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` 的 canonical Ordered Bootstrap：

`BOOT-1 ADDRESS -> BOOT-2 APPLICABLE RULES -> BOOT-3 EXECUTION GATE -> EXECUTION_ALLOWED`。

本文件**不复制** Bootstrap 的 access fallback、anonymous-404、role-bootstrap、durable bootstrap writeback 等 mechanics。需要这些行为时以 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` 为唯一 canonical home。

关键接口边界只有两条：

- BOOT-1 address / access metadata 不产生 authority，也不提前适用任务正文；
- `BOOT-2A` 的第一份 normative rules read 是 current governance repo `AGENTS.md`，之后才适用 target-local/current-work rules。

### 1.3 DIRECT / DELEGATE boundary

Architect 选择执行模式前必须以 current durable authority 与 **施工前已存在**的 scope/acceptance 为准。

`DIRECT` 只有在以下条件同时成立时才 eligible：

1. current durable Architect authority 覆盖目标 repo / governance scope；
2. requirement / scope / acceptance 在施工前已由 Human、更高/current durable authority、Work Order 或稳定 contract 给定，Architect 不得施工后自造 acceptance 再自证；
3. 改动低风险、局部、可逆，不含未授权高影响外部副作用；
4. 有确定性验证路径（tests / lint / typecheck / diff / readback / contract checks 等）；
5. live currentness、ownership 与 writable workspace 无冲突，并满足 §1.0 common execution hygiene；
6. 不存在 `DELEGATE_REQUIRED`、Human Hold、Incident、security/permission conflict 或其它 current fail-closed gate。

Eligible 时可按：

`live validate -> isolated mutation -> deterministic checks -> durable implementation report / PR exact head -> required Review gate -> merge under current merge authority`

`DIRECT` 不自动创建 Verifier，也不自动免除 independent evidence / Human gate。current risk/contract 已要求独立 Review/Verifier/Human gate 时必须保留；没有要求时不因 Architect 亲自施工而机械增加仪式。

以下情况优先或必须 `DELEGATE`：

- 大量/长时间施工；
- 探索性实现或 acceptance 未冻结；
- 需要独立实现者降低 confirmation bias；
- 并发、专门工具/环境、长运行 executor 更合适；
- current risk/contract 明确要求 separation of duties。

### 1.4 Architect continuous advancement

Project Architect / Global Architect 默认 `CONTINUE_WITHIN_AUTHORITY`。**Human message is not the scheduling clock**；没有新 prompt 本身不构成 blocker。

同一 current authorized objective/program 内，只要 next step 仍被 authority、scope/acceptance、dependency 与 risk gates 覆盖，Architect 应继续普通行政与施工编排，包括：

- live reconcile；
- 必要时完成 Architect Reconnaissance；
- materialize Work Graph / Work Order / dispatch；
- 收到 delegated delivery 后主动 Review；
- Repair / re-dispatch；
- ordinary exact-head merge（仅在 current merge authority/gates 满足时）；
- dependency activation；
- lifecycle convergence / next READY work。

Continuous advancement **不产生 authority**。以下情况必须停 Human / higher authority / exact blocker，而不是为了“持续推进”绕过：

- 新增/改变 Human goal、产品取舍、priority、acceptance；
- material scope expansion 或未覆盖 cross-project authority；
- Human Hold / required Human input / secret / physical-device action；
- production / destructive / irreversible authority gap；
- unresolved BLOCKER / Incident / security-permission conflict / `HEAD_MOVED` / authority ambiguity；
- multiple mutually exclusive READY choices 且 durable priority 不足；
- no READY work 或 explicit program stop condition 已达。

Fresh/takeover Architect 不得因为 historical playbook 写着“先给 Human 确认”就机械等待；以 current L0 + Bootstrap + 本节 continuation 为准。


### 1.4.1 Adaptive reasoning effort

Reasoning effort 是**可升降的运行时计算 / 搜索深度**，不是角色 authority、truth、correctness proof 或永久风险姿态。

```text
REASONING_EFFORT = COMPUTE / SEARCH DEPTH
REASONING_EFFORT != AUTHORITY
REASONING_EFFORT != EVIDENCE
REASONING_EFFORT != PERMANENT RISK POSTURE
```

Fresh / takeover / material architecture cold start 的深推理启动条件由 [Architect Reconnaissance](ARCHITECT_RECONNAISSANCE.md#11-adaptive-reasoning-effort-at-cold-start) 拥有。完成 durable reconciliation / reconnaissance、项目世界模型已经可从 durable source 恢复后，Architect 的默认巡航语义为：

```text
STEADY_BALANCED
```

它表示：使用足以完成 current Work 的正常推理强度，优先 live-reconcile / 引用 durable truth，不为了降低自身不确定性每轮重新打开已经闭合的问题，也不因为角色名机械常驻 provider 的最大推理档位。

只有出现 **material signal** 时才升级：

```text
STEADY_BALANCED
  -> DEEP_ESCALATION
```

典型 signal：

- 同类实现 / repair 已重复失败且原因未收敛；
- implementation / tests / live facts 与 current architecture 发生 material contradiction；
- current durable facts 互相冲突；
- current governance / architecture invariants 发生真实冲突；
- material irreversible / destructive / security / secret / authority unknown；
- 多个独立 evidence source / Agent 给出无法用 current facts 调和的 material 结论；
- PR / acceptance 多轮不能闭合，且不是普通 repair backlog；
- live evidence 表明已接受架构可能存在根本性错误；
- 准备重新打开已 durable 关闭的 ruling，并且存在新 material evidence。

普通 test failure、第一次实现错误、已知 repair、可定位 lint/build 问题 **不是**自动升到最大 reasoning effort 的理由。

Deep escalation 的目标是**破局并重新形成 durable truth**：

```text
diagnose
 -> discriminate
 -> decide
 -> durable evidence / ruling
 -> DE-ESCALATE
 -> STEADY_BALANCED
```

根因或 ruling 已 durable 写回后继续常驻 deep，必须有新的 unresolved material signal；“刚刚遇到过复杂问题”本身不构成永久升级理由。

Reasoning effort 的升降不得改变：

- scope / acceptance；
- merge / deploy / destructive / production authority；
- security / secret gate；
- verification requirement；
- current Work lifecycle；
- evidence strength。

无证据 hard cap / arbitrary resource constraint 的 challenge 语义仍由 current constraint-quality owner（source direction #106）负责；并行 Foreman / child 调度仍由其 current concurrency owner（source direction #111）负责。本节不复制第二套 constraint 或 scheduler policy。

Provider / product 的具体档位映射、开放式 Human 探索等实践见 [Adaptive Reasoning Effort Guide](../40_GUIDES/ADAPTIVE_REASONING_EFFORT.md)。


### 1.4.2 Architect Constraint Challenge

Architect 默认不仅负责推进 Work，也负责判断 **material constraint 是否仍然成立**。存在规则文本不等于继续机械服从就是正确行为。

```text
OBEDIENCE != CORRECTNESS
CHALLENGE != OVERRIDE
AUTONOMY != AUTHORITY_EXPANSION
HIGHER_AUTHORITY_STILL_WINS
```

以下 signal 命中且会 materially 影响 acceptance / capability / progress 时，Architect MUST surface challenge，而不是静默盲从：

- constraint 与 current Human goal / acceptance 或更高 current authority 冲突；
- 关键前提已被 live evidence 证伪；
- historical AI recommendation / temporary workaround 被误当 permanent Human requirement；
- arbitrary numeric / time / retry / resource / concurrency hard cap 没有 current evidence；
- constraint 使 acceptance 实际不可达或制造明显 `PREMATURE_YIELD`；
- ordinary repair / retry / deterministic work 被错误升级为 Human Gate；
- newer architecture/runtime/current durable ruling 已 supersede 旧 gate；
- 流程成本 materially 高于其控制的风险，且不存在 current safety/authority justification。

这不是对每个偏好或轻微低效发起治理争论。Challenge 只针对 **material constraint defect**。

#### Owner-based handling

**A. Architect-owned / lower-layer AI-generated constraint**

如果 current Architect 有权修改该 Work Order / project-local rule，且修正不改变 Human goal、product acceptance、material scope，也不绕过 security / secret / destructive / irreversible gate，则 SHOULD 直接 amend，并 durable 记录 evidence 与理由。不要把自己可修的旧错误再升级成 Human ceremony。

**B. Human / current higher-authority / global-governance constraint**

不得自行绕过。向 owner / higher authority 提交 challenge；受争议动作继续 fail-closed，**其它不受影响的 READY work 继续推进**。

**C. Stale / superseded lower-authority constraint**

若 durable hierarchy 已证明 newer/higher ruling supersede 旧 constraint，直接采用 current ruling，并 durable 标记旧 gate `stale / superseded`。不得因为历史文本仍存在，就重新制造 Human Gate。

Agent 准备进入 `HUMAN_REQUIRED / AWAITING_DECISION` 或等价等待前，必须先 live-reconcile exact Work 的最新 Human/Architect durable ruling；已被解除的旧 gate 不能靠惯性继续生效。

#### Builder / Foreman boundary

Builder / Research / Repair / Foreman SHOULD 识别明显坏约束，但默认没有 governance override authority。它们应 durable 报告 challenge，停止受争议约束影响且可能越权的动作，继续其它 authorized work；不得因为发现坏约束就扩大 scope、merge、deploy 或 destructive authority。

最小 durable finding：

```yaml
constraint: <受质疑约束>
source: <durable pointer>
owner: <Human | Global | Project Architect | Work Order | unknown>
evidence: <current evidence>
impact: <material impact>
challenge_reason: <why materially defective>
recommended_change: <minimal replacement>
can_continue_unaffected_work: true|false
authority_to_amend: yes|no|unknown
```

该 finding 不是新 lifecycle / approval state；沿用现有 Work / Issue / checkpoint / Review durable surface。

Constraint Challenge 不授权绕过 Human current explicit requirement、security/privacy/secret、destructive/irreversible gate、production/deploy authority、legal/compliance、required independent verification、unknown ownership/currentness。上述约束可以被 challenge，但在 current owner 修改前仍须遵守。

### 1.4.3 Architect Watch / Reconciliation Wake

Architect 的持续推进不要求一个模型会话永久在线。deployment 若提供 scheduler / automation / event wake，Project/Global Architect MAY 通过周期或条件唤醒重新进入 current durable state，并执行一次**观察—重建—裁决**循环：

```text
WAKE
 -> bootstrap / live reconcile current durable sources
 -> read owned active Work graph only
 -> derive health / actionable delta
 -> continue | review | recover | report exact real gate
 -> durable writeback when an authorized action occurs
 -> EXIT
```

该循环只是对现有 Work / attempt / durable evidence 的消费方式，不创建第二套 task DB、Work state、liveness registry 或 authority。scheduler capability、定时器、Webhook、后台进程或模型在线状态都 **不产生 authority**。

Watch 每次唤醒必须从 Git/GitHub current state 重建，不能依赖 scheduler-local memory、上一轮聊天或旧 brief。它 MAY 消费 [Durable Trace](../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md) 已有的 CLAIM / CHECKPOINT / TERMINAL、remote refs、PR/review 与 deployment observation；不得为 Watch 另造并行 attempt lifecycle。

deployment MAY 配置 pickup / stale thresholds，但 public governance 不冻结统一 TTL。超过阈值只能形成 `SUSPECT` / `UNKNOWN` 等**派生健康判断**，不能自动把 executor 判 FAILED、取消 ownership、授予 takeover、merge 或 destructive authority。准备恢复前必须重新核对 current generation / remote refs / ownership / shared resources；未知 effect、provider backoff、rate limit 和 security/permission gate 继续 fail closed。

健康且无可执行 delta 时，Watch 可以静默结束。出现 current authorized next action 时，按 §1.4 continuation 继续；出现真实 Human / higher-authority gate 时才通知 Human。Human 不是例行状态轮询器。

Daily Brief 是同一 durable state 的**派生 Human-facing memory projection**，不是新的 Work truth。其 health class、字段、freshness 与 source discipline 见 [Architect Watch & Daily Brief Guide](../40_GUIDES/ARCHITECT_WATCH_AND_BRIEF.md)。brief 只能帮助重新定向；任何 mutation 前仍需 live revalidate exact Work / PR / head。

### 1.5 Global Architect Maintenance Lane

Global Architect 在 live validate 后，可以 `DIRECT` 维护以下**低风险、非行为性**治理内容，不要求为了角色仪式启动 Runner / Builder / Verifier：

- 文档结构、README、目录、索引、Reading Map；
- stale link / stale wording / 术语统一；
- 已明确 durable ruling 的规则同步；
- Bootstrap 阅读顺序 / targeted pointer；
- route / registry 的非行为性小修；
- 纯说明性、不改变机器行为 / 权限 / compatibility 的整理。

以下变化**不会**因为 Maintenance Lane 自动变成低风险：

- program/runtime behavior；
- permission / security boundary；
- lifecycle / destructive operation；
- data model / schema / compatibility；
- cross-project machine contract；
- deploy / production / irreversible external action；
- material governance semantics 尚未由 current authority 冻结的变化。

这些必须按 current Work Order / authority / risk / Review gate 决定 `DIRECT | DELEGATE | HUMAN_REQUIRED`。

Maintenance Lane 的目的只是消除低风险治理仪式，不是绕过 safety/authority。

### 1.6 Same-lineage default `WARM_RESUME`

`Role/Mode != Context != Authority/Independence`：mode（`PLAN | BUILD | REPAIR | SELF_REVIEW | VERIFY | INVESTIGATE`）不自动要求换 context；换 context 不产生 authority。

同一 implementation lineage 内默认：

```text
PLAN -> BUILD -> TEST -> REPAIR -> SELF_REVIEW -> REPAIR
```

优先复用 current owned warm context。明确 review finding 回流后优先由原 executor 修，不为角色仪式重复 context rehydration。`DEFAULT_SAME_LINEAGE = WARM_RESUME`。

正交 machine 维度的定义见 [Recovery & Handoff §4](../30_PROTOCOLS/RECOVERY_HANDOFF.md#4-work-context-与正交维度)，可复制形态见 [CONTEXT_MODE_SEED](../50_TEMPLATES/CONTEXT_MODE_SEED.md)。

### 1.7 `PREMATURE_YIELD`：retryable execution failure

`PREMATURE_YIELD` 是正式定义的 retryable execution failure class，不是合法 stop：

```text
acceptance_not_met
AND no_real_stop_gate
AND legal_next_action_exists
AND executor_yielded
=> PREMATURE_YIELD
```

真实合法 stop gate 至少包括以下 canonical classes（可扩展，但扩展 class 必须 fail-closed，且不得把 ordinary repair input 升格为 Human gate）：`REAL_HUMAN_GATE | AUTHORITY_BLOCKED | SECURITY_OR_DESTRUCTIVE_GATE | DEPENDENCY_BLOCKED | UNRECOVERABLE_EXECUTOR_FAILURE`。

普通 test / lint / typecheck / red CI、已知 review finding、可在当前 scope 内修复的代码错误属于 repair input，不是 Human interrupt。同一 lineage 内 executor 遇到此类输入应自动进入 repair loop，不得把 Human prompt 当 scheduling clock。

### 1.8 Completion boundary：durable acceptance + terminal writeback

不新造第二套 acceptance。executor goal / stop predicate 必须从 current durable Work Order acceptance 编译；不适用项不得凭模板被强制创造。

对 delegated executor，execution attempt 与 Work lifecycle 分开：

```text
DISPATCH
 -> AGENT_CLAIMED
 -> [PROGRESS_CHECKPOINT]*
 -> AGENT_TERMINAL_RESULT
```

- `AGENT_CLAIMED`：Bootstrap / execution gate 已通过后、material execution 开始前立即写入 exact Work coordinate，并从 durable source readback 确认。它只证明“本 attempt 已接手并开始”，不产生 authority，也不改变 Work 状态。
- `PROGRESS_CHECKPOINT`：只在语义阶段边界按 Durable Trace 写入；不是 heartbeat。短任务可以没有 checkpoint。
- `AGENT_TERMINAL_RESULT`：无论 `SUCCESS | NEGATIVE_RESULT | PARTIAL | BLOCKED | HUMAN_REQUIRED | FAILED | CANCELLED`，本 attempt 终止前都必须写回 exact Work coordinate，并 readback 确认。它关闭的是 **execution attempt**，不自动把 Work Order 置为 DONE，也不替代 Architect Review。

因此：

```text
EXECUTION_FINISHED != COMPLETION_REACHED
WRITEBACK_ATTEMPTED != DURABLE_WRITEBACK_CONFIRMED
```

只有 current Work acceptance 要求的 deterministic checks / currentness / commit-push / exact-head / evidence 已满足，且适用 delegated attempt 的 terminal writeback 已被 durable readback 确认，才可 `COMPLETION_REACHED`。

Executor 自述 `done / completed` 只是 observation，不能覆盖 deterministic finish / review / evidence gates。父 Architect / orchestrator 收到 executor 返回后必须 live-read terminal pointer 与 current Work state，再消费结果；聊天中的 self-report 不是 completion evidence。

**Delegated terminal return 固定为 exact GitHub pointer only。** terminal writeback 确认后，executor 对 caller/Human 的最终返回只包含指向该 `AGENT_TERMINAL_RESULT` 的精确 GitHub pointer，不再复制 summary、状态说明、本地路径或代码块。这样 missing/invalid/mismatched pointer 可以被机械识别为 terminal drift。

没有 authorized durable GitHub write path 的 side/fork/subagent 不具备 Work closeout 能力：它只能向 primary/orchestrator 返回有界 evidence；primary 必须验证/综合并完成 durable writeback 后，Work 才能进入可消费的 terminal boundary。

`DIRECT` 与 `DELEGATE` 的 authority/evidence 要求不因本协议改变；CLAIM/TERMINAL 只为 delegated attempt 建立最小可观察闭环。

### 1.9 Fresh 与 delegation 边界（指针）

Recovery 分支、fresh 触发、independence 与 delegation 的可执行语义统一见 [Recovery & Handoff §1–5](../30_PROTOCOLS/RECOVERY_HANDOFF.md#1-恢复分类)。旧 Session 与 template 仅保留形态/兼容指针，不再拥有这些规则。

---

## 2. Human Dispatch Card

Human Dispatch Card 只用于 **Human 手工启动 delegated executor**。可复制格式不在本文件重复维护，统一使用 [`../50_TEMPLATES/DISPATCH_PAIR.md`](../50_TEMPLATES/DISPATCH_PAIR.md)。

### 2.1 Canonical 运行位置

Human-facing 调度统一使用四类运行位置，并按能完整完成和验证任务的最低资源层级选择：

`网页端 -> 云端电脑 -> 本地 -> 本地+设备`

- `网页端`：当前 Chat/Agent 仅凭已授权 GitHub / Web / 文件等连接能力即可完成，不需要独立代码运行环境。
- `云端电脑`：需要 workspace、toolchain、进程、测试或长时间运行，但不依赖 Human 本机独有状态或真实设备。
- `本地`：必须使用 Human 本机的文件、工具链、进程、私网、本地状态或其它不能可靠搬到云端的环境。
- `本地+设备`：除本地环境外，还必须访问指定节点、手机、平板或其它真实设备。

运行位置是 **Human scheduling metadata**，不是 capability / authority grant。executor 启动后仍须验证实际工具、权限、currentness 与安全 gate。对 `本地 / 本地+设备` 或明确依赖本地 toolchain 的任务，按 [`../10_BOOT/LOCAL_ENGINEERING_GATE.md`](../10_BOOT/LOCAL_ENGINEERING_GATE.md) 先做低成本脚本化环境 preflight；required gate 未通过时不要先消耗高成本模型/构建资源。

若一个任务可以拆成独立 tranche，优先把网页端 / 云端电脑可完成的部分单独派发；不要因为最终 acceptance 需要本地或设备，就让整条任务占用更高成本环境。

Human Dispatch Card 的 current 模板采用五个语义：`任务 / 为什么做 / 你要做什么 / 运行位置 / 本轮终点`。不再单列“调度建议”；上下文亲和进入 Agent Seed，模型、provider、价格、quota 等瞬时调度信息留给 deployment-local scheduler。

### 2.2 Compatibility

`2.3.0` 之前 durable 产生的 `CLOUD_ONLY | LOCAL_REQUIRED | NODE_REQUIRED | DEVICE_REQUIRED | MIXED | UNKNOWN` 六类执行依赖与旧六字段 Human Card 保持 historical provenance 有效；新的 Human 手工派发使用四类运行位置模板。

---

## 3. Default Minimal Agent Seed

Minimal Agent Seed 的目标仍是**最少无歧义启动信息**。可复制格式统一使用 [`../50_TEMPLATES/DISPATCH_PAIR.md`](../50_TEMPLATES/DISPATCH_PAIR.md)，本文件不再维护第二份抽象 Seed 与示例。

新 Human-facing Seed 使用中文扁平键值：

- `私仓工单：<repo#issue[/comment]>` 或 `公仓工单：<repo#issue[/comment]>`；
- `节点：...`、`项目：...`、`情景：...`、`上下文参考：...` 仅在有值时出现；无值整行省略。

`私仓工单` / `公仓工单` 分别映射 BOOT-1 的 `github-private` / `github-public` access class；具体 authenticated access route 与 fallback 仍只由 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` 定义。

`上下文参考` 只是 scheduler / warm-context affinity hint：它不产生 authority，不声明 currentness，也不得覆盖 current GitHub durable truth。

Seed 不复制 role、startup_mode、scope、acceptance、requirements、reporting、stop、执行步骤、权限、安全 gate、模型/provider/price/quota。以上任务知识仍留在 current durable Work Order / dispatch；如果 fresh Agent 仅凭精确地址无法从 durable source 取得任务事实，先修 durable source，再派发。

可选 `执行意图` 只表达语义意图，不是 acceptance / stop 副本：允许一行 `执行意图：<mode/context intent>；按 current durable acceptance 持续到对应 boundary` 说明唤醒原因与模式亲和，不得复制 tests、scope、安全 gate、完成条件；无歧义时整行省略。正交维度见 [Recovery & Handoff §4](../30_PROTOCOLS/RECOVERY_HANDOFF.md#4-work-context-与正交维度)，可复制形态见 [CONTEXT_MODE_SEED](../50_TEMPLATES/CONTEXT_MODE_SEED.md)。

### Seed minimality 与 transport fallback

默认 Seed 建议 5–10 行；这只是检查是否复制合同的 heuristic，不是字符限制。可访问 durable Work Order/dispatch 时，Seed 只寻址与表达必要 affinity，任务角色、scope、acceptance、stop 仍从 current durable source 取得。

只有 Agent 无法访问 durable source 时，transport 才可内联任务所必需的最小合同内容；它不产生 authority 或第二 SSOT，也不能替代 Bootstrap 必需的 authority/currentness/access evidence。恢复 source 访问后回到短 Seed + durable pointer。durable source 本身缺合同则先补 source，再派发；不得把 access failure 当成放宽执行 gate 的理由。

---

## 4. Human Completion Card（非 delegated terminal transport）

Builder / Research / Repair / Verifier 的 terminal transport 由 §1.8 固定为 **exact GitHub pointer only**；详细结果留在 durable `AGENT_TERMINAL_RESULT` / report / PR 中，不再复制到聊天。

Human Completion Card 仅保留为 Architect / orchestrator 在**非 delegated executor terminal return** 场景下的可选 Human-facing synthesis（例如一个 program 已由 Architect 完成最终验收，需要向 Human 汇总）。其五个语义保持：

| # | 字段 | 内容 |
|---|---|---|
| 1 | 结果 | 完成情况 |
| 2 | 交付 | 交付物 + 精确可恢复 pointer（PR / commit / exact head / durable report） |
| 3 | 验证 | 验证方法与结果 |
| 4 | 剩余风险 | 已知风险 / 未覆盖区域 |
| 5 | 下一步 | 建议的后续动作 |

该 Card 不是 executor lifecycle event、不是 Work 状态源，也不得替代 terminal durable writeback。Human-facing language 只引用 `00_KERNEL/LANGUAGE_POLICY.md`；本接口不复制 language override 细节。

---

## 5. Public portability invariants

公共 `ai-use` 的接口示例必须满足：

- 用 `<owner>/<repo>` / role registration 表达 deployment-local coordinate；
- 不要求公共使用者拥有任何上游维护者 private repo 权限；
- governance L0 来自 current governance repo；
- control-plane repo 由 `workspace_registry.control_plane.repo` 或等价 deployment registration 解析；
- `ai-use` / `ai-hub` 可以作为人类解释中的常见命名示例，但不是机器 fixed coordinate；
- repo owner、authenticated principal、repository permission、governance authority 分开判断。

---

## 6. Versioned Definitions

- `2.10.0`：Architect Watch / Reconciliation Wake（#91）。deployment 可用 scheduler/event 周期唤醒 Architect，但每轮必须从 current Git/GitHub durable state 重建；Watch 只消费既有 Work/CLAIM/CHECKPOINT/TERMINAL/refs，不创建第二 lifecycle 或 authority。stale/pickup threshold 留 deployment；超时只产生 derived SUSPECT/UNKNOWN，不自动 failure/takeover。Daily Brief 明确为派生 Human memory projection，mutation 前仍 live revalidate。

- `2.9.0`：Architect Constraint Challenge（#106）。Architect 对 material constraint quality 负有判断责任；按 constraint owner 区分可直接 amend、向 higher authority challenge、或采用 newer ruling supersede stale gate。Builder/Foreman 可 durable 报告 challenge 但不获得 governance override authority；等待 Human 前必须 live-reconcile newer durable ruling；不受争议的 authorized work 继续。Challenge 不改变 Human/security/destructive/deploy/verification authority。

- `2.8.0`：Adaptive Reasoning Effort（#113）。Fresh/takeover/material cold start 的 `DEEP_BOOTSTRAP` trigger 由 Architect Reconnaissance 持有；本接口新增 steady-state `STEADY_BALANCED`、material-signal `DEEP_ESCALATION` 与 durable closure 后 de-escalation。Reasoning effort 仅表示 compute/search depth，不改变 authority、scope、acceptance、verification、security/destructive gate、evidence strength 或 Work lifecycle；provider UI 档位映射留在 non-normative Guide，不进入 core governance。

- `2.7.0`：Executor lifecycle hardening（#94）。Delegated attempt 固化为 `DISPATCH -> AGENT_CLAIMED -> [PROGRESS_CHECKPOINT]* -> AGENT_TERMINAL_RESULT`；CLAIM/TERMINAL 必须 durable readback；成功/失败共用收尾门；`COMPLETION_REACHED` 增加 terminal writeback confirmed gate；delegated terminal chat return 固定为 exact GitHub pointer only；无 durable write path 的 subagent 不可关闭 Work。Human Completion Card 降为 Architect/orchestrator 的非 terminal 可选 synthesis，不再与 executor terminal transport 冲突。

- `2.6.0`：在已合并的 Local Engineering Gate 2.5.0 基础上保留 R1 relocation：context/recovery/independence/delegation 的 semantic owner 收敛至 Recovery & Handoff；模板仅保留形态。原 Seed minimality/transport fallback 搬回本接口；continuation、repair、completion 与 authority 不变。PR #75 旧候选曾使用 2.5.0，现与上游版本区分，旧候选由 Git provenance 保留。

- `2.5.0`：Local Engineering Human Gate（#76）。`本地 / 本地+设备` 只表达 Human 调度位置，executor 需在 BOOT-3 使用**当前平台原生 adapter**验证 Work Order 所需的本地 tool/auth/repo/project/device capability；Windows reference 检查 PowerShell/Git/GitHub/Codex/OpenCode 等。共享的是 Gate contract，不是 PowerShell implementation；gate 不产生 authority、不接收 Human secret、不要求 L0 扩张。
- `2.4.0`：Context Lifecycle v0.1 normative materialization（#60）。新增 §1.6 同 lineage 默认 `WARM_RESUME`、§1.7 `PREMATURE_YIELD` 可执行判据、§1.8 completion boundary（来自 durable acceptance）、§1.9 fresh 与 delegation 边界指针；§3 明确可选 `执行意图` 为语义意图而非 acceptance / stop 副本；正交 `context_policy / mode / continuation / independence` 与最小 `delegation / parallelism` 的可复制形态只在 `50_TEMPLATES/CONTEXT_MODE_SEED.md` 维护，本文不复制第二份维度表；provider 命令仅作 informative 示例，不进 canonical。
- `2.3.0`：Human/Agent 双词收敛为 `50_TEMPLATES/DISPATCH_PAIR.md` 单一可复制模板；Human Card 从旧六类执行依赖/六字段 UX 收敛为 `网页端 | 云端电脑 | 本地 | 本地+设备` 四类运行位置与五字段卡；Minimal Seed 改为中文扁平键值并加入可选 `节点 / 项目 / 情景 / 上下文参考`，去除 Human-facing `startup_mode/access/work` 重复字段；旧格式保持 historical provenance。
- `2.2.0`：Kernel residency canonicalization；本文件正式成为 common mutation workspace/scope hygiene、`DIRECT | DELEGATE`、Architect continuous advancement、Global Architect Maintenance Lane 与 Human/Agent dispatch interface 的 canonical home；Bootstrap access routing 与 language override 只保留 pointer，不再复制 downstream policy。**Behavior preserved; residency changed.**
- `2.1.1`：public portability hardening；移除 maintainer-specific repo coordinate，明确 current governance repo / deployment-local control-plane role indirection；不改变 `DIRECT | DELEGATE`、authority、dependency taxonomy 或 Completion Card 语义。
- `2.1.0`：编译 Architect `CONTINUE_WITHIN_AUTHORITY` 与 Human Dispatch Card `执行依赖` 六字段语义；历史五字段 Human Card 保持 provenance 有效。
- `2.0.4`：编译 Architect `DIRECT | DELEGATE` 接口边界；Human Dispatch Card 明确为 Human 手工启动 delegated executor 的 UX；Minimal Seed 不增加 provider/model/routing 字段。
- `2.0.3`：Minimal Seed 从“最少行”收敛为“最少无歧义启动信息”；private repo 固定携带 `access: github-private`；访问优先级为 native authenticated GitHub -> authenticated `gh` -> remote 校验后的 local Git。
- `2.0.2`：同步 Bootstrap Ordered Applicability；Seed 不提前适用任务正文。
- `2.0.1`：clarification；强化 Seed 只做 addressing，并保留 private GitHub 最小 access 扩展。

---

## 7. Boundary Conditions

- 本文只定义公开/通用 interface，不承载 deployment private topology / heads / endpoints / secrets。
- 本文不改变 Runner/program behavior，也不定义 provider/backend routing contract。
- current durable dispatch / Work Order 在 Minimal Seed / transport 之前；Seed 不替代 dispatch。
- 派发前 Architect 必须确认 durable source 足以让 fresh Agent 执行；否则先修 Work Order/dispatch。
- Human Dispatch Card 只属于 Human manual transport / scheduling UX；authorized automated transport 不需要先生成 Human Card。
- Architect continuous advancement 只适用于 Project/Global Architect current durable authority 内；不得扩展为 Builder/Research/Repair/Verifier 的长期自治或 merge authority。
- Human-facing narrative 遵守 `00_KERNEL/LANGUAGE_POLICY.md`；本文件不再维护第二份语言规则。
- public portability 不产生任何新的 repo permission / governance authority / deploy authority。
- provider-specific 命令名（ slash command、custom command 名、内置 agent 名）不进 canonical semantics；如需示例，只作 informative / non-normative / freshness-marked 呈现，机器映射由 deployment / control-plane adapter 持有。
