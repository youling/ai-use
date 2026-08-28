# Bootstrap Check Protocol

**Classification: L2 Targeted Reference.** 仅在启动 / 派发 / 恢复场景触发时读取。

## 启动模型（固化）

启动采用统一的 **Bootstrap Ordered Applicability Model**：

```text
1 ADDRESS
  A Seed + Access Route
  B Durable Dispatch
  C Work Coordinate

2 APPLICABLE RULES
  A Global L0
  B Target Repo / Project Local
  C Current Work / Latest Ruling

3 EXECUTION GATE
  A Authority + Access
  B Live State
  C Bootstrap Conclusion

=> EXECUTION_ALLOWED
```

必须严格按 `1 -> 2 -> 3` 执行。任一关键 gate 无法通过时，立即 `EXECUTION_NOT_ALLOWED`；不得跳过或倒序补读后继续施工。

Seed 只负责寻址，不承载完整任务知识；Durable Dispatch / Work Order 承载任务上下文；Bootstrap Check 负责确认启动链已按顺序建立并且当前状态允许执行。

---

## 1. ADDRESS — 定位

### BOOT-1A Seed + Access Route

解析最小启动地址：dispatch pointer、`work`、`startup_mode`，以及必要的 `access` / exact ref。

**最小 Seed 的目标是“最少无歧义启动信息”，不是机械追求最少行。** 对 private repository，`access: github-private` 属于 bootstrap-critical addressing metadata，必须显式携带；public repository 在 pointer / live metadata 已无歧义时可省略 access。

`access` 只决定首次 durable/live read 的访问路由，不产生 authority。路由选择在本槽位完成：

1. **平台原生 GitHub 能力优先**：若当前 Agent / 宿主提供已授权 GitHub connector、integration 或 native GitHub tool，并能读取目标 repo，则优先用它完成首次 GitHub durable/live read。
2. **本机已认证 `gh` 回退**：原生 GitHub 能力不存在、未连接或实测不可用时，才回退到本机已认证 GitHub CLI / API 路径（`gh`）。
3. **本地 Git workspace 最后进入**：local clone / worktree 只是执行副本，不是首次 SSOT 发现入口；使用其 branch/head/文件作为执行依据前，必须先与 remote exact ref / live metadata 校验。
4. 对 `github-private`，**禁止先用匿名公网 URL / raw HTTPS 探路**；匿名 `404` 不构成 repo 不存在或无权限的 durable 证据。只有已知 `github-public` 时，公开 HTTPS 才可作为后续读取回退。
5. native GitHub 与 authenticated `gh` 都不可用时，报告 `ACCESS_BLOCKED` / `ACCESS_DRIFT`；不得靠匿名公网 404、陈旧 checkout 或猜测继续。

这里只做寻址与访问路径解析，不把 Seed 扩展成任务合同，也不把 access capability 当成治理 authority。

### BOOT-1B Durable Dispatch

使用 BOOT-1A 已选定的 GitHub route 定位当前有效的 `ARCHITECT_*_DISPATCH` / resume dispatch，确认 pointer 可解析，并判断其 current / superseded / historical 状态。

**在 `BOOT-2A` 之前，1B 只能确认地址与 currentness。不得把 Dispatch 正文中的 scope、acceptance、language、behavior 指令作为已适用规则执行。**

### BOOT-1C Work Coordinate

确认 owner/repo、issue、step、role 等 coordinate 无歧义；处理 exact-step、latest-wins、superseded 等当前寻址语义。

**在 `BOOT-2A` 之前，1C 同样只做 coordinate / authority-pointer 解析，不提前适用任务正文。**

本阶段只回答：**“我在哪、用哪条可信 GitHub 路径读 durable state、谁派我来的、当前任务坐标是什么。”**

---

## 2. APPLICABLE RULES — 适用规则

### BOOT-2A Global L0

加载当前 machine-facing Global L0：`youling/ai-use/AGENTS.md`。

这是执行前置不变量。未确认当前 L0 已加载，`BOOT-2A` 不得 PASS。

目标仓 / 项目本地规则和当前 Work Order 可以细化任务，但不得反向覆盖 Human / Global durable ruling / L0 已编译的强制不变量。

### BOOT-2B Target Repo / Project Local

读取目标仓 / 项目本地的必要规则，例如 repo-local `AGENTS.md`、README、直接相关 contract。

该槽位适用于业务项目、control plane、governance、Release 等不同角色；**不要求任务必须存在独立业务 Project**。

### BOOT-2C Current Work / Latest Ruling

现在才对当前 Work Order、Durable Dispatch、latest amendment / ruling 做**规范性适用**，确定：

- Active Mission；
- owns / scope；
- forbidden；
- acceptance；
- stop condition；
- 当前任务特有的行为要求。

本阶段只回答：**“当前适用的上位规则、目标仓/项目本地规则和本案任务分别是什么。”**

---

## 3. EXECUTION GATE — 开工门

### BOOT-3A Authority + Access

确认：

- 当前 identity / role 无歧义；
- 当前角色拥有本轮所需 authority；
- dispatch author / authority pointer 合法（任务契约要求时）；
- BOOT-1A 选择的 `github-private` / `github-public` 访问路径与 live metadata 一致且实测可用；
- 原生 GitHub / `gh` / filesystem capability 不被误当成 Authority。

BOOT-1A 决定“先走哪条访问路径”；BOOT-3A 决定“该访问能力是否真的可用，以及当前角色是否有权执行”。两者不得混为一谈。

### BOOT-3B Live State

live-read 当前执行状态，至少覆盖与任务相关的：

- lifecycle / current status；
- dependencies / native relationships；
- exact head / branch / target ref；
- currentness / superseded state；
- HEAD_MOVED / relationship drift / authority conflict 等阻断条件。

与 Seed、自述、旧报告或本地 checkout 冲突时，以 current GitHub durable/live state 为准并 fail closed。

### BOOT-3C Bootstrap Conclusion

只有 `BOOT-1A -> BOOT-3B` 全部通过，才可形成最终 Bootstrap 结论并进入 execution。

推荐最小 durable 表示：

```text
BOOT-1A PASS
BOOT-1B PASS
BOOT-1C PASS
BOOT-2A PASS
BOOT-2B PASS
BOOT-2C PASS
BOOT-3A PASS
BOOT-3B PASS
BOOT-3C PASS

EXECUTION_ALLOWED
```

任一项失败时，例如：

```text
BOOT-1A ACCESS_BLOCKED
BOOT-3C BLOCKED

EXECUTION_NOT_ALLOWED
```

不得靠猜、补一句自评或绕过 gate 继续施工。

---

## 与旧七项检查的对应

旧检查没有消失，只被收敛到稳定顺序：

- Identity / Authority / Access -> `BOOT-1A` 路由选择 + `BOOT-3A` capability/authority 核验
- Entry Point -> `BOOT-1A/1B/1C`
- Active Mission / Boundary -> `BOOT-2C`
- State -> `BOOT-3B`
- Global L0 loaded -> 新增为明确的 `BOOT-2A` 执行前置证明

## 可回写要求

**Bootstrap Check Report 必须可回写 durable source**（当前 authority issue / dispatch comment）。
仅存在于聊天中的“我已确认”不算数；未回写 durable source 时，按未验证处理。

Bootstrap report 的人类可读叙述遵守 `AGENTS.md` L0 language invariant：默认简体中文；code / path / SHA / machine identifier / protocol constant 保留原文。
