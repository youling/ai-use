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

## 边界

Seed 负责寻址，不承载完整知识。

任务目标、范围、验收条件属于工单/持久调度，不复制到 Seed。

Agent 生命周期属于 Agent Interface，不由每个 Seed 重复定义。
