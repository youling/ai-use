# ADR-0023 — Fresh Architect 冷启动后执行有界 Issue 主题收敛

- **Status:** Human ruling accepted in [ai-use #167](https://github.com/youling/ai-use/issues/167#issuecomment-6688308326); normative adoption pending exact-head review and merge
- **Decision level:** L2 targeted cross-project coordination and Work-entry hygiene
- **Canonical Issue mechanics:** [GitHub Native First §4.2](../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md#42-冷启动后的-issue-主题收敛少入口不丢原子-work)
- **Trigger pointer:** [Bootstrap — post-cold-start Issue convergence](../10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md#architect-cold-start-后的-issue-收敛)
- **Historical pilot:** [ai-use #167](https://github.com/youling/ai-use/issues/167)
- **Decision:** 2026-11-06

## 发生了什么

长期多人/多模型协作中，相同产品目标可能因不同日期、代理商、模型会话和架构师注意力偏移而产生许多相近的 Issues。即使每份 Issue 都有真实证据，新 Architect 冷启动时若没有少量可恢复的主题入口，依旧会花大量时间在重复路径、旧路线、被替代计划间推断最新事实。旧界面/标签不会自动展示其余 Issue 的真正有效性。

之前已有“**一个主题入口 + 若干原子 Work/评论 lane**”的 owner-local 实测：精简索引、原生关系和标签能够减少寻址成本；但**同一 Topic 并行 Foreman claim/锁的完整模型没有通过实测**，不能机械把所有独立 Issue 变为同一个可写 issue。

## 决策

1. **Fresh/takeover Architect** 在完成既有 BOOT-1/2/3、durable writeback、必要 ARCH-0 后，对**本次 target project/program 已恢复的 active Work 邻域**执行一次轻量主题查重/收敛。它是 post-bootstrap follow-through，不追加 bootstrap gate，不要求整仓/全工作空间扫描。
2. 保持 Project Architect 对自己项目的原子 Work、依赖、owner、Review 和 Issue 处置权。Global Architect 只处理治理或已有跨项目授权的问题。Foreman 不借“整理工作”取代其它 Work owner。
3. 使用已有 GitHub Issues、native parent/subissue/blocked-by、PR/Development、comment/pointer 形成**唯一当前主题入口 + 原有原子 Work 证据链**；不建立第二 Work DB、工单生命周期、全局层级或强制合并编号。
4. 只有经过当前实际 source/claim/PR/验收核实、没有独立有效 Work 或归属冲突，才能在留 canonical/反向指针后按当前权限关闭证明为重复的 Issue。不要通过关闭 Issue 冒称实际产品完成、取消正在执行的 attempt 或提升其它任务 acceptance。
5. 目标是**有效入口数量减少和恢复成本降低**，不是 OPEN Issue 数字越低越好。搜索不完整/缺访问权限/未知 owner 时明确 UNKNOWN；旧唯一原始证据和执行历史仍应保留。
6. 同样的定向去重在**创建新 Issue 前**也适用，但普通小修和已有一条清晰 current Work 时不额外增加规范仪式。

## 不采纳

- **冷启动先扫描所有开放 Issues 才允许执行**：会把认知恢复变成冗长项目审计，并打断正常 READY 工作。
- **把所有相似 Issue 合并为一个 Issue**：不同 owner、独立交付/验收、在途 claim、PR review 和 host 互斥无法靠标题等同。
- **自动关闭所有过期/未更新 Issue**：OPEN/活动时间不能直接推出权责、有效性或可删除性。
- **让一个新监工/中央 Agent 管所有状态**：继续用各项目 Architect + Foreman/Subagent 与现有 GitHub 原生关系；不要集中详细施工上下文。
- **建立全局镜像数据库/任务 ID 迁移**：破坏 GitHub native durable truth、权限和历史工作坐标。

## 兼容与待验

本决策只添加 post-bootstrap 的定向工作法，不改变已有 BOOT 三段、`EXECUTION_ALLOWED`、`ARCHITECT_READY`、Work Coordinate、attempt lifecycle、claim、PR Review、权限或人类主权。旧 Issue/历史评论/PR 仍有效；自然适用时可加源指针/精简索引，**不追溯 mass migration**。

验收反例：在同一个 topic 下有两个独立写域、两份有效的 Foreman 任务，不能因为标题相近自动关闭其中一个；搜索只返回第一页时，不得宣布没有其它任务；仅有旧截图和历史记录但 source still unique 的 Issue 不能删除；跨项目任务由两个 Architect 管理，不能因总架构师可读取就改写另一个 owner 的 Issue。

**独立缺口：** 这不等于已实现 `Change-aware Work Graph`。变更影响传播、受影响下游任务的重新规划与失效验收的自动计算，仍归对应 control-plane owner 的独立实现/验证，不因 issue topic index 进度而被虚报已完成。
