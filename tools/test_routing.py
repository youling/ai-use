"""Structural regressions in source fixtures and independent Git history; not fresh-agent tests."""
import copy
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
sys.dont_write_bytecode = True
import routing


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((routing.ROOT / routing.CATALOG).read_text(encoding="utf-8"))

    def test_valid_catalog(self):
        routing.validate_catalog(self.catalog)

    def test_duplicate_id_rejected(self):
        self.catalog["entries"].append(copy.deepcopy(self.catalog["entries"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            routing.validate_catalog(self.catalog)

    def test_missing_home_rejected(self):
        self.catalog["entries"][1]["home"] = "missing-canonical-fixture.md"
        with self.assertRaisesRegex(ValueError, "missing"):
            routing.validate_catalog(self.catalog)

    def test_path_escape_rejected(self):
        self.catalog["entries"][1]["home"] = "../outside.md"
        with self.assertRaisesRegex(ValueError, "escapes"):
            routing.validate_catalog(self.catalog)

    def test_stable_id_removal_rejected(self):
        previous = copy.deepcopy(self.catalog)
        self.catalog["entries"][1]["id"] = "renamed-language"
        with self.assertRaisesRegex(ValueError, "stable route ID"):
            routing.validate_catalog(self.catalog, previous)

    def test_authority_field_rejected(self):
        self.catalog["entries"][1]["authority"] = "synthetic-fixture"
        with self.assertRaisesRegex(ValueError, "unknown entry fields"):
            routing.validate_catalog(self.catalog)

    def test_extra_l0_rejected(self):
        self.catalog["entries"][1]["reading_level"] = "L0"
        with self.assertRaisesRegex(ValueError, "L0"):
            routing.validate_catalog(self.catalog)

    def test_projection_overwrite_target_rejected(self):
        self.catalog["projections"]["human"] = "AGENTS.md"
        with self.assertRaisesRegex(ValueError, "projection paths"):
            routing.validate_catalog(self.catalog)

    def test_projection_reproducibility_and_scene_propagation(self):
        current = routing.render(self.catalog)
        self.assertEqual(current, routing.render(copy.deepcopy(self.catalog)))
        self.catalog["entries"][0]["when"] = "synthetic updated trigger"
        changed = routing.render(self.catalog)
        for view in ("START_HERE.md", "READING_MAP.md", "docs/ROUTING_INDEX.md"):
            self.assertNotEqual(current[view], changed[view])
            self.assertIn("synthetic updated trigger", changed[view])

    def test_concrete_coordinate_rejected(self):
        with self.assertRaisesRegex(ValueError, "concrete work coordinate"):
            routing.check_public("synthetic", "```text\nwork: fixture-owner/fixture-repo#123\n```\n")

    def test_endpoint_and_node_rejected(self):
        for value in ("endpoint: https://example.invalid/service", "节点：synthetic-node"):
            with self.assertRaises(ValueError):
                routing.check_public("synthetic", "```text\n" + value + "\n```\n")

    def test_placeholder_allowed(self):
        routing.check_public("synthetic", "```text\n私仓工单：<owner>/<repo>#<issue>\n节点：<node_id>\n```\n")

    def test_bad_anchor_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing anchor"):
            routing.check_links("README.md", "[fixture](AGENTS.md#nonexistent-synthetic-heading)")

    def test_duplicate_heading_slug(self):
        self.assertEqual(routing.anchors("## A\n## A\n"), {"a", "a-1"})


class CurrentBaseTests(unittest.TestCase):
    """No R74 objects are copied: a new root proves the CLI has no dispatch-base dependency."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-use-routing-test-")
        self.root = pathlib.Path(self.temp.name).resolve()
        self.assertEqual(self.root.parent, pathlib.Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        paths = set(routing.git("ls-files").decode().splitlines()) | {"tools/check_r74_migration.py"}
        for path in paths:
            source = routing.ROOT / path
            if source.is_file():
                target = self.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        self.env = dict(os.environ)
        self.env.pop("ROUTING_BASE_REF", None)
        self.git("init", "--quiet")
        for key, value in [("user.name", "Synthetic Test"), ("user.email", "test@example.invalid"),
                           ("commit.gpgsign", "false"), ("core.autocrlf", "false")]:
            self.git("config", key, value)
        self.commit("synthetic independent root")
        self.base = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.git("rev-list", "--count", "HEAD").strip(), "1")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, env=self.env,
                                       text=True, encoding="utf-8", stderr=subprocess.STDOUT)

    def commit(self, message):
        self.git("add", ".")
        self.git("-c", "core.hooksPath=", "commit", "--quiet", "-m", message)

    def cli(self, *args, environment_base=None, script="routing.py"):
        env = dict(self.env)
        if environment_base is not None:
            env["ROUTING_BASE_REF"] = environment_base
        return subprocess.run([sys.executable, "-X", "utf8", "tools/" + script, *args],
                              cwd=self.root, env=env, capture_output=True, text=True, encoding="utf-8")

    def assert_pass(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_generic_accepts_future_l0_and_legacy_anchor_migration(self):
        # These changes represent separately authorized future governance in a fixture only.
        (self.root / "AGENTS.md").write_text("# Future kernel fixture\n", encoding="utf-8", newline="\n")
        (self.root / "docs/SESSION_LIFECYCLE.md").write_text("# Future compatibility entry\n", encoding="utf-8", newline="\n")
        self.commit("synthetic future governance")
        result = self.assert_pass(self.cli("--check", "--check-whitespace", environment_base=self.base))
        self.assertEqual(result["base_ref"], self.base)
        self.assertIn("AGENTS.md", result["changed_markdown_checked"])
        self.assertEqual(result["l0_routing"], "KERNEL_ONLY")
        self.assertEqual(self.assert_pass(self.cli("--check"))["base_ref"], self.git("rev-parse", "HEAD").strip())
        # The explicit migration proof is stricter, without becoming generic governance.
        proof = self.cli("--base-ref", self.base, script="check_r74_migration.py")
        self.assertNotEqual(proof.returncode, 0)
        self.assertIn("R74 L0 changed", proof.stderr)

    def test_event_base_detects_committed_whitespace_and_cli_override(self):
        (self.root / "synthetic-event.txt").write_text("event change \n", encoding="utf-8", newline="\n")
        self.commit("synthetic whitespace defect")
        failed = self.cli("--check", "--check-whitespace", environment_base=self.base)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("synthetic-event.txt", failed.stdout + failed.stderr)
        result = self.assert_pass(self.cli("--check", "--check-whitespace", "--base-ref", "HEAD", environment_base=self.base))
        self.assertEqual(result["base_ref"], self.git("rev-parse", "HEAD").strip())

    def test_explicit_base_detects_committed_bad_link(self):
        (self.root / "synthetic-current.md").write_text("[missing](missing-fixture.md)\n", encoding="utf-8", newline="\n")
        self.commit("synthetic broken pointer")
        failed = self.cli("--check", "--base-ref", self.base)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("missing-fixture.md", failed.stderr)

    def test_new_branch_zero_base_and_invalid_ref(self):
        with mock.patch.object(routing, "ROOT", self.root):
            base = routing.resolve_base_ref("0" * 40)
        self.assertEqual(self.git("ls-tree", "-r", base), "")
        failed = self.cli("--check", "--base-ref", "missing-event-base")
        self.assertNotEqual(failed.returncode, 0)

    def test_opt_in_proof_checks_legacy_anchors(self):
        self.assert_pass(self.cli("--base-ref", self.base, script="check_r74_migration.py"))
        (self.root / "docs/SESSION_LIFECYCLE.md").write_text("# Future compatibility entry\n", encoding="utf-8", newline="\n")
        self.commit("synthetic legacy anchor migration")
        self.assert_pass(self.cli("--check", "--base-ref", self.base))
        failed = self.cli("--base-ref", self.base, script="check_r74_migration.py")
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("R74 legacy anchor removed", failed.stderr)

    def test_opt_in_proof_requires_explicit_base(self):
        result = self.cli(script="check_r74_migration.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--base-ref", result.stderr)


if __name__ == "__main__":
    unittest.main()
