# Bootstrap Check Protocol

**Classification: L2 Targeted Reference.** 仅在启动 / 派发 / 恢复场景触发时读取。

## 启动模型（固化）

启动采用统一的 **Bootstrap Ordered Applicability Model**：

```text
1 ADDRESS
  A Seed
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

### BOOT-1A Seed

解析最小启动地址：dispatch pointer、`work`、`startup_mode`，以及必要的 `access` / exact ref。

这里只做寻址，不把 Seed 扩展成任务合同。

### BOOT-1B Durable Dispatch

定位当前有效的 `ARCHITECT_*_DISPATCH` / resume dispatch，确认 pointer 可解析，并判断其 current / superseded / historical 状态。

**在 `BOOT-2A` 之前，1B 只能确认地址与 currentness。不得把 Dispatch 正文中的 scope、acceptance、language、behavior 指令作为已适用规则执行。**

### BOOT-1C Work Coordinate

确认 owner/repo、issue、step、role 等 coordinate 无歧义；处理 exact-step、latest-wins、superseded 等当前寻址语义。

**在 `BOOT-2A` 之前，1C 同样只做 coordinate / authority-pointer 解析，不提前适用任务正文。**

本阶段只回答：**“我在哪、谁派我来的、当前任务坐标是什么。”**

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
- `github-private` / `github-public` 等访问路径与 live metadata 一致；
- Capability 不被误当成 Authority。

### BOOT-3B Live State

live-read 当前执行状态，至少覆盖与任务相关的：

- lifecycle / current status；
- dependencies / native relationships；
- exact head / branch / target ref；
- currentness / superseded state；
- HEAD_MOVED / relationship drift / authority conflict 等阻断条件。

与 Seed、自述或旧报告冲突时，以 current durable/live state 为准并 fail closed。

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
BOOT-3B BLOCKED_HEAD_MOVED
BOOT-3C BLOCKED

EXECUTION_NOT_ALLOWED
```

不得靠猜、补一句自评或绕过 gate 继续施工。

---

## 与旧七项检查的对应

旧检查没有消失，只被收敛到稳定顺序：

- Identity / Authority / Access -> `BOOT-3A`
- Entry Point -> `BOOT-1A/1B/1C`
- Active Mission / Boundary -> `BOOT-2C`
- State -> `BOOT-3B`
- Global L0 loaded -> 新增为明确的 `BOOT-2A` 执行前置证明

## 可回写要求

**Bootstrap Check Report 必须可回写 durable source**（当前 authority issue / dispatch comment）。
仅存在于聊天中的“我已确认”不算数；未回写 durable source 时，按未验证处理。

Bootstrap report 的人类可读叙述遵守 `AGENTS.md` L0 language invariant：默认简体中文；code / path / SHA / machine identifier / protocol constant 保留原文。
