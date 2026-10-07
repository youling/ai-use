# Candidate operation

1. Resolve current accepted Work/image/context/SecretReference owner. Verify exact
   registry manifest digest; local config ID is a separate identity.
2. Host stages only relevant context and bounded inputs, plus protected runtime
   credentials. Project model auth only under current provider/custody authority.
3. Launch non-root foreground server with owned lease, resource limits and loopback
   authentication. Active checkout lives in Linux-native storage. Do not start a
   model merely to prove metadata readiness; reserve any inference separately.
4. Recover live GitHub Work/ref before writes. Per-operation credentials must remain
   current after atomic Host refresh. Expired/unready projections stop safely.
5. Select sanitized bounded evidence, confirm durable readback, stop only owned
   container, revoke/remove current owned secrets. Preserve Host key/vendor data.

Model provider key, GitHub credential and OPENCODE_PASSWORD are independent. Device
OAuth/config-state schemas must be validated for the exact upstream version before
use; do not assume legacy auth.json compatibility. No paid model fallback.

On update failure keep last accepted immutable digest. On unknown write outcome
inspect GitHub before retry. Image build success, HTTP readiness or token capability
does not grant Work, merge, package publication or stable-promotion authority.
