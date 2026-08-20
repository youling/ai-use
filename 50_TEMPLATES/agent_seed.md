# Agent Seed — 寻址种子模板

**分层**: 派发者（Human / Architect）填写 → Agent 接收执行
**分类**: L2 Targeted Reference · 50_TEMPLATES（默认不进入 Agent 启动上下文）

| 项 | 内容 |
| --- | --- |
| 用途 | 给执行 Agent 提供**只负责寻址**的最小启动种子，使其无歧义定位 durable source 并启动 |
| 谁使用 | 派发者（Human / Architect）填写；执行 Agent 按此启动 |
| 什么时候使用 | 每次派发 Agent 执行时（新 Work Order / Warm Resume / 切换职责） |
| 禁止用途 | 不承载任务知识（scope / acceptance / requirements / stop）；不含调度建议；不复制 dispatch 正文、旧 findings、Architect 裁决；不替代 `ARCHITECT_*_DISPATCH` comment |

## 填空模板

```text
按 `youling/<repo>#<issue>` 的 <DISPATCH_TYPE> comment `<id>` 执行。

work: youling/<repo>#<issue>@<step>
startup_mode: Fresh <Role>
```

## 唯一允许的最小扩展

仅当 pointer 无法无歧义启动时，补一行 bootstrap-critical 引用（如 private GitHub 访问路由）：

```text
access: github-private | github-public
```

> 若仅凭上述三行无法从 durable source 取得任务事实，说明 Work Order / dispatch 不完整：先修 durable source，再派发。长 Seed 默认视为 interface drift。

## 规范源

- `docs/AGENT_INTERFACE.md` §3（Default Minimal Agent Seed）
- `docs/AGENT_INTERFACE.md` §1（Durable Dispatch 与 Seed 分工）