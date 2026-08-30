# Agent Interface — Canonical L2 Reference

**Classification: L2 Targeted Reference.** Read when dispatching/executing Agent work, choosing Architect execution mode, advancing an authorized program, or producing/reviewing Human/Agent interface artifacts.

**Protocol Version: 2.2.0**

本文是 **execution / dispatch / continuation interface** 的 canonical home。公共 `ai-use` 不绑定任何特定 owner/repo、私有 control-plane 名称或上游维护者账号。

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

---

## 2. Human Dispatch Card

Human Dispatch Card 只用于 **Human 手工启动 delegated executor**，恰好六个语义字段，顺序固定：

| # | 字段 | 内容 |
|---|---|---|
| 1 | 任务 | 一句话任务标题 |
| 2 | 为什么做 | 背景 / 理由 |
| 3 | 你要做什么 | 本轮工作内容 |
| 4 | 执行依赖 | objective execution-environment dependency；以 canonical class 开头 |
| 5 | 调度建议 | 只给 Human：难度、上下文规模、模型建议、词元/时间粗估、并行策略、本轮重点 |
| 6 | 本轮终点 | 完成边界 / stop condition |

`执行依赖` 与 `调度建议` 必须分离。执行依赖不授予 capability / authority，也不编码 provider/model/price/quota，更不进入 Minimal Agent Seed。

### 2.1 Canonical execution dependency classes

`执行依赖` MUST 以以下六类之一开头：

- `CLOUD_ONLY` — 不依赖 local checkout/toolchain、private node/network、real device、local daemon/long-running process 或 physical interaction；实际 connector/tool capability 仍须 startup 验证。
- `LOCAL_REQUIRED` — 必须使用 local filesystem/workspace/toolchain/process/runtime，但不要求特定 node。
- `NODE_REQUIRED` — 必须进入指定 managed/execution node 或 private-network path。
- `DEVICE_REQUIRED` — 必须访问真实 phone/tablet/其它 device 或 device-control path。
- `MIXED` — 有有意义的 cloud tranche，但最终 acceptance 依赖 local/node/device evidence；应优先拆 cloud tranche。
- `UNKNOWN` — current evidence 不足以真实分类；不得因为任务看起来只是文字就默认 `CLOUD_ONLY`。

关键边界：

- `CLOUD_ONLY != CAPABILITY_OR_AUTHORITY_GRANT`；
- secret/Human/physical confirmation gate 独立存在；
- dependency taxonomy 不写具体 provider/model/价格/quota。

### 2.2 Generic 示例

```text
任务: <control-plane-repo>#<issue> / routing + docs 收敛
为什么做: 旧治理映射与 current public contract 不一致
你要做什么: targeted GitHub 核验、文档同步、exact diff readback
执行依赖: CLOUD_ONLY — authenticated GitHub R/W + Web
调度建议: 上下文 Medium；文档编辑 + targeted GitHub 核验；可单 delegated executor 完成
本轮终点: 提交 PR，报告 exact head + 验证结果后停止，等 Architect Review
```

Human Card 是手工 transport / scheduling UX，不是 Agent 指令或状态源，也不是所有 delegated execution 的治理必经节点。

兼容性：2.1.0 canonical compilation 之前 durable 产生的五字段 Human Card 保持 historical provenance 有效；之后的新 Card 使用六字段顺序。

---

## 3. Default Minimal Agent Seed

Minimal Agent Seed 的目标是**最少无歧义启动信息**，不是固定最少行。它只用于 Agent-facing delegated execution；Architect `DIRECT` 不制造虚假的 Agent Seed。

### 3.1 Public / access 已无歧义

```text
按 `<owner>/<repo>#<issue>` 的 <DISPATCH_TYPE> comment `<id>` 执行。

work: <owner>/<repo>#<issue>@<step>
startup_mode: Fresh <Role>
```

`<owner>/<repo>` 是使用者当前 deployment 的真实 target repo coordinate，不是公共文档作者的 owner/repo。

### 3.2 Private GitHub canonical seed

private repo 首次 durable read 依赖 authenticated route，因此必须带 `access: github-private`：

```text
按 `<owner>/<private-repo>#<issue>` 的 `ARCHITECT_BUILD_DISPATCH` comment `<id>` 执行。

work: <owner>/<private-repo>#<issue>@<step>
startup_mode: Fresh Builder
access: github-private
```

如果 target 是 deployment-local control plane，repo coordinate 从 `workspace_registry.control_plane.repo`（或等价 deployment registration）取得；不得把示例中的 `ai-hub`、`../hub` 或上游维护者账号当 fixed address。

### 3.3 Seed 允许的最小扩展

只有 pointer 无法无歧义启动时，才补 bootstrap-critical 精确引用（如 private/public access hint、exact ref）。Seed 不得复制：

- scope / acceptance / requirements / reporting / stop；
- Human Card 的执行依赖或调度建议；
- 启动读取顺序、evidence 清单、执行步骤、禁止事项或验证清单；
- 难度、token/时间估计、模型建议；
- dependencies / relationships；
- Builder 自评、旧 findings、Architect 旧裁决或 counted Verifier 输出；
- provider/model/routing/pricing/quota metadata。

fresh Agent 仅凭 exact dispatch pointer + 必要 access metadata 无法从 durable source 取得任务事实时，说明 Work Order/dispatch 不完整：先修 durable source，再派发。

### 3.4 Access metadata boundary

`access: github-private | github-public` 只描述 BOOT-1A 的 access class，不承载任务合同，也不授予 authority。

**Canonical access route 与 fallback 只定义在 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`。** 本文件不再复制 native connector / authenticated `gh` / local Git / public HTTPS 的优先级与错误语义，避免两份 route policy 漂移。

`Capability != Authority` 仍是 L0 invariant。

---

## 4. Human Completion Card

Agent 完成后，Builder / Research / Repair / Verifier 保持详细 durable report。Human Completion Card 恰好五个语义：

| # | 字段 | 内容 |
|---|---|
| 1 | 结果 | 完成情况 |
| 2 | 交付 | 交付物 + 精确可恢复 pointer（PR / commit / exact head / durable report） |
| 3 | 验证 | 验证方法与结果 |
| 4 | 剩余风险 | 已知风险 / 未覆盖区域 |
| 5 | 下一步 | 建议的后续动作 |

Human-facing language 只引用 `00_KERNEL/LANGUAGE_POLICY.md`；本接口不复制 language override 细节。

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
