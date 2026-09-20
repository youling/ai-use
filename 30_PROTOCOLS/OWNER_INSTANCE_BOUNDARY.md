# Owner / Instance Boundary

**Classification: L2 Targeted Reference.** 仅在 semantic owner、存储/实例拆分、private overlay、pointer/projection 或 secret handling 边界需要判断时读取。

**Protocol Version: 1.0.0**

语义 owner：[工作项 #66](https://github.com/youling/ai-use/issues/66)；长期裁决：[ADR-0005](../90_HISTORY/ADR-0005_OWNER_NATIVE_DERIVATION.md)。本协议细化既有 L0，不另立 authority、项目 schema、vault 或全局保密分类制度。

## 1. 先分清 owner、位置与消费者

| 概念 | 拥有什么 / 不拥有什么 |
| --- | --- |
| Semantic owner | 对某个 domain fact、identity、contract 或 lifecycle 的含义、合法变化与冲突裁决负责；由 current owner contract 确定。 |
| Physical / storage location | 文件、仓库、数据库、对象或运行位置；回答数据在哪里，不因存储方便而获得语义主权。 |
| Consumer pointer / reference | 指向 owner 的 canonical identity/source 及必要 revision；允许定位和访问，不复制出第二份 SSOT。API 是访问 seam，同样不转移 ownership。 |
| Derived projection / read model | 由 source 与解释逻辑生成的 cache、index、snapshot、导航或 summary；保留 provenance/currentness，可重建，不反向定义源语义。 |
| Private instance / overlay | 面向特定部署的配置、实例状态或本地补充；只能拥有明确属于自身 domain 的事实，不能接管被引用 domain 的事实。 |
| Secret reference / secret value | reference 用于安全定位或请求 secret；value 是能直接行使访问、签名、解密、恢复等能力的材料。两者不可混用，也不能默认 reference 可以公开。 |

`identity != locator`：改路径、主机、repo 或存储产品不自动产生新实体；名称相同也不能证明是同一实体。identity/locator 映射与迁移由 owner 维护，不从邻近目录或访问成功推断。

## 2. Single-canonical-copy invariant

同一语义事实 MUST 有明确的 canonical owner/source。保存、备份、缓存、索引、公开摘录或私有投影不因成为另一份物理 copy 而产生第二个 owner；本规则不禁止冗余存储或灾备。

消费者 MUST 保留 owner/source pointer 及用途所需 provenance，区分源事实、派生结果和本地独有事实。若需要改变外域事实，走 owner 的 current mutation contract；不能先改本地 mirror，再让 owner 接受既成事实。多处 copy 冲突时回到 current canonical source reconcile，不按最新文件时间、读取方便或展示效果选真相。

公共治理只保存可复用机制、协议与 inert 示例。真实部署 registration、runtime configuration、当前 Work、账户/节点/endpoint/topology 留在对应实例 owner；`reusable mechanism != private instance fact`。跨仓使用 pointer/contract/adapter，不能把外域模型全文吸收成自己的 schema。

复制或派生 MUST 保留 source handling constraints 与 provenance；公开输出必须满足源允许的公开/脱敏边界。换成 projection、Release、网页或 cache 不能绕过原 access、retention、删除或 secret-handling 约束。

## 3. Private overlay 的准入条件

Private overlay 只有同时满足以下条件才可作为当前 consumer artifact：

1. **Explicit owner pointer**：标明 foreign-domain source、canonical identity 与本地 owner；读取者能区分谁定义哪部分语义。
2. **Bounded local purpose**：例如部署配置、受限访问的执行副本或查询加速；不是另建一份无边界的 owner registry。
3. **Reconciliation / currentness rule**：说明何时 live-read、何时失效/重建、冲突如何回到 owner，以及中断后如何确定已发生的 effect。
4. **No unique foreign-domain truth**：外域事实的唯一最新值不得只藏在 overlay。真正属于本地 domain 的新增事实可留本地，但必须与源字段分开，不能伪装成源事实。
5. **Source constraints preserved**：private ACL 不解除源的安全、provenance、retention 或删除义务；能读取的消费者不自动获得修改 owner 的 authority。

例如 owner-domain 的记录通过 canonical pointer 供私有部署引用，本地另存该部署的配置并按 owner revision 重建查询 cache：这不建立第二 owner。若 cache 中出现 owner 不知道的唯一外域状态，必须先 reconcile 或修正 ownership contract，不能称其为“只是 overlay”。

## 4. 什么时候拆出 private instance / repo

拆分应由实际证据触发，不按仓库名字、美观或“以后可能需要”机械拆仓：

- 已有任务确实需要 real private/runtime facts；
- instance 需要独立 lifecycle、access 或 retention；
- public-safe mechanism 与 deployment-local state 已无法在同一 artifact 中保持清晰且可审查的边界。

命中这些信号时，先在 owner-local decision 中说明需隔离的内容、访问者、生命周期和 canonical pointer，再选择最小充分的 instance/storage/repo 边界；并非一律新建仓库。拆分 MUST 保留原 semantic owner，按 [Change Lifecycle](CHANGE_LIFECYCLE.md) 处理 material contract/migration，不能把移动文件当作移交 authority。

## 5. Privacy / access 与 secret 分开判断

Private ACL 和 ordinary private data 首先是访问边界；“放在私仓”本身不定义一种永久 secret 分类。能行使 signing、access、decryption、recovery 能力的材料按功能属于 secret；Human 也可明确指定额外 scoped content 的保护要求。

`secret value != secret reference`。reference 的 schema、locator 与可见范围由 owner-local contract 决定；reference 也可能携带敏感 locator，若其自身足以授予能力则按 secret value 处理。公共协议不规定 vault 产品、SecretReference schema、具体存储平面或私有路径。

`runtime secret delivery != recoverable secret custody`：能向运行进程注入 secret，只证明 delivery 可用，不证明安全托管、轮换、撤销或灾难恢复成立。后者须有 owner-local custody/recovery contract 与适当 evidence，不靠公开保存 secret 来证明。

`exact Human Gate != credential handoff`：需要 Human 的是具体授权、账户/设备确认或 provider-native 操作，不是把密码、token、private key 交给 Agent。疑似泄露或 classification 不明时，对 exact suspect material 暂停传播/使用并 reconcile；不能据此发明永久全局敏感类。

## 6. Unknown 与执行结果

owner、identity mapping、source revision、此前 mutation effect 或 secret boundary 不明时，`UNKNOWN -> reconcile; never blind replay`。只读取解决当前缺口所需的 owner/current evidence；未解决前不能覆盖源事实、重复高影响操作或宣称已同步。

`connectivity/tool success != lifecycle promotion`：可连接、API 成功、文件已写入或缓存可查询，不能把任务推进为 accepted/ready/complete。lifecycle promotion 仍由 owner 的 acceptance、current evidence 与 mutation contract 决定。

Current Read/freshness 见 [Durable Data Doctrine](../docs/DURABLE_DATA_DOCTRINE.md)；GitHub surface 的角色见 [GitHub Native First](GITHUB_NATIVE_FIRST.md)。它们消费本 ownership 边界，不建立新的 authority。
