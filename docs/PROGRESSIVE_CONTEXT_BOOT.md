# 渐进式上下文启动

## 目的

Agent 不通过恢复完整聊天或完整历史恢复角色，而通过最小可信启动集合逐步加载当前工作所需上下文。

## 核心原则

- Trusted Boot Set：仅包含启动角色所必需的宪法、身份、权限边界、入口路由和实时核验规则。
- Role Profile：不同角色按职责加载不同上下文。
- Lazy Import：历史、项目细节、专项知识仅在当前任务需要时加载。
- Invalidate / Reconcile：发现 durable source 变化或冲突时，只重新核验受影响上下文。

## 权威判断

- Durable existence != Current authority
- Artifact validity != Process validity

GitHub 中存在的报告、PR、历史裁决和产物，需要根据当前任务、来源、替代关系和证据强度判断其作用。

## Architect Reconnaissance 的互补边界

Progressive Context Boot 负责恢复和校验**内部 durable context**：当前角色、authority、Work Order、项目规则、repo/live state，以及哪些历史 artifact 仍 current。

它不负责证明快速变化的**外部生态事实**今天仍成立。Fresh / takeover Architect 或 material new-domain / major architecture pivot 在 Bootstrap 得到 `EXECUTION_ALLOWED` 后，还需要按 `docs/ARCHITECT_RECONNAISSANCE.md` targeted 完成：

```text
internal durable context
  -> BOOT-1 / BOOT-2 / BOOT-3
  -> EXECUTION_ALLOWED

external current-state alignment
  -> ARCH-0A External Current-State Scan
  -> ARCH-0B Project / Repo Reconciliation
  -> ARCH-0C Architecture Delta & Reuse Decision
  -> ARCHITECT_READY
```

两层互补但不互相替代：

- 只做 external research，不能绕过 Bootstrap authority/currentness gate；
- 只恢复 repo / Issue / 历史 docs，也不足以证明快速变化生态下的第一轮 material architecture 已 current；
- ordinary Hot Resume、小 bug、确定性维护不因角色为 Architect 自动重复 `ARCH-0`；已有同 scope 且 live-revalidate 仍 current 的 reconnaissance 可引用并补最小 delta。

外部 source 是 architecture evidence，不是 authority；Git/GitHub 仍是项目 durable SSOT。

## 边界

Seed 负责寻址，不承载完整知识。

任务目标、范围、验收条件属于工单/持久调度，不复制到 Seed。

Agent 生命周期属于 Agent Interface，不由每个 Seed 重复定义。
