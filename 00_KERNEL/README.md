# 00_KERNEL

Kernel 层：zero-prompt cold-start chain 的第一个逻辑阶段，承载稳定规则与核心治理不变量，也是后续层发生错误时的**容错基座**。

准备执行/恢复/接管时，`00_KERNEL` 的**必经入口**是 governance repo 根目录的 `../AGENTS.md`（机器 L0）。加载 L0 后，Agent 不需要等待 Human 再提示下一份文档；按 `../NAMESPACE.md` 的链式路由和 `../READING_MAP.md` 的场景触发继续。

这不表示必须通读本目录：除 `../AGENTS.md` 外，其它 Kernel 文档仍只在场景命中时 targeted 读取。

Kernel-first 的目的不是形式上的“先读一篇”，而是先建立最小可信判断框架：Human sovereignty、identity/authority hierarchy、durable truth、scope/fail-closed、语言与 continuation 等 invariant。一旦这些 invariant current-load 成功，后续 role/protocol/guide/template/history 输入只能细化，不能反向覆盖它们。

## Kernel 设计约束

**内核必须精妙、短小、直接。** L0 只保留“即使后层出错，Agent 仍必须拥有”的最小判断原语，以及进入后续层所需的稳定 pointer；详细流程、枚举、provider/tool 适配、角色专用机制、长示例与可替换 policy 应优先下沉到 L2/L3，并由 L0 用短 invariant + pointer 引用。

判断一条规则是否应进入 L0，可用反事实测试：**如果删掉它，而后层随后给出错误/陈旧输入，Agent 是否会失去识别该错误所必需的身份、authority、truth、scope 或 fail-closed 能力？** 只有答案为“会”的内容才默认属于 Kernel。`重要`、`常用`、`方便` 本身不是进入 L0 的理由。

因此：

- 后层文档陈旧、缺失、冲突或错误时，Agent 应用 Kernel 判断其 currentness / authority / applicability，再选择吸收、`SKIP`、隔离或 `STOP_BLOCKED`；
- 后层故障可以阻塞当前任务，但不应让 Agent 丢失已经建立的身份/authority/durable-truth 判断；
- 只有 Kernel 本身无法 current-load / 校验时，才属于 cold-start root failure，必须 fail closed；
- 这种“先最小内核、后可替换上下文”的顺序是 zero-prompt cold-start 的主要容差来源；
- 新增治理语义时，默认先问“能否作为 L2 机制 + L0 一句 invariant/pointer 表达”，避免 Kernel 随系统功能线性膨胀。

包含：

- 机器 L0 规则（`../AGENTS.md`）
- 治理宪法（`../CONSTITUTION.md`）
- zero-prompt 链式路由（`../NAMESPACE.md`）
- 阅读/触发索引（`../READING_MAP.md`）
- 人类可见输出规范（`LANGUAGE_POLICY.md`）

本层不替代 `AGENTS.md`；`AGENTS.md` 仍是机器 L0 唯一规范源。Namespace 定义下一跳，Reading Map 决定当前层是 `NEXT | SKIP | STOP_*`。
