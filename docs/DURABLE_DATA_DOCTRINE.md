# Durable Data Doctrine v0.2

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

## 8. Current Read / derived freshness

`canonical/history cost != current-read cost`：长期保存完整历史，不意味着每次查询必须加载全部历史。消费者应 **read the smallest sufficient artifact**，从能回答当前问题的最小 catalog/index/projection 开始，必要时按 pointer 下钻 canonical source 与 provenance；不能用“小”作为省略必要证据的理由。

已知 exact identity/address 且直接读取 canonical source 更小、更充分时，优先该路径；index/snapshot 不是每次查询的必经层。

大型 durable-data 系统可按需采用 Current Read Plane：

```text
Canonical Source
 -> reviewed normalized interpretation
 -> tiny catalog / bounded index
 -> query projection / graph / snapshot
 -> source / provenance drill-down
```

这是 optional pattern，不要求 SQLite、数据库、特定 query engine 或中央 runtime。derived result MUST 保留 canonical identity/source pointer 及支撑结论所需 provenance，不能因为查询更快而成为新的写 authority。owner/storage/private overlay 边界见 [Owner / Instance Boundary](../30_PROTOCOLS/OWNER_INSTANCE_BOUNDARY.md)；同 domain 的多个 derived surfaces 按 [Diagram-as-Code](../30_PROTOCOLS/DIAGRAM_AS_CODE.md#41-共享派生解释边界) 共用解释边界或证明语义等价。

### 8.1 Snapshot freshness 与 query freshness

`snapshot_freshness != query_freshness`：snapshot 对它的 source revision 正确，不证明它能回答当前 target 的问题；旧 snapshot 也不必全量重建后才能回答所有查询。currentness claim 必须绑定明确 query class、范围与 live-resolved target，不能把某次查询成立外推为整个 snapshot current。

以旧 snapshot 回答较新 target 时，MUST 能证明：

1. **Source revision**：snapshot 基于哪个 exact canonical revision/checkpoint，以及其 source completeness。
2. **Target revision**：本次要回答哪个 current revision/checkpoint；不得仅用模糊的“latest”。
3. **Ancestry / delta completeness**：source 与 target 的关系成立，相关变化已完整取得；包含 query 所依赖的记录、关系、删除与适用 non-Git state。非 Git source 使用 owner 定义的等价 checkpoint/delta contract。
4. **Interpreter version**：derivation/normalized interpretation 的版本与配置已知且适用；代码/语义变化也须计入影响判断。
5. **Query correctness**：完整 delta 证明该 query class 未受影响，或已正确应用所需 incremental overlay；只检查有变化的文件名不自动等于语义无影响。

无法证明 ancestry、delta completeness 或相关 non-Git state 时，不能声称新 target current。incomplete、truncated、forbidden、unknown evidence 一律不给 currentness claim；保留可证的旧 revision/historical result 或返回 UNKNOWN，并 targeted reconcile/重建。空搜索结果和不可见记录不能替代完整性证据。

### 8.2 Incremental overlay 与重建

Incremental derived store 若声称与 full rebuild 等价，SHOULD 在 owner-local 对所声明 query classes 保有对照 tests/evidence，覆盖其 contract 涉及的新增、修改、删除、关系变化与 interpreter migration。测试只证明记录范围内的等价，不替代本次 target/delta currentness guard；overlay 的本地新值也不能接管 canonical truth。

## 9. Recovery 分层

`git clone != full GitHub operational-plane recovery`。恢复设计应区分实际需要的层，而非默认一个备份动作覆盖全部：

| 层 | 应说明的恢复边界 |
| --- | --- |
| Canonical Git truth / refs | 需要保存哪些 Git objects、branches/tags/refs，以及恢复后的 revision 核对。 |
| Desired platform configuration | rules/protection、workflow/integration 等 desired settings 的 owner、可恢复声明与重新应用所需 authority；Git 中有配置不证明平台已生效。 |
| Non-Git GitHub metadata | 所需 Issues/PRs/reviews、relationships、Projects/fields 等平台对象的导出、关联映射与恢复保真范围。不能假定能原样重建原 IDs/authors/timestamps。 |
| External payload / object data | 未纳入 Git 的 artifact、package、release attachment、外部对象等内容的独立保存、access 与完整性验证。 |

只对项目实际需要的层声明 owner-local recovery contract、retention 与验证范围；不规定统一备份产品或全量导出每种 metadata。恢复工具成功不证明所有层已恢复，derived store 可重建也不证明其 canonical payload 仍可取得。

---

## Durable state 的三类常见归属

这是一条语义分界，不是强制存储产品清单：

1. **Institutional durable truth**：代码、contract、Work Graph、Issue/PR/Review、commit、architecture decision、工程 evidence 等组织/工程事实，通常由 Git/GitHub 或等价 durable collaboration system 承载。
2. **Business durable truth**：真实业务对象、交易/运营历史、业务 evidence 等，应由项目自己的 durable business store 承载；不能因为工程系统也“有状态”就把业务事实强行迁入 GitHub。
3. **Replaceable / rebuildable state**：Agent context、chat working memory、workspace、process、cache、index、ephemeral runtime state 等默认是可替换执行状态，除非项目 contract 明确把其中某部分提升为 durable source。

三类可以互相引用，但引用不改变 ownership。派生层也不能反向覆盖 canonical source 的语义主权。

---

## 使用边界

本 v0.2 保留七个最小问题：`Identity / Semantics / Provenance / Immutability / Derivation / Retention / Migration`，并兼容补充 optional Current Read、query freshness 与 recovery 分层；不把可选读取模式变成统一技术要求。

以下主题可能与 durable data 强相关，但不在本文件里扩成统一制度：

- Authority；
- Privacy & Secrets；
- Deletion；
- Regulatory / legal retention；
- 项目特定 data quality / access-control / backup policy。

遇到这些场景，应读取对应 current governance / security / project-local contract；不存在足够规则时按上层 fail-closed 原则处理，而不是从本 doctrine 推导未授权要求。
