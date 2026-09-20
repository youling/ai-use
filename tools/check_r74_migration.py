"""Opt-in #74 migration proof, not steady-state governance or a CI default.

The #74 Work Order owns this one-time L0 equality / seven legacy-anchor proof.
Both revisions are caller-selected: no historical commit is a permanent rule.
Run explicitly for an R74 delivery; do not import this proof into generic CI.
"""
import argparse
import json
import sys

sys.dont_write_bytecode = True
import routing

LEGACY_PATHS = (
    "docs/SESSION_LIFECYCLE.md", "docs/DeepSeekPP-github-mcp-usage.md",
    "50_TEMPLATES/CONTEXT_MODE_SEED.md", "50_TEMPLATES/DISPATCH_PAIR.md",
    "50_TEMPLATES/architect_handoff_check.md", "50_TEMPLATES/architect_handoff_transaction.md",
    "50_TEMPLATES/capability_self_check.md",
)


def check(base, head):
    def blob(ref, path):
        return routing.git("show", ref + ":" + path)

    routing.require(blob(base, "AGENTS.md") == blob(head, "AGENTS.md"), "R74 L0 changed")
    for path in LEGACY_PATHS:
        old = routing.anchors(blob(base, path).decode("utf-8"))
        new = routing.anchors(blob(head, path).decode("utf-8"))
        routing.require(old <= new, "R74 legacy anchor removed: " + path)
    return {"proof": "R74_MIGRATION_ONLY", "base": base, "head": head,
            "l0_blob": "UNCHANGED", "legacy_anchor_files": len(LEGACY_PATHS), "result": "PASS"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True, help="Explicit migration acceptance base from current #74 authority")
    parser.add_argument("--head-ref", default="HEAD", help="Exact committed candidate; defaults to HEAD")
    args = parser.parse_args()
    print(json.dumps(check(routing.resolve_base_ref(args.base_ref),
                           routing.resolve_base_ref(args.head_ref))))
