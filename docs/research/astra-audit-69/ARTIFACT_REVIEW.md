# 逐文件审查与处置表

Artifact Version: 1.0.0
Authority: 非规范性审计注解；不改变受审文件的当前效力。
Baseline: `345184f19bc5e1546c86e6c9e234d5c653437747`

本表覆盖冻结 tree 的全部 47 个文件。正文已逐文件读取；不是只审标题、关键词或可达子图。行数、bytes、Git blob SHA、SHA-256 与原始版本行见 [inventory.json](evidence/inventory.json)。该 inventory 的 `class` 是审计 rubric：例如 provider 旧指南被判作 historical donor，不表示原文件已经自带退休声明；`version_headers` 是候选文本抓取，不是语义版本解析器。

下面的路径以[冻结仓库根](https://github.com/youling/ai-use/tree/345184f19bc5e1546c86e6c9e234d5c653437747)为准。KEEP 表示未识别到需要迁移的当前职责，不是全场景正确性认证；REFINE/REFACTOR/RETIRE 均是待 Global review 的建议。RETIRE 指退出当前入口，保留历史。F 编号对应[报告](REPORT.md)。

| 文件 | 当前职责 / 边界 | 建议与审查结论 |
| --- | --- | --- |
| `AGENTS.md` | L0 3.0.0：Human、权限、范围、证据、持续执行与最小路由 | KEEP；#35/#36 的语义保全有历史依据；不增加平台操作细节 |
| `CONSTITUTION.md` | 治理原则、架构师职责、Human Gate、来源与适用说明 | KEEP + REFINE provenance；公开编纂与部署本地 ruling 不应要求外部读者访问 private 上游 |
| `NAMESPACE.md` | 编号链、逻辑与物理 namespace、层级规则 | REFACTOR；与 Reading Map 共 20,138 bytes；保链和路径，收敛为薄兼容入口（F07） |
| `READING_MAP.md` | scenario reading、invariant canonical homes、compatibility notes | REFACTOR；保 kernel-first 和 fault containment；一个手审 catalog 支持派生视图，消除活模板历史绕路 |
| `README.md` | Human 介绍、贡献入口、权威与边界 | REFINE；维持 Human 可读简介，减少与其他入口重复 mechanics（F07） |
| `START_HERE.md` | 模块介绍、操作入口、索引 | REFACTOR；薄导航；Alignment Template 指到没有对应模板的 Constitution §1（F09） |
| `LICENSE` | Apache 2.0 许可文本 | KEEP；不改变许可，不将许可理解成执行权限 |
| `00_KERNEL/LANGUAGE_POLICY.md` | 人类叙述语言与 override | KEEP；低成本 readback 应覆盖；抽样英文审查记录需明确 override 证据边界（F10） |
| `00_KERNEL/README.md` | L0-first、zero-prompt、越层冲突处理 | REFINE；保薄入口，重复解释交给受审 catalog（F07） |
| `10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md` | address/applicability/execution、检查输出与恢复入口 | KEEP + REFINE 路由；access 能力不是 authority，不能被 handoff 顺序反转（F01） |
| `10_BOOT/WORKSPACE_BOOTSTRAP_PROTOCOL.md` | 实例 workspace topology、registry schema 与治理归属 | REFACTOR storage boundary；语义 owner 不等于必须公开存储，#66 接住 private overlay（F03） |
| `10_BOOT/README.md` | Bootstrap 两协议索引 | KEEP；未来检查其指针与 catalog 同步 |
| `20_ROLES/README.md` | 指向 docs 内 Agent Interface 与 Reconnaissance | KEEP；逻辑目录为空不是缺角色契约；不要为整齐先搬路径 |
| `30_PROTOCOLS/CHANGE_LIFECYCLE.md` | L0/L1/L2、STRICT/PERIODIC、Issue/ADR/PR/exact-head、bulk plan | KEEP + REFINE；历史 dogfood 有效；明确 native enforcement 和 process guard 的差别（F05） |
| `30_PROTOCOLS/DIAGRAM_AS_CODE.md` | DERIVED authority、分层、currentness、呈现证据与 dogfood | REFINE；核心原则保留，长 geometry/provider 细节下沉 guide；同解释边界的视图语义比较 |
| `30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md` | durable execution/ruling/supersede trace | KEEP；保可恢复最小证据，不把 trace 扩成每一步长日志 |
| `40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md` | scenario regression checklist，含失败输入/恢复等 | KEEP + REFINE；不是自动执行测试；后续用相同五类任务卡测重构前后 reader 行为 |
| `40_GUIDES/README.md` | guide 导航及安全规则指针 | REFINE；Secrets & output 章节已不在 L0，文件链接存在不代表语义指针有效（F09） |
| `50_TEMPLATES/CHANGE_LIFECYCLE.md` | Issue/ADR/PR/bulk-plan 可复制形态 | KEEP；与 canonical change protocol 同步检查；避免机械为小修建 ADR |
| `50_TEMPLATES/CONTEXT_MODE_SEED.md` | mode/context/authority 正交、freeze/repair 等 machine contract | REFINE canonical 标记；ADR-0002 明确接受语义驻留，迁移不得丢枚举或误将 Warm 当独立性（F08） |
| `50_TEMPLATES/DIAGRAM_AS_CODE.md` | 图文结构、authority/source/currentness 模板 | KEEP + REFINE；从相同 reviewed catalog 派生，provider 经验不是全局容量事实 |
| `50_TEMPLATES/DISPATCH_PAIR.md` | Execution/Verifier 派工与接受形态 | REFACTOR 示例；使用 inert synthetic coordinate，移除当前可复制实例值；不扩散原值（F02） |
| `50_TEMPLATES/HUMAN_WORKSPACE_BOOTSTRAP.md` | Human 启动实例模板 | REFINE；与 private registry storage seam 一并对齐，不能默认公共宪法接收实例拓扑（F03） |
| `50_TEMPLATES/README.md` | 模板角色、读取与 canonical 边界 | REFINE；“仅形态”与实际 machine contract 驻留要一致（F08） |
| `50_TEMPLATES/architect_handoff_check.md` | 当前可发现的 handoff 检查清单 | REFACTOR；固定旧方 artifact/Human 确认和 Session §5，需区分 planned transfer 与 crash takeover（F01） |
| `50_TEMPLATES/architect_handoff_transaction.md` | PREPARED/ACCEPTED 等事务与检查顺序 | REFACTOR；Bootstrap 不应读成接受后才进行；contract 与模板职责明确（F01/F08） |
| `50_TEMPLATES/bootstrap_check_request.md` | Bootstrap 请求/回写模板 | KEEP；按 current protocol 校验字段与路径；不能从模板自行创造新授权 |
| `50_TEMPLATES/capability_self_check.md` | 可用能力与权限自检记录 | KEEP + REFINE；观察应注明主体/环境/时间/限制，不能提升为 authority 或跨实例可用性 |
| `50_TEMPLATES/pointer_response.md` | durable pointer、短摘要与范围 | KEEP；与 docs-as-code、durable trace 相容，利于避免复制大块历史 |
| `90_HISTORY/ADR-0001_DOCS_AS_CODE_CHANGE_LIFECYCLE.md` | Change Lifecycle 接受理由、被拒替代方案 | KEEP；历史 rationale，未来修订不能就地改写旧接受事件 |
| `90_HISTORY/ADR-0002_CONTEXT_LIFECYCLE_V0_1.md` | Context Lifecycle 与 safety/repair/finish 语义理由 | KEEP；#61 修复后 exact-head 接受；PR body 的旧 head 是摘要漂移（F11） |
| `90_HISTORY/ADR-0003_STAGE_AWARE_REUSE.md` | 复用总体复杂度与 stage-aware 决策理由 | KEEP；补历史索引；不将案例 schema/runtime 泛化成全球默认（F09） |
| `90_HISTORY/README.md` | 历史入口、ADR 索引 | REFINE；缺 ADR-0003，补自动/手动同步检查（F09） |
| `docs/AGENT_INTERFACE.md` | 角色、DIRECT/DELEGATE、independence、权限与公开模板边界 | KEEP；有明确 canonical mechanics；长文按 section targeted 读，不重复驻 L0 |
| `docs/ARCHITECT_RECONNAISSANCE.md` | ARCH-0、外部 current research、stage-aware reuse | REFINE；material 架构先问 GitHub 是否已解通用部分、Lab 是否已有证据；普通小修不全量扫描 |
| `docs/DURABLE_DATA_DOCTRINE.md` | canonical ownership、DERIVED、history/currentness 基础 | REFINE；补 bounded current read、完整 delta、interpretation/provenance 与 metadata recovery；不引入领域 schema |
| `docs/PROGRESSIVE_CONTEXT_BOOT.md` | 分层按需读与 durable context | KEEP + REFINE 入口；与 current Reading Map 同一 interpretation，避免另一个独立 router |
| `docs/SESSION_LIFECYCLE.md` | 历史完整生命周期与当前 recovery/context 控制并存 | REFACTOR current/history 切面；旧 Fast Restore 全 OPEN/Human 确认被 active template 调用；保修复/接管语义（F01） |
| `docs/DeepSeekPP-github-mcp-usage.md` | 特定 provider 配置、截断经验及搜索/写入建议 | RETIRE 当前指南身份；无条件自动执行、直接写 main、空搜索推断均不宜复制；保 incident donor（F04） |
| `docs/issue-26-mcp-injection-truncation-root-cause.md` | 工具注入截断 root-cause 历史 | KEEP as history；不把一次 client incident 当所有 provider 当前能力；原 #26 不可读不妨碍标出证据限制 |
| `human/README.md` | Human SSOT 构想、协作流程与入口 | REFINE；对有工具写入的读者指回 L0/Bootstrap；模块流程不能替代仓治理（F06） |
| `human/DEPOSITOR_PROMPT.md` | 当前 0.1.3 实验 prompt，来源/空上下文/运输边界 | KEEP + REFINE 测试入口；与 versioning 旧 prompt-only 结论对齐；#43 的 0.2.0 尚未接受（F06） |
| `human/DEPOSITOR_PROMPT_v0.1.md` | 旧 prompt 副本 | RETIRE 当前入口身份；明确 superseded，保版本演化证据（F06） |
| `human/PROMPT_VERSIONING.md` | prompt 版本变更与回归方法 | REFINE；prompt-only 旧 NO_DEPOSIT_NEEDED 与现有 SOURCE_CONTEXT_UNAVAILABLE 区分同步（F06） |
| `human/tests/DEPOSITOR_TEST_CASE_001_prompt_only_scope_confusion.md` | prompt-only 历史失败案例 | KEEP as historical test reference；案例不是当前 0.1.3 执行通过记录 |
| `human/tests/DEPOSITOR_TEST_CASE_002_control_plane_misclassified_as_external_knowledge.md` | control-plane 分层误判的历史案例 | KEEP；作为回归输入 donor，勿把历史观察当独立再现 |
| `human/tests/DEPOSITOR_TEST_CASE_003_v0.1.2_prompt_self_capture_and_transport.md` | v0.1.2 self-capture/transport 失败及修正方向 | KEEP；加版本/历史边界，与当前测试结果分开 |

机械结果的具体局限、近期 PR 合规、平台能力、五类 usability 场景及迁移成本均在[报告](REPORT.md)；本表不另造第二套权威分层。
