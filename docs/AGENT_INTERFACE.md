# Agent Interface — Canonical L2 Reference

**Classification: L2 Targeted Reference.** Only read when dispatching, executing, or reviewing Agent work orders.

**Protocol Version: 2.1.1**

本文编纂 Human 与 Agent 之间的固定接口契约。部署实例的 control-plane repo 可以按自身需要映射本文，但公共 `ai-use` **不绑定任何特定 owner/repo、私有控制面名称或上游维护者账号**。

---

## 1. Dispatch Structure

执行先区分 `DIRECT | DELEGATE`：

- `DIRECT`：满足 `AGENTS.md` L0 eligibility 时，Project/Global Architect 在 current durable authority / scope / acceptance 内自己施工；不为了角色仪式创建 Builder dispatch / Agent Seed。required Review / merge / Human/high-risk gate 仍保留。
- `DELEGATE`：由 durable Work Order + current Architect dispatch 启动可替换 executor。Human 可以手工 transport Seed，也可以由 current durable authority 允许的 execution transport 传递；Human copy/paste 不是普通 executor 的治理必经节点。

`DIRECT | DELEGATE` 是执行方式，不产生 authority，也不改变 deploy/destructive/production/irreversible authority。

### 1.1 Durable Dispatch Comment

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

具体机器 gate 由部署实例自己的 control-plane contract 定义。公共 contract 不假设 control plane 一定叫 `ai-hub`，也不指向任何上游维护者的 private repo。

### 1.2 Agent 启动适用顺序

Seed 只提供地址；执行时按 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md`：

`BOOT-1 ADDRESS -> BOOT-2 APPLICABLE RULES -> BOOT-3 EXECUTION GATE -> EXECUTION_ALLOWED`。

关键顺序：

- `BOOT-1A` 解析 generic `<owner>/<repo>` pointer 与 access route；private 首读优先已授权 native GitHub，失败再 authenticated `gh`，禁止匿名公网 404 探路；
- `BOOT-1B/1C` 在 `BOOT-2A` 前只做 address/currentness，不提前适用任务正文；
- `BOOT-2A` 加载**current governance repo 的 `AGENTS.md`**；fork/clone/自建 deployment 不返回固定上游 owner/repo；
- `BOOT-2B` 再加载 target repo/project local context；
- `BOOT-2C` 才规范性适用 current Work Order / Dispatch / latest ruling；
- 任一关键 gate 未通过时不得 execution。

### 1.3 DIRECT / DELEGATE boundary

Architect 选择执行模式前必须以 current durable authority 与 pre-existing acceptance 为准。

`DIRECT` 不得用于：

- acceptance 尚未冻结、需要边做边定义需求的探索性施工；
- current contract 明确 `DELEGATE_REQUIRED` / separation-of-duties；
- Human Hold / Incident / security / permission conflict；
- 未授权 production/deploy/destructive/irreversible external action。

`DELEGATE` 适合长时间/大量施工、并发、专门工具/环境、需要独立实现者降低 confirmation bias 等工作。

### 1.4 Architect continuous advancement

Project Architect / Global Architect 默认 `CONTINUE_WITHIN_AUTHORITY`。Human message 不是 scheduling clock；没有新 prompt 本身不构成 blocker。

同一 current authorized objective/program 内，只要 next step 仍被 authority、scope/acceptance、dependency 与 risk gates 覆盖，Architect 应继续普通行政与施工编排：materialize Work Order/dispatch、收到 delivery 后 Review、Repair/re-dispatch、ordinary exact-head merge、dependency activation、lifecycle convergence。

Continuous advancement 不产生 authority。新增/改变 Human goal、产品取舍、priority、acceptance、material scope/cross-project authority，或 Human Hold / secret / physical-device / production-destructive-irreversible authority gap / BLOCKER / Incident / security-permission conflict / `HEAD_MOVED` / authority ambiguity 时必须停 Human / higher authority。no READY work 或 explicit stop condition 也应停止。

Fresh/takeover Architect 不得因为历史 playbook 写着“先给 Human 确认”就机械等待；以 current L0 + current Bootstrap continuation classification 为准。

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

- `CLOUD_ONLY` — 不依赖 local checkout/toolchain、private node/network、real device、local daemon/long-running process 或 physical interaction；实际 connector/tool capability 仍须启动验证。
- `LOCAL_REQUIRED` — 必须使用本地 filesystem/workspace/toolchain/process/runtime，但不要求特定 node。
- `NODE_REQUIRED` — 必须进入指定 managed/execution node 或 private-network path。
- `DEVICE_REQUIRED` — 必须访问真实 phone/tablet/其它 device 或 device-control path。
- `MIXED` — 有有意义的 cloud tranche，但最终 acceptance 依赖 local/node/device evidence；应优先拆 cloud tranche。
- `UNKNOWN` — current evidence 不足以真实分类；不得因为任务看起来只是文字就默认 `CLOUD_ONLY`。

关键边界：

- `CLOUD_ONLY != CAPABILITY_OR_AUTHORITY_GRANT`；
- secret/Human/physical confirmation gate 独立存在；
- dependency taxonomy 是公开通用语义，不写具体 provider/model/价格/quota。

### 2.2 Generic 示例

```text
任务: <control-plane-repo>#<issue> / routing + docs 收敛
为什么做: 旧治理映射与 current public contract 不一致
你要做什么: targeted GitHub 核验、文档同步、exact diff readback
执行依赖: CLOUD_ONLY — authenticated GitHub R/W + Web
调度建议: 上下文 Medium；文档编辑 + targeted GitHub 核验；可单 delegated executor 完成
本轮终点: 提交 PR，报告 exact head + 验证结果后停止，等 Architect Review
```

Human Card 是用户决策提示 / 手工 transport UX，不是 Agent 指令或状态源，也不是所有 delegated execution 的必经治理节点。

兼容性：2.1.0 canonical compilation 之前 durable 产生的五字段 Human Card 保持历史 provenance 有效；之后的新 Card 使用六字段顺序。

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

如果 target 是 deployment-local control plane，repo coordinate 应从 `workspace_registry.control_plane.repo`（或等价 deployment registration）取得；**不得把示例中的 `ai-hub`、`../hub` 或某个上游维护者账号当 fixed address。**

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

### 3.4 访问路由

`access: github-private | github-public` 只描述 BOOT-1A 的访问类别，不承载任务合同，也不授予 authority。

访问优先级：

1. 当前 Agent / 宿主已授权 native GitHub capability；
2. authenticated `gh`；
3. remote exact-ref 校验后的 local Git workspace；
4. 仅 `github-public` 必要时可回退公开 HTTPS。

`github-private` 的匿名 `404` 不是 repo/permission durable evidence。native GitHub 与 authenticated `gh` 都不可用时，报告 `ACCESS_BLOCKED` / `ACCESS_DRIFT`。

`Capability != Authority`。

---

## 4. Human Completion Card

Agent 完成后，Builder / Research / Repair / Verifier 保持详细 durable report。Human Completion Card 恰好五个语义：

| # | 字段 | 内容 |
|---|---|---|
| 1 | 结果 | 完成情况 |
| 2 | 交付 | 交付物 + 精确可恢复指针（PR / commit / exact head / durable report pointer） |
| 3 | 验证 | 验证方法与结果 |
| 4 | 剩余风险 | 已知风险 / 未覆盖区域 |
| 5 | 下一步 | 建议的后续动作 |

面向 Human 的叙述默认简体中文；code/path/SHA/protocol constant 保留原文。英文 Work Order / template / header 本身不构成 language override。

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

- `2.1.0`：编译 Architect `CONTINUE_WITHIN_AUTHORITY` 与 Human Dispatch Card `执行依赖` 六字段语义。
- `2.1.1`：public portability hardening；移除 maintainer-specific repo coordinate，明确 current governance repo / deployment-local control-plane role indirection；不改变 `DIRECT | DELEGATE`、authority、dependency taxonomy 或 Completion Card 语义。
