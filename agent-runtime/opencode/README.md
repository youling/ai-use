# OpenCode reference candidate 1.0.0

OpenCode exact upstream version `2.0.22`, amd64. Recipe pins upstream OCI source
`sha256:11f2b6c96d380867387fbee390c06cb47efffd9fdc37009b4cd40795b45dad19`
and Debian13-slim source
`sha256:a99cfc517144bc59b1978475ec53b46ecabec7e43635402ee5b77cc54cd1b20a`.
Signed Debian snapshot `20261007T140000Z` pins package indexes; retain signature
checking. Upstream musl executable/loader/C++ libraries stay one source unit;
workflow tools remain Debian glibc-native. No npm substitution or provider secrets.

Foreground `opencode serve`, uid1000, Linux-native `/workspace`. Git, rg, jq, curl
and Python are included; gh and PyYAML are not image dependencies. Accepted prior
native hierarchy evidence is historical donor evidence, not a claim of new public
hierarchy testing. Public migration changes labels/notice location, not the runtime
binary. [runbook](runbook.md) and [contract](../contract/README.md).

Build: `docker build --build-arg SOURCE_REVISION=<exact-head> -t runtime-candidate agent-runtime/opencode`.
Run deterministic checks: `python agent-runtime/conformance/image_check.py runtime-candidate`.
No inference occurs. Conformance saves manifest/version/tool/source metadata.
`package-manifest.observed.tsv` is historical construction observation; current
build generates `/usr/share/agent-runtime/package-manifest.tsv` and CI exports it.

Exact upstream [MIT license](https://github.com/anomalyco/opencode/blob/v2.0.22/LICENSE)
is preserved as LICENSE.opencode in source and image. ai-use authored additions
follow the repository Apache-2.0 license; dependencies retain their own notices under
`/usr/share/doc`. OCI license label describes authored recipe/upstream, not a claim
that every OS dependency shares these licenses. Preserve SBOM/package provenance.
Source/revision/license labels are installed; do not publish with `unreleased`.
