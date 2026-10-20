# GitHub 任务自助发现 — 项目架构师交接词

> 适用于任何已存在的 Project Architect；Human 复制到各自对话时，不必另填表。
> Current governance: [ai-use AGENTS.md](../AGENTS.md) → [GitHub Native First §4.1](../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md#41-任务自助发现issue--labels--saved-views--projects)；全局来源 [#167](https://github.com/youling/ai-use/issues/167)。

请作为你**当前实际拥有的项目仓库**架构师，开展一次 GitHub OPEN 工单的自助可发现性整理。目标是让 Human 和其他 Agent **不用再逐个问你**就能看见：哪些事当前可安排、谁已经在执行、哪里需要复核/裁决、什么是 P0/研究/长程、哪种执行环境和任务规模合适。

**沿用原 Work Graph/工头/claims/PR/write-set，不开平行总工单，不替其他 Architect 改事实。** 先 live revalidate 本仓 OPEN Issues（确认分页/可见范围）；首轮做简短清点，重点定向读取每项最新有效 dispatch、AGENT_CLAIMED、terminal、后续续接/架构师裁决，避免机械重读全部历史评论。

**逐项整理本仓当前任务**：
1. 确认原目标和验收仍成立，写清**下一项具体可执行动作**（谁做、在哪里做、用什么证据确认），并给最小的 current source/PR/评论指针。没有原 owner 授权的候选不得改成可认领。
2. 按 current owner 事实决定状态：`状态:待派发`、`状态:待认领`、`状态:执行中`、`状态:待审计`、`状态:待裁决`、`状态:阻塞`。尚待补齐/暂缓/多分支混合或事实不明的保持未分类并说明原因；Closed 用 GitHub 原生状态，不重新标注。
3. 标注已有 owner 认可的 `优先级:P0/P1/P2`、主要 `类型:研究/实施/验证/运维`，需要时加 `周期:长程`。补充**Effort S/M/L、最低合适执行环境（网页/云端/本地/本地+设备）、Next actor、真实前置依赖**；这些是供 Human 灵活分配供应商额度的提示，不绑定具体模型、不修改原验收。
4. 优先使用本仓 GitHub Labels、Issues Saved Views、原生 Sub-issues/Dependencies 和私有总 Project。**实际配置标签定义的颜色与说明**：状态色彩鲜明（待派发灰/待认领绿/执行中蓝/待审计紫/待裁决橙/阻塞红），P0 突出，其余类型和长程色调收敛；给 Issue 加标签不等于已设置标签颜色。只调整有证据、归你管辖的现有 Issue，保留已有标签和历史评论；不抢有效 claim。
5. **规划本仓 Milestones**：每个 Milestone 对应同仓一个可验收的交付阶段，明确目标、包含的原子 Issues 和退出条件，真实期限可填、未知不编造；长程父 Issue 可不分配阶段，跨仓路线交由私有 Project。先核对已存在 Milestones 再创建，避免同一交付的 Issue+PR 重复计数。若连接器缺 Label/Milestone API 且宿主 `gh` 无可用登录，先评估已有仓库的一次性 GitHub Actions（repo `GITHUB_TOKEN` + Ubuntu `gh`）是否能在当前授权与预算内完成，成功后原生回读并清理临时 workflow；个人 Saved Views/私有跨仓 Project 仍需用户级能力。实在不可用再记录具体权限或工具缺口。
6. 修复明显过期或互相矛盾的下一步指针，短句足够；若跨仓库资源、真实权威或项目阶段待人裁决，就指出**唯一具体需要谁做的决定**，其余授权工作继续。不要为分类制造一批新 Review、安全前置或子任务。

**交付**：在原项目仓中留一条可回读的简短索引/清点回执，报告 OPEN 总数、已核实可领、在途、待审计、待裁决、实际阻塞、长期/研究任务、UNKNOWN/暂缓数量；回链具体 Issue、保留的 owner、尚缺的权限或 GitHub Project 配置动作。对每个状态说清事实来源及核验时间。改过的标签必须回读，并分别报告 `ISSUE_LABELS_APPLIED / LABEL_COLORS_CONFIGURED / MILESTONES_CREATED / MILESTONES_ASSIGNED / SAVED_VIEWS_CREATED / PRIVATE_PROJECT_CREATED` 是否已验证；未完成的不能冒称落地。

本轮完成的是**现有工单可发现性**，不是自动启动执行 Agent，也不是立刻批量处理所有旧 Issue 或在公仓复制私有任务内容。Human 可以据此挑选工作与 Provider；真正启动仍服从当前合法 dispatch/claim。
