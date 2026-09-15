# ADR-0002：Context Lifecycle v0.1（Work Context 执行连续性）

状态：Accepted
来源 Issue：#60
相关预研：#59
相关评审：`ai-hub#143#issuecomment-5667145750`
相关裁决：`ai-use#59#issuecomment-5667150159`
相关输入：`ai-use#60#issuecomment-5669586389`（Global Architect seed review，`ACCEPT_WITH_REVISION`）；`ai-use#60#issuecomment-5670052669`（control-plane subagent research，provenance 保持 `NON_NORMATIVE`，其中 vendor-neutral subagent 原则经 PR #61 exact-head review `5210913953` / adjudication `5210917887` 明确接受为 #60 normative extension 后才进入本 Decision 第 10 条）

## Context

Fleet 真实工作 lineage（`fleet#90 / PR #92`）出现可复现的执行缺陷：同一 worktree 内测试未全绿、Builder 知道下一步、无 Human gate、无 authority blocker，仍结束当前 turn 等待 Human 发送“继续”。执行 surface 把“本轮有一个合理中间结果”误当成“任务允许结束”。

`#59` 确认这不是缺少项目知识，而是执行接口没有充分表达 session affinity、mode switch、completion boundary 与 `PREMATURE_YIELD`。Human prompt 被误用为 scheduling clock；“切角色”被机械实现为“换会话”，导致昂贵 rehydration；warm session 被误用为 truth 或 independence 证据。

本次裁决只做 vendor-neutral governance，不做 runtime 实现，不改 ai-hub / Fleet schema，不做 provider 集成。

## Decision

1. `Role/Mode != Context != Authority/Independence`。mode 不自动要求换 context；换 context 不产生 authority。machine 语义正交拆分为 `context_policy / mode / continuation / independence`，另加最小 `delegation / parallelism` 缝合；Human-facing 可保留 `FRESH_VERIFY` 等 convenience label，但 machine 不把三者混成单枚举。
2. 同一 implementation lineage 默认 `WARM_RESUME`：`PLAN -> BUILD -> TEST -> REPAIR -> SELF_REVIEW -> REPAIR` 优先复用 current owned warm context；明确 review finding 回流后优先由原 executor 修，不为角色仪式重复 rehydration。
3. Fresh context 默认主要用于 independence 场景：independent verification、security / permission boundary review、high-risk final acceptance、adversarial review、context contamination / unrelated new work、true parallel work；恢复路径同样是 fresh 触发：warm context missing / invalid（`CONTEXT_UNAVAILABLE`）时从 durable checkpoint / current state 做 `FRESH_CONTEXT` 重建。不得因 warm 方便取消 current contract 已要求的 fresh independent verification。
4. `PREMATURE_YIELD` 是 retryable execution failure class，不是合法 stop：`acceptance_not_met AND no_real_stop_gate AND legal_next_action_exists AND executor_yielded => PREMATURE_YIELD`。真实合法 stop gate 至少包括以下 canonical classes（可扩展，但扩展 class 必须 fail-closed，且不得把 ordinary repair input 升格为 Human gate）：`REAL_HUMAN_GATE | AUTHORITY_BLOCKED | SECURITY_OR_DESTRUCTIVE_GATE | DEPENDENCY_BLOCKED | UNRECOVERABLE_EXECUTOR_FAILURE`。普通 test / lint / typecheck / red CI、已知 review finding、可在当前 scope 内修复的代码错误是 repair input。
5. Completion boundary 不新造第二套 acceptance：executor goal / stop predicate 必须从 current durable Work Order acceptance 编译；只有本任务 acceptance 要求的 deterministic checks / currentness / commit-push / exact-head / evidence 均满足，才可 `COMPLETION_REACHED`。不适用项不得凭模板被强制创造。executor 自述 `done / completed` 只是 observation。
6. `Warm while useful; durable before fragile; fresh when independence matters.` Warm context 是 working memory / cache，不是 truth。context compaction、provider / backend handoff、session termination / replacement、workspace ownership transition、long-running crash 风险前必须先建 current durable checkpoint。
7. Provider neutrality：产品命令（`/goal`、`/resume`、`/review`、subagent / custom command 等）不进 Kernel / canonical semantics；ai-use 只定义 goal / completion / mode / context semantics，provider adapter 自己映射。`PROVIDER_COMMAND_IS_AUTHORITY = NO`。
8. Seed 保持最小寻址：durable Work Order / dispatch 是任务 truth；Seed 只寻址与 context affinity。保留 `DISPATCH_PAIR.md` 职责，仅加指向新模板的 targeted pointer。允许一行可选 `执行意图：<mode/context intent>；按 current durable acceptance 持续到对应 boundary`，只说明唤醒原因，不复制 tests / scope / 安全 gate / stop。`SEED_SECOND_SSOT = NO`。
9. 安全与独立性冻结：`FORK_CONTEXT != FRESH_CONTEXT`；`SELF_REVIEW != FRESH_VERIFY`；`COMPACT_SAME_CONTEXT` 前执行 durable checkpoint，摘要不覆盖 GitHub current truth；`SIDE_CONTEXT` / subagent 结果可回流但不转移 Work ownership / authority；provider 不支持目标动作时 fail closed。
10. Subagent 是隔离与并行机制，不是 authority 来源，也不是默认 mode 切换方式：`MAIN_CONTEXT_OWNS_WORK = YES`；`SUBAGENT_RESULT = evidence/summary/pointer`；`MODE_CHANGE != SPAWN_SUBAGENT`；`SAME_LINEAGE_REPAIR = WARM_PRIMARY_BY_DEFAULT`；读多并行优先，写并行必须隔离 workspace 或拒绝；默认拒绝嵌套 subagent。`SUBAGENT_IS_FRESH_VERIFY_BY_DEFAULT = NO`。
11. 落点收敛：`docs/AGENT_INTERFACE.md`（continuation / `PREMATURE_YIELD` / completion boundary / 可选执行意图说明）；`docs/SESSION_LIFECYCLE.md`（Work Context lifecycle / `durable-before-fragile` / fresh triggers / 正交组合关系，reconcile 后仍是 compatibility playbook 而非 bootstrap authority）；`50_TEMPLATES/CONTEXT_MODE_SEED.md`（vendor-neutral 可复制 contract）；`DISPATCH_PAIR.md` 只加 pointer；`READING_MAP.md` 只加 targeted routing。L0 `AGENTS.md` 不扩写。

HOLD（明确非规范）：具体 provider slash command 名、context token / length 数值阈值、自动 provider scoring / marketplace、永久 project-wide immortal session、warm context 替代 exact-head / fresh independent verification、scheduler authority 扩张。

## Alternatives

### A. 用一张扁平 command 表表达 context / mode

未采用。把 context policy、mode、independence 混成不可组合的单枚举后，`FRESH_VERIFY`、普通修复、side research 无法正交表达，adapter 只能按命令名猜 capability。

### B. 把“核心目标”作为 Seed 默认必填字段

未采用。每次把 candidate PR exact head / tests all green 重写进 Seed 会形成第二份 task contract，违反 Seed 只寻址原则；改为可选语义意图行。

### C. 同一 Project 永久绑定一个无限增长 session

未采用。避免把 session memory 提升为 durable truth；长期 Project Architect Context 与短 / 中寿命 Work Context 分离，Work 完成后归档或 compact。

### D. provider 命令进入 canonical semantics

未采用。2026-09-15 复核确认 ChatGPT / Codex 与 OpenCode 命令面仍在演进（如 Codex `/fork` 复制 local chat、OpenCode `subagent: true` 与 Plan `ask` 权限语义），canonical 若绑定命令名会随 provider 漂移；只允许 freshness-marked informative 示例，机器映射由 deployment / control-plane adapter 持有。

### E. 切角色即换会话 / spawn subagent

未采用。同一 lineage 内切 mode 默认 inline primary；subagent 只用于有界且实质独立的工作单元，默认不用于 `BUILD -> REPAIR / SELF_REVIEW`、finding 回流或单测变红。

## Consequences

正向：

- 同一 lineage 消除为仪式付出的 rehydration 成本，`PREMATURE_YIELD` 可被机械识别为 repair input；
- completion 与 independence 仍绑定 durable acceptance 与 exact-head / fresh evidence，不因 warm 方便被稀释；
- provider 演进只影响 adapter，不污染 vendor-neutral governance；
- control-plane 可直接消费 `CONTEXT_MODE_SEED.md` 的正交 seam，无需第二 task DB。

代价：

- executor / scheduler 必须实现 `PREMATURE_YIELD` 判据与 durable-before-fragile checkpoint，不能只靠“等 Human 继续”；
- fresh verification 的独立性举证责任仍在 adapter / verifier，不能从 fork / subagent 会话名推导；
- provider 行为变化时 informative 示例需刷新 freshness 标记，否则视为过期证据。

## Supersedes / Superseded by

无。本 ADR 不改写 `ADR-0001`；`SESSION_LIFECYCLE.md` 早期模板与本裁决冲突处以后者为准，并按正文 reconcile 说明标记 historical 参考。
