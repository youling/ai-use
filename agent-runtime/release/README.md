# Release and update policy 1.0.0

`upstream observation -> proposal -> candidate -> conformance -> optional private
consumer canary -> acceptance -> separately authorized publication/promotion`.
Failure/unknown input retains the existing accepted digest. `stable`/`previous`
are convenience tags; Host truth is immutable manifest digest plus reviewed source.
Do not equate image config ID with registry manifest digest.

本仓首次授权制品为 `2.0.22-runtime.1-candidate-f8a4a873`，源版本
`f8a4a873933e8b0e8e36d2c82cc7ecd480eeecfa`；[发行回执](https://github.com/youling/ai-use/issues/123#issuecomment-6044487814)记录公共可见性、仓库关联与匿名 exact-manifest pull/hash 验证，[关闭裁决](https://github.com/youling/ai-use/issues/123#issuecomment-6247066989)接受该有界 candidate。

```text
ghcr.io/youling/opencode-foreman@sha256:fa92f37752ff6132b161ed4c2563897c94b014ab70d650846dcb09f354f55261
```

该证据不代表 stable、后续发行或 Host 部署完成，也不是本次文档同步的新实测。发行后 gate 已按当时回执关闭；实际当前设置在下一次获授权操作前重新读取。其它部署可使用 `ghcr.io/<repository-owner>/opencode-foreman`，但必须独立核验其真实 namespace、权限、可见性与匿名拉取，不能借用本仓回执。

The manual publication workflow requires all of:

1. `RUNTIME_RELEASE_ENABLED=true` repository variable (default absent/disabled).
2. current main contains `agent-runtime/release/authorization.json`, with schema
   1.0.0, action PUBLISH_CANDIDATE, exact approved source revision, unique candidate
   tag and authority_pointer linking current reviewed authorization. 当前 [authorization.json](authorization.json)
   仅记录已消耗的首次 candidate 授权，不能重用为再次发行或 stable promotion 的许可。
3. successful exact-revision `Agent runtime conformance` run supplied by ID.
4. a preconfigured protected `runtime-release` environment; repository owner must
   configure required reviewers before enabling the variable. Enabling workflow
   without environment protection is prohibited.

Build source is exact authorized revision and is smoke/scanned again before push.
It uses Actions GITHUB_TOKEN with packages:write only in gated job, not a Human PAT.
No PR, schedule or upstream event publishes. Manual input/credential capability
does not grant authority. No stable/previous tags are auto-written. First release
must record manifest digest, source revision, package visibility/linkage and SBOM.
Stable promotion and retiring donor duplicate source require their own review.

Upstream check workflow compares the latest release against pinned version and
uploads observation metadata. No source rewrite, Issue spam, inference, package
push or automatic promotion. New version work pins all inputs and verifies license,
compatibility, recovery, update/rollback before seeking acceptance.

`lifecycle.py` returns only update/rollback proposals with exact validated digests;
it never mutates provider tags. Breaking HOST_AGENT major/schema or unsupported
architecture fails closed and needs a compatibility decision.
