# Release and update policy 1.0.0

`upstream observation -> proposal -> candidate -> conformance -> optional private
consumer canary -> acceptance -> separately authorized publication/promotion`.
Failure/unknown input retains the existing accepted digest. `stable`/`previous`
are convenience tags; Host truth is immutable manifest digest plus reviewed source.
Do not equate image config ID with registry manifest digest.

Candidate version is `2.0.22-runtime.1-candidate`; OCI source and exact revision
must match. Proposed package: `ghcr.io/<repository-owner>/opencode-foreman`.
Actual namespace availability, repository linkage, permissions and visibility
are NOT evidenced until first separately authorized release. First GHCR package
defaults private; its owner must set public visibility and prove anonymous pull
of the recorded digest before claiming PUBLIC_OCI_PACKAGE PASS.

The manual publication workflow requires all of:

1. `RUNTIME_RELEASE_ENABLED=true` repository variable (default absent/disabled).
2. current main contains `agent-runtime/release/authorization.json`, with schema
   1.0.0, action PUBLISH_CANDIDATE, exact approved source revision, unique candidate
   tag and authority_pointer linking current reviewed authorization. No authorization
   file is supplied by this implementation.
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
