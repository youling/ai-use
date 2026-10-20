# ADR-0019 — GitHub 原生可见任务池与人机自助协作

- Status: Proposed; Human direction in [#167](https://github.com/youling/ai-use/issues/167); current normative authority requires reviewed PR/merge
- Decision level: L2 cross-project visibility contract
- Canonical semantics: [GitHub Native First §4.1](../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md#41-任务自助发现issue--labels--saved-views--projects)
- Adoption: project-local, within existing Architect/Foreman ownership

## Why

Human 指出复杂项目协作的关键不只是权限和 Agent 自动化，而是**共享情境、可见分工、自主寻找下一件事情**。若每个参与者都得等人逐次口头询问，任务会在等待后被遗忘；长期目标是让人和 AI 像成熟组织成员一样通过当前工作视图作出有根据的主动选择，而不是靠中心调度员逐项转达。

旧 Issue 多已写优先级、状态和下一步，却未充分利用原生 Labels、Issues Saved Views、Projects、依赖关系；文本 OPEN 与真实有效 claim/terminal 可以不同步。

## Decision

- 复用 owner Issue/PR/durable Work 为执行真值；标签、Saved Views、个人私有 Project 只是可核查、可刷新且可回源的**任务运营投影**。
- 支持独立的执行阶段、优先级、类型、长程属性、工作量和最小执行环境，让 Human 按当前供应商额度挑工作；不把模型/provider 指定写成永久任务要求。
- 优先盘点真实 Work，明确“下一步/Next actor/证据”；区分尚待实际派发、有效 dispatch 待真实 Claim、已有活跃 Claim、需独立验证/裁决、真实阻塞与暂缓未知；不根据 Issue Open 猜测。
- 先仓库级 labels/个人 saved views，再选择性收录跨仓库私有 Project；自动化只有在降低真实管理成本时才采用单向来源同步。不新建任务数据库、控制平面或审批角色。
- Human 可调整排程，但 Project 拖卡/贴标签不等于 Work lifecycle 授权；私有实例的标签、Project、实际任务事实和权限仍归项目/部署 owner。

## Alternatives

拒绝「每人都等架构师口头指导」「每个 GitHub Project 成为第二套状态真值」「按标题/Issue Open 批量填可领」「为所有旧 Issue 建新工单」。前者消耗调度时间，后几者会制造重复 owner 和误派工。

## Counterexamples / compatibility

- 同一 OPEN Issue 的旧 PARTIAL 已接受但无新 dispatch，不得贴 `待认领`；随后存在 current 有效 CLAIM 应贴 `执行中`。
- GitHub 登录 assignee 是同一个人但不同逻辑 Agent 在途，不可据 assignee 夺取 Work。
- PRIVATE Repo 的事项只出现在 private Project，不得通过 public ai-use Issue 镜像内容。
- Human 调整 P0 可以影响排程，但不等于授予生产操作/机密读取。
- 不修改 L0、现役 Work 状态机或 owner/authority；本 ADR 是理由，具体字段仅由 GitHub Native First 持有。
