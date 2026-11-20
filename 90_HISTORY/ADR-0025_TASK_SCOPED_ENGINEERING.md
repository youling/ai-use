# ADR-0025 — 软件工程原则按开发任务触发

- 状态：Accepted Human direction，正式生效以关联 PR 合并为准；来源：[ai-use #195](https://github.com/youling/ai-use/issues/195)。
- 变更等级：L2；延续 [ADR-0021](ADR-0021_ARCHITECT_ENGINEERING_AND_STAGE_DIAGRAMS.md) 和 [ADR-0024](ADR-0024_PORTABLE_SOFTWARE_RELEASE.md)。
- 当前规范唯一入口：[软件架构与工程实践](../30_PROTOCOLS/SOFTWARE_ARCHITECTURE_PRACTICE.md)；阅读触发由 [Routing Catalog](../ROUTING_CATALOG.yaml) 负责。

## 问题与决定

此前 `software-engineering` 的阅读路由仅匹配 Architect，即使软工原则已明确适用于所有自研软件，实际执行编码、修复、构建的 Foreman/Builder 也可能不加载它。Human 决定：**工程原则属于开发任务的约束，不属于某个职位的专属知识**。

任何承担软件开发或相关代码 Review 的 Agent 均定向阅读并遵守 §2–2.1；只有涉及实质性模块、接口、领域或架构判断时才深入 §3–6。已在当前 Work 中加载仍适用的规则可复用；不为普通小修另做 ARCH-0、全域设计或新审批。非开发任务无需加载。

## 边界与取舍

保留既有架构决策权、Work/派单与验证授权；遵守工程原则不授权末端执行者推翻已批准架构。没有新增角色、L0、第二份手册、固定模板或新的审核状态。相较仅对 Architect 生效，此变化会增加开发执行者的必要定向阅读，但可避免局部通过、长期耦合恶化。由现有 L2 路由与原规范共同承载；后续变更仍走正常 docs-as-code 生命周期。
