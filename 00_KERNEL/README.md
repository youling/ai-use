# 00_KERNEL

Kernel 层：zero-prompt navigation chain 的第一个逻辑阶段，承载稳定规则与核心治理不变量。

准备执行/恢复/接管时，`00_KERNEL` 的**必经入口**是 governance repo 根目录的 `../AGENTS.md`（机器 L0）。加载 L0 后，Agent 不需要等待 Human 再提示下一份文档；按 `../NAMESPACE.md` 的链式路由和 `../READING_MAP.md` 的场景触发继续。

这不表示必须通读本目录：除 `../AGENTS.md` 外，其它 Kernel 文档仍只在场景命中时 targeted 读取。

包含：

- 机器 L0 规则（`../AGENTS.md`）
- 治理宪法（`../CONSTITUTION.md`）
- zero-prompt 链式路由（`../NAMESPACE.md`）
- 阅读/触发索引（`../READING_MAP.md`）
- 人类可见输出规范（`LANGUAGE_POLICY.md`）

本层不替代 `AGENTS.md`；`AGENTS.md` 仍是机器 L0 唯一规范源。Namespace 定义下一跳，Reading Map 决定当前层是 `NEXT | SKIP | STOP_*`。
