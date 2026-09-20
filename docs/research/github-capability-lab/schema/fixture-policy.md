# Capability Lab fixture policy

**Policy version: 1.0.0** · scope: R4 public evidence fixtures

此 policy 实现 [frozen R4](https://github.com/youling/ai-use/issues/73#issuecomment-5750977205)，不授予执行者新权限。每次运行先确认 current Work、明确的 public repo、已有权限、碰撞安全的 synthetic 名称和最小 fixture；执行前持久记录计划。工具能调用 endpoint 不等于允许调用。

## 允许的最小实验

仅限 synthetic、reversible、repo-contained 的 branches/commits、PR、Issues/comments/labels/可逆关系、标准 GitHub-hosted Actions least permissions、bounded REST/GraphQL reads、理解 retention/cleanup 的 repo artifacts/caches。draft/test tag 或 release 还须明确非生产、collision-safe、无生产消费者混淆且可清理。

App 注册/安装、OAuth/PAT 扩权、组织/账户/plan 变化、Projects 创建/配置、ruleset/protection/bypass、外部 provider/cloud credentials、private repo 访问扩展、public canary 接触 private nodes/resources、production mutation 均要求独立 current Human/admin gate；R4 不运行这些 canary。当前 fixture coordinate allowlist 仅 `youling/ai-use`，不得默认为任何同 owner 仓库已获授权或公开。

## 执行前记录

每份 fixture 必须明确问题、repository/visibility、principal/permission class、source 与 fixture revision、API/tool/runner/config、输入/步骤/边界、预期正反结果、停止条件，以及以下清理合约：

1. 可能创建的资源、synthetic namespace 与碰撞检测。
2. 每类资源的 cleanup action 与 readback；不能清理的持久证据明确保留。
3. replay/idempotency：不是用新 ID 再造一份掩盖旧操作。
4. UNKNOWN mutation result：先 live-read 精确资源与关联，判明是否发生 effect，再决定 retry/skip/stop。
5. retry 之前必须落 durable receipt：请求意图、已知 ID、结果或 UNKNOWN、readback、清理状态；不得保存 token、完整敏感响应或私有 topology。

只读 fixture 也写明 `READ_ONLY`、无远端资源和失败时 incomplete/UNKNOWN 的处理。混合或负向 write probe 按 mutating 管理；意外成功不能因为“本来应失败”忽略。

## 清理与恢复

成功路径用 readback 确认效果，然后移除 owned synthetic 关系、关闭 synthetic Issues，并再次确认关系为空、Issue 已关闭。失败/中断时依据已存 ID 对账；先恢复到明确状态，再决定是否继续。不得盲重放不确定 mutation，不得改他人关系或历史重写。

cleanup failure 保持可见，不得删除用于解释失败的 receipt。Git commit status 等不能真正删除的 effect 必须在计划中明确为持久 append-only 证据；本轮只重用旧 read=200/write=403 收据，不重新运行此 probe。Actions 的 artifacts/caches 在到期后可能不可取回，必须先保留解释结论所需的小型 payload 或 compact digest receipt。

fixture 定义、计划与真实执行收据分开保存：`RECIPE_ONLY` 表明尚未运行，`EXECUTED` 必须有 exact receipt 支持。source snapshot、fixture bytes 或实验语义变动触发 revalidation；新文件/commit 时间不是新的观察时间。

## 对下游的证明义务

复用顺序为：语义匹配 → target environment/permissions/currentness → 仅未解决的 owner-local delta → owner 最终采用/生产决策。Lab 不替下游配置平台，也不标记其他项目生产就绪。owner 提供的证据只有在移除 private/domain-specific facts 后才可进入公开 Lab，且保留来源与脱敏限制。
