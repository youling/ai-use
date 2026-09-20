# ADR-0007：GitHub Actions Resource-Budget Aware Use

**Artifact Version: 1.0.0**  
状态：Proposed / exact-head Review pending  
裁决来源：[Governance #89](https://github.com/youling/ai-use/issues/89)  
语义 owner：[GitHub Native First](../30_PROTOCOLS/GITHUB_NATIVE_FIRST.md)

## Context

GitHub-native-first 若只比较“平台有没有能力”，会漏掉执行资源成本。同一个 Actions workflow 在 public standard runner、private GitHub-hosted runner、larger runner 或 self-hosted runner 上具有不同的额度/计费与可用性条件。对 private deployment 来说，GitHub-hosted Actions minutes 还是会耗尽的共享资源。

当前 GitHub 官方文档说明：public repository 的 standard GitHub-hosted runner usage 免费；private repository 的 GitHub-hosted runner 使用 plan allowance，超出 allowance 后进入计费/预算约束；self-hosted runner 不消耗 GitHub-hosted runner minutes；larger runner 单独计费。外部 billing 条件仍需 live revalidate。

## Decision

1. Actions admission 先判断 repository visibility、runner class、current budget state 和是否真的需要 GitHub platform semantics。
2. PRIVATE / INTERNAL repo 默认优先 local deterministic validation；generic GitHub behavior 优先复用 public Capability Lab；已有授权 self-hosted runner 可在确需 platform semantics 时作为下一选择；GitHub-hosted Actions 只用于剩余不可替代证据。
3. PUBLIC repo 的 standard GitHub-hosted Actions 仍是优先 native validation/canary surface，但免费不授权浪费；避免重复 workflow、无必要 matrix/heartbeat/artifact 与 unchanged canary rerun。
4. budget exhausted/blocked 不等于 verification PASS。其它证据无法证明同一 property 时，保持 UNKNOWN/BLOCKED。
5. 实际 quota、账单、预算是 deployment-local private current state，不进入 public ai-use。
6. Generic canary 尽量 public-once/downstream-delta-only，降低整个 portfolio 的重复 Actions 消耗。

## Alternatives and tradeoffs

把 Actions 永远禁用于 private repo 会失去真实 event/permission/runner semantics 的必要证据；不采用。继续默认每个 repo 都跑完整 CI 能获得更多机械回执，却把 hosted minutes 当作无限资源并重复验证 generic behavior；不采用。

self-hosted runner 可以避开 hosted-minute 消耗，但它有自身运维、安全与环境一致性成本，因此只在已存在、已授权且适用时优先，不把“自建 runner”变成新的强制基础设施。

## Compatibility

不修改 L0，不降低 exact-head/evidence 要求，不把 public canary 当 private production proof，不改变 owner-local adoption authority。该 ADR 只改变 GitHub Actions 的默认资源选择顺序与 evidence honesty。

官方入口：
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
