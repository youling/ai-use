# R80 bounded semantic regression evidence

**Artifact Version: 1.0.0**

这是 [R3 Work Order #80](https://github.com/youling/ai-use/issues/80) 的一次 synthetic reader evidence，非规范、生产验收、Capability Lab schema 或 Global Architect Review。

## 固定输入与独立性

候选规范 revision：`c8bfee320903e8bd9ff5e8f4781d7514d848b32f`。四个场景使用该提交的 `AGENTS.md` 与下列限定 sources。source implementation 来自不继承 parent history 的 Fresh Builder；reader 为另一个无 parent history 的只读 context。parent 预先固定判定标准，reader 只收到规范原文与问题，不读取判定标准、实现者自述或旧 reader 报告。四场景由同一个新 reader context 顺序回答，不声称四个互相独立的 reader。

这是 supplied-source comprehension walkthrough，未测 cold-start navigation、真实平台 mutation、规模/性能或生产数据。parent assessment 仍是本任务的 self-review，不能替代 exact-head Global Architect Review。

| Source | SHA-256（Git blob 内容） |
| --- | --- |
| `30_PROTOCOLS/OWNER_INSTANCE_BOUNDARY.md` | `780aab483cb63b5ef4609832f336304a31b940db93b0a4e08a1c7b57aee90395` |
| `30_PROTOCOLS/GITHUB_NATIVE_FIRST.md` | `a9843eaeb7ea2f739620746b8562976dd9554fb3eb8e6d9c368436e01aa842b8` |
| `docs/ARCHITECT_RECONNAISSANCE.md` | `abb4d3903823223e67794856d2c801f23db995a3e531664bae3146b13a48d135` |
| `docs/DURABLE_DATA_DOCTRINE.md` | `79e045f2642216f8e3879806f3e2a7756c3145921ec6db4a165ea3a5c6196b08` |
| `30_PROTOCOLS/DIAGRAM_AS_CODE.md` | `f5fae70fcec8cdb5809ff3cb2147a38e1e956bccf0813a3e7010cfc7ca06a39b` |

`AGENTS.md` Git blob：`895ac985494569f58e28264b010f9f3cccc32dc2`，与 R3 base `674afc5f11274d0c5ec691663783dd00c746d282` 相同。后续 evidence-only commit 不改变上述 source；最终 head 身份与 CI 留在 PR / #80 build report。

## 四个固定场景

### 1. native-control

Sources：[GitHub Native First](../../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md)、[Reconnaissance](../ARCHITECT_RECONNAISSANCE.md)。

问题：一个 GitHub-hosted 项目准备自建跨工单控制 dashboard、状态列和 webhook worker。团队认为 Projects 可用且 CI 全绿，所以可直接让拖拽列改写所有业务状态，并把文档写成 PLATFORM_ENFORCED。你会怎样选路、评估原生能力和授权边界？若只是已冻结方案里的普通 bugfix，流程是否相同？

预定判据：触发 targeted native-first；Projects authority 须 explicit owner contract；区分 DERIVED/HUMAN_OWNED/SUGGESTED；event hint → live-read → reconcile → idempotent mutation；CI 不证明 platform enforcement；普通 bugfix 无 mandatory scan。

### 2. private-overlay

Source：[Owner / Instance Boundary](../../30_PROTOCOLS/OWNER_INSTANCE_BOUNDARY.md)。

问题：owner 域已定义事实和稳定身份。另一个消费者想在私有仓缓存这些事实，保存部署配置和 secret reference，并因读写方便自称新 SSOT；更换 endpoint 后还打算给原对象换身份。哪些做法成立、哪些需要改正？怎样判断是否拆分私有实例，怎样处理含糊的敏感字段，以及怎样处理一次连接成功后的生命周期结论？

预定判据：overlay 不转移 owner；owner pointer、bounded purpose、currentness rule、无 unique foreign-domain truth；identity != locator；secret reference/value 与 privacy/access 分开；evidence-triggered split、UNKNOWN reconcile；连接成功不提升 lifecycle。

### 3. snapshot-target

Source：[Durable Data Doctrine](../DURABLE_DATA_DOCTRINE.md)。

问题：查询使用 r10 的旧 snapshot，目标是 r12，interpreter 版本已知。A：已确认 r10 是祖先，完整 delta 显示所问实体及依赖没有变化。B：同样的 delta 列表在 API 限额下被截断，没看到该实体变化。C：完整相关变化已用 incremental overlay 应用。三种情形分别能声称什么 currentness？应该读取多大的 artifact，如何验证 overlay 与 rebuild、如何追溯来源，以及只 git clone 能否恢复整个平台？

预定判据：A 可证明特定 query 在新目标成立，snapshot 本身仍旧；B 不声称 current/UNKNOWN；C 须 source、target、ancestry/delta、interpreter 与 query correctness/equivalence evidence；最小充分 artifact、canonical pointer；四类 recovery 分开。

### 4. derived-disagreement

Sources：[Diagram-as-Code](../../30_PROTOCOLS/DIAGRAM_AS_CODE.md)、[Durable Data Doctrine](../DURABLE_DATA_DOCTRINE.md)。

问题：同一 canonical domain 的 index 解析器和 diagram 解析器对一条 owner 关系给出不同结果。diagram renderer 校验和浏览器渲染都成功，画面更清楚。团队建议按 renderer schema 修改领域事实并把所有实体一次性画入总图。下一步怎么处理，什么证据才支持两个派生面等价？

预定判据：冲突为 derivation defect，回源核对；共享 reviewed normalized interpretation 或证明 semantic equivalence；renderer schema 不拥有 ontology，render 成功不证明 truth；bounded drill-down 保留关键语义。

## Reader 观察与 parent 判定

reader 核对的 HEAD 与所有 bundle 均为上述 candidate revision，报告先读 AGENTS、只读指定 sources，未读取 rubric/旧评估；没有外部动作。以下为可复核的回答摘要，非推理过程。

| 场景 | 实际回答中的关键结论 | Parent 对预定判据的 assessment |
| --- | --- | --- |
| native-control | 做 targeted ARCH-0/native comparison，按 seam 记录六种 decision；Projects capability 不授予业务写权；拖拽映射已有 owner transition 或仅改呈现；保留三类字段；event 经 live-read/reconcile/幂等 guard；CI 不足以证明 PLATFORM_ENFORCED；普通 frozen bugfix 无强制扫描。 | PASS，全部判据覆盖。未测真实 GitHub 配置。 |
| private-overlay | 接受受约束 cache/本地配置，拒绝第二 SSOT；明确五项 overlay 条件和原 owner mutation；endpoint 变化不重置 identity；实际 access/lifecycle/retention 证据决定拆分；reference 不默认公开，授予能力的 reference 按 value 处理；含糊材料 scoped fail-closed/reconcile；连接成功不代表 ready/accepted/complete。 | PASS，全部判据覆盖。未触及真实 secret 或部署。 |
| snapshot-target | A/C 只可能对限定 query 支持 r12，不把整个 r10 snapshot 变成 current；B truncated => UNKNOWN/保留旧历史结果；主动指出还须 source completeness、live-resolved target、interpreter/config 与相关 non-Git state，C 还需 ancestry；最小充分读取、canonical pointer、overlay/full-rebuild 对照和四层 recovery。 | PASS；reader 正确保留题设未给事实的条件，没有无条件晋升 currentness。没有执行真实增量引擎。 |
| derived-disagreement | 视为 derivation defect，回 current canonical/source revision/interpreter 核对；renderer 不裁决 ontology，render 仅证明相应呈现结果；共享解释边界或限定 query/domain 的 identity/field/relation/derivation 对照；bounded drill-down 保留语义，无统一节点数上限。 | PASS，全部判据覆盖；不虚构强制 equivalence-test schema。没有真实 renderer/生产图测试。 |

未发现阻止这四个场景判断的文本内矛盾。结论仅支持此 revision 的有界阅读表现，不证明所有 Agent/场景均正确。

本次可选 OpenCode transport 未取得成功模型输出，不能计作 reader evidence；实际能力缺口与 fallback 记录在 [#80 checkpoint](https://github.com/youling/ai-use/issues/80#issuecomment-5750909716)。上表来自其后的无历史只读 reader。

## 结构与兼容证据

固定 R3 base 下的 parent 一次性检查确认：L0 Git blob 相同；旧 catalog entries 与 schema/navigation/projection/compatibility metadata 原样保留；只加两个 routes；七项 Data 基础问题原文保留；既有 Diagram renderer/readability/drill-down 段落保留，新增内容为补充；三个扩展文档的原 section anchors 保留。Data versioned H1 从 v0.1 改为 v0.2。

现有 `python tools/test_routing.py`：20 tests PASS。`python tools/routing.py --check --check-whitespace --base-ref <R3-base>`：schema、四个 generated projections、changed Markdown links/anchors 与 whitespace PASS；四投影均重新生成，其中 NAMESPACE 字节不变。有限 public-copy guard 与新增内容人工复核未发现新增私有实例事实，不宣称穷尽式 secret clearance。

复核方式：checkout candidate revision，按上述 source 限定向 fresh reader 提供四个问题，隐藏判据，独立比较答案；机械检查使用仓库现有工具。reader 输出不是确定性测试；GitHub Actions 负责结构回归，semantic Review 负责最终意义判断。
