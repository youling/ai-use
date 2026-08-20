# Bootstrap Check Protocol

**Classification: L2 Targeted Reference.** 仅在启动/派发/恢复场景触发时读取。

## 启动模型（固化）

启动由三层分工，各司其职，**不要把完整任务知识塞入 Seed**：

| 层 | 职责 |
| --- | --- |
| **Seed** | 只负责**定位 durable source**（寻址），不承载任务知识。规范格式见 `docs/AGENT_INTERFACE.md` §3。 |
| **Durable Dispatch** | 负责**任务上下文**（角色、scope、acceptance 等），见 `docs/AGENT_INTERFACE.md` §1。 |
| **Bootstrap Check** | 负责**启动状态验证**（本文件）：执行前确认身份/入口/权限/访问/任务/边界/状态已就绪。 |

Seed 不复制 Dispatch/Work Order 的任务知识；Dispatch 不替代 Bootstrap Check 的状态验证；
Bootstrap Check 不承载完整任务上下文。

## 固定检查项

执行前按序确认以下 7 项：

1. **Identity** —— 当前身份（node / agent_type / session）已知且无歧义。
2. **Entry Point** —— 已定位 durable source 入口（pointer / ref），且能无歧义启动。
3. **Authority** —— 当前角色在范围内拥有对应权限，不越权。
4. **Access** —— 所需访问路径（github-private / github-public）与 live metadata 一致。
5. **Active Mission** —— 已确认当前精确任务（Work Order）及其当前状态。
6. **Boundary** —— 已确认 owns / forbidden / acceptance 边界。
7. **State** —— 已核对 durable / live state，与 seed 冲突时以 durable source 为准。

## 可回写要求

**Bootstrap Check Report 必须可回写 durable source**（当前 authority issue / dispatch comment）。
仅存在于聊天中的"我已确认"不算数；未回写 durable source 时，按未验证处理。

## 输出

Bootstrap Check 结果与 `ARCHITECT_*_DISPATCH` / Work Order 对齐后，可回写为确认评论；
状态冲突或无法确认某项时报告 `BLOCKED`，不靠猜继续。
