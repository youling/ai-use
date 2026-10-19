# ADR-0017 — 产品先交付：可选安全增强与 Human 安全门禁主权

- **Status:** Proposed; Human direction captured in [#163](https://github.com/youling/ai-use/issues/163); normative materialization requires exact-head PR Review/merge
- **Decision level:** L2 material normative governance
- **Canonical role principle:** [CONSTITUTION.md §2](../CONSTITUTION.md#2-governance-hierarchy)
- **Scope:** Global Architect、Project Architect；Foreman/子执行者遵循已授权 Work 的同一产品取舍，不自行获得治理权
- **Does not override:** 当前 L0 fail-closed、Human 授权、外部强制条件、现有设备/数据 ownership 或真实生产动作权限

## Context

两起真实工程返工暴露同一错误：架构师把 AI 自行建议的权限最小化、OAuth 单一 scope、JIT、额外恢复/审计体系等，升级成首个可用版本的 P0 或验收门禁，导致已可运行的能力无法尽快形成稳定的实际产品闭环。Human 明确要求安全机制由 Human 选择，不得在功能尚未实际投用前擅自设置一套必须先完成的安全工程。

此要求聚焦**新增安全增强**的产品取舍和排序，不是授权绕过已有的身份/设备权限、泄露凭据、破坏用户数据或暴露可未经授权操作的远控端点。后者是当前 L0/Constitution 已存在的操作边界，不是本 ADR 新建的安全功能。

## Decision

1. **功能闭环先行**：Architect 以 Human 指定的最小实机闭环、可观察成功和一段由 Human 决定的稳定使用为主线；优先复用已经证明有效的设备身份、会话通道和实现。不凭 AI 自己设定固定稳定天数。
2. **新增安全增强默认非关键路径**：精细 OAuth scope、统一最小权限、JIT、复杂 RBAC、全面审计、额外代理/凭据基础设施、全功能恢复体系等，只能作为 `OPTIONAL / DEFERRED` 建议或独立工作；除非 Human 明确选为当前阶段的需求，或现有明确生效的强制契约对该具体操作提出要求。不得通过技术实现、测试或 PR Review 把它们偷换为 Human 验收条件。
3. **Human 定安全产品需求**：是否添加可选安全机制、需要何种具体权限范围、何时加固及何时算稳定，由 Human 主张。Architect 负责披露实际风险、可选方案和后果，不得以「安全最佳实践」自动取得决定权。
4. **阻断最小化**：遇到真实、可指明的权限/安全/数据归属或外部强制阻断，只停止受影响的真实操作；其它已授权 READY 工作继续。优先寻找受保护的既有执行路径、可信内部隔离试验或缩小暴露面的功能验证，而不是追加整个未来安全体系作为必经前置。
5. **内部组织连接器允许宽 scope**：Human 可选择覆盖管理、ACL、DNS 等多项能力的组织级 OAuth client。单项操作需要 `auth_keys` 不等于 client 只能持有 `auth_keys`；权限存在不等于已授权执行所有外部动作。不得从一个操作需求推导全局 scope 上限。
6. **成果指标**：验收以 Human 能在真实目标上完成明确功能操作及持续稳定表现为准；CI、PR、Review 是手段，不是代替功能投用的里程碑。作者先做确定性测试，审查遵循已有按风险分级规则。

## Alternatives considered

- **每个产品开工即安全完备（security-first as a universal gate）：拒绝。** 混淆 Human 需求与 AI 风险建议，增加额外依赖和无效返工，阻滞已有能力投用。
- **完全关闭认证、保全与权限边界：拒绝。** 与 L0 及既有真实操作授权直接冲突，也会把用户数据与设备暴露为未经授权的操作对象；该选项不属于可选安全增强。
- **统一规定上线后 N 天强制安全化：拒绝。** 稳定窗口和项目交付节奏是 Human 产品取舍，不能由架构师猜测。

## Compatibility, supersession and consequences

不回写或修改既有事件、PR、单机证据和历史 ADR；旧 AI-origin 的可选安全建议**不再自动构成当前里程碑 Gate**，但已获 Human/higher/current contract 授权的具体边界仍有效，争议需按原权威来源核对。没有新角色、审批流程、Review 轮次或默认生产部署权限。

收益是减少安全过度设计和无目的审查，形成从「真实可用→稳定观察→Human 决定增强」的交付顺序。代价是 Human 需知晓已延期的风险；Architect 必须把风险作为可定位的债/备选说明，并对不可隔离的真实危险动作保持单点阻断。

## Counterexamples

- **GhostFleet / ThinkPad：** 已有身份和 DCR 能力，仅需持久连通读/控。Architect 不得将新 OAuth 最小 scope、Courier、JIT 或全部高级恢复能力升级为这个既有目标的前置。若某一具体远控动作确实缺少授权，则仅拦住该动作，不停掉身份/目录/只读测试。
- **内部组织 OAuth：** Human 决定用宽 scope 的组织 Client。Architect 不能要求 `auth_keys` 必须唯一；但不能据宽 scope 自动执行未经批准的设备删除、ACL 改写。
- **真实 Public Access 绕过：** 若某个可公开访问的写控制接口可绕过已经要求的认证，不能直接上线那个接口；可隔离此入口继续开发/内网试用，而不是要求先完成与这处风险无关的完整安全规划。
- **既有用户状态：** 对未知 owner 的目录和原始密钥不能用「安全可选」作为覆盖或外发理由；保全与身份边界属于已生效基础规则。

## Review boundary

本 ADR 与 Constitution §2 是唯一一次小范围 L2 materialization；当前 Human 原话与本 ADR 的解释边界必须在 [#163](https://github.com/youling/ai-use/issues/163) 及 exact-head semantic Review 可追溯。L0、Change Lifecycle、Foreman 状态机和各项目/Host 事实不在此次修改范围内。
