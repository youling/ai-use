# Agent Runtime Container 1.0.0

Public generic owner: [Work #123](https://github.com/youling/ai-use/issues/123).
Status: candidate awaiting exact-head Architect review. No package has been
published by this migration. [Ownership ADR](../90_HISTORY/ADR-0016_PUBLIC_AGENT_RUNTIME.md).

One Foreman runtime per independent image. [OpenCode](opencode/README.md) is the
first amd64 reference; DSH and Claude Code remain future siblings, not dependencies.
The container consumes [context/exchange/credentials](contract/README.md) and reads
GitHub durable Work directly. Fleet, a broker or a scheduler is not required.

- [Host Windows reference helpers](host/windows/README.md)
- [Conformance](conformance/README.md)
- [Release/update/rollback](release/README.md)
- [Migration provenance](migration-ledger.json)

Private deployment owners retain resolved physical paths, identity bindings,
custody and real consumer receipts. Public tests use inert fixtures only. Existing
HOST_AGENT semantics remain at [the common Host protocol](../30_PROTOCOLS/HUMAN_HOST_ENVIRONMENT.md)
and [template](../50_TEMPLATES/HOST_AGENT_CONTRACT.md); this tree consumes them.

Repository-only validation: `python -m pytest agent-runtime/conformance -q`.
Image conformance runs on standard GitHub-hosted Ubuntu runners; no model inference
or private credentials are needed. Build success does not grant merge or release.
