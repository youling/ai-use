# Local Engineering Human Gate 0.1.0

**Classification: L2 Targeted Reference.**

**Status: CANDIDATE — Global Architect review required before normative merge.**

Source: `youling/ai-use#76`.

## Purpose

Local execution should not consume substantial model/runtime resources until the Human-selected workstation is proven compatible with the current Work Order.

This is a capability/readiness gate, not an authority gate.

```text
Capability != Authority
Human Gate != credential disclosure
environment ready != task authorized
```

## Applicability

Run when the current task is scheduled as `本地` / `本地+设备`, or the Work Order explicitly requires a local toolchain/private-network capability.

Do not create BOOT-4. The gate is a targeted BOOT-3 check:

```text
BOOT-3A Authority + Access
 -> Local Engineering Human Gate
 -> BOOT-3B Live State
 -> BOOT-3C Durable Conclusion
```

## Reference implementation

Windows reference: `tools/local_engineering_gate.ps1`.

The script is deterministic and non-inference-based. It can check:

- PowerShell 7;
- Git;
- GitHub CLI version/auth/repository read+push capability;
- optional Codex CLI version/auth;
- optional OpenCode version/configured credentials/model inventory;
- intended repo/origin/base/cleanliness;
- optional project-private remote-capability adapter.

It never auto-upgrades tools, logs in, reads raw secret files, or spends an LLM inference call merely to prove readiness.

## Result states

Per check: `PASS | UPDATE_REQUIRED | BLOCKED | UNKNOWN | NOT_REQUIRED`.

Overall: `READY | READY_WITH_WARNINGS | BLOCKED | UNKNOWN`.

- required `BLOCKED` => `BLOCKED`;
- required `UNKNOWN` => `UNKNOWN`;
- `UPDATE_REQUIRED` is warning unless current Work Order uses `-RequireLatest`;
- optional `BLOCKED/UNKNOWN` is warning-only;
- no state grants authority.

Effectful work must not start while a required gate is `BLOCKED` or `UNKNOWN`.

## Version currentness

Latest is live evidence, never a hard-coded remembered number.

The Windows reference uses current stable GitHub Releases when authenticated `gh` access exists:

- `PowerShell/PowerShell`;
- `cli/cli`;
- `openai/codex`;
- `anomalyco/opencode`.

If stable currentness cannot be resolved, result is `UNKNOWN`. No automatic upgrade occurs.

## Credential safety

The gate may prove only sanitized capability classes:

- GitHub CLI session active;
- intended repo readable and push-capable;
- Codex CLI reports authenticated session when required;
- OpenCode reports configured provider credentials when required.

Never emit access tokens, cookies, API keys, auth JSON content, private keys or provider secrets.

Missing credentials stop at the exact capability. Human repairs through the native provider/app flow; Human never pastes a secret into chat/GitHub.

## OpenCode readiness

When required, Work Order may supply regex patterns for configured provider/account classes and required model inventory.

Reference non-inference probes:

```text
opencode auth list --format json
opencode models --refresh
```

Deployment-specific provider/tier/model names stay in the Work Order or deployment scheduler. ai-use does not hard-code them.

## Repository safety

The script can validate repo/origin/base/cleanliness but never performs `reset`, `clean`, `stash` or force checkout.

A dirty or drifted workspace is surfaced rather than destroyed.

## Project remote probe hook

Public ai-use does not know private project endpoints.

The gate accepts an explicit project-owned adapter path: `-ProjectProbeScript <path>`.

Adapter JSON:

```json
{"state":"PASS | BLOCKED | UNKNOWN","detail":"sanitized summary","authority_effect":"NONE"}
```

If remote/node/device capability is required, missing/failed adapter blocks. For repo-only work, the same probe may be informational.

## Output and exit codes

`-Json` emits sanitized machine-readable evidence for BOOT-3 writeback.

Exit codes:

```text
0 READY / READY_WITH_WARNINGS
2 BLOCKED
3 UNKNOWN
```

`-SelfTest` checks internal version parsing without touching providers/models.

## First consumer

`youling/fleet#168` is the first intended consumer.

Wave 1 is repo-only: PowerShell/Git/GitHub/Codex/OpenCode/repo readiness are required; Fleet remote-management state is informational when a private adapter exists.

The later private Linux canary upgrades the project remote probe to required.