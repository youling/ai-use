# GitHub 任务自助发现 — 项目架构师交接词

> 适用于任何已存在的 Project Architect；Human 复制到各自对话时，不必另填表。
> Current governance: [ai-use AGENTS.md](../AGENTS.md) → [GitHub Native First §4.1](../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md#41-任务自助发现issue--labels--saved-views--projects)；全局来源 [#167](https://github.com/youling/ai-use/issues/167)。

请作为你**当前实际拥有的项目仓库**架构师，开展一次 GitHub OPEN 工单的自助可发现性整理。目标是让 Human 和其他 Agent **不用再逐个问你**就能看见：哪些事当前可安排、谁已经在执行、哪里需要复核/裁决、什么是 P0/研究/长程、哪种执行环境和任务规模合适。

**沿用原 Work Graph/工头/claims/PR/write-set，不开平行总工单，不替其他 Architect 改事实。** 先 live revalidate 本仓 OPEN Issues（确认分页/可见范围）；首轮做简短清点，重点定向读取每项最新有效 dispatch、AGENT_CLAIMED、terminal、后续续接/架构师裁决，避免机械重读全部历史评论。

**逐项整理本仓当前任务**：
1. 确认原目标和验收仍成立，写清**下一项具体可执行动作**（谁做、在哪里做、用什么证据确认），并给最小的 current source/PR/评论指针。没有原 owner 授权的候选不得改成可认领。
2. 按 current owner 事实决定状态：`状态:待派发`、`状态:待认领`、`状态:执行中`、`状态:待审计`、`状态:待裁决`、`状态:阻塞`。尚待补齐/暂缓/多分支混合或事实不明的保持未分类并说明原因；Closed 用 GitHub 原生状态，不重新标注。
3. 标注已有 owner 认可的 `优先级:P0/P1/P2`、主要 `类型:研究/实施/验证/运维`，需要时加 `周期:长程`。补充**Effort S/M/L、最低合适执行环境（网页/云端/本地/本地+设备）、Next actor、真实前置依赖**；这些是供 Human 灵活分配供应商额度的提示，不绑定具体模型、不修改原验收。
4. 优先使用本仓 GitHub Labels、Issues Saved Views、原生 Sub-issues/Dependencies 和私有总 Project。标签尚不存在时由有对应权限的 repo owner/执行环境创建；只调整有证据、归你管辖的现有 Issue，保留已有标签和历史评论。不得因 Issue Open、旧标题 P0、收到 terminal 或 Github assignee 直接推断执行状态；不抢有效 claim。
5. 修复明显过期或互相矛盾的下一步指针，短句足够；若跨仓库资源、真实权威或项目阶段待人裁决，就指出**唯一具体需要谁做的决定**，其余授权工作继续。不要为分类制造一批新 Review、安全前置或子任务。

**交付**：在原项目仓中留一条可回读的简短索引/清点回执，报告 OPEN 总数、已核实可领、在途、待审计、待裁决、实际阻塞、长期/研究任务、UNKNOWN/暂缓数量；回链具体 Issue、保留的 owner、尚缺的权限或 GitHub Project 配置动作。对每个状态说清事实来源及核验时间。改过的标签必须回读；没创建的标签/Project 必须如实说明。

本轮完成的是**现有工单可发现性**，不是自动启动执行 Agent，也不是立刻批量处理所有旧 Issue 或在公仓复制私有任务内容。Human 可以据此挑选工作与 Provider；真正启动仍服从当前合法 dispatch/claim。
