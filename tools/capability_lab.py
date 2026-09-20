"""Deterministic, offline Capability Lab validation and index generation (stdlib).

Implements only the JSON Schema keywords used by claim.schema.json. Unsupported
keywords fail closed. Structural PASS is neither semantic review nor live proof.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
LAB = "docs/research/github-capability-lab"
SCHEMA = LAB + "/schema/claim.schema.json"
PUBLIC_REPOSITORIES = {"youling/ai-use"}
REVIEWED = {"REVIEWED_EVIDENCE", "REUSABLE_DONOR"}
KEYWORDS = {"$schema", "$id", "$defs", "$ref", "title", "description", "type",
            "properties", "required", "additionalProperties", "items", "minItems",
            "uniqueItems", "minLength", "pattern", "enum", "const", "format", "anyOf"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def serialized(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def semantic_digest(claim):
    """Review binds all claim content except promotion bookkeeping itself."""
    return sha256(serialized({k: v for k, v in claim.items()
                              if k not in {"promotion_status", "review"}}).encode())


def check_schema_contract(schema):
    require(isinstance(schema, dict) and not set(schema) - KEYWORDS, "unsupported schema keyword")
    for group in ("properties", "$defs"):
        for child in schema.get(group, {}).values():
            check_schema_contract(child)
    if "items" in schema:
        check_schema_contract(schema["items"])
    for child in schema.get("anyOf", []):
        check_schema_contract(child)


def validate_schema(value, schema, document, where="claim"):
    require(not set(schema) - KEYWORDS, where + ": unsupported schema keyword")
    if "$ref" in schema:
        ref = schema["$ref"]
        require(ref.startswith("#/$defs/") and ref.count("/") == 2, "unsupported schema ref")
        validate_schema(value, document["$defs"][ref.split("/")[-1]], document, where)
    if "anyOf" in schema:
        for branch in schema["anyOf"]:
            try:
                validate_schema(value, branch, document, where)
                break
            except ValueError:
                pass
        else:
            raise ValueError(where + ": no matching schema alternative")
    if "type" in schema:
        types = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}
        require(schema["type"] in types, "unsupported schema type")
        require(type(value) is types[schema["type"]], where + ": wrong type")
    if "enum" in schema:
        require(value in schema["enum"], where + ": invalid enum")
    if "const" in schema:
        require(value == schema["const"], where + ": invalid constant")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        require(set(schema.get("required", [])) <= set(value), where + ": missing required field")
        if schema.get("additionalProperties") is False:
            require(not set(value) - set(properties), where + ": unknown field")
        for key in value.keys() & properties.keys():
            validate_schema(value[key], properties[key], document, where + "." + key)
    if isinstance(value, list):
        require(len(value) >= schema.get("minItems", 0), where + ": empty required list")
        if schema.get("uniqueItems"):
            require(len({serialized(v) for v in value}) == len(value), where + ": duplicate item")
        for i, item in enumerate(value):
            if "items" in schema:
                validate_schema(item, schema["items"], document, f"{where}[{i}]")
    if isinstance(value, str):
        require(len(value.strip()) >= schema.get("minLength", 0), where + ": empty required text")
        if "pattern" in schema:
            require(re.search(schema["pattern"], value) is not None, where + ": invalid pattern")
        if schema.get("format") == "date-time":
            try:
                instant = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
                require(instant.tzinfo is not None, where + ": date-time needs timezone")
            except ValueError as exc:
                raise ValueError(where + ": invalid date-time") from exc
        elif "format" in schema:
            require(schema["format"] == "uri", "unsupported schema format")
            parts = urlsplit(value)
            require(parts.scheme == "https" and bool(parts.netloc), where + ": invalid HTTPS URI")


def local_file(root, pointer, prefix=None):
    p = PurePosixPath(pointer)
    require(pointer and "\\" not in pointer and ":" not in pointer and
            not p.is_absolute() and ".." not in p.parts, "path escapes repository")
    require(prefix is None or pointer.startswith(prefix + "/"), "pointer outside required lane")
    resolved = (root / pointer).resolve()
    require(resolved.is_relative_to(root.resolve()), "symlink escapes repository")
    require(resolved.is_file(), "missing local pointer: " + pointer)
    return resolved


def public_guard(text, where):
    """Bounded tripwire, not a secret scanner or proof of repository visibility."""
    patterns = [r"gh[pousr]_[A-Za-z0-9]{12,}", r"github_pat_[A-Za-z0-9_]{12,}",
                r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----",
                r"(?i)bearer\s+[a-z0-9._-]{12,}",
                r'(?i)["\']?(?:api_key|access_token|password|client_secret)["\']?\s*[:=]\s*["\']?[^\s"\'<>]{6,}',
                r"(?i)https?://(?:localhost|127\.\d+\.\d+\.\d+|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)",
                r'(?i)"visibility"\s*:\s*"(?:private|internal)"',
                r"(?i)\b(?:NORMATIVE(?:_AUTHORITY)?|PRODUCTION(?:_READY|_AUTHORITY)?)\s*[=:]\s*(?:YES|TRUE)\b",
                r"(?i)(?:[A-Z]:\\Users\\|/home/[^/]+/|/Users/[^/]+/)" ]
    require(not any(re.search(pattern, text) for pattern in patterns), where + ": public-safe guard")
    for url in re.findall(r"https?://[^\s\"<>]+", text):
        parts = urlsplit(url.rstrip(".,);"))
        require(not parts.username and not parts.password, where + ": credential-bearing URL")
        require(not re.search(r"(?i)(token|secret|password|signature|api_key)=", unquote(parts.query)),
                where + ": credential-bearing URL query")
        host = (parts.hostname or "").lower()
        require(not host.endswith((".internal", ".local", ".lan")), where + ": private endpoint")
        if host in {"github.com", "api.github.com", "raw.githubusercontent.com"}:
            nodes = parts.path.strip("/").split("/")
            if host == "api.github.com" and nodes[0] == "repos":
                nodes = nodes[1:]
            require(len(nodes) >= 2 and "/".join(nodes[:2]) in PUBLIC_REPOSITORIES,
                    where + ": repository coordinate not public-allowlisted")
    for coordinate in re.findall(r'"repository"\s*:\s*"([^"{}]+)"', text):
        require(coordinate in PUBLIC_REPOSITORIES, where + ": repository coordinate not public-allowlisted")


def check_digest(root, item, prefix):
    path = local_file(root, item["path"], prefix)
    data = (git(root, "show", item["git_revision"] + ":" + item["path"])
            if item.get("git_revision") else path.read_bytes())
    require(sha256(data) == item["sha256"], "digest mismatch: " + item["path"])
    return path


def validate_claims(root, claims, schema):
    check_schema_contract(schema)
    ids = set()
    for filename, claim in claims:
        validate_schema(claim, schema, schema)
        cid = claim["capability_id"]
        require(cid not in ids, "duplicate capability_id: " + cid)
        ids.add(cid)
        require(filename == cid + ".json", "capability_id must match stable filename")
        require(claim["environment"]["repository"] in PUBLIC_REPOSITORIES,
                "repository coordinate not public-allowlisted")
        public_guard(serialized(claim), filename)
        source = claim["source_revision"]
        require(source["repository"] == claim["environment"]["repository"], "source repository mismatch")
        require((source["kind"] == "GIT") == (source["commit"] is not None), "source revision kind mismatch")
        if source["commit"]:
            require(git(root, "cat-file", "-t", source["commit"]).strip() == b"commit", "source commit missing")
        local_file(root, source["receipt_path"])
        check_digest(root, claim["fixture_revision"], LAB + "/fixtures/" + cid)
        observation_times = []
        executed_fixture_digests = []
        for receipt in claim["receipts"]:
            path = check_digest(root, receipt, LAB + "/receipts/" + cid)
            record = read_json(path)
            validate_schema(record, schema["$defs"]["receipt"], schema, "receipt")
            require(record["capability_id"] == cid, "receipt capability mismatch")
            observation_times.append(record["observed_at"])
            for artifact in record["artifacts"]:
                check_digest(root, artifact, None)
                if artifact["path"].endswith(".json"):
                    raw = read_json(root / artifact["path"])
                    if isinstance(raw, dict) and "fixture_sha256" in raw:
                        executed_fixture_digests.append(raw["fixture_sha256"])
        require(claim["verified_at"] in observation_times, "verified_at has no matching observation receipt")
        if claim["fixture_revision"]["execution"] == "EXECUTED":
            require(claim["fixture_revision"]["sha256"] in executed_fixture_digests,
                    "executed fixture has no matching observation digest")
        if claim["promotion_status"] in REVIEWED:
            require(bool(claim["review"]), "reviewed promotion requires semantic review receipt")
            for review in claim["review"]:
                review_path = local_file(root, review["path"], LAB + "/receipts/" + cid)
                require(review["content_sha256"] == semantic_digest(claim), "semantic review digest drift")
                report = read_json(review_path)
                validate_schema(report, schema["$defs"]["review_receipt"], schema, "review receipt")
                require(report["content_sha256"] == semantic_digest(claim), "review receipt content mismatch")
                reviewed = json.loads(git(root, "show", report["reviewed_head"] + ":" + LAB + "/claims/" + filename))
                require(semantic_digest(reviewed) == semantic_digest(claim), "reviewed head content drift")
        if claim["promotion_status"] == "INVALIDATED":
            require(claim["status"] == "INVALID", "invalidated promotion requires INVALID status")
        if claim["status"] == "INVALID":
            require(claim["promotion_status"] == "INVALIDATED", "INVALID requires invalidated promotion")
        require(claim["cleanup_recovery"]["mode"] != "MUTATING" or
                bool(claim["cleanup_recovery"]["possible_resources"]), "mutating fixture needs resource plan")
        if "OWNER_LOCAL_PRODUCTION_EVIDENCE" in claim["evidence_classes"]:
            require(any(read_json(root / receipt["path"])["origin"] == "SANITIZED_OWNER_PROVIDED"
                        for receipt in claim["receipts"]), "owner evidence needs sanitized owner receipt")
    for path in sorted((root / LAB).rglob("*")):
        if path.is_file():
            public_guard(path.read_text(encoding="utf-8"), str(path.relative_to(root)))


def render_index(claims):
    fields = ("capability_id", "question", "status", "promotion_status", "evidence_classes",
              "verified_at", "revalidate_before")
    entries = []
    for _, claim in sorted(claims, key=lambda pair: pair[1]["capability_id"]):
        entry = {field: claim[field] for field in fields}
        entry["claim_path"] = "claims/" + claim["capability_id"] + ".json"
        entry["use"] = "REQUIRES_CLAIM_AND_TARGET_REVALIDATION"
        if claim["status"] != "CURRENT" or claim["promotion_status"] not in REVIEWED or "UNKNOWN" in claim["evidence_classes"]:
            entry["use"] = "NOT_CURRENT_EVIDENCE"
        entries.append(entry)
    return serialized({"schema_version": "1.0.0", "kind": "DERIVED_DISCOVERY_ONLY",
                       "entries": entries})


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.PIPE)


def check_baseline(root, base, r4_acceptance=False):
    """Compare exact supplied base; never treat a missing/zero ref as permission."""
    revision = git(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}").decode().strip()
    prior = git(root, "ls-tree", "-r", "--name-only", revision, "--", LAB + "/claims").decode().splitlines()
    current_ids = {read_json(path)["capability_id"] for path in (root / LAB / "claims").glob("*.json")}
    for path in prior:
        previous = json.loads(git(root, "show", revision + ":" + path))
        require(previous["capability_id"] in current_ids, "stable capability_id removed; retain superseded record")
    if r4_acceptance:
        # A scoped R4 proof, not a permanent ban on future authorized L0 changes.
        current = git(root, "hash-object", "--path=AGENTS.md", "AGENTS.md").decode().strip()
        old = git(root, "rev-parse", revision + ":AGENTS.md").decode().strip()
        require(current == old, "AGENTS.md changed")
        changed = git(root, "diff", "--name-only", revision, "--", "docs/research/astra-audit-69").decode().strip()
        require(not changed, "historical audit donor changed")


def run(root=ROOT, write=False, base="HEAD", r4_acceptance=False):
    schema = read_json(root / SCHEMA)
    claims = [(path.name, read_json(path)) for path in sorted((root / LAB / "claims").glob("*.json"))]
    require(bool(claims), "no claims")
    validate_claims(root, claims, schema)
    check_baseline(root, base, r4_acceptance)
    expected = render_index(claims)
    index = root / LAB / "index.json"
    if write:
        index.write_text(expected, encoding="utf-8", newline="\n")
    else:
        require(index.is_file() and index.read_text(encoding="utf-8") == expected, "index drift; run --write")
    return len(claims)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--base-ref", default=os.environ.get("CAPABILITY_LAB_BASE_REF") or "HEAD")
    parser.add_argument("--r4-acceptance", action="store_true", help="also prove this R4 tranche leaves L0 and historical donors unchanged")
    args = parser.parse_args()
    try:
        count = run(write=args.write, base=args.base_ref, r4_acceptance=args.r4_acceptance)
        print(f"Capability Lab PASS: {count} claims; offline structure/index only; semantic review separate")
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        raise SystemExit("Capability Lab FAIL: " + str(exc))
