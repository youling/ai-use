# 文档 / 代码变更留痕模板

**版本：0.1.0**

以下内容就是可复制模板。先按 `30_PROTOCOLS/CHANGE_LIFECYCLE.md` 判定 `L0 | L1 | L2` 与 `STRICT_DOCS_AS_CODE | PERIODIC_DOCS`，再复制最接近的一组。

没有适用字段就删除，不留空壳。

---

## L0：无语义变化

适合错字、排版、死链、等价重述。

### PR

```text
变更等级：L0
变更对象：README / 导航链接整理
为什么是 L0：只修正死链与排版，不改变规则、事实、行为、authority 或 contract。
验证：链接 readback；diff review；相关 checks 通过。
回滚：直接 revert 本 PR 即可。
```

L0 不要求单独 Issue；如果改着改着发现含义变了，停止并升级 L1/L2。

---

## L1：实质变化

### Issue

```text
标题：【实现】统一双词派单模板与四类运行位置

背景：当前已有 Human Dispatch Card / Minimal Agent Seed 语义，但缺少单一可复制模板，导致各架构师自行发挥。
目标：新增统一模板；Human 派发卡收敛运行位置；Agent Seed 改为中文扁平键值。
范围：模板 + 对应 canonical interface 文档；不改 runtime authority / deploy / destructive gate。
Acceptance：模板可直接复制；旧格式保留 historical provenance；PR exact-head Review 后合并。
变更等级：L1
```

### PR

```text
关联：Closes #<issue>
变更等级：L1

改了什么：
- 新增 / 更新哪些 Artifact；
- 哪些语义发生变化；
- 哪些旧格式仅保留 historical provenance。

验证：
- targeted tests / lint / schema / readback；
- git diff / secret scan（如适用）。

Review：exact head <sha>
回滚：revert 本 PR；历史 Issue / PR 保留。
```

---

## L2：架构 / 治理长期变化

### Issue

```text
标题：【架构】调整 <领域> 的 canonical ownership / schema / authority boundary

背景：现有模型在 <场景> 出现冲突或长期漂移。
要解决的问题：<一句话说明>。
拟改变：<ownership / authority / schema / stable ID / lifecycle / cross-project contract>。
明确不改变：<非目标>。
Acceptance：<新的长期不变量>。
变更等级：L2
ADR：REQUIRED
```

### ADR

```text
# ADR-XXXX：<裁决标题>

状态：Accepted
来源 Issue：#<issue>

## Context
为什么现在必须做长期选择。

## Decision
选择什么；新的 ownership / contract / invariant 是什么。

## Alternatives
至少记录被认真考虑但未采用的主要方案，以及为什么没选。

## Consequences
得到什么；付出什么；迁移/兼容成本是什么。

## Supersedes / Superseded by
没有就省略。
```

### PR

```text
关联：Closes #<issue>；ADR-XXXX
变更等级：L2

本 PR 实施 ADR-XXXX：
- 变更 canonical Artifact；
- 必要迁移 / compatibility；
- 明确不顺手扩大 runtime / authority / scope。

验证：
- deterministic checks；
- migration / compatibility checks；
- exact-head semantic Review。

Review：exact head <sha>
回滚：按 ADR 与 migration 边界执行 revert / supersede；不得改写旧 ADR 历史。
```

---

## PERIODIC_DOCS：周期性低关键文档维护

### 周期维护 Issue

```text
标题：【文档维护】2026-09 derived / navigation refresh

模式：PERIODIC_DOCS
范围：README 导航、CURRENT_STATE derived view、链接与人类浏览摘要。
Canonical source：<repo/contracts/registry/issues 等真实来源>。
本轮只做：从 current durable source 同步现状；不重新定义 authority / schema / ownership / contract。
升级条件：若发现需要改变 canonical 语义，拆出 L1/L2 Issue，本 Issue 不承载。
完成：批量 PR + checks + Review + merge 后关闭。
```

### PR

```text
关联：#<periodic-maintenance-issue>
模式：PERIODIC_DOCS

刷新：
- <doc A>：同步 current source；
- <doc B>：修正 stale pointer；
- <doc C>：更新 derived summary。

未改变：authority / canonical truth / schema / ownership / behavior。
验证：source readback + drift/generated check。
```

---

## 快速判定

```text
只是错字/排版/死链？
  -> L0

改变规则、事实、模板、代码/工具行为？
  -> L1

改变 authority / stable ID / schema / SSOT ownership / lifecycle / 长期接口？
  -> L2 + ADR

只是低关键 derived/navigation 文档跟随 canonical source 更新？
  -> PERIODIC_DOCS

拿不准？
  -> 不降级；按 L1 起步，必要时由 Architect 判为 L2。
```
