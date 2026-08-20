# Pointer Response — 指向 durable source 的回应

**分层**: Agent 层（对 Human 的回应）
**分类**: L2 Targeted Reference · 50_TEMPLATES

| 项 | 内容 |
| --- | --- |
| 用途 | 当 Human 在聊天中提供本应存在于 durable source 的任务知识时，Agent 回指 durable source，不在聊天里搬运第二份合同 |
| 谁使用 | 执行 Agent |
| 什么时候使用 | Human 在聊天补充 scope / acceptance / requirements 等应 durable 化的内容；或 fresh Agent 仅凭 seed 无法启动时 |
| 禁止用途 | 不是推诿 / 拒绝执行；不要求 Human 重述已有 durable 内容；不因 chat 有内容就把聊天当任务合同 |

## Pointer 格式要求

**所有 pointer 必须放在独立代码块内**（不嵌入正文句子）。原因：

- 一键复制；
- 方便二次派发；
- 降低人工转录错误。

支持的 pointer 类型与格式：

```text
<repo>#<issue> comment <id>
```

```text
PR:
<repo>#<pull>
```

```text
Commit:
<sha>
```

## 填空模板

```text
pointer: <任务知识应落 durable source>
聊天提供的内容: <...>
应落到: <Work Order / dispatch comment / contract 位置>
durable 落盘后: <继续执行的 next action>
若暂无法落盘: <最小可行临时事实 + 转存期限>（不得演化成第二份合同）
```

## 规范源

- `docs/AGENT_INTERFACE.md` §3.1（先修 durable source，再派发）
- `docs/PROGRESSIVE_CONTEXT_BOOT.md`（Durable existence != Current authority）
