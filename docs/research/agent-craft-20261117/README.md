# Agent Craft / 工艺师：横向职责与可验证工艺循环（2026-11-17）

> **NON-NORMATIVE / PUBLIC-SAFE / RESEARCH CANDIDATE**。本报告只提出候选方法与合成评估，不修改 L0、角色权限、部署合同或现有 Work。没有对任何真实用户工作流、私有 Run、供应商配额或本机 ZCode 安装做新实测；一线事实仅以匿名失败类别呈现。

## 裁决建议

**接受“工艺师”作为可兼任的横向技术责任，不接受新增审批层、自动授予 Host/凭据/项目写权。** 其独立性是可以提出工具改进问题、维护可复现实验、交付版本化 Skill，使用原 owner 的真实现场回归来判断是否值得推广。项目 Owner 仍决定具体采用和生产验收，ai-use 只归纳跨工具/跨项目通用原则。

两条循环复用同一 GitHub Work/Claim/Review/Checkpoint/Terminal，不创建第二个任务账：

- **交付循环**：Human outcome → 当前 Work → Foreman 施工 → 独立验证 → 产品接受。
- **工艺循环**：一线失败/能力疑问 → 工艺候选 → 版本/实现差异检验 → 合成正负控 → 当前 owner 的现场回归 → Skill 版本修订 → 具名消费者采用/拒绝 → 回读是否真的改善。

研究不应强迫本地工头暂停产品工作，也不得以“主动研究自身 Harness”为由绕过供应商限流、身份、授权或客户数据边界。

## 本次正向和反向核验

**本次已读取的公共基线**：ZCode 开源 main @ fec975905a2abd4c07e35c40d51fa097a2258ec9（源仓称 v3.18.2）。该版本的官方动态工作流 Skill、Cron handler、后台 Run 追踪/恢复代码已检查；**并未读取用户设备上安装的确切版本，也未复跑私有 DWF**。被审阅的补充 Skill 为用户提供的 dwf-max-orchestration v1.5.0，不在本公共仓复制原件与私有运行台账。

| 观察或主张 | 证据等级 | 对工艺版本的处理 |
| --- | --- | --- |
| 历史实测达到 16 路并发；24 配置接受 | OWNER-REPORTED HISTORY | 保留历史标定，不作为动态配额下的当前配置目标；配置接受 ≠ 真实运行峰值 |
| 通知未独立触发下一轮、波间空窗 | OWNER-REPORTED HISTORY | 记录为通知/唤醒/消费链某一环未闭合；须分别观察 run terminal、通知生成、通知投递、模型实际 wake 与补池；不得无证据锁定单个函数 |
| “醒来先对账、再补 READY” | CANDIDATE OPERATING RULE | 值得试验；通知只是 hint，Run/Owner 的 live state 才是事实，补池必须先经过 authority/READY/单写入者门 |
| Cron 作为兜底时钟 | CONTEXT-DEPENDENT | 只在已授权的施工窗口启用；Cron 自身、Model provider、会话状态仍可能失效，不能宣称端到端绝对可靠 |
| 主会话轻量编排，耗时细节下沉 | QUALIFIED PRACTICE | 有价值，但不可把“所有任务一律 workflow 化”变成通用规则；考虑调用成本、工具约束、工作类型和 provider 额度 |
| 实际通知处理、并发上限和后台回放 | SOURCE-INSPECTED only | 公开源码有接口和恢复设计，不证明目标机器安装的二进制版本或供应商真正行为 |

### 与当前 ZCode 公共合同的三个潜在冲突（请原 Skill Owner 定点核对）

1. **路由/触发**：公开官方 dynamic-workflows Skill 表明只有用户显式指定 workflow/工作流作为手段，才调用 CreateWorkflow；一般多路独立研究默认 Agent/直接施工。补充 Skill 的“超过三路并行即使用”描述可以触发**读取工艺参考**，不应解释为自行取得创建 Workflow 的授权。
2. **子代理模型档位**：官方 Skill 对每个 subagent 的显式 model 选择有“用户要求/指定”条件；“轻 lane 自动改成 $low/$high”需符合当前用户已批准的 model/provider 映射，不能因省配额自动扩展权限或切换收费提供商。
3. **Cron**：ZCode CronCreate 的工具说明限定在用户显式要求调度未来任务时使用；自动化轮不允许自建、更新或删除排程，CronPauseSelf 限于真实绑定的 scheduled turn。不能把“要保持任务流转”扩展为 Agent 擅自永久创建 Cron。定时器应由已授权的施工窗口启停，终态自停或经当前 owner 停止。

**可移植性补充**：Agent Skills 公开规范允许 name、description、license、compatibility、metadata、allowed-tools 这些 frontmatter 字段，示例把版本写在 metadata.version。补充 Skill 的顶层 version 并非可移植标准字段；若要跨 Harness 复用，可移至 metadata.version。ZCode 自己的 bundled Skill 也使用 when_to_use 这样的产品扩展字段，说明**产品本地可用 ≠ 跨客户端格式兼容**。不应为了形式验证而擅自改正在本地可用的 Skill；由原 Skill Owner 运行相应客户端校验。

## 工艺包最低交付物（不是新增治理表格）

1. **适用范围**：Harness/Provider/OS/实际安装版本与 SHA、所需工具/权限、禁用情形和有效期。
2. **再现方式**：最小脚本或工具命令、输入摘要、正负控、预期/实际输出，明确缓存回放是否误当新执行。
3. **可用性和失效**：静态编译通过、合成回归、目标 Host 回归、消费者采用分别标级；未知明确写 UNKNOWN。
4. **证据传递**：原 Owner Work 的一个精确指针、当前版本、具名消费者/ACK 和下一动作；不要求每次新开 Issue 或重贴日志。
5. **退出条件**：Human cutoff、无 READY、provider 确定性停止、授权失效或风险门；Skill 不能给系统增加自主运行权限。

## 最小可检验的“唤醒即对账”设计

**通知、定时 tick、人工介入都只是一条唤醒 hint。** 下一步应 live-read 当前 Work/Runner 状态，而非沿用回忆中的“波次应已完成”。

候选算法采用三段：**Observe**（权威 Run/Claim/Owner 状态、进度与当前权限）→ **Decide**（STOP/HOLD/INSPECT/可派发 READY，预算与配额、是否仍有人工决策）→ **Commit**（只有 current Owner 的原子 claim/唯一写入者才能启动 effect，结果回写 durable source）。本研究附的 reference test 仅测试前两段，**不提供 Commit 或真实 Cron/Workflow 实现**。

建议把通知链拆成 run_terminal → notification_constructed → notification_delivered → primary_turn_woke → reconciled → ready_claimed。未观察到后一段，不推断上一段发生。若模型 provider 与 Cron 共享失效域，Cron 不是独立故障容灾；若需要真正不同失效域的 watchdog，必须在测出当前方案不足且获 owner 部署权限后再讨论。

工艺评估优先检查以下实际结果，而非设置最大并发数字：**终态到下一个 READY claim 的空窗时长**、有效吞吐（被接受交付/墙钟时间）、失败/重复副作用、模型额度与费用、通知到达率、人工唤醒次数、独立恢复率和消费者真实采用率。允许轻任务在健康资源内排队，但不要为凑并发而饥饿主会话或越过限流。

## 试点与提升门槛

- **试点 A：现有一条授权长程工作**。先记录 v1.5 历史基线，再在下一次真实 Work/真实额度窗口做 A/B 或交替比较；至少要有通知丢失、重复唤醒、限流变慢、人工停止四组负控。工头是现场执行者；工艺师维护用例/复盘；不自动重启已暂停任务。
- **试点 B：第二条独立 Work**。由不同消费 Owner 自主选择是否采用 Skill 改动，提供 before/after 和明确拒绝/接受理由。只有两个 Work 独立消费且取得实证改进，才考虑把稳定跨场景原则交给 ai-use 的现有 Agent Interface/Foreman home；ZCode 特定工具参数继续留在 Skill。
- **止损**：若实际通知和 cron 实现与当前公开源码版本不同，先记录版本差异并缩小 claim；若无合法 READY、额度或权限，静默收口/停时钟。试点不能用新增常驻守护服务、第二中央队列或新审批职务作为先决条件。

## 外部研究（官方原始来源；非当前项目实测）

- [ZCode dynamic-workflows bundled Skill @ fec9759](https://github.com/zai-org/ZCode/blob/fec975905a2abd4c07e35c40d51fa097a2258ec9/apps/zcode-cli/packages/bundled-skills/skills/dynamic-workflows/SKILL.md)：路由、模型档位、编译/类型、状态与确认边界；当前本机版本未核。
- [ZCode Cron handler @ fec9759](https://github.com/zai-org/ZCode/blob/fec975905a2abd4c07e35c40d51fa097a2258ec9/apps/zcode-cli/packages/core/src/tool/handlers/cron.ts)：sessionId/automationTurn/CronPauseSelf 权限来源。
- [ZCode resumed workflow tracker @ fec9759](https://github.com/zai-org/ZCode/blob/fec975905a2abd4c07e35c40d51fa097a2258ec9/apps/zcode-cli/packages/core/src/runtime/methods/dynamic-workflow-run-track.ts)：恢复态后台注册与通知流程；与通知投递成功不同。
- [Agent Skills 标准](https://agentskills.io/specification)：frontmatter、metadata.version、可移植目录结构。
- [OpenAI：Harness engineering](https://openai.com/index/harness-engineering/)：环境可读性、版本化规则、结构性测试与文档维护。
- [OpenAI：Testing Agent Skills Systematically](https://developers.openai.com/blog/eval-skills)：prompt→trace/artifact→checks→score；验收先于改 Skill。
- [OpenAI：Build an Agent Improvement Loop](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)：trace/feedback/eval→harness 改进；示例非普遍收益保证。
- [OpenTelemetry 2026-11-12 agent instrumentation](https://opentelemetry.io/blog/2026/agent-harness-genai-instrumentation/)：用协议与可执行校验替代模型自评；闭源 CLI 内部细节可观测性有限。
- [GitHub webhook 最佳实践](https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks)：通知/事件去重与可重投，事件不自动代表最终效果。
- [Temporal：Durable Execution means deciding what survives failure（2026-11）](https://temporal.io/blog/durable-execution-means-deciding-what-survives-failure)：Activity 副作用重试须稳定业务键，恢复与接受结果要分离；仅借鉴机制，不建议立刻引入 Temporal。

**待后续决定**：是否开展下一次有合法窗口的工艺试点；原 ZCode Skill 的本机版本/验证由其 Owner 决定。当前不提出修改 ai-use L0、追加角色等级、自动创建计划任务或修改任何真实 Host。
