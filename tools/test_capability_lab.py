"""Bounded contract regressions; no network, live canary or semantic acceptance."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
import capability_lab as lab


class ClaimContractTests(unittest.TestCase):
    def setUp(self):
        self.schema = lab.read_json(lab.ROOT / lab.SCHEMA)
        self.claims = [(p.name, lab.read_json(p)) for p in sorted((lab.ROOT / lab.LAB / "claims").glob("*.json"))]
        self.claim = copy.deepcopy(next(c for _, c in self.claims if c["capability_id"] == "pagination-incomplete-enumeration"))
        self.claim.update(promotion_status="UNREVIEWED", review=[])
        self.name = self.claim["capability_id"] + ".json"

    def validate(self):
        lab.validate_claims(lab.ROOT, [(self.name, self.claim)], self.schema)

    def test_representative_set_passes(self):
        self.assertTrue({"pagination-incomplete-enumeration", "actions-least-permission-matrix-artifact",
                         "reversible-issue-relationship"} <= {c["capability_id"] for _, c in self.claims})
        lab.validate_claims(lab.ROOT, self.claims, self.schema)

    def test_invalid_evidence_and_promotion_enums(self):
        for field, value in [("evidence_classes", ["DOCUMENTED_CURRENT"]),
                             ("promotion_status", "AUTO_ACCEPTED")]:
            with self.subTest(field=field):
                changed = copy.deepcopy(self.claim)
                changed[field] = value
                with self.assertRaisesRegex(ValueError, "invalid enum"):
                    lab.validate_claims(lab.ROOT, [(self.name, changed)], self.schema)

    def test_normative_and_production_self_promotion_rejected(self):
        for value in ("NORMATIVE", "PRODUCTION", "NORMATIVE_AUTHORITY", "PRODUCTION_READY"):
            with self.subTest(value=value):
                self.claim["promotion_status"] = value
                with self.assertRaises(ValueError):
                    self.validate()
        self.claim["promotion_status"] = "UNREVIEWED"
        self.claim["authority"] = "normative"
        with self.assertRaisesRegex(ValueError, "unknown field"):
            self.validate()
        del self.claim["authority"]
        self.claim["proves"].append("NORMATIVE_AUTHORITY = YES")
        with self.assertRaisesRegex(ValueError, "public-safe guard"):
            self.validate()

    def test_missing_required_currentness_limits_cleanup_adoption(self):
        for field in ("limits", "verified_at", "invalidated_by", "revalidate_before",
                      "source_revision", "fixture_revision", "cleanup_recovery", "adoption_delta"):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.claim)
                del changed[field]
                with self.assertRaisesRegex(ValueError, "missing required"):
                    lab.validate_claims(lab.ROOT, [(self.name, changed)], self.schema)

    def test_empty_required_fields_rejected(self):
        for field in ("limits", "adoption_delta", "revalidate_before"):
            changed = copy.deepcopy(self.claim)
            changed[field] = []
            with self.assertRaisesRegex(ValueError, "empty required"):
                lab.validate_claims(lab.ROOT, [(self.name, changed)], self.schema)
        self.claim["cleanup_recovery"]["unknown_result"] = " "
        with self.assertRaisesRegex(ValueError, "empty required"):
            self.validate()

    def test_duplicate_capability_id_and_filename_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate capability_id"):
            lab.validate_claims(lab.ROOT, [(self.name, self.claim)] * 2, self.schema)
        with self.assertRaisesRegex(ValueError, "stable filename"):
            lab.validate_claims(lab.ROOT, [("renamed.json", self.claim)], self.schema)

    def test_stale_invalid_unknown_and_unreviewed_never_current(self):
        for status in ("HISTORICAL", "STALE", "INVALID", "UNKNOWN"):
            for promotion in ("UNREVIEWED", "REVIEWED_EVIDENCE", "REUSABLE_DONOR", "SUPERSEDED", "INVALIDATED"):
                changed = copy.deepcopy(self.claim)
                changed.update(status=status, promotion_status=promotion)
                index = json.loads(lab.render_index([(self.name, changed)]))
                self.assertEqual(index["entries"][0]["use"], "NOT_CURRENT_EVIDENCE")
                self.assertEqual(len(index["entries"]), 1, "uncertain evidence must not disappear")
        self.claim.update(status="CURRENT", promotion_status="REVIEWED_EVIDENCE")
        self.claim["evidence_classes"].append("UNKNOWN")
        self.assertIn("NOT_CURRENT_EVIDENCE", lab.render_index([(self.name, self.claim)]))
        self.claim["evidence_classes"].remove("UNKNOWN")
        self.assertIn("REQUIRES_CLAIM_AND_TARGET_REVALIDATION", lab.render_index([(self.name, self.claim)]))

    def test_public_private_secret_coordinate_guard(self):
        samples = ['{"repository":"fixture-owner/private-repository"}',
                   'https://github.com/fixture-owner/private-repository/issues/1',
                   '{"visibility":"private"}', 'https://user:example-secret@example.invalid/x',
                   'https://example.invalid/x?access_token=synthetic',
                   'https://10.1.2.3/api', 'https://node.internal/api',
                   'gh' + 'p_' + 'A' * 30, 'github_' + 'pat_' + 'B' * 30]
        for sample in samples:
            with self.subTest(sample=sample):
                with self.assertRaises(ValueError):
                    lab.public_guard(sample, "synthetic test")
        lab.public_guard('https://github.com/youling/ai-use/issues/82', "public fixture")

    def test_missing_escaped_and_wrong_lane_pointer(self):
        for pointer in (lab.LAB + "/fixtures/missing.json", "../outside.json", "AGENTS.md"):
            self.claim["fixture_revision"]["path"] = pointer
            with self.assertRaises(ValueError):
                self.validate()

    def test_fixture_and_receipt_digest_drift(self):
        for field in ("fixture_revision", "receipts"):
            changed = copy.deepcopy(self.claim)
            target = changed[field] if field == "fixture_revision" else changed[field][0]
            target["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                lab.validate_claims(lab.ROOT, [(self.name, changed)], self.schema)

    def test_live_metadata_cannot_claim_git_revision(self):
        self.claim["source_revision"]["commit"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "source revision kind mismatch"):
            self.validate()

    def test_no_timestamp_refresh_without_observation(self):
        self.claim["verified_at"] = "2030-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "matching observation"):
            self.validate()

    def test_review_requires_receipt_structure_and_content_binding(self):
        self.claim["promotion_status"] = "REVIEWED_EVIDENCE"
        with self.assertRaisesRegex(ValueError, "semantic review receipt"):
            self.validate()
        self.claim["review"] = [{"path": self.claim["receipts"][0]["path"],
                                 "content_sha256": lab.semantic_digest(self.claim)}]
        with self.assertRaises(ValueError, msg="ordinary observation cannot masquerade as semantic review"):
            self.validate()
        self.claim["review"][0]["content_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "semantic review digest drift"):
            self.validate()

    def test_invalid_state_requires_explicit_invalidation(self):
        self.claim["status"] = "INVALID"
        with self.assertRaisesRegex(ValueError, "invalidated promotion"):
            self.validate()
        self.claim["promotion_status"] = "INVALIDATED"
        self.validate()

    def test_index_is_bounded_deterministic_and_read_only(self):
        before = copy.deepcopy(self.claims)
        rendered = lab.render_index(self.claims)
        self.assertEqual(rendered, lab.render_index(list(reversed(self.claims))))
        self.assertEqual(before, self.claims)
        for entry in json.loads(rendered)["entries"]:
            self.assertFalse({"observed", "environment", "receipts", "authority", "available"} & entry.keys())

    def test_unsupported_schema_keyword_fails_even_in_unused_definition(self):
        self.schema["$defs"]["unused"] = {"unevaluatedProperties": False}
        with self.assertRaisesRegex(ValueError, "unsupported schema keyword"):
            self.validate()

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "duplicate.json"
            p.write_text('{"status":"UNKNOWN","status":"CURRENT"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                lab.read_json(p)

    def test_offline_generation_detects_index_drift_without_promoting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cid = self.claim["capability_id"]
            for part in ("schema", "fixtures/" + cid, "receipts/" + cid):
                shutil.copytree(lab.ROOT / lab.LAB / part, root / lab.LAB / part)
            claim_path = root / lab.LAB / "claims" / self.name
            claim_path.parent.mkdir()
            original = lab.serialized(self.claim).encode()
            claim_path.write_bytes(original)
            (root / "AGENTS.md").write_text("synthetic kernel\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            lab.git(root, "add", ".")
            lab.git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                    "commit", "-qm", "synthetic pagination fixture")
            self.assertEqual(lab.run(root, write=True, r4_acceptance=True), 1)
            self.assertEqual(claim_path.read_bytes(), original)
            self.assertEqual(lab.run(root), 1)
            (root / lab.LAB / "index.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "index drift"):
                lab.run(root)


class RepositoryBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "AGENTS.md").write_text("synthetic kernel\n", encoding="utf-8")
        self.claims = self.root / lab.LAB / "claims"
        self.claims.mkdir(parents=True)
        (self.claims / "stable.json").write_text('{"capability_id":"stable"}\n', encoding="utf-8")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "synthetic base")
        self.base = self.git("rev-parse", "HEAD").decode().strip()

    def git(self, *args):
        return lab.git(self.root, *args)

    def test_stable_id_removal_rejected_against_git_base(self):
        (self.claims / "stable.json").write_text('{"capability_id":"renamed"}\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "stable capability_id removed"):
            lab.check_baseline(self.root, self.base)

    def test_kernel_freeze_is_explicit_r4_only(self):
        (self.root / "AGENTS.md").write_text("synthetic authorized future update\n", encoding="utf-8")
        lab.check_baseline(self.root, self.base)
        with self.assertRaisesRegex(ValueError, "AGENTS.md changed"):
            lab.check_baseline(self.root, self.base, r4_acceptance=True)

    def test_missing_base_fails_closed(self):
        with self.assertRaises(subprocess.CalledProcessError):
            lab.check_baseline(self.root, "missing-synthetic-base")


if __name__ == "__main__":
    unittest.main()
