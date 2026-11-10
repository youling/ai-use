# Agent Runtime Container 1.0.0

Public generic owner: [Work #123](https://github.com/youling/ai-use/issues/123).
状态：公共源码已由 PR #124 合并，审阅源版本
`f8a4a873933e8b0e8e36d2c82cc7ecd480eeecfa`（merge `45de55617f1921055aef660c13310650eb15625a`）。
首次授权的公共 OCI candidate 已[交付并完成匿名 exact-digest pull 验证](https://github.com/youling/ai-use/issues/123#issuecomment-6044487814)，随后[验收关闭](https://github.com/youling/ai-use/issues/123#issuecomment-6247066989)。这是历史交付证据，本次文档同步没有重新拉取镜像。

```text
ghcr.io/youling/opencode-foreman@sha256:fa92f37752ff6132b161ed4c2563897c94b014ab70d650846dcb09f354f55261
```

该制品仍为 candidate；stable promotion、后续发行、真实 Host 部署和模型就绪各按独立授权/验收处理。首次单次发行授权已消耗。[Ownership ADR](../90_HISTORY/ADR-0016_PUBLIC_AGENT_RUNTIME.md)。

One Foreman runtime per independent image. [OpenCode](opencode/README.md) is the
first amd64 reference; DSH and Claude Code remain future siblings, not dependencies.
The container consumes [context/exchange/credentials](contract/README.md) and reads
GitHub durable Work directly. Fleet, a broker or a scheduler is not required.

- [Host Windows reference helpers](host/windows/README.md)
- [Conformance](conformance/README.md)
- [Release/update/rollback](release/README.md)
- [Migration provenance](migration-ledger.json)
- [Windows first-run Textual setup](setup/README.md)（PR #128 基础源码已合并；后续修复与真实 Host readiness 分别验收，默认先预览）
- [Textual V2 beginner guide and synthetic screens](setup/V2_GUIDE.md)（源码指南与合成画面；实际运行验收回到原 Work）
- [Windows double-click EXE and ROOT_OVERLAP help](setup/EXE_GUIDE.md) (Work #137 unsigned CI candidate)

Private deployment owners retain resolved physical paths, identity bindings,
custody and real consumer receipts. Public tests use inert fixtures only. Existing
HOST_AGENT semantics remain at [the common Host protocol](../30_PROTOCOLS/HUMAN_HOST_ENVIRONMENT.md)
and [template](../50_TEMPLATES/HOST_AGENT_CONTRACT.md); this tree consumes them.

Repository-only validation: `python -m pytest agent-runtime/conformance -q`.
Image conformance runs on standard GitHub-hosted Ubuntu runners; no model inference
or private credentials are needed. Build success does not grant merge or release.
