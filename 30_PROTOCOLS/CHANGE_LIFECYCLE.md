# 文档即代码与变更生命周期

**Classification: L2 Targeted Reference**  
**Protocol Version: 0.1.0**

本协议定义代码与文档 Artifact 的统一变更留痕方式。目标不是把所有 Markdown 都变成重治理对象，而是让**真正会影响 Human / Agent 判断的文档**拥有和代码一样可审查、可追溯、可回滚的生命周期。

核心句：

> **Issue 管理由，ADR 管长期裁决，Artifact 承载当前内容，PR 管审查，checks 管机械验证，Git 管历史。**

---

## 1. 什么算 Artifact

以下对象只要进入 Git，就按 Artifact 看待；文档不因扩展名是 `.md` 而低于代码：

- Code / script / config / schema；
- `AGENTS.md`、Protocol、Prompt、Template；
- Architecture / Operating Model / Contract / Runbook；
- SSOT / canonical registry / durable fact model；
- ADR；
- README / navigation / derived state / report。

不同 Artifact 的治理强度可以不同，但都应保留 Git history。不要把“文档”理解成可以直接覆盖、无需解释来源的附件。

---

## 2. 两种文档治理模式

### 2.1 `STRICT_DOCS_AS_CODE`

当文档满足任一条件时，默认进入严格模式：

- 是 Agent 冷启动、执行、Review、恢复的规则输入；
- 定义 authority、scope、ownership、schema、stable ID、lifecycle、contract；
- 承载 canonical truth / SSOT；
- 改动会改变 Human / Agent 的行为、判断或验收方式；
- 是重要 Architecture / ADR / Prompt / Protocol / Template；
- 项目明确声明该文档属于严格 docs-as-code。

严格模式要求按 §3 的变更等级走 branch / PR / Review；L1/L2 必须有 Issue，L2 还要有 ADR。

`ai-use` 自身的治理文档默认属于 `STRICT_DOCS_AS_CODE`。

### 2.2 `PERIODIC_DOCS`

低关键、可再生、derived / navigation / presentation 类文档可以使用周期性维护：

- README 的非规范性导航；
- 可由 canonical source 重新生成的视图；
- 周期性状态汇总 / 人类浏览摘要；
- 不承担 authority / contract / canonical truth 的说明材料。

允许一个周期性维护 Issue 聚合多项同类刷新，再由一个或多个 PR 收敛；更新频率由项目按漂移成本决定，不在 ai-use 固定天数。

**升级规则：**一旦某次更新触及 normative rule、canonical truth、authority、schema、stable ID、ownership、长期行为语义或兼容性，就不能继续按 `PERIODIC_DOCS` 处理，必须升级到 `STRICT_DOCS_AS_CODE` 并重新判定 L1/L2。

Project Architect 负责项目内默认模式与文档例外的 durable 声明；跨项目或 ownership 冲突由 Global Architect 裁决。Builder / Research 不得为了省流程自行把 L1/L2 降成 L0 或 PERIODIC。

---

## 3. 变更等级

### L0 — 非语义维护

只允许：

- 错字、标点、排版；
- 死链修复；
- 不改变含义的等价重述；
- 纯格式 / lint / generated formatting。

流程：

```text
branch
  -> 修改
  -> checks（如适用）
  -> PR
  -> Review
  -> merge
```

L0 可以不单建 Issue，但 PR 必须说明为什么确定“无语义变化”。如果 Review 时发现含义、行为或 current truth 已变化，立即升级 L1/L2。

### L1 — 实质变化

典型包括：

- 普通规则、Prompt、Template、Runbook 的语义变化；
- Code / tool behavior 改变；
- durable fact / asset fact / current state 的实质更新；
- 普通迁移；
- 非架构级 contract 扩展；
- 需要解释“为什么现在要改”的文档变化。

流程：

```text
Issue
  -> branch
  -> 修改
  -> checks
  -> PR
  -> exact-head Review
  -> merge
  -> Issue 收敛
```

Issue 是本次变化的 rationale / acceptance anchor；不要把完整历史理由只塞在 commit message 或 chat。

### L2 — 长期架构 / 治理变化

典型包括：

- authority / governance boundary；
- stable ID / identity model；
- schema 或 canonical fact-state 语义；
- SSOT / ownership / directory responsibility；
- lifecycle state machine / compatibility contract；
- 长期 cross-project interface；
- 一旦遗忘“为什么这样设计”就容易重复踩坑的难逆裁决。

流程：

```text
Issue
  -> ADR
  -> branch
  -> 修改 / migration
  -> checks
  -> PR
  -> exact-head Review
  -> merge
  -> Issue 收敛
```

ADR 记录的是**长期设计选择与取舍**，不是重复粘贴 Issue。后续改变裁决时新增 ADR 或明确 supersede；不要改写旧 ADR 让历史看起来从未发生。

---

## 4. 文档与代码的共同规则

1. **PR-first。** 受治理 Artifact 不直接改 main；L0 也用 branch + PR 留 diff。
2. **版本历史不删除。** 错误方案用 revert / supersede / correction 收敛，不通过改写历史制造“从来没发生过”。
3. **Review 绑定 exact head。** L1/L2 的重要结论必须基于被审查的 exact diff/head；head 漂移后重新核对。
4. **Checks 与语义 Review 分工。** CI/checks 负责格式、schema、generated view、测试等机械验证；Architect/Reviewer 负责语义、authority、currentness 与 scope。
5. **不要重复 Git metadata。** author、timestamp、commit parent 等已有 Git 事实不要求每个 Markdown 再写一遍；只有机器或 Human 真正需要稳定读取的 metadata 才进入 Artifact 正文。
6. **文档不是第二 SSOT。** derived/read-model 文档必须能指回 canonical source；周期性文档不能因“更好读”而夺取事实 ownership。
7. **代码也按同一等级判断。** 小代码 diff 不自动是 L0；只要改变行为就是至少 L1，架构/authority/schema seam 变化可升 L2。

---

## 5. Issue / ADR / PR 各自回答什么

| Artifact | 主要回答 |
| --- | --- |
| Issue | 为什么改、当前问题、范围、acceptance、stop |
| ADR | 为什么长期选择 A 而不是 B、代价、被替代关系 |
| Branch/Artifact | 实际内容与实现 |
| PR | 这一次 exact diff 改了什么、如何验证、关联哪个 Issue/ADR |
| Checks/CI | 哪些机械约束已通过/失败 |
| Git history | 什么时候、由什么 diff 演化到现在 |

不要让同一段长说明在五个地方全文复制；使用 durable pointer 连接即可。

---

## 6. 周期性文档维护

`PERIODIC_DOCS` 推荐模式：

```text
周期维护 Issue
  -> live read canonical source
  -> 批量刷新 derived/navigation docs
  -> checks / drift scan
  -> PR
  -> Review
  -> merge
```

一个维护 Issue 可以覆盖同周期、同性质的多份低关键文档；不要为了每个日期、链接、数字机械开一个 Issue。

如果刷新过程中发现：

- canonical source 自身需要改变；
- 文档描述与真实 contract 冲突；
- 需要改变 authority/schema/ownership；
- 不是“同步现状”而是在重新定义现状；

则停止把该项当周期维护，另开 L1/L2 Issue。

---

## 7. 回滚与历史

效果不好时优先：

1. 用新 Issue/PR 说明 regression；
2. 对 exact commit / PR 做 revert，或用新版本 supersede；
3. 保留旧 Issue / ADR / PR 作为 historical evidence；
4. 如果旧版本只在特定条件下更好，记录 applicability，而不是简单宣称“旧版错误”。

Git 的价值不仅是恢复文件，更是保留**系统当时为什么这么想**。

---

## 8. 使用入口

需要实际创建 Issue / ADR / PR 时，使用：

`50_TEMPLATES/CHANGE_LIFECYCLE.md`

本协议只定义语义；模板只提供可复制形态。若模板与本协议冲突，以本协议为准并修模板 drift。
