# Capability Observation — Cold-start Contract v0.1

**Classification: L2 Targeted Reference.** Fresh / takeover Architect 冷启动需要形成 current-session capability observation 时读取。

本文件只定义 AI / client / surface 的动态能力观察。它不定义 authority、不证明 liveness、不替代 Bootstrap / Work Order / Dispatch / Fleet capability truth，也不把一次 observation 升级为永久 registry 事实。

```text
MODEL != CLIENT/SURFACE != TOOL/CONNECTOR
!= EXECUTION ENVIRONMENT != AUTHORIZATION != AUTHORITY
CAPABILITY != AUTHORITY
OBSERVATION != LIVENESS
```

## 1. 触发与 BOOT-3 位置

默认触发 Fresh / takeover `Global Architect`、`Project Architect`，以及 current deployment 明确要求的等价 Architect cold-start。

普通 delegated `Builder / Research / Repair / Verifier / Release` 不因本文件获得 taskless READY / IDLE；它们仍需要 current Dispatch / Work Order。若未来要建立 specialist idle/probe 模式，必须另行裁决。

不增加 `BOOT-0` / `BOOT-4`：

```text
BOOT-1 ADDRESS
-> BOOT-2 APPLICABLE RULES
-> BOOT-3A Authority + Access
-> low-cost current-session observation
-> BOOT-3B Live State
-> BOOT-3C project-local durable bootstrap writeback
-> optional central observation mirror
-> EXECUTION_ALLOWED / continuation classification
```

BOOT-3C project-local durable writeback 仍是 cold-start authority/currentness 完成 gate。central mirror 只是非关键 telemetry，不能反向授予或撤销 authority。

## 2. Probe v0.1

**P0 — 默认，无外部副作用。** 只观察当前会话/客户端真实可见的 product、surface、mode、model/client/runtime label（不可见则 `UNKNOWN`）、tool/connector inventory、native renderer/interaction，以及当前 surface 的 shell/workspace/browser/file/scheduling 能力。不得用产品常识或模型自述把未验证能力写成当前可用。

**P1 — 仅 route-relevant safe probe。** 只有能力已暴露且会影响当前 placement/routing 时，才做最小低风险 probe，例如 public Web read、只读 runtime version、task-private temp file create/read/delete、public benign browser read、最小 artifact readback。不要为了填满能力表逐项测试。

**P2 — 默认不自动执行。** private/external account write、connected-app write、signed-in browser mutation、background side effect、managed node / real device operation、production/destructive/irreversible probe，除非 current Human/task authority 明确允许。Capability 存在也不产生 action authority。

## 3. Vocabulary

每项 capability 至少表达：

```text
capability_id
state
scope
evidence
notes? / unknown_reason?
```

`state`：

```text
AVAILABLE_NOW | AVAILABLE_WITH_APPROVAL | AVAILABLE_OTHER_MODE
UNAVAILABLE | UNKNOWN
```

`evidence`：

```text
PROBED_SUCCESS | CLIENT_VISIBLE | TOOL_INVENTORY
DOCUMENTED_CURRENT | SELF_REPORT_ONLY | UNKNOWN
```

约束：

- `SELF_REPORT_ONLY` 不得作为 scheduler hard eligibility；
- `DOCUMENTED_CURRENT` 不等于当前账户/surface 已验证；
- `UNAVAILABLE` 尽量限定 scope，不无证据升级为 product-wide；
- `AVAILABLE_OTHER_MODE` 不自动证明当前账户可调用；
- 真正依赖动态能力执行前仍须 current-session re-probe/live validation。

## 4. Human-facing card

第一屏只回答高价值事实，不默认展示完整 capability inventory：

```text
CAPABILITY CARD
subject: <product / surface / mode>
can_now: <high-value current capabilities>
other_mode: <evidenced alternate placement | none>
unknowns: <material unknowns | none>
best_placement: <placement | UNKNOWN>
needs_human: <meaningful gate | none>
```

## 5. Central durable mirror

若 deployment 已通过 workspace/control-plane registration 或等价 current durable pointer 注册 capability observation ledger，Fresh/takeover Architect 在 project-local BOOT-3C 成功后尝试 mirror：

```text
ARCHITECT_CAPABILITY_OBSERVATION v0.1
logical_role: <exact logical role>
subject:
  product: <value | UNKNOWN>
  surface: <value | UNKNOWN>
  mode: <value | UNKNOWN>
  model_label: <value | UNKNOWN>
  client_label: <value | UNKNOWN>
  client_version: <value | UNKNOWN>
  agent_runtime: <value | UNKNOWN>
  agent_runtime_version: <value | UNKNOWN>
probe_version: capability-probe/v0.1
scope: current-session
capability_summary: <compact evidence-bearing summary>
unknowns: <compact list | none>
authority_effect: NONE
```

公共 governance 不硬编码维护者私有 repo/Issue/account。ledger coordinate 必须来自 deployment-local registration；未注册时不猜。

GitHub-comment carrier 可直接以 server `created_at` 为 event time、comment id 为 record pointer；comment author 仅是 transport provenance，不证明 logical role/authority。语义修正用新 correction/superseding record，不改写过去 observation。其它 durable carrier 可实现等价语义。

## 6. Mirror failure

central mirror 是 scheduling/discovery telemetry，不是 Bootstrap authority source。project-local BOOT-3C 已成功，而 ledger 未注册、不可访问或写失败时，如实记录：

```text
BOOTSTRAP_PROJECT_DURABLE = PASS
CAPABILITY_LEDGER_WRITEBACK = UNAVAILABLE
CAPABILITY_OBSERVATION = SESSION_LOCAL_ONLY
```

不得谎称 central observation 已建立；也不得仅因非关键 mirror 失败就把本来合法的 `EXECUTION_ALLOWED` 变成 blocker。若失败同时暴露真实 authority/access/security 冲突，则按那个真实 gate 独立 fail closed。

## 7. Consumption boundary

Historical observation 是 capability cache/evidence，不是 liveness 或永久 truth。Scheduler/Architect 可用近期 observation 做 placement shortlist，但选中 session 后仍需 re-probe。Static role/agent registry 不因 observation 自动增加 tool/provider/runtime capability；quota、价格、临时限流、当前登录态等快速变化事实不固化为长期规则。Fleet node/device capability 继续由 Fleet/project-local owner 管理。

## 8. Security / non-goals

Observation/mirror 只留支撑 classification 的最小 sanitized evidence；禁止 secret/token/password/private key、完整 secret-bearing env、不必要的 private hostname/IP/provider locator/peer inventory、与 placement 无关的 account data。

v0.1 不做 giant capability encyclopedia、第二 scheduler/liveness registry、provider/model 固定名单、Minimal Agent Seed 扩容、non-Architect taskless READY/IDLE、Fleet schema/lifecycle 改造、capability telemetry DB/daemon，也不把 observation 解释成 authority/approval/execution permission。
