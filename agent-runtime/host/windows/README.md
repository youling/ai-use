# Windows/WSLC reference Host adapter 1.0.0

Optional platform implementation of the [portable contract](../../contract/README.md).
Requires Host Python >=3.10, PyYAML; optional App provider requires cryptography.
The image requires neither library. Platform-native WSLC manages containers; no
Fleet/GhostFleet API or broker is invoked.

`launch.py`: supply `--host-agent`, `--wslc`, new `--attempt`, `--name`,
`--github-projection`, `--input`, `--output`. It validates V1/enabled/recovery,
immutable image, declared nonoverlapping roots and no reparse paths. It stages only
HOST_AGENT and records lease/image/attempt label. Normal serve requires a protected
`--server-env` containing OPENCODE_PASSWORD and optional authorized OPENCODE_API_KEY,
plus github_credential.py in input; loopback publication defaults to port4096.
`--stop` requires the same arguments and verifies lease/image/label. `--canary`
uses frozen work.json/github_recovery.py/github_credential.py inputs without inference.

`project_github.py`: use an existing owner-approved NONSECRET private binding
(app_id, app_slug, installation_id, repo, repo_id, work, private_key_ref).
Never place this binding's real values or the key in the public repository. First
`--mode probe`; `--mode project --directory <protected-dir> --generation <id>`
verifies App/install and actual one-repository contents/issues token inventory.
The Host consumes its existing catalog key in place; no key enters the container.
Protected directory ACL/ownership must be established by the Host before use.
`--mode revoke` revokes the current projected token; then remove owned projection.
Superseded tokens require separate revocation or honest returned-expiry handling.

The adapter supports native local image config IDs; registry consumers must resolve
the accepted manifest digest and verify the local pulled config before supplying
this reference launcher. A local config ID is not an OCI manifest digest. No new
identity, account, key or permission widening is authorized by these scripts.
