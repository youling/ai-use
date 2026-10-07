# Context, exchange and direct recovery contract 1.0.0

Consume [HOST_AGENT V1](../../50_TEMPLATES/HOST_AGENT_CONTRACT.md) from its resolved
owner. It is a discovery projection referencing canonical Work/config/SecretReference
owners, not another full-machine SSOT. The runtime-specific block enables the chosen
agent and binds an immutable image. Reject missing/disabled/stale/conflicting inputs.

| Container surface (example) | Access and owner |
| --- | --- |
| <code>/host-context/HOST_AGENT.md</code> | Bounded read-only nonsecret context file |
| `/exchange/in` | Read-only Work/ref/write-set/config inputs with exact binding |
| `/exchange/out` | Bounded evidence/patch/receipts; no raw credentials |
| `/run/secrets/github` | Read-only directory projection of short-lived credential |
| Model auth | Provider-specific scoped runtime projection; separate custody |
| `/workspace` | Linux-native active source; disposable and Git-recoverable |

Resolve physical roots and ACLs on Host; never bake them into the image. No Host
home, root App key, hot Windows repo, control socket or ambient privileged mount.
Only the discovery file is staged, not its parent. Inputs/outputs/secrets must be
separate, declared and without symlink/reparse/mount injection. Host owns resource
limits, lifecycle and labels/lease used for stop. Stop only a verified owned attempt.

The optional reference credential document contains opaque token, returned expiry,
repository ID/name, Work, permissions and generation together. Host atomically
replaces it; directory mounting makes replacement observable. Reopen and validate
every Git/API operation. Reject expiry, partial JSON, wrong Work/repo/permissions
or redirected API. Token goes only through trusted HTTPS/process memory or Git's
private protocol pipe, never argv/env/URL/config/store/log/evidence/image.
Root signing key stays with its existing Host owner. Model provider auth is separate
from machine GitHub identity and server password. No paid fallback or automatic login.

Machine scope never grants governance authority. Freeze current Work, exact source
head and allowed write-set before mutation. Unknown outcomes require remote readback
before retry. GitHub Issue/checkpoint/ref is durable truth; exchange/session DB is
not currentness. Fresh recovery must fetch live Work and exact SHA, validate binding,
then write allowed commit/checkpoint directly under current authority. A new runtime
must recover without the prior container, home or DB. Cleanup follows durable evidence
readback and deletes only known owned artifacts. Expired credentials stop as readiness
failure; they never justify transferring the root key.

Reference direct client targets github.com; GitHub Enterprise requires a separately
reviewed endpoint adapter. Optional gh is not required; Git and HTTPS suffice.
