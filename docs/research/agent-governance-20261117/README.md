# 2026-11-17 Agent 治理与可恢复执行调研

**Classification: L3 / NON-NORMATIVE。** 本报告是架构判断的研究输入，不新增 L0 规则、角色、Work 状态、权限或验收门禁。

## 范围与结论

- 核验日期：**2026-11-17，CST / Asia/Shanghai（UTC+08:00）**。
- 初始内部对照基线：[ai-use main 8a73ecef71a4a87df5022537692a79f5c8a617f2](https://github.com/youling/ai-use/commit/8a73ecef71a4a87df5022537692a79f5c8a617f2)。主线集成复核基线为 [main 2e524b071c1b0864bdcee6fa90592f7a7dd40f9a](https://github.com/youling/ai-use/commit/2e524b071c1b0864bdcee6fa90592f7a7dd40f9a)；已接受规范及工具能力仍应按具体 Work 回读当前 owner。
- 范围：十四组主题、29 个公开官方来源链接，覆盖长程 harness、记忆、评估、工具调用、MCP、A2A、GitHub 原生协作、AGENTS.md、源码管理、OpenAI 与 LangGraph。
- 综合过程：由有界 SIDE_CONTEXT 整理，Global Architect 复核来源、现有语义 owner 与已接受主线后收录为 L3；本研究不构成 SDK、Host 或运行能力的独立验收。
- 已完成：官方网页与精确版本资料核查、与既有规范定向对照。未执行：模型实验、SDK 兼容试验、生产负载、部署实例与设备验收。
- 阶段判断：治理核心为 **MATURE**；本轮采纳判断为 **KEEP + REUSE_KNOWLEDGE_NATIVE_IMPLEMENT**。优先学习机制，在已有边界内改进；本轮证据不支持更换工作状态机或引入新运行平台。

官方规格证明的是 DOCUMENTED_CAPABILITY；供应商工程案例是其公开实验报告，不是本项目的 MEASURED。研究的采纳建议与正式规范变更分开处理。来源、日期和可支持结论逐项见 [SOURCES](SOURCES.md)。

## 十四组事实与本地判断

### 01｜记忆应保存经验证的规律

Anthropic 2026-11-06 的案例区分原始记录、笔记、组织化表示和注入上下文；它也展示了用记录纠正错误笔记。对本项目的推论是：把快速变化、可直接回读的状态反复抄入记忆，会增加维护和漂移风险。[来源 S01](SOURCES.md#s01)

**ADAPT。** 归入 [Recovery & Handoff](../../../30_PROTOCOLS/RECOVERY_HANDOFF.md) 与 [Durable Trace](../../../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md)：保留已验证规律、反例和来源，当前状态仍回源。未知是本项目的实际恢复收益；暂缓固定“做梦”调度器及新知识库。

### 02｜评估结论必须与配置和问题绑定

Anthropic 2026-11-13 强调先定义测量问题，区分观察与因果判断，记录运行及评分配置，并暴露评分器失败。一次成功演示不能证明普遍稳定能力。[来源 S02](SOURCES.md#s02)

**ADAPT。** 归入 [Durable Trace](../../../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md) 和 [Constitution](../../../CONSTITUTION.md) 的证据、验证原则。比较时明确任务、版本、配置和未覆盖面；不把供应商样本规模变成普通 PR 的强制门禁。本地跨执行器可比性仍未测。

### 03｜脚手架应随实际能力调整

Anthropic 2026-03-24 的长程开发案例随模型变化，删去此前有用的上下文重置、逐 sprint 编排，并调整 evaluator 的位置。结构复杂度本身不是可靠性。[来源 S03](SOURCES.md#s03)

**KEEP / ADAPT。** [Agent Interface](../../AGENT_INTERFACE.md) 与 [Recovery](../../../30_PROTOCOLS/RECOVERY_HANDOFF.md) 已有最小充分执行、上下文和独立性边界。阶段成果留痕继续保留，是否细拆或增设验证应由实际故障决定；未知是各执行器的稳定能力边界。

### 04｜连续工作需要可恢复产物

Anthropic 2025-11-26 的案例用增量实现、Git 历史、进度记录和实际功能检查减少接班猜测；单靠压缩不能保证后续会话理解真实现场。[来源 S04](SOURCES.md#s04)

**KEEP。** 复用 [Local Worksite Log](../../../30_PROTOCOLS/LOCAL_WORKSITE_LOG.md) 与 Recovery，不复制第二份进度账本。供应商案例支持机制，不能证明任何部署已经具备可接续现场；该事实需实例证据。

### 05｜工具发现与结果应按需展开

Anthropic 的代码调用案例先加载必要接口，在执行环境筛选中间结果，再返回模型所需摘要；同时承认代码运行增加隔离、资源和监控成本。[来源 S05](SOURCES.md#s05)

**KEEP / ADAPT。** 归入 [Agent Interface](../../AGENT_INTERFACE.md) 的定向执行：先少量工具元数据，再读所需完整接口；摘要保留错误、分页与截断边界。案例节省比例不外推本项目，当前成本收益未知。

### 06｜MCP 新协议改变连接假设

官方当前稳定版为 **2026-07-28**。新版移除协议级初始化握手与 session，按请求声明版本和能力；跨调用状态使用显式 handle。[来源 S06](SOURCES.md#s06)

**ADAPT_BEHIND_SEAM。** 版本兼容属于实例工具 adapter；公共判断遵循 [ARCH-0](../../ARCHITECT_RECONNAISSANCE.md)。协议已发布不表示连接器已升级；采用前查清双方协议、SDK 和回退行为，不规定全员追新。

### 07｜异步 Task 不是治理 Work

MCP Tasks 已迁入扩展；声明扩展能力后，服务器可返回持久 handle，客户端查询或补充输入。取消请求是协作式的，不能据响应断言底层工作已停止。[来源 S07](SOURCES.md#s07)

**DEFER 运行接入，复用恢复知识。** [Durable Trace](../../../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md) 保留原 Work 与外部 task ID、结果的关联。旧实验 API 与新版兼容、任务有效期及取消后的真实状态仍待消费者核验，不引入第二套生命周期。

### 08｜权限由实际边界落实

MCP 要求 token 绑定目标资源并禁止透传为上游凭据。Anthropic 的隔离经验同时指出：可靠连接器仍可能返回不可信内容，模型提示不能替代环境限制。[来源 S08](SOURCES.md#s08)

**KEEP。** 对齐 [Constitution](../../../CONSTITUTION.md) 和 [Owner / Instance Boundary](../../../30_PROTOCOLS/OWNER_INSTANCE_BOUNDARY.md)。工具可调用不等于获授权；减少重复审批依赖清晰的授权与执行边界。具体配置有效性仍须实例证据。

### 09｜A2A 互通不提供恰好一次执行

A2A 1.0 于 2026-03-12 发布；官方最新 release 为 **v1.0.1**，规范页仍显示 1.0.0，二者需分开记录。Send Message 的幂等性为 MAY，不是 exactly-once 保证。[来源 S09](SOURCES.md#s09)

**DEFER 整体接入，REUSE_KNOWLEDGE。** 遵循 [ARCH-0](../../ARCHITECT_RECONNAISSANCE.md) 与 Recovery：可借鉴发现、版本协商和异步回执，先证明真实互通需求。Task 状态不得替换既有 Work、claim 或验收；本地实现与重放语义未知。

### 10｜优先使用 GitHub 原生关系

GitHub 提供子任务、阻塞关系及 Projects 视图；部分 Projects 编辑会同步回 Issue／PR。官方能力与账号、token、连接器的实际能力需分别核对。[来源 S10](SOURCES.md#s10)

**REUSE_NATIVE。** 语义 owner 已是 [GitHub Native First](../../../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md)。优先关系与精确链接，缺少 mutation 能力时不另建调度数据库。不能泛称 Projects 只读；每个可写字段仍服从原 owner 契约。

### 11｜AGENTS.md 是入口，不是权限系统

官方格式是普通 Markdown，无必填 schema，支持子目录的局部说明；实际加载和优先级仍取决于执行器及其上层规则。[来源 S11](SOURCES.md#s11)

**KEEP。** 保持 [L0](../../../AGENTS.md) 短小稳定，细节留在语义归属处，通过 [Reading Map](../../../READING_MAP.md) 展开。就近文件不能覆盖 Human 和平台权限；不同 harness 的实际加载行为尚未逐个测量。

### 12｜不照搬超大规模源码系统

Anthropic 的 Scion 面向异常大的 monorepo 与 CI 规模；原文承认 Git 适用于绝大多数仓库，也列出浅克隆、稀疏检出和镜像等既有办法。[来源 S12](SOURCES.md#s12)

**REJECT 本轮仿建。** 按 [ARCH-0](../../ARCHITECT_RECONNAISSANCE.md) 的成熟阶段复用原则，先量化实际瓶颈。当前没有足够证据迁移 VCS、自建评审系统或弱化 GitHub 真值；未来规模问题以测量重开。

### 13｜OpenAI 的长程经验同样强调外化状态

OpenAI 的案例使用规划、工具反馈、修复与状态更新循环；Skills 保存按需加载的程序，compaction 管理会话上下文。特定模型的长时实验不代表所有执行器都可靠。[来源 S13](SOURCES.md#s13)

**KEEP / REUSE_KNOWLEDGE。** 映射 [Recovery](../../../30_PROTOCOLS/RECOVERY_HANDOFF.md) 和 Agent Interface：分别判断会话是否继续、项目是否可恢复。宿主继续负责工具和审批边界；provider 线程不是 Work authority，本地收益尚未测试。

### 14｜LangGraph 明确恢复会重放代码

官方说明重试及 interrupt 恢复可能从节点开头执行，checkpoint 不使外部副作用自动恰好一次；幂等键需先持久化，且外部服务必须支持去重。[来源 S14](SOURCES.md#s14)

**REUSE_KNOWLEDGE_NATIVE_IMPLEMENT。** 归入 [GitHub Native First](../../../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md) 的回读与幂等修改原则。学习失败模型即可，不必引入 LangGraph；任何 adapter 的实际重放保证仍需独立确认。

## 恢复重放：两个应保留的具体反例

**副作用成功，回执丢失。** 执行器生成 K1、提交外部写入，然后在保存回执前崩溃。接班者发现本地无记录，生成 K2 重试，会把已完成操作再做一次。可迁移的处理顺序是：从已持久身份推导或预存稳定操作键；执行；查询并回写结果。只有外部服务真正按该键去重时，键才有效。没有确认响应应记为 UNKNOWN，不是“未执行”。依据 [S14](SOURCES.md#s14)，现有 owner 仍为 Native First 与 Durable Trace。

**审批后恢复，动作已经变化。** 框架保存一个同意值，并不保证新参数、新版本或重排后的问题仍是原获准动作。LangGraph 的多个 interrupt 恢复值按顺序匹配，更说明不能把布尔值脱离上下文复用。对 ai-use 的推论是：恢复时核对原动作语义、当前版本与权限，结果不明先回源。把写操作放在审批之后，也不能消除随后崩溃造成的重复。

## 采纳边界与停止条件

本轮收敛为三类成果：保留现有治理骨架；将经过验证的记忆、评估配置和恢复反例纳入 L3 经验；把 MCP／A2A 版本变化留在消费者 adapter 的适配问题中。[PR #190](https://github.com/youling/ai-use/pull/190) 已经独立语义核验并合并：末端研究分诊、Foreman 派单与父级验收、执行上下文来源及 pointer-first 交接均回到原 canonical home。本报告借用这些已接受的接口定位改进，不将外部资料直接升级为新规范。

“穷尽”在此指决策范围内的充分覆盖：主要候选与反例已有原始来源；每组结论已映射现有 owner；剩余未知已缩为实例版本、失联恢复和实际收益；继续泛搜未显示会改变路线的缺口。因此停止本轮检索，不宣称覆盖整个互联网。仅当新来源推翻关键假设、消费者提出真实互通需求或现场证据暴露问题时，定向重开。

所有接受、实现与发布仍由各自 owner 按现行契约处理。本研究既不认证部署，也不增加固定轮询、通用审批、全量测试或新数据库。
