# Durable Trace Principle

**Classification: L2 Targeted Reference.**

## 目的

任何**具有事实价值的 Agent 行为**必须留下 durable artifact，以便未来恢复、核验与交接。
聊天输出不是事实源；只有落盘到 durable source（Git / GitHub / durable docs / 当前 authority
issue）才算留下 trace。

## 必须留下 trace 的行为

- **决策**（architecture / authority / scope 相关决策）
- **修改**（文件、配置、代码的改动）
- **验证**（tests / build / diff / exact-head 等验证结果）
- **状态变化**（task state transitions、release decisions）
- **风险判断**（blocking conditions、已知风险、未覆盖区域）

## 不 trace 的内容

- 临时推理过程（chain-of-thought）
- 已丢弃的探索路径
- 非权威草稿

## Pointer 规则

完成任何上述行为后，**返回精确可恢复 pointer**（PR / commit / exact head / durable report
pointer）。durable trace 必须产生可恢复引用；只存在于聊天的结论不是 pointer，不算数。
