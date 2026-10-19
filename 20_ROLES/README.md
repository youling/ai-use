# 20_ROLES — role ownership

角色层定义谁对什么结果负责，不把每种工具动作都设成长期职位。各角色共同服从 Human 当前可验证目标，而不是自身流程/PR/Agent 数量；原则见 [Constitution §2](../CONSTITUTION.md#2-governance-hierarchy)，推进机制见 [Agent Interface §1.4.4](../docs/AGENT_INTERFACE.md) 和 [Foreman](FOREMAN.md)。

- [Constitution §2](../CONSTITUTION.md#2-governance-hierarchy)：Human、Global Architect、Project Architect、Foreman 的职责与权限边界。
- [Architect Discovery role boundary](ARCHITECT_DISCOVERY.md)：穷尽调研与路线选择归 Architect，规范细节引用现有 [Architect Reconnaissance](../docs/ARCHITECT_RECONNAISSANCE.md)。
- [Foreman Role Contract](FOREMAN.md)：工头对受托 Work/有限阶段的完整执行责任、子对话与父级验收原则。
- [Agent Interface](../docs/AGENT_INTERFACE.md)：派发、continuation、PREMATURE_YIELD、terminal 与 Architect Review 的语义 owner。
- [Recovery & Handoff](../30_PROTOCOLS/RECOVERY_HANDOFF.md)：session/context、子对话隔离、独立性和恢复。

工头只有一种，不另设“主工头”。Subagent 是有界执行上下文；历史 Builder / Research / Repair / Verifier 等标签按原 Work 保留 provenance，但在新角色模型中通常是执行模式，而不是平级治理职位。Runner、自动化和调度器是执行设施，不是审批角色。
