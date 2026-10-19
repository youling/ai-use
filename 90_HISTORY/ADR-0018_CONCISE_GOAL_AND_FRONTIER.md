# ADR-0018 — 目标导向手册去冗余与前沿技术判断

- Status: Accepted direction from Human 2026-10-20; normative content lands only when Issue #165 PR is reviewed/merged
- Issue: [#165](https://github.com/youling/ai-use/issues/165)
- Decision: L2; common principles in [AGENTS.md](../AGENTS.md) / [CONSTITUTION.md](../CONSTITUTION.md), stage-specific mechanics remain in their existing single owners
- Supersedes: any reading of [ADR-0017](ADR-0017_DELIVERY_FIRST_HUMAN_SECURITY_GATES.md) or Agent Interface 2.12.0 as requiring Python-first, Rust-later or a fixed technology maturity sequence. Does not rewrite historic deliberation.

## Context / evidence

Human 指出手册反复罗列禁止项，导致 Agent 注意力偏离业务目标；上次 Python/Rust 只是举例，TypeScript 或其他路线同样可能最优。仅比较眼前开发时间也不充分：新建数据模型提前采用前沿技术，可能免去未来大规模迁移。

**PostgreSQL 反例（2026-10-20 官方 current state）**：
- PostgreSQL 19 RC1 于 2026-10-15 发布；GA 现计划 2026-11-19，RC2 计划 11-12。来源：https://www.postgresql.org/about/news/postgresql-19-rc-1-released-3409/
- SQL/PGQ 属性图功能虽在早期 PostgreSQL 19 Beta 宣布，但官方 2026-09-24 Beta4 已明确 **revert SQL/PGQ**，RC1 无此能力。来源：https://www.postgresql.org/about/news/postgresql-19-beta-4-released-3386/
- 教训同时成立：应积极发现新技术减少架构锁定，却不能根据早期新闻把 RC 未包含的功能当实物。项目选择应在项目自身 owner 内基于 live 版本核实，**本治理 ADR 不命令 HT 部署 PG19**。

## Decision

**少而明确**：L0 只保留 Human 目标/主权、current truth、scope、继续推进、证据、中文与定向读取；Constitution §2 仅一个跨角色总纲；Foreman 只负责调度差异，Agent Interface 只负责执行/Challenge，Reconnaissance 负责研究与技术路线判断。删掉正文中的语言示例、重复反例与重复约束；历史 provenance 不删除。

**动态而不教条**：技术方案考虑当下交付、长期维护、未来功能与迁移成本。能快速可靠交付的已有工具可直接选；新/RC/Beta 也可在原型期大胆做有界试验、用当前精确版本和真实功能测试筛选。不能新增通用“最新优先”或“稳定优先”硬门禁。

**不为删减牺牲 authority**：Human 当前决定、真实设备与机密边界、durable Git truth、原 Work ownership/验收、Review/merge 授权及准确证据继续有效；速度不等于可以越权。减少文字不改变既有 Work 状态机或真实运行代码。

## Compatibility / acceptance

1. AGENTS.md 明显缩短、仍可自主恢复 L0 所有必要不变量和现有路由。
2. Constitution 重复相邻总纲合并；角色/执行/调研文件净字符数下降，没有新平行语义 owner；旧 ADR 历史仍在。
3. Case A：前沿 RC 确有可验证新能力，原型可以优先探索，不因“非 GA”机械否决。Case B：PG19 RC1 无 SQL/PGQ，不能宣称已包含图功能。Case C：TypeScript 比 Python 更适合当前需求时可以采用。Case D：工头面对慢 child/独立 READY 主动调度，不以更多 Agent 数量为目标。Case E：无授权的生产/删除不能借“少限制”执行。
4. 结构、链接、exact-head L2 semantic Review 和适用 CI 验证；单次批量提交，避免为了精简反复触发 PR 修复。

This ADR owns rationale and supersession only, not a new process or executable policy.
