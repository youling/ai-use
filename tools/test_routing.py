"""Deterministic negative fixtures for routing migration; not fresh-agent tests."""
import copy
import json
import sys
import unittest
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

    def test_old_compatibility_anchors_preserved(self):
        routing.check_previous_anchors(routing.BASE)


if __name__ == "__main__":
    unittest.main()
