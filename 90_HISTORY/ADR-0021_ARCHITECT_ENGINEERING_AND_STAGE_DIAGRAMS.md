# ADR-0021 — 以软件工程边界与阶段图示约束 Architect 的局部最优

- Status: Human direction accepted in [ai-use #177](https://github.com/youling/ai-use/issues/177); normative adoption pending exact-head PR Review/merge
- Decision level: L2 — cross-project architecture practice / diagram-driven stage communication
- Decision date: 2026-10-24
- Canonical engineering method: [软件架构与工程实践](../30_PROTOCOLS/SOFTWARE_ARCHITECTURE_PRACTICE.md)
- Canonical diagram/progress semantics: [Diagram-as-Code §3.1](../30_PROTOCOLS/DIAGRAM_AS_CODE.md#31-阶段性进展图示与领域边界复盘)

## 问题与依据

复杂软件工程的难点通常不在某一个函数怎么写，而在正确识别领域、职责归属、变化原因、依赖方向、稳定接口和持久事实来源。即使模型可以迅速生成大量正确代码，也可能优先采用对当前上下文最顺手的代码组织方式，积累隐性耦合和维护负担。

纯文字阶段总结可能掩盖跨模块依赖、来源和业务语义混淆、重复写入权或未证实的“完成”状态。Human 明确要求架构师在重要阶段把进展画出来，让结构与未知项必须能够被别人理解；这是一种外显推理、复盘和交接的辅助手段，并不自动证明领域已正确划分。

## 裁决

1. **Architect 负责解释系统如何拆分**：以变化原因、内聚/耦合、接口契约、状态 owner 和替换影响为线索，而不是以文件数量、框架习惯或某种流行模式代替设计。Foreman 按已授权边界实施，发现缺陷则挑战。
2. **重要架构阶段 MUST 图示化总结**：在当前 GitHub Work/PR/checkpoint 中引用阶段图源，采取 `CREATE | UPDATE | REUSE_CURRENT`，描述领域/依赖/数据流、相对上阶段的可核验变化、剩余 UNKNOWN/gate 和下一步。小型窄修复可标 `NOT_APPLICABLE` 加理由。
3. **图是 DERIVED 推理/导航，不是事实权威**：current canonical code/contracts/Issue/PR 优先；图源必须 Git 可 diff 或有等价机器可读的 owner source，动态信息有 source revision 和核验窗口，不虚构完成比例或将漂亮渲染等同语义通过。
4. **软件工程方法与画图机制分属唯一 canonical homes**：软件工程方法归 `SOFTWARE_ARCHITECTURE_PRACTICE.md`，图的形态和阶段图归既有 `DIAGRAM_AS_CODE.md`。Agent Interface 和 routing 只给角色入口，不复制下层方法。
5. **风险适配**：保持 Project Architect 自治、不引入额外审批角色；不全项目强制 DDD/六边形/微服务/固定层数、统一语言或 renderer；选用实际需要的 fitness checks。
6. **推进与纠错**：阶段图应尽早暴露逆向依赖、重复真值与未明确 owner，随后通过 exact code/diff/test/source 验证、修复或明确 UNKNOWN。可以复用当前图加变化说明，不为每次 checkpoint 重复制图。

## 被否决的替代方案

- **只给各 Agent 背 SOLID/DDD 术语**：可能增加描述而不改变实际代码边界，缺少对变化影响的检验。
- **为每个函数/小修复强制出全景图**：增加审查负担、让图表沦为仪式。
- **某个 renderer 的成功就是架构验收**：只检查画法/排版，不能证明模块耦合、source currentness 或授权正确。
- **按数据库/文件/服务数量划分业务领域**：实现载体不等于领域语义，容易产生重复写入权。
- **创建新的进展图状态库**：违反 GitHub/owner-native 现有 durable Work 的 SSOT 边界。

## 反例与向后兼容

- 只拆成几个文件却存在循环 import 和共享可变全局状态 → 不合格；图/依赖检查必须暴露真实耦合。
- 来源记录、不可变证据与业务解释被画作同一 canonical owner → 回到真实数据语义检查；不能用图重定义 owner。
- 图显示“已完成”，实际上只有模型自述、无 PR/test/readback → 应标为候选或 UNKNOWN，不得升级验收。
- 已有 current 完整图，本阶段只新增局部验证 → 引用现有图并说明 delta，即满足复盘，不要求新建一份。
- 单文件修复没有领域边界变化 → 沿用普通 Review/测试，不增加新画图门槛。
- 后来实测推翻本阶段图 → 保留旧图的 historical provenance，按 owner source 修复派生图而非覆盖事实。

本裁决是对现行图示治理和架构师角色职责的**增量扩展**，不重写历史 Work/Claim/Diagram，不自动触发任何项目的重构、部署、合并或额外数据访问。下一阶段需要在真实项目上检验这项复盘是否实际减少重复实现与边界误判，不能仅凭文件落地宣称有效。
