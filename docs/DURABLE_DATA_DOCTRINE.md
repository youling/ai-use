# Durable Data Doctrine v0.1

**Classification: L2 Targeted Reference.**

本文件只定义跨项目可复用的最小 durable-data 语义。它不指定数据库、对象存储、Git 平台或其它 storage engine，也不替代项目自己的数据模型、隐私、安全、删除、合规与业务 retention contract。

当项目设计长期保存的数据、事实、证据、schema 或 migration 时，至少回答下面七类问题。答案可以很短，但不能靠默认猜测。

---

## 1. Identity

Durable entity 应有足够稳定的身份语义，使系统知道“这是同一个对象，还是两个对象”。

至少明确：

- canonical identity / entity key 是什么；
- identity 在什么 scope 内唯一；
- dedup / merge 的边界是什么。

Display name、标题、昵称、文件名等可变标签默认不等于长期 identity，除非项目 contract 明确把它定义为 canonical key。

---

## 2. Semantics

Durable field、record 与 state 必须有可区分的语义，尤其不要把以下状态无意压成同一个值：

- `unknown`：目前不知道；
- `absent`：确认不存在；
- `not-applicable`：该字段对当前对象不适用。

项目可以使用自己的表示方式；本 doctrine 不规定必须使用某种 null/enum/schema 技术。

---

## 3. Provenance

关键事实与重要派生结果应能追到足以支持其结论的来源或 evidence lineage。

需要的 provenance 强度由项目风险与用途决定。并非每个 durable datum 都必须携带同样的 observation metadata，也不要求所有 provenance 存储都采用 append-only；但不能在需要核验来源时只剩无法解释的最终值。

---

## 4. Immutability

项目应明确区分：

- 哪些内容属于 append-only / versioned history / evidence；
- 哪些内容属于允许覆盖的 current state。

“durable”只表示需要跨会话、进程或执行环境保留，不自动意味着 immutable。反过来，current state 可以覆盖，也不自动要求每次覆盖都生成一份完整历史。

---

## 5. Derivation

Canonical/source data 与 derived/rebuildable data 应保持语义区分。

Cache、index、embedding、materialized view、summary 等派生层可以长期保存，但不得仅因为保存时间长、查询方便或使用频繁，就静默升级成唯一事实来源。

当派生数据承担关键决策输入时，应能说明它来自什么 source，以及 source 或 derivation logic 变化后如何判断是否需要重建。

---

## 6. Retention

需要长期保存的数据应声明适合当前项目的 retention class，而不是因为“不敢删”默认永久保存所有东西。

常见语义可以包括：

- `permanent`；
- `long-term / compressible`；
- `short-term`；
- `rebuildable`。

具体期限、成本权衡、隐私/法规义务与删除策略属于项目或专门 contract，本文件不替项目决定。

---

## 7. Migration

Durable schema / format / compatibility 发生变化时，演进应当：

- 可解释：知道旧语义如何映射到新语义；
- 可测试：关键 compatibility / conversion path 有可验证证据；
- 在确有需要时保留 conversion、recovery 或 rollback path。

Storage engine 的替换不等于语义 migration；反之，即使 storage engine 不变，字段或状态语义变化也可能是 material migration。

---

## Durable state 的三类常见归属

这是一条语义分界，不是强制存储产品清单：

1. **Institutional durable truth**：代码、contract、Work Graph、Issue/PR/Review、commit、architecture decision、工程 evidence 等组织/工程事实，通常由 Git/GitHub 或等价 durable collaboration system 承载。
2. **Business durable truth**：真实业务对象、交易/运营历史、业务 evidence 等，应由项目自己的 durable business store 承载；不能因为工程系统也“有状态”就把业务事实强行迁入 GitHub。
3. **Replaceable / rebuildable state**：Agent context、chat working memory、workspace、process、cache、index、ephemeral runtime state 等默认是可替换执行状态，除非项目 contract 明确把其中某部分提升为 durable source。

三类可以互相引用，但引用不改变 ownership。派生层也不能反向覆盖 canonical source 的语义主权。

---

## 使用边界

本 v0.1 只冻结七个最小问题：`Identity / Semantics / Provenance / Immutability / Derivation / Retention / Migration`。

以下主题可能与 durable data 强相关，但不在本文件里扩成统一制度：

- Authority；
- Privacy & Secrets；
- Deletion；
- Regulatory / legal retention；
- 项目特定 data quality / access-control / backup policy。

遇到这些场景，应读取对应 current governance / security / project-local contract；不存在足够规则时按上层 fail-closed 原则处理，而不是从本 doctrine 推导未授权要求。
