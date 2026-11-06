# Agent Runtime Container 1.0.0

Public generic owner: [Work #123](https://github.com/youling/ai-use/issues/123).
Status: public source accepted and merged from PR #124 exact head
`f8a4a873933e8b0e8e36d2c82cc7ecd480eeecfa` (merge `45de55617f1921055aef660c13310650eb15625a`).
First OCI/GHCR package publication remains separately gated and has not occurred. [Ownership ADR](../90_HISTORY/ADR-0016_PUBLIC_AGENT_RUNTIME.md).

One Foreman runtime per independent image. [OpenCode](opencode/README.md) is the
first amd64 reference; DSH and Claude Code remain future siblings, not dependencies.
The container consumes [context/exchange/credentials](contract/README.md) and reads
GitHub durable Work directly. Fleet, a broker or a scheduler is not required.

- [Host Windows reference helpers](host/windows/README.md)
- [Conformance](conformance/README.md)
- [Release/update/rollback](release/README.md)
- [Migration provenance](migration-ledger.json)
- [Windows first-run Textual setup](setup/README.md) (review candidate; dry-run first)
- [Textual V2 beginner guide and synthetic screens](setup/V2_GUIDE.md) (Work #132 review candidate)
- [Windows double-click EXE and ROOT_OVERLAP help](setup/EXE_GUIDE.md) (Work #137 unsigned CI candidate)

Private deployment owners retain resolved physical paths, identity bindings,
custody and real consumer receipts. Public tests use inert fixtures only. Existing
HOST_AGENT semantics remain at [the common Host protocol](../30_PROTOCOLS/HUMAN_HOST_ENVIRONMENT.md)
and [template](../50_TEMPLATES/HOST_AGENT_CONTRACT.md); this tree consumes them.

Repository-only validation: `python -m pytest agent-runtime/conformance -q`.
Image conformance runs on standard GitHub-hosted Ubuntu runners; no model inference
or private credentials are needed. Build success does not grant merge or release.
