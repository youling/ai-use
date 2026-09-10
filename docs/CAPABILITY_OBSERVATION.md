# Capability Observation — Cold-start Contract v0.1

**Classification: L2 Targeted Reference.** Fresh / takeover Architect 冷启动且需要形成 current-session capability observation 时读取。

本文件只定义 **AI / client / surface 的动态能力观察**。它不定义 Architect authority、不证明 session liveness、不替代 Bootstrap、Work Order、Dispatch、Fleet node/device capability truth，也不把一次观察升级为永久 registry 事实。

核心不变量：

```text
MODEL
!= CLIENT / SURFACE
!= TOOL / CONNECTOR
!= EXECUTION ENVIRONMENT
!= AUTHORIZATION
!= AUTHORITY

CAPABILITY != AUTHORITY
OBSERVATION != LIVENESS
```

---

## 1. 触发与位置

默认触发：

- Fresh / takeover `Global Architect`；
- Fresh / takeover `Project Architect`；
- current deployment / task 明确要求 capability observation 的等价 Architect cold-start。

普通 delegated `Builder / Research / Repair / Verifier / Release` **不因本文件自动获得 taskless READY / IDLE 语义**。它们仍按 current Agent Interface 要求使用 current Dispatch / Work Order；若未来需要“只启动 specialist 做 capability probe、然后空闲待命”，必须另行裁决，不能从本文件推导。

本 hook 不增加 `BOOT-0` / `BOOT-4`。顺序固定为：

```text
BOOT-1 ADDRESS
-> BOOT-2 APPLICABLE RULES
-> BOOT-3A Authority + Access
-> current-session low-cost capability observation
-> BOOT-3B Live State
-> BOOT-3C project-local durable bootstrap writeback
-> [if deployment has a registered capability ledger] compact mirror
-> EXECUTION_ALLOWED / continuation classification
```

能力观察只是 BOOT-3 的辅助 evidence。**BOOT-3C project-local durable bootstrap writeback 仍是 cold-start authority/currentness 完成 gate。** central capability mirror 是非关键 telemetry，不得反向成为 authority gate。

---

## 2. Probe v0.1

### P0 — 默认低成本、无外部副作用

只根据当前会话 / 客户端真实可见事实观察：

- product / client / surface / mode；
- model label（客户端不可见则 `UNKNOWN`）；
- client / agent runtime version（不可见则 `UNKNOWN`）；
- 当前实际暴露的 tools / connectors；
- renderer / native interaction 能力；
- shell / workspace / browser / file-artifact / scheduling 等 execution surface 是否在**当前 surface**可用。

不得用产品常识、营销文档或模型自述，把未验证能力写成当前可用。

### P1 — 仅做 route-relevant safe probe

只有当某项能力已经由当前 tool inventory / client surface 暴露，且 probe 本身低风险、可逆、无敏感副作用时，才做最小 active probe，例如：

- public Web 只读获取；
- shell/runtime 只读版本查询；
- task-private 临时文件 create/read/delete；
- public benign browser page 只读；
- 最小 native/file artifact readback。

P1 不为了“把表填满”逐项测试。只验证可能影响**当前 placement / routing** 的能力。

### P2 — 默认禁止自动执行

以下属于 account-bound / external-side-effect / device-side probe，除非 current Human / task authority 明确允许，否则只标记状态，不执行：

- private account write；
- connected app write；
- signed-in browser mutation；
- scheduled/background side effect；
- local managed node / real device operation；
- production、destructive、irreversible probe。

P2 capability 即使存在，也不产生对应 action authority。

---

## 3. Observation vocabulary

每项 capability 至少表达：

```text
capability_id
state
scope
source / evidence
notes? / unknown reason?
```

`state` 使用：

```text
AVAILABLE_NOW
AVAILABLE_WITH_APPROVAL
AVAILABLE_OTHER_MODE
UNAVAILABLE
UNKNOWN
```

`evidence` 使用：

```text
PROBED_SUCCESS
CLIENT_VISIBLE
TOOL_INVENTORY
DOCUMENTED_CURRENT
SELF_REPORT_ONLY
UNKNOWN
```

规则：

- `SELF_REPORT_ONLY` 不得作为 scheduler hard eligibility；
- `DOCUMENTED_CURRENT` 说明产品/服务当前文档支持，不等于这个账户 / surface 已验证可用；
- `UNAVAILABLE` 必须尽可能限定 scope，例如 `current-surface`，不得无证据升级成 product-wide 不可用；
- `AVAILABLE_OTHER_MODE` 只说明已知其它 mode/surface 可能承载，不自动证明当前账户可调用；
- 重要动态能力被实际选中用于执行前，仍需 current-session re-probe / live validation。

---

## 4. Human-facing Capability Card

第一屏保持很短，优先回答“现在能做什么、应放哪里跑、什么仍未知”，例如：

```text
CAPABILITY CARD
subject: <product / surface / mode>
can_now: <high-value current capabilities>
other_mode: <known alternate placement, if evidenced>
unknowns: <material unknowns>
best_placement: <current evidence-based placement | UNKNOWN>
needs_human: <meaningful approval/gate | none>
```

详细观察可放在第二层 machine-readable record。不要默认把几十项 capability 堆给 Human。

---

## 5. Central durable observation

若 deployment 已通过 workspace / control-plane registration 或等价 current durable mechanism 注册**集中 capability observation ledger**，Fresh/takeover Architect 在 project-local BOOT-3C durable bootstrap report 成功后，尝试 mirror 一条 compact record：

```text
ARCHITECT_CAPABILITY_OBSERVATION v0.1
logical_role: <exact logical role>
subject:
  product: <visible/declarable product | UNKNOWN>
  surface: <surface | UNKNOWN>
  mode: <mode | UNKNOWN>
  model_label: <visible label | UNKNOWN>
  client_label: <visible label | UNKNOWN>
  client_version: <visible version | UNKNOWN>
  agent_runtime: <visible runtime | UNKNOWN>
  agent_runtime_version: <visible version | UNKNOWN>
probe_version: capability-probe/v0.1
scope: current-session
capability_summary: <compact evidence-bearing summary>
unknowns: <compact list | none>
authority_effect: NONE
```

公共 governance **不得硬编码某个维护者的私有 control-plane repo / Issue / account**。ledger coordinate 必须来自 deployment-local registration / current durable pointer；没有注册时不得猜。

在 GitHub comment ledger 这一实现中：

- GitHub server `created_at` 可作为 durable observation event time；无需再制造第二个 authoritative timestamp；
- comment author 只提供 transport provenance，不证明 `logical_role` 或 governance authority；
- comment id 可作为 record pointer，不必再生成第二个 observation id；
- 语义修正使用新的 correction / superseding record，不编辑历史观察来改写过去语义。

其它 durable carrier 可以实现等价语义，不要求一定使用 GitHub Issue comment。

---

## 6. Mirror failure semantics

central mirror 是 scheduling / discovery telemetry，不是 Bootstrap authority source。

若 project-local BOOT-3C durable report 已成功，而 central ledger：

- 未注册；
- 当前不可访问；
- 当前写入失败；

必须如实区分，例如：

```text
BOOTSTRAP_PROJECT_DURABLE = PASS
CAPABILITY_LEDGER_WRITEBACK = UNAVAILABLE
CAPABILITY_OBSERVATION = SESSION_LOCAL_ONLY
```

**不得**宣称 central observation 已建立；但也**不得仅因非关键 telemetry mirror 失败就把本来合法的 Architect `EXECUTION_ALLOWED` 变成权限 blocker**。如果 ledger failure 同时暴露真正的 authority / access / security 冲突，则按那个真实 gate 独立 fail closed。

---

## 7. Scheduler / registry boundary

历史 capability observation 是 cache / evidence，不是 liveness，也不是永久 capability truth。

- scheduler / Architect 可以用近期 observation 做候选 placement shortlist；
- 被选中的新/current session 必须在依赖动态能力前 re-probe；
- static agent/role registry 不因一条 observation 自动增加 tool/provider/runtime capability；
- provider quota、价格、临时限流、当前登录态等快速变化事实不得被本记录静默固化为长期规则；
- Fleet node/device capability truth 继续由 Fleet/project-local owner 管理，不进入 AI-client capability ledger。

---

## 8. Security / privacy

Observation 与 mirror 禁止写入：

- secret、token、password、private key、完整 secret-bearing environment；
- 不必要的 private hostname / IP / provider locator / peer inventory；
- 与 placement 无关的 account/private data；
- raw command output 中可能携带的凭据。

只保留支撑 capability classification 所需的最小 sanitized evidence。

---

## 9. Non-goals

v0.1 不做：

- giant capability encyclopedia；
- 第二套 scheduler / liveness registry；
- provider/model 固定名单；
- Minimal Agent Seed 扩容；
- non-Architect taskless READY/IDLE 角色制度；
- Fleet schema / node lifecycle 改造；
- 为 capability telemetry 新建 DB/daemon；
- 把 capability observation 解释成 authority、approval 或 execution permission。
