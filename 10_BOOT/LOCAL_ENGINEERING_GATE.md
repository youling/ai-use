# Local Engineering Human Gate 1.0.0

**Classification: L2 Targeted Reference.**

**Contract Version: 1.0.0**

**Status: active**

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

## Cross-platform contract / platform-native adapters

The **Gate contract is shared; adapter code is not**.

```text
Local Engineering Gate contract
= result vocabulary / required-vs-optional semantics / sanitization / authority boundary

Windows adapter
!= Linux adapter
!= Android/controller-device adapter
```

Adapters MUST preserve the common machine envelope and fail-closed semantics, but MUST use the platform-native toolchain. A platform MUST NOT be forced to install another platform's shell/runtime merely to satisfy the generic Gate.

Common abstract capability classes include local shell/runtime, source-control client, repository authentication/currentness, sub-agent runtime, project remote capability and device-control capability. The current Work Order decides which are required.

### Windows reference adapter

Current reference: `tools/local_engineering_gate.ps1`.

```text
adapter_id = windows-pwsh
adapter_version = 0.1.1
platform = windows
```

The script is deterministic and non-inference-based. It can check:

- PowerShell 7;
- Git;
- GitHub CLI version/auth/repository read+push capability;
- optional Codex CLI version/auth;
- optional OpenCode version/configured credentials/model inventory;
- intended repo/origin/base/cleanliness;
- optional project-private remote-capability adapter.

It never auto-upgrades tools, logs in, reads raw secret files, or spends an LLM inference call merely to prove readiness.

### Future Linux adapter

Reuse this contract with Linux-native implementation such as Bash/Python plus native Git/runtime/systemd/network probes required by the Work Order. Linux MUST NOT require PowerShell merely because the first reference adapter is Windows.

### Future Android/controller-device adapter

Android uses a controller/device capability model rather than a desktop-workstation clone. A future adapter should validate controller toolchain plus ADB/device authorization/transport and required automation capability, preserving `UNAUTHORIZED != OFFLINE` and controller identity != target identity. It MUST NOT assume on-device PowerShell, GitHub CLI, Codex/OpenCode, SSH, sudo or desktop worktrees.

### Version separation

```text
gate_contract_version
!= adapter_version
```

Contract and adapter versions evolve independently. An adapter may return `NOT_REQUIRED` only for a capability that is genuinely inapplicable under the current Work Order/profile; it may not silently skip a required abstract capability.

Git branch copies do not gain governance authority merely because their file metadata says `active`; current authority still follows the reviewed/merged governance source.

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
opencode auth list --help
opencode auth list [--format json when supported]
opencode models --refresh
```

The Windows adapter feature-detects the optional `--format` flag. If structured output is supported it is preferred; otherwise the documented plain `opencode auth list` form is used. If both usable auth-inventory probes fail, the result is `UNKNOWN` rather than falsely claiming credentials are absent. A successful but explicitly empty inventory is `BLOCKED`.

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

All platform adapters emit the same leading identity fields:

```text
gate_contract_version
adapter_id
adapter_version
platform
execution_profile
```

`-Json` emits sanitized machine-readable evidence for BOOT-3 writeback.

Exit codes:

```text
0 READY / READY_WITH_WARNINGS
2 BLOCKED
3 UNKNOWN
```

`-SelfTest` checks Windows-adapter internal parsing/identity without touching providers/models. Other platform adapters must provide an equivalent deterministic self-test.

## First consumer

`youling/fleet#168` is the first intended consumer.

Wave 1 is repo-only: PowerShell/Git/GitHub/Codex/OpenCode/repo readiness are required; Fleet remote-management state is informational when a private adapter exists.

The later private Linux canary upgrades the project remote probe to required.