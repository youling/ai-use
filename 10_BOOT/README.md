# 10_BOOT

启动路由层。

职责：

- 确认下一步所需上下文；
- 避免全仓扫描；
- 保持渐进式上下文加载。

相关协议：

- Bootstrap Check（`BOOTSTRAP_CHECK_PROTOCOL.md`）
- Workspace Bootstrap（`WORKSPACE_BOOTSTRAP_PROTOCOL.md`）
- 渐进式上下文启动（`../docs/PROGRESSIVE_CONTEXT_BOOT.md`）

恢复场景与 handoff 见 [Recovery & Handoff](../30_PROTOCOLS/RECOVERY_HANDOFF.md)。文档路由见 [Reading Map](../READING_MAP.md)（[catalog](../ROUTING_CATALOG.yaml) 的投影）。
