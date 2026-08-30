# 00_KERNEL

Kernel 层是 zero-prompt cold-start chain 的第一个逻辑阶段，也是 lower-layer fault 出现时仍可依赖的**最小判断基座**。

准备执行 / 恢复 / 接管时，`00_KERNEL` 的必经入口是 current governance repo 根目录的 `../AGENTS.md`。L0 current-load 后，Agent 不等待 Human 逐跳提示；按 `../NAMESPACE.md` + `../READING_MAP.md` targeted 扩展。

这不表示通读本目录：除 `../AGENTS.md` 外，其它文档仍按 scene trigger 读取。

## Kernel ABI freeze

`AGENTS.md 3.0.0` 起，L0 按 microkernel residency 管理。Kernel ABI 只要求 Agent 在 lower layer 缺失、陈旧、冲突或错误时仍保有以下判断能力：

1. Human sovereignty + authority hierarchy；
2. `Capability != Authority`；
3. durable truth + currentness；
4. scope + no silent authority expansion；
5. fail closed；
6. zero-prompt continuation；
7. evidence-bound mutation。

详细流程、枚举、provider/tool 适配、role-specific mechanics、long examples 与 replaceable policy 不因“重要”就进入 L0；它们进入自己的 canonical driver/protocol/reference，由 L0 只保留 invariant + stable pointer。

## Kernel residency test

新增或回迁 L0 前必须做反事实测试：

> 如果删掉这条，而 lower layer 随后给出 stale / conflicting / hostile input，Agent 是否会失去识别错误所必需的 identity / authority / truth / scope / fail-closed 判断能力？

只有答案为“会”，才默认允许 Kernel residency。

`importance != kernel residency`。

## One semantic, one canonical home

- Kernel primitive -> `../AGENTS.md`；
- governance hierarchy / merge principle / verification / Incident -> `../CONSTITUTION.md`；
- Bootstrap / access mechanics -> `../10_BOOT/`；
- execution / dispatch / continuation -> `../docs/AGENT_INTERFACE.md`；
- Architect reconnaissance -> `../docs/ARCHITECT_RECONNAISSANCE.md`；
- durable trace mechanics -> `../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md`；
- language details -> `LANGUAGE_POLICY.md`；
- routing -> `../NAMESPACE.md` + `../READING_MAP.md`。

其它文档引用这些 semantics 时只写必要 invariant / summary / pointer，不复制完整 mechanics。

## Fault containment

- lower-layer fault 可阻塞当前 task，但不得反向改写已建立的 Kernel identity / authority / durable-truth / scope / fail-closed model；
- lower layer 与 L0 冲突时，先判 currentness/authority/applicability，再 `SKIP | isolate | supersede | STOP_BLOCKED`；
- 只有 Kernel 本身无法 current-load / 校验时，才属于 cold-start root failure。

本目录不替代 `AGENTS.md`。Namespace 决定默认下一跳，Reading Map 决定当前层 `NEXT | SKIP | STOP_*`。
