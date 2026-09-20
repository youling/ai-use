"""Small offline routing catalog compiler/checker (Python standard library).

Borrowed #69's bounded Markdown-link/backtick scan and Git-blob comparison method.
No network/provider probe. --write changes projections; a new-branch comparison
may materialize the empty tree object in Git metadata. No historical L0/anchor
baseline is imposed here; opt-in tranche proofs belong to migration tooling.
Checks prove structural consistency, not semantic correctness or secret clearance.
"""
import argparse
import json
import os
import pathlib
import posixpath
import re
import subprocess
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = "ROUTING_CATALOG.yaml"
PROJECTIONS = {"human": "START_HERE.md", "reading": "READING_MAP.md",
               "compatibility": "NAMESPACE.md", "index": "docs/ROUTING_INDEX.md"}


def git(*args, input=None):
    return subprocess.check_output(["git", *args], cwd=ROOT, input=input)


def resolve_base_ref(value):
    """Event/explicit base, local HEAD by default; a zero before means new branch."""
    if value and set(value) == {"0"}:
        return git("hash-object", "-w", "-t", "tree", "--stdin", input=b"").decode().strip()
    return git("rev-parse", "--verify", "--end-of-options",
               (value or "HEAD") + "^{commit}").decode().strip()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local_path(path):
    require(isinstance(path, str) and path and "\\" not in path, "invalid path")
    p = pathlib.PurePosixPath(path)
    require(not p.is_absolute() and ".." not in p.parts and ":" not in path,
            "path escapes repository: " + path)
    require((ROOT / path).is_file(), "missing canonical/projection pointer: " + path)


def validate_catalog(c, previous=None):
    require(set(c) == {"schema_version", "format", "boundary", "navigation",
                       "projections", "entries", "compatibility"}, "unknown catalog fields")
    require(c["schema_version"] == "1.0.0", "unsupported schema version")
    require(c["projections"] == PROJECTIONS, "projection paths are fixed in schema 1")
    n = c["navigation"]
    require(set(n) == {"entry", "chain", "layers", "results", "notes"}, "unknown routing metadata")
    require(n["chain"] == ["00", "10", "20", "30", "40", "50", "90"], "chain changed")
    require(set(n["layers"]) == set(n["chain"]), "layer labels missing")
    require(set(n["results"]) == {"NEXT", "SKIP", "STOP_READY", "STOP_BLOCKED"}, "routing results changed")
    require(all(isinstance(x, str) and x for x in [c["format"], c["boundary"], n["entry"],
                *n["notes"], *n["layers"].values(), *n["results"].values()]), "invalid routing text")
    ids = []
    for e in c["entries"]:
        require(set(e) == {"id", "layer", "reading_level", "roles", "when", "home",
                           "section", "templates", "public"}, "unknown entry fields")
        require(isinstance(e["id"], str) and re.fullmatch(r"[a-z][a-z0-9-]*", e["id"]), "invalid route ID")
        ids.append(e["id"])
        require(e["layer"] in n["chain"], "unknown layer")
        require(e["reading_level"] in {"L0", "L1", "L2", "L3"}, "unknown reading level")
        require(isinstance(e["roles"], list) and e["roles"] and all(isinstance(x, str) and x for x in e["roles"]), "invalid role trigger")
        require(isinstance(e["when"], str) and e["when"], "missing scene trigger")
        require(isinstance(e["section"], str) and isinstance(e["public"], bool), "invalid projection metadata")
        local_path(e["home"])
        require(isinstance(e["templates"], list), "invalid template pointers")
        for p in e["templates"]:
            local_path(p)
            require(p.startswith("50_TEMPLATES/"), "template points outside templates")
    require(len(ids) == len(set(ids)), "duplicate route IDs")
    require([e["id"] for e in c["entries"] if e["reading_level"] == "L0"] == ["kernel"], "L0 routing expanded")
    require(next(e for e in c["entries"] if e["id"] == "kernel")["home"] == "AGENTS.md", "kernel home changed")
    if previous:
        old_ids = {e["id"] for e in previous["entries"]}
        require(old_ids <= set(ids), "stable route ID removed/renamed; requires schema migration")
    for row in c["compatibility"]:
        require(set(row) == {"path", "route", "status", "note"}, "unknown compatibility metadata")
        local_path(row["path"])
        require(row["route"] in ids, "compatibility route missing")
        require(row["status"] in {"forward", "retired-forward"}, "unknown compatibility state")


def link(source, target, label=None):
    return "[" + (label or target) + "](" + posixpath.relpath(target, posixpath.dirname(source) or ".") + ")"


def render(c):
    """All routing prose comes from catalog metadata; renderer supplies layout."""
    output = {}
    titles = {"human": "START HERE", "reading": "Reading Map", "compatibility": "Namespace — Compatibility Projection", "index": "Routing Index — DERIVED"}
    for kind, path in PROJECTIONS.items():
        lines = ["# " + titles[kind], "", "<!-- Generated by tools/routing.py; edit ROUTING_CATALOG.yaml. -->",
                 "", "来源：" + link(path, CATALOG) + " · schema " + c["schema_version"] + "。", "", c["boundary"], ""]
        n = c["navigation"]
        lines += [n["entry"], ""]
        if kind == "human":
            lines += ["ai-use 是可复用的人机协作治理与协议。体系概览见 " + link(path, "README.md") + "。", ""]
        if kind != "index":
            lines += ["`" + " -> ".join(n["chain"]) + "`", ""]
            chosen_notes = n["notes"] if kind == "reading" else [n["notes"][0], n["notes"][3]]
            lines += ["- " + x for x in chosen_notes] + [""]
        if kind in {"reading", "compatibility"}:
            lines += ["| Result | 判定 |", "| --- | --- |"]
            lines += ["| `" + k + "` | " + v + " |" for k, v in n["results"].items()] + [""]
        if kind == "index":
            lines += ["```mermaid", "flowchart TD", '  K["AGENTS.md / L0"] --> C["ROUTING_CATALOG.yaml"]']
            for i, (view, target) in enumerate(PROJECTIONS.items()):
                lines += ['  C --> P' + str(i) + '["' + target + '"]']
            lines += ['  C --> H["targeted canonical homes"]', "```", "",
                      "箭头表示 routing/projection，不表示 authority 或执行顺序。", ""]
        if kind in {"human", "reading", "index"}:
            lines += ["| ID / reading level | 角色与场景 | Canonical home |", "| --- | --- | --- |"]
            for e in c["entries"]:
                if kind == "human" and not e["public"]:
                    continue
                roles = "/".join(e["roles"])
                home = link(path, e["home"]) + (" " + e["section"] if e["section"] else "")
                lines += ["| `" + e["id"] + "` / " + e["reading_level"] + " | " + roles + "；" + e["when"] + " | " + home + " |"]
            lines += [""]
        if kind == "reading":
            lines += ["## Artifact shapes（仅生成对应 artifact 时）", "", "| Route | Shapes |", "| --- | --- |"]
            lines += ["| `" + e["id"] + "` | " + " · ".join(link(path, p) for p in e["templates"]) + " |" for e in c["entries"] if e["templates"]]
            lines += [""]
        if kind == "compatibility":
            lines += ["| Layer | 目录角色 |", "| --- | --- |"]
            lines += ["| `" + k + "` | " + n["layers"][k] + " |" for k in n["chain"]]
            lines += ["", "场景与 canonical home 见 " + link(path, PROJECTIONS["reading"]) + "；无需通读每层。", ""]
        if kind in {"reading", "index"}:
            lines += ["## Compatibility forwards", "", "| 旧路径 | 当前 home |", "| --- | --- |"]
            by_id = {e["id"]: e for e in c["entries"]}
            lines += ["| " + link(path, row["path"]) + " | " + link(path, by_id[row["route"]]["home"]) + "；" + row["note"] + " |" for row in c["compatibility"]]
            lines += [""]
        lines += ["更新 source 后运行 `python tools/routing.py --write`；验证运行 `python tools/routing.py --check`。", ""]
        output[path] = "\n".join(lines)
    return output


def anchors(text):
    result, counts = set(re.findall(r'<a\s+id="([^"]+)"', text)), {}
    for h in re.findall(r"^#{1,6}\s+(.+)$", text, re.M):
        h = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", h)
        slug = re.sub(r"[^\w\-\s]", "", h.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug + ("-" + str(count) if count else ""))
    return result


def check_links(path, text):
    # Bounded scan from audit_69, extended with anchors and repository containment.
    nofence = re.sub(r"(?ms)^(```|~~~).*?^\1[^\n]*", "", text)
    for raw in re.findall(r"\[[^\]\n]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", nofence):
        u = urllib.parse.urlsplit(raw.strip("<>"))
        if u.scheme or u.netloc:
            continue
        dest = posixpath.normpath(posixpath.join(posixpath.dirname(path), urllib.parse.unquote(u.path))) if u.path else path
        local_path(dest)
        if u.fragment:
            require(urllib.parse.unquote(u.fragment) in anchors((ROOT / dest).read_text(encoding="utf-8")),
                    "missing anchor: " + path + " -> " + raw)
    for raw in re.findall(r"`([\w./-]+\.md)`", nofence):
        if any(x in raw for x in ("<", ">", "*", "|", "://")):
            continue
        dest = posixpath.normpath(posixpath.join(posixpath.dirname(path), raw))
        require((ROOT / dest).is_file() or (ROOT / raw).is_file(), "unresolved pointer: " + path + " -> " + raw)


def check_public(path, text):
    """Reject concrete coordinates in copyable fences, plus obvious credential shapes.

    This is a bounded fixture guard, not an assertion that arbitrary prose is safe.
    """
    blocks = re.findall(r"(?ms)^```[^\n]*\n(.*?)^```", text)
    for block in blocks:
        stripped = re.sub(r"<[^>]*>", "PLACEHOLDER", block)
        require(not re.search(r"(?<![\w/])[\w.-]+/[\w.-]+#\d", stripped), "concrete work coordinate in " + path)
        require(not re.search(r"https?://[^\s<>]+", block), "endpoint in copyable fence: " + path)
        require(not re.search(r"(?m)^\s*(?:节点|身份|账号|node|node_id|identity|account|repo|governance_repo|control_plane_repo|私仓工单|公仓工单)\s*[:：]\s*(?!<)[A-Za-z0-9]", block), "non-inert coordinate field in " + path)
    require(not re.search(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", text), "credential-like content in " + path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-whitespace", action="store_true",
                        help="Check the same event/current-base diff with git diff --check")
    parser.add_argument("--base-ref", default=os.environ.get("ROUTING_BASE_REF"),
                        help="Diff/previous-catalog base; env ROUTING_BASE_REF, otherwise local HEAD. Zero before uses an empty tree.")
    a = parser.parse_args()
    base = resolve_base_ref(a.base_ref)
    c = json.loads((ROOT / CATALOG).read_text(encoding="utf-8"))
    old_paths = git("ls-tree", "-r", "--name-only", base).decode().splitlines()
    previous = json.loads(git("show", base + ":" + CATALOG)) if CATALOG in old_paths else None
    validate_catalog(c, previous)
    views = render(c)
    if a.write:
        for path, value in views.items():
            (ROOT / path).write_text(value, encoding="utf-8", newline="\n")
    for path, value in views.items():
        require((ROOT / path).read_text(encoding="utf-8") == value, "projection drift: " + path)
    changed = set(git("diff", "--name-only", base, "--").decode().splitlines())
    changed |= set(git("ls-files", "--others", "--exclude-standard").decode().splitlines())
    checked = sorted(p for p in changed if p.endswith(".md") and (ROOT / p).is_file())
    for path in checked:
        check_links(path, (ROOT / path).read_text(encoding="utf-8"))
    public = sorted({*PROJECTIONS.values(), "human/README.md", "human/DEPOSITOR_PROMPT.md",
                     "40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md",
                     *(p.relative_to(ROOT).as_posix() for p in (ROOT / "50_TEMPLATES").glob("*.md"))})
    for path in public:
        check_public(path, (ROOT / path).read_text(encoding="utf-8"))
    if a.check_whitespace:
        subprocess.run(["git", "diff", "--check", base, "--"], cwd=ROOT, check=True)
    print(json.dumps({"catalog": CATALOG, "route_ids": len(c["entries"]), "projections": len(views),
                      "base_ref": base,
                      "changed_markdown_checked": checked, "copyable_surfaces_checked": len(public),
                      "l0_routing": "KERNEL_ONLY", "compatibility": "CURRENT_POINTERS_VALID",
                      "whitespace": "PASS" if a.check_whitespace else "NOT_REQUESTED", "result": "PASS"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
