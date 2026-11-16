# 来源登记｜Agent 治理调研 2026-11-17

**L3 / NON-NORMATIVE。** 返回 [研究报告](README.md)。全部为公开官方资料；核验日期均为 **2026-11-17 CST / Asia/Shanghai（UTC+08:00）**。本表不包含本项目运行测量。

证据标记：DOCUMENTED_CAPABILITY 表示官方规范或文档描述的能力及约束；PUBLIC_PRIMARY_REPORT 表示供应商公开工程案例或实验，尚未在本项目复现。后者仅用于本表的来源说明，不新增 ai-use 的规范枚举。UNKNOWN 表示页面没有可靠给出发布日期或固定软件版本，不能用抓取日期补造。

## S01

- 主题：选择性记忆、记忆纠错与来源。
- 官方 URL：[The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory)。
- 发布日期：2026-11-06。版本：网页文章；无固定 runtime 版本。
- 证据：PUBLIC_PRIMARY_REPORT。
- 直接支持：原始记录、笔记、组织化表示与注入上下文的分层；对照记录纠错；随环境变化产生的记忆漂移；组织化记忆与原文检索的互补。
- 限制：供应商选定实验及模型结果不证明通用记忆效果，不证明本项目需要 Wiki、向量库或定时后台整理。

## S02

- 主题：评估设计、配置来源和结论范围。
- 官方 URL：[Building strong safety evaluations](https://www.anthropic.com/research/building-strong-safety-evaluations)。
- 发布日期：2026-11-13。版本：网页文章。
- 证据：PUBLIC_PRIMARY_REPORT。
- 直接支持：观察性与因果评估区分；提前确定指标；评分器偏差、失败和校准；报告模型、提示、采样、评分器、日期及不确定性。
- 限制：源文聚焦安全评估。报告迁移的是测量和可复现方法，不把它的样本规模或领域评分标准当成普通工程门禁。

## S03

- 主题：按实际能力调整 harness。
- 官方 URL：[Harness design for long-running application development](https://www.anthropic.com/research/harness-design-long-running-apps)。
- 发布日期：2026-03-24。版本：文章比较的模型与 harness 配置以原文为准。
- 证据：PUBLIC_PRIMARY_REPORT。
- 直接支持：模型变化后移除上下文重置或 sprint 结构；保留有实际价值的计划与评估；评估者的收益取决于任务难度与模型可靠能力。
- 限制：案例不是多代理普遍优于单代理的证明，也不支持取消现行独立验收或 Human 指定的阶段交付。

## S04

- 主题：长程工作与跨会话接续。
- 官方 URL：[Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)。
- 发布日期：2025-11-26。版本：官方工程案例。
- 证据：PUBLIC_PRIMARY_REPORT。
- 直接支持：初始化与增量工作、Git 历史和进度记录、实际功能验证；压缩不能独立解决全部长程接续问题。
- 限制：原文主要针对应用开发；文件名与流程细节是示例，不构成全项目强制结构。

## S05

- 主题：代码调用工具与按需上下文。
- 官方 URL：[Code execution with MCP](https://www.anthropic.com/research/code-execution-with-mcp)。
- 发布日期：2025-11-04。版本：网页工程案例。
- 证据：PUBLIC_PRIMARY_REPORT。
- 直接支持：按需工具发现、在执行环境过滤中间结果、代码组织多步调用；运行代码需要相应隔离、资源控制及监控。
- 限制：示例 token 节省率不是本项目测量；减少展示内容不能隐去分页、截断和错误。

## S06

- 主题：MCP 当前协议和兼容边界。
- 官方 URL：[Versioning](https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning)；[Key Changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog)；[正式 release](https://github.com/modelcontextprotocol/modelcontextprotocol/releases/tag/2026-07-28)；[发布说明](https://blog.modelcontextprotocol.io/posts/2026-07-28/)。
- 发布日期：正式版本 2026-07-28；可变文档的单独更新日期 UNKNOWN。
- 版本：current stable protocol 2026-07-28；changelog 对照前版 2025-11-25。
- 证据：DOCUMENTED_CAPABILITY。
- 直接支持：移除协议级初始化握手与 session；每请求版本／能力；显式 handle；新版请求与通知机制及旧版兼容边界。
- 限制：标准与 SDK 发布不证明具体客户端、服务器或连接器已经支持；broken stream 重发要求也不保证外部副作用恰好一次。

## S07

- 主题：MCP Tasks 扩展。
- 官方 URL：[Tasks overview](https://modelcontextprotocol.io/extensions/tasks/overview)；[2026-07-28 Tasks 规范](https://github.com/modelcontextprotocol/ext-tasks/blob/main/specification/2026-07-28/tasks.md)；[C# SDK Tasks 兼容说明](https://csharp.sdk.modelcontextprotocol.io/v2/concepts/tasks/tasks.html)。
- 发布日期：协议族 2026-07-28；扩展页面及 SDK 页面单独发布日期 UNKNOWN。
- 版本：io.modelcontextprotocol/tasks；规范路径 2026-07-28；C# v2 页面作为具体兼容反例。
- 证据：DOCUMENTED_CAPABILITY。
- 直接支持：能力声明后的服务端 task handle、tasks/get、tasks/update、协作式取消；C# 新版与旧实验 Tasks API 的兼容限制。
- 限制：扩展能力声明不等于每工具 task 请求标志；具体支持、保存期限、取消是否停止工作仍需消费者核对。协议 Task 不等于治理 Work。

## S08

- 主题：授权、执行隔离与不可信内容。
- 官方 URL：[MCP Authorization Security Considerations](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations)；[How we contain Claude across products](https://www.anthropic.com/research/how-we-contain-claude)。
- 发布日期：MCP 规范族 2026-07-28，页面单独更新日期 UNKNOWN；Anthropic 文章 2026-05-25。
- 版本：MCP 2026-07-28；Anthropic 为产品隔离工程案例。
- 证据：MCP 为 DOCUMENTED_CAPABILITY；Anthropic 为 PUBLIC_PRIMARY_REPORT。
- 直接支持：目标资源及 token audience 校验、禁止 token passthrough、PKCE；环境、模型与外部内容多层边界；连接器可信不等于所取内容可信。
- 限制：没有测量任何部署的安全性，案例不授权绕过实际审批或访问边界。

## S09

- 主题：A2A 版本、异步交付与幂等范围。
- 官方 URL：[A2A specification](https://a2a-protocol.org/latest/specification/)；[1.0 发布说明](https://a2a-protocol.org/latest/blog/2026/03/12/a2a-protocol-ships-v10-production-ready-standard-for-agent-to-agent-communication/)；[官方 release 列表](https://github.com/a2aproject/A2A/releases)。
- 发布日期：1.0.0 于 2026-03-12；v1.0.1 发布 UI 为 2026-05-28，其 release 内 changelog 日期为 2026-05-26，保留两种日期的原语义。
- 版本：latest release v1.0.1；官网 specification 页显示 Latest Released Version 1.0.0。二者并列登记，不以网页标题代替最新 tag。
- 证据：DOCUMENTED_CAPABILITY。
- 直接支持：发现、版本协商、多种结果交付机制；Send Message 幂等为 MAY；每次请求的认证授权及任务访问范围。
- 限制：协议互通不提供本项目 authority 或 exactly-once 保证；未安装、未测试任何 A2A SDK。

## S10

- 主题：GitHub 原生子任务、依赖与 Projects。
- 官方 URL：[Sub-issues REST](https://docs.github.com/en/rest/issues/sub-issues)；[Issue dependencies REST](https://docs.github.com/en/rest/issues/issue-dependencies?apiVersion=2026-03-10)；[Creating issue dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)；[About Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/about-projects)。
- 发布日期：UNKNOWN；均为核验日现行文档。
- 版本：REST 示例使用 API 2026-03-10；UI／Projects 为现行页面，无固定客户端版本。
- 证据：DOCUMENTED_CAPABILITY。
- 直接支持：父子关系和 blocked-by 读写 API；UI 依赖权限；Projects 过滤、表格、看板、路线图与部分字段双向同步。
- 限制：连接器覆盖与目标 token 权限另行确认；Projects 不能泛称只读，原生状态也不自动成为治理 authority。

## S11

- 主题：AGENTS.md 的可移植入口。
- 官方 URL：[AGENTS.md](https://agents.md/)。
- 发布日期：UNKNOWN。版本：核验日现行站点；普通 Markdown，无必填 schema。
- 证据：DOCUMENTED_CAPABILITY。
- 直接支持：面向 Agent 的仓库说明、根目录与子目录说明、按目录定位规则的格式约定。
- 限制：站点描述不证明每个 harness 的实际加载行为；文件自身不能提升权限或覆盖平台及 Human 上层约束。

## S12

- 主题：源码系统规模与迁移理由。
- 官方 URL：[Redesigning source control at Anthropic](https://www.anthropic.com/research/redesigning-source-control)。
- 发布日期：2026-10-13；页面注明 2026-10-15 更新。
- 版本：Scion 内部工程案例，非可直接采用的通用发行。
- 证据：PUBLIC_PRIMARY_REPORT。
- 直接支持：特定超大规模负载下的 Git／CI 瓶颈；Git 对多数仓库仍合适；浅克隆、稀疏检出、镜像等先行经验。
- 限制：供应商规模不能作为本项目更换 VCS、评审系统或真值源的证据。

## S13

- 主题：OpenAI 长程循环、Skills、compaction 与宿主边界。
- 官方 URL：[Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)；[Shell + Skills + Compaction](https://developers.openai.com/blog/skills-shell-tips)；[Codex as a platform](https://developers.openai.com/blog/codex-as-a-platform)。
- 发布日期：前两篇分别为 2026-02-23、2026-02-11；第三篇发布日期 UNKNOWN，已打开并核查现行正文。
- 版本：长程案例明确 GPT-5.3-Codex 及其推理配置；其余能力以页面及所链接 API 契约为准，不泛化为所有 Codex 版本。
- 证据：长程案例、技巧为 PUBLIC_PRIMARY_REPORT；harness 接口描述为 DOCUMENTED_CAPABILITY。
- 直接支持：反馈与修复循环、持久项目材料、按需版本化程序、会话压缩；宿主仍负责工具、环境、审批和返回原记录系统的边界。
- 限制：特定长时实验不证明本地稳定能力；provider session／compaction 不自动提供项目真值、权限或离机原件保存。

## S14

- 主题：LangGraph 重试、interrupt 与副作用。
- 官方 URL：[Fault tolerance](https://docs.langchain.com/oss/python/langgraph/fault-tolerance)；[Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)；[Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)。
- 发布日期：UNKNOWN。版本：核验日现行 Python 文档，未固定 SDK release；旧 durable-execution 地址现重定向到 Persistence。
- 证据：DOCUMENTED_CAPABILITY。
- 直接支持：节点重试／恢复的 at-least-once 执行；checkpoint 不覆盖外部副作用；预先持久化的稳定幂等键与服务端去重；丢失确认应视作未知并查询；interrupt 恢复重跑及多个恢复值的顺序匹配。
- 限制：只迁移失败模型与恢复方法，不引入框架；没有执行 SDK、验证任意 adapter 或证明 exactly-once。

## 内部对照与复用限制

初始规范对照固定于 [8a73ecef71a4a87df5022537692a79f5c8a617f2](https://github.com/youling/ai-use/commit/8a73ecef71a4a87df5022537692a79f5c8a617f2)：L0、Architect Reconnaissance、Agent Interface、Recovery & Handoff、GitHub Native First，以及它们指向的证据与现场合同。主线集成复核使用已接受的 [main 2e524b071c1b0864bdcee6fa90592f7a7dd40f9a](https://github.com/youling/ai-use/commit/2e524b071c1b0864bdcee6fa90592f7a7dd40f9a)，纳入 PR #190 的规范接受及 PR #182 的有限离线工具范围。本文不以未合并 PR 的候选条款证明现行规则。

可变文档可能继续修订；版本路径固定的是协议族，不保证分支文件字节永远不变。实施者应复核真正依赖的规范、SDK／服务版本及目标环境，仅重查受变化影响的事实。任何供应商结果都需保留原任务与实验边界，不能改写为本项目的安装、部署、兼容或性能回执。
