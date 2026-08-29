# Agent Interface — Canonical L2 Reference

**Classification: L2 Targeted Reference.** Only read when dispatching, executing, or reviewing Agent work orders.

**Protocol Version: 2.1.0**

本文编纂 Human 与 Agent 之间的固定接口契约。所有 ai-hub 映射以本文为准；ai-hub 只做自身映射，不重复全文。

---

## 1. Dispatch Structure

执行先区分 `DIRECT | DELEGATE`：

- `DIRECT`：满足 `AGENTS.md` L0 的 Architect Direct Implementation Lane eligibility 时，Architect 自己施工，不需要为了角色仪式创建 Builder dispatch / Agent Seed；仍须遵守 current durable scope/acceptance、deterministic evidence、required Review / merge / Human/high-risk gates。
- `DELEGATE`：由 durable Work Order + Architect dispatch 启动可替换 executor。Human 可以手工 transport Seed，也可以由 current durable authority 允许的执行 transport 传递；Human 不再是普通 executor copy/paste 的治理必经节点。

`DIRECT | DELEGATE` 是执行方式，不产生 authority，也不得携带 provider/model routing 语义到本公共契约或 Minimal Seed。

对 `DELEGATE`，接口由两层组成：

1. **Durable Dispatch Comment** — Architect 在 Work Order 发布的 `ARCHITECT_*_DISPATCH` 评论，携带角色/启动元数据。scope/base/owns/forbidden/acceptance 已在 Work Order 中，dispatch comment 不重复。
2. **Human Dispatch Card** + **Minimal Agent Seed** — 当 Human 负责手工启动 executor 时，Human Card 给用户决策；Seed 给 Agent 寻址。若由授权的 execution transport 启动，仍使用同一 durable dispatch / addressing 语义，但不要求 Human 充当搬运中继。

### 1.1 Durable Dispatch Comment

每次 Agent-facing delegated execution **必须**有一个 current `ARCHITECT_*_DISPATCH` comment。Durable dispatch 携带 task knowledge；Minimal Seed / transport payload 只寻址。

Dispatch comment 的字段由 Architect 按任务需要填写，不强制统一字段集。以下为常见字段参考（非必须全集）：

```text
ARCHITECT_EXECUTOR_DISPATCH
---
work_coordinate: `<owner/repo>#<issue>@<step>`
role: `<Builder | Verifier | Research | Repair | Release>`
startup_mode: `<Fresh Builder | Warm Resume | Fresh Verifier | ...>`
access: `github-private | github-public`
```

Durable Work Order + dispatch layer 携带任务知识；Human seed 只负责寻址。派发前 Architect 必须确认 durable source 足以让 fresh Agent 执行。

### 1.2 Agent 启动适用顺序

Seed 只提供地址；Agent 执行时必须按 `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` 的统一主干完成：

`BOOT-1 ADDRESS -> BOOT-2 APPLICABLE RULES -> BOOT-3 EXECUTION GATE -> EXECUTION_ALLOWED`。

其中：

- `BOOT-1A` 解析 Seed 与 access route；`github-private` 优先当前 Agent / 宿主的已授权原生 GitHub capability，实测不可用时回退 authenticated `gh`；禁止先以匿名公网 URL / raw HTTPS 试探 private repo；
- `BOOT-1B/1C` 在 `BOOT-2A` 前只解析 dispatch / coordinate 的地址与 currentness，**不得提前适用任务正文**；
- `BOOT-2A` 必须先加载 Global L0 `AGENTS.md`；
- `BOOT-2B` 再加载 target repo / project local context；
- `BOOT-2C` 才规范性适用 current Work Order / Dispatch / latest ruling；
- 任一关键 gate 未通过时不得进入 execution。

本节只提供接口 pointer，不复制完整 Bootstrap 协议。

### 1.3 DIRECT / DELEGATE boundary

Architect 选择 `DIRECT | DELEGATE` 前必须以 current durable authority 与 pre-existing acceptance 为准。

`DIRECT` 不得用于：

- acceptance 尚未冻结、需要边做边定义需求的探索性施工；
- current contract 明确 `DELEGATE_REQUIRED` / separation-of-duties；
- Human Hold / Incident / security or permission conflict；
- 未授权 production/deploy/destructive/irreversible external action。

`DELEGATE` 仍是一等路径，适合长时间/大量施工、并发、专门工具/环境、需要独立实现者降低 confirmation bias 等工作。

无论采用哪条路径，都不得把 provider/model 名称、价格、quota 等执行路由事实写进 Minimal Seed 或把它们升级为 Work Order truth。

### 1.4 Architect continuous advancement

Project Architect / Global Architect 的默认 continuation semantic 是 `CONTINUE_WITHIN_AUTHORITY`。Human message / 追问不是 scheduling clock；没有新的 Human prompt 本身不构成 blocker，也不把普通阶段边界自动变成 Human approval gate。

在同一 current authorized objective/program 内，只要 next step 仍被 current authority、scope/acceptance、dependency 与 risk gates 覆盖，Architect 应继续完成普通行政与施工编排，包括：materialize Work Order/dispatch、收到 Builder/Research/Repair delivery 后主动 Review、Review PASS 后按 current merge authority 做 ordinary exact-head merge、dependency gate 解开后 activate 已授权 next READY work、以及 lifecycle/state convergence。

Continuous advancement **不是 authority expansion**。出现需要新增/改变 Human goal、产品取舍、优先级、acceptance、material scope/cross-project authority，或 Human Hold / Human-required input / secret / physical-device / production-destructive-irreversible authority gap / unresolved BLOCKER、Incident、security/permission conflict、`HEAD_MOVED`、authority ambiguity 时，必须停 Human / higher authority。没有 READY work 或 program explicit stop condition 已达也应停止，不虚构下一项工作。

Human-facing ordinary stage report 应优先说明“已推进到哪里 / durable pointer / 现在被什么真实 gate 卡住”，而不是默认以“是否继续？”结尾。

## 2. Human Dispatch Card

Human Dispatch Card 用于**Human 手工启动 delegated executor** 的场景，**恰好六个语义字段**，按以下顺序：

| # | 字段 | 内容 |
|---|------|------|
| 1 | 任务 | 一句话任务标题 |
| 2 | 为什么做 | 背景 / 理由 |
| 3 | 你要做什么 | 本轮工作内容 |
| 4 | 执行依赖 | objective execution-environment dependency；以 canonical class 开头 |
| 5 | 调度建议 | 只给 Human：难度、上下文规模、模型建议、词元/时间粗估、并行策略、本轮重点 |
| 6 | 本轮终点 | 完成边界 / stop condition |

`执行依赖` 与 `调度建议` 必须分离：前者描述任务客观需要什么环境，后者描述 Human 应如何调度。`执行依赖` 不授予 capability / authority，也不得编码 provider/model/price/quota。

### 2.1 Canonical execution dependency classes

`执行依赖` MUST 以以下六类之一开头，并 MAY 在破折号后附最小 capability facts：

- `CLOUD_ONLY` — 完成任务不需要 local checkout/toolchain、private node/network、real device、local daemon/long-running process 或 physical/secret interaction；例如 authenticated GitHub R/W、Web、已授权 connector/MCP 即可满足客观依赖。
- `LOCAL_REQUIRED` — 必须使用本地 filesystem/workspace/toolchain/process/runtime，但不要求特定 Fleet/execution node。
- `NODE_REQUIRED` — 必须进入指定 managed/execution node 或 private-network path。
- `DEVICE_REQUIRED` — 必须访问真实 phone/tablet/其它 device 或 device-control path。
- `MIXED` — 存在有意义的 cloud tranche，但最终 acceptance 还依赖 local/node/device evidence；Architect 应优先拆出 cloud tranche，避免整单长期占用稀缺本地资源。
- `UNKNOWN` — current evidence 不足以真实分类；不得因为任务“看起来只是文字”就默认 `CLOUD_ONLY`。

关键边界：

- `CLOUD_ONLY` 只说明任务**不依赖 local/node/device state**，不保证任意 web Agent 已连接所需 connector/tool；实际 capability 仍须启动时验证。
- `CLOUD_ONLY != CAPABILITY_OR_AUTHORITY_GRANT`；GitHub write / review / merge authority 仍按 current durable authority 独立判断。
- Secret/Human/physical confirmation gate 独立存在；不能为了方便调度把此类任务伪装成 autonomous `CLOUD_ONLY`。
- dependency taxonomy 是公开通用语义，不写具体 provider/model/价格/quota。

### 2.2 示例

```text
任务: ai-hub#50 / routing + docs 收敛
为什么做: 旧治理文档仍残留已经退场的路由/Gate 语义
你要做什么: targeted GitHub 核验、治理文档同步、exact diff readback
执行依赖: CLOUD_ONLY — authenticated GitHub R/W + Web
调度建议: 上下文 Medium；文档编辑 + targeted GitHub 核验；可单 delegated executor 完成
本轮终点: 提交 PR，报告 exact head + 验证结果后停止，等 Architect Review
```

Human Card 是用户决策提示 / 手工 transport UX，不是 Agent 指令、状态源，也不是所有 delegated execution 的必经治理节点，更不是每个阶段的确认卡。

## 3. Default Minimal Agent Seed

Minimal Agent Seed 的目标是**最少无歧义启动信息**，不是固定追求最少行。它只用于 Agent-facing delegated execution；Architect `DIRECT` 自己施工时不制造虚假的 Agent Seed。

### 3.1 Public / access 已无歧义

当目标 repo 为 public，或 exact pointer 已足以无歧义解析访问路由时，默认 Seed 保持三行：

```text
按 `youling/<repo>#<issue>` 的 <DISPATCH_TYPE> comment `<id>` 执行。

work: youling/<repo>#<issue>@<step>
startup_mode: Fresh <Role>
```

### 3.2 Private GitHub canonical seed

private repo 的首次 durable read 依赖 authenticated route，因此 `access: github-private` 是 bootstrap-critical addressing metadata，**必须包含**：

```text
按 `youling/ai-hub#123` 的 `ARCHITECT_BUILD_DISPATCH` comment `456789` 执行。

work: youling/ai-hub#123@step
startup_mode: Fresh Builder
access: github-private
```

这不是把任务合同塞回 Seed；`access` 只告诉 BOOT-1A 目标访问类别。

### 3.3 Seed 允许的最小扩展

只有当 pointer 无法无歧义启动时，才补最少的 bootstrap-critical 精确引用（如 private/public access hint、exact ref）。Seed **不得**复制以下内容：

- role（当 `startup_mode` 已无歧义表达角色时）、scope / acceptance / requirements / reporting / stop；
- Human Card 的 `执行依赖` 或调度建议；
- 启动读取顺序、输入依据/evidence 列表、当前目标、执行步骤、禁止事项或验证清单；
- 难度、词元/时间估计、模型建议等人类调度信息；
- 依赖关系、native relationships；
- Builder 自评、旧 findings、Architect 既往裁决或其他 counted Verifier 输出；
- provider/model/routing/pricing/quota metadata。

若 fresh Agent 仅凭 exact dispatch pointer + 必要 access metadata 无法从 durable source 取得这些事实，说明 Work Order/dispatch 不完整：先修 durable source，再派发。

### 3.4 访问路由

`access: github-private | github-public` 描述 BOOT-1A 的控制面入口路由，不承载任务合同，也不授予 authority。

访问优先级固定为：

1. **当前 Agent / 宿主的已授权原生 GitHub capability**：例如平台内建 GitHub connector / integration / native GitHub tool；若它能 authenticated 读取目标 repo，优先使用。
2. **本机已认证 `gh`**：原生 capability 不存在、未连接或实测失败时回退。
3. **本地 Git workspace**：只作为执行副本；在使用 branch/head/文件事实前必须与 remote exact ref / live metadata 校验，不是首次 SSOT 发现入口。
4. 对 `github-public`，必要时可再回退公开 HTTPS；对 `github-private`，禁止把匿名公网 URL/raw HTTPS 作为首次探路手段。

private repo 的匿名 `404` 不构成 repo 不存在或无权限的 durable 证据。native GitHub 与 authenticated `gh` 都不可用时，报告 `ACCESS_BLOCKED` / `ACCESS_DRIFT`，不得靠陈旧 local clone 或猜测继续。

Capability != Authority：能读 private repo 不代表能施工、Review、merge 或 deploy；authority 在 BOOT-3A 独立验证。

## 4. Human Completion Card

Agent 完成后，Builder/Research/Repair/Verifier 保持详细的持久报告。Human Completion Card **恰好五个语义**：

| # | 字段 | 内容 |
|---|------|------|
| 1 | 结果 | 完成情况 |
| 2 | 交付 | 交付物 + 精确可恢复指针（PR / commit / exact head / durable report pointer） |
| 3 | 验证 | 验证方法与结果 |
| 4 | 剩余风险 | 已知风险 / 未覆盖区域 |
| 5 | 下一步 | 建议的后续动作 |

## 5. Versioned Definitions

- `2.1.0`：分别编译两项已生效治理规则：Architect `CONTINUE_WITHIN_AUTHORITY` continuation semantic（Human prompt 不是 scheduling clock；只在真实 gate 停），以及 Human Dispatch Card `执行依赖` 字段（Card 从五字段升级为六字段；dependency fact 与调度建议分离；不进入 Minimal Seed、不产生 authority）。两项规则保持独立 acceptance。
- `2.0.4`：编译 Architect `DIRECT | DELEGATE` 接口边界；Human Dispatch Card 明确为 Human 手工启动 delegated executor 的 UX，不再是所有 execution transport 的必经层；Minimal Seed 不因 Direct Lane 或自动化 transport 增加 provider/model/routing 字段。
- `2.0.3`：把 Minimal Seed 从“最少行”收敛为“最少无歧义启动信息”；private repo 固定携带 `access: github-private`；BOOT-1A 统一访问顺序为平台原生 GitHub capability → authenticated `gh` → 经 remote 校验后的 local Git workspace，private repo 禁止匿名公网 404 探路。
- `2.0.2`：同步 Bootstrap Ordered Applicability；不改变 Seed 字段，只增加 `BOOT-1 -> BOOT-2 -> BOOT-3` 的启动顺序 pointer，并明确 BOOT-1 不提前适用任务正文。
- `2.0.1`：clarification patch；不增加新的任务知识字段，只强化 Minimal Agent Seed 的唯一职责是 bootstrap addressing，并给出 private GitHub 的最小 `access` 扩展示例。
- Human Dispatch Card 六字段顺序：任务 → 为什么做 → 你要做什么 → 执行依赖 → 调度建议 → 本轮终点。
- `执行依赖` class：`CLOUD_ONLY | LOCAL_REQUIRED | NODE_REQUIRED | DEVICE_REQUIRED | MIXED | UNKNOWN`；dependency fact ≠ scheduling recommendation ≠ capability/authority grant。
- Minimal Agent Seed：public / access 已无歧义时三行；private repo canonical 四行（pointer → work → startup_mode → `access: github-private`）。
- Human Completion Card 五语义：结果 → 交付 → 验证 → 剩余风险 → 下一步。
- Dispatch Comment 携带 task knowledge；Human seed 只携带 addresses / bootstrap-critical access metadata。

## 6. Boundary Conditions

- 本文只定义公开/通用方法论。不包含 ai-hub 私有状态/拓扑/heads/endpoints/secrets。
- 本文不改变 Runner/程序行为，也不定义 provider/backend routing contract。
- `ARCHITECT_*_DISPATCH` comment 在 Human seed / delegated transport 之前；seed 不替代 dispatch comment。
- 派发前 Architect 必须确认 durable source 足以让 fresh Agent 执行（见 Work Order 完整性要求）。
- Human Dispatch Card 只属于 Human 手工 transport / scheduling UX；authorized automated transport 不需要先生成 Human Card 才能运行。
- Architect continuous advancement 只适用于 Project/Global Architect current durable authority 内；不得扩展为 Builder/Research/Repair/Verifier 的长期自治或 merge authority。
- 人类可见叙述的语言遵守 `AGENTS.md` L0 invariant；英文任务/模板本身不构成 language override。
