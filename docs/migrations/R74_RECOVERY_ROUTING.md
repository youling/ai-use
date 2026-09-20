# R74 Recovery / Routing Migration

**Artifact Version: 1.1.0**
Base：`e6de9acdafbc3b9d12802ecf8de25f444074553b`
Target branch：`codex/r74-recovery-routing`
Change level：L2 / STRICT_DOCS_AS_CODE
Authority：[frozen decision](https://github.com/youling/ai-use/issues/73#issuecomment-5749622582) · [Work Order](https://github.com/youling/ai-use/issues/74)
Pre-edit durable plan：[migration/Bootstrap checkpoint](https://github.com/youling/ai-use/issues/74#issuecomment-5749653022)

Repair：[Review 5260592093](https://github.com/youling/ai-use/pull/75#pullrequestreview-5260592093)；[repair delta plan](https://github.com/youling/ai-use/issues/74#issuecomment-5750577175)。本轮在原分支合入 current main `3198450f97607c4317498a34bac79523b4e850e9` 的 #76/#77/#79 既有 Local Engineering Gate，仅把它的 targeted route 编译进 catalog，不重写 gate adapter。

## Goal and non-goal

R1 收敛 recovery 与 template semantic ownership；R2 收敛 routing catalog/projections，并保留可比较的 fresh-reader evidence。L0 不改，R3/R4/R5、项目 storage doctrine、Lab、平台设置与 merge 不在本轮。构建报告由 #74 的 exact published head/PR 收据锚定，本页不把未发布 local commit 当 durable authority。

## Semantic relocation map

| Original surface | Current owner | 保全 / 冲突处置 |
| --- | --- | --- |
| Session §1 / §7 / §10.1，Context Mode Seed | [Recovery §4](../../30_PROTOCOLS/RECOVERY_HANDOFF.md#4-work-context-与正交维度) | Work Context 与 Project Architect Context 分离；session name 非状态源 |
| Context Mode Seed machine seam / §安全与独立性 / §delegation | [Recovery §4–5](../../30_PROTOCOLS/RECOVERY_HANDOFF.md#4-work-context-与正交维度) | 全部 context_policy/mode/continuation/independence/delegation/parallelism 值；fork/self-review 不冒充 fresh verify；nested default deny、isolated writes 与父子责任保留 |
| Session §10.3–10.4、Context Mode Seed durable-before-fragile/fresh | [Recovery §3–5](../../30_PROTOCOLS/RECOVERY_HANDOFF.md#3-三条恢复路径) | warm 默认、fresh 触发、checkpoint 风险边界保留；crash 不倒推旧方必须提供产物 |
| Session §3–6 / handoff check / transaction / START_HERE handoff chain | [Recovery §1–3](../../30_PROTOCOLS/RECOVERY_HANDOFF.md#1-恢复分类) | 三分支；Bootstrap 在确认前；planned transaction 适用时保留；crash missing-old-state 不假阻塞；单一 primary/current authority 不豁免 |
| Agent Interface §1.4、§1.6–1.8 / template duplicate | [Agent Interface](../AGENT_INTERFACE.md) | continuation、PREMATURE_YIELD、真实 stop 与 acceptance-derived completion 留在原 owner；template 删除语义副本 |
| DISPATCH_PAIR 最小化与 access fallback | [Agent Interface §3](../AGENT_INTERFACE.md#3-default-minimal-agent-seed) | 5–10 行 heuristic / 最小 transport fallback 搬回协议；不放松 authority/currentness gate |
| Capability Self Check | [Bootstrap §4](../../10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md#4-targeted-capability-preflight) | 六类 targeted capability evidence、无 secret、必要能力 gap 的结论边界；模板只形态，不建立 Lab |
| Session §11 | [Recovery §7](../../30_PROTOCOLS/RECOVERY_HANDOFF.md#7-project-reproducibility-contract) | project-native deps/lockfile/setup/run/test/lint/runtime/env names/fixtures 保全；只 relocation，不建新 ownership doctrine |
| Durable Trace recovery list | [Durable Trace](../../30_PROTOCOLS/DURABLE_TRACE_PRINCIPLE.md) | checkpoint 仍在原 owner；存在则验证，不存在则按 Recovery 用 current state 重建 |

## Routing and changed-file map

| Files | 职责 |
| --- | --- |
| [ROUTING_CATALOG.yaml](../../ROUTING_CATALOG.yaml) | reviewed scene/role/level/home + compatibility metadata；初始稳定 IDs；JSON-compatible YAML 1.2 |
| [START_HERE](../../START_HERE.md) / [READING_MAP](../../READING_MAP.md) / [NAMESPACE](../../NAMESPACE.md) | 完整生成的 Human / reading / compatibility projections，无手工 competing routing table |
| [ROUTING_INDEX](../ROUTING_INDEX.md) | 小型 DERIVED Mermaid/index，只有 navigation edges |
| [tools/routing.py](../../tools/routing.py) / [test_routing.py](../../tools/test_routing.py) / [routing workflow](../../.github/workflows/routing.yml) | offline stdlib catalog/paths/anchors/stable IDs/projection/privacy fixtures；相关 CI |
| README、00_KERNEL/README、10_BOOT/README、40_GUIDES/README、50_TEMPLATES/README、90_HISTORY/README、human/README | 当前入口 pointer 同步；不改角色或 authority |
| Bootstrap、Agent Interface、Durable Trace、Progressive Context、Recovery protocol | 上表 canonical relocation 与消费者指针 |
| Context Mode Seed、Dispatch Pair、handoff check/transaction、capability self check | shapes + current protocol pointers；实例坐标替换为占位符 |
| 40_GUIDES/PUBLIC_COLD_START_CHECKLIST | 三种 recovery 与真实 gap 的 reader 场景；当前 fixture 坐标 inert |
| [ADR-0004](../../90_HISTORY/ADR-0004_RECOVERY_ROUTING_SINGLE_SOURCE.md) | #73 冻结长期裁决的 rationale/tradeoff 文件化，待 exact-head Review |

## Compatibility and provenance

human/README 的自起链改为 current L0/catalog/Bootstrap pointer；旧 Depositor v0.1 仅加 historical/current forward，current 0.1.3 未改，未引入 0.2 语义。

旧文件都保留原路径；Session 旧 section headings/anchors 转 current home。CONTEXT_MODE_SEED、handoff 与 capability 模板保留旧 anchors，转协议定义。旧 Session 与 provider/Context Mode Seed 正文可从 exact base Git blob 追溯；不复制旧 live instruction，不删除 Git provenance。旧 REQUEST/ACCEPTED 中文字段仍可解释；新 current contract 不将它们套到 crash。

[DeepSeek guide](../DeepSeekPP-github-mcp-usage.md) 退休为 current Bootstrap/Interface/Change Lifecycle forward。#26 研究与 #69 audit artifacts 原样保留为历史 evidence，未提升为 normative authority。templates 对实际私有坐标的清理只改 current 文本，不重写历史。

## Execution / validation / rollback

阶段：live base + durable plan → 独立 clone/branch → R1/R2 bulk edits → deterministic checks → isolated fresh-reader snapshots → 少量逻辑 commits → 一个 published PR/exact-head CI → #74 final report → Global Review。

常规结构验证：`python tools/routing.py --check --check-whitespace --base-ref <current-base-ref>`、`python tools/test_routing.py`；machine-readable 文件 parse；changed-current links/anchors、inert copyable surfaces、当前 compatibility pointers 与 kernel-only L0 route。CLI 的显式 base 优先，其次 `ROUTING_BASE_REF`，本地未提供时取 `HEAD` 检查工作副本差异；CI 使用 PR base / push before，零 before 用 empty tree 检查首次创建的内容，不回退 R74 历史 SHA。catalog/projection 改动运行 `python tools/routing.py --write` 后再 check。

本轮一次性证明由 [check_r74_migration.py](../../tools/check_r74_migration.py) 单独承担：显式执行 `python tools/check_r74_migration.py --base-ref e6de9acdafbc3b9d12802ecf8de25f444074553b --head-ref <candidate-sha>`，比较 R74 的 L0 Git blob 与七个旧入口 anchors。base 取自本工单 authority，不是常规校验器/CI 的永久规则；未来迁移不能把本脚本冒充通用 L0/compatibility 治理。generic regression 使用独立新 Git history，证明不依赖该 SHA，且未来 L0/anchor 改动只在显式 R74 proof 下被拒绝。

结构 fixtures 不代表真实 Agent 行为；原五类 readers 的 files/bytes/hops/blockers/canonical accuracy/crash outcome 是初次候选的冻结证据。本次 repair 未重跑模型读者，source delta 与新的 exact-head 机械证明由 #74 repair report 分别记录。

Rollback boundary：仅 feature branch，可由后续 current authority revert/supersede；兼容路径保留，不重写历史。若语义 single-source 或实际 reader 成本/正确性无法满足，停在 Review boundary 报 exact conflict。

当前 checkpoint：implementation candidate，mechanical/fresh-reader/final published-head receipts 以 #74 报告为准；本 artifact 不自行宣称 acceptance 已通过。
