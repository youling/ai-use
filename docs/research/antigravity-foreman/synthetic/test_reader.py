"""
Independent Oracle Test Suite for Synthetic Reader Contract (TASK.md)

Contract requirements verified:
1. Checkpoint key format: json.dumps([account, generation, shard], ensure_ascii=False, separators=(',', ':'))
2. Non-negative integer max accepted seq as partition checkpoint value
3. Cross-partition duplicate message_id preservation (no deduplication across partitions)
4. Exact duplicate replay deduplication within partition by (account, generation, shard, message_id, seq)
5. Same message_id with different seq within partition accepted (not deduplicated)
6. Old send_time with new seq: seq dominates ordering and filtering; send_time ignored
7. Restart / checkpoint reuse: seq <= incoming checkpoint filtered; seq > checkpoint accepted
8. Empty source input: preserves incoming checkpoints, empty records list, caller inputs unchanged
9. Input immutability: records list, record dicts, incoming checkpoints dict not mutated
10. Deterministic sorting by (account, generation, shard, seq, message_id)
11. No checkpoint overrun: unaccepted records never advance checkpoint; checkpoint is max accepted seq
12. Unicode and delimiter handling in partition keys, message_ids, text
13. Very large textual identifiers and large sequence numbers
14. Out-of-order sequence processing within partition
15. Red negative controls: explicitly exposing the baseline demo_reader.py flaws
"""

import copy
import importlib.util
import json
import os
import sys
import unittest


def get_candidate_module():
    """
    Dynamically loads candidate module from CANARY_CANDIDATE_FILE environment variable,
    falling back to local demo_reader.py.
    """
    candidate_env = os.environ.get("CANARY_CANDIDATE_FILE", "demo_reader.py")
    if not os.path.isabs(candidate_env):
        if os.path.exists(candidate_env):
            candidate_path = os.path.abspath(candidate_env)
        else:
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            candidate_path = os.path.join(repo_root, candidate_env)
    else:
        candidate_path = candidate_env

    if not os.path.exists(candidate_path):
        raise FileNotFoundError(f"Candidate file not found at: {candidate_path}")

    spec = importlib.util.spec_from_file_location("candidate_reader", candidate_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create module spec for: {candidate_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CANDIDATE = get_candidate_module()


def make_checkpoint_key(account, generation, shard):
    return json.dumps([account, generation, shard], ensure_ascii=False, separators=(',', ':'))


class TestSyntheticReaderContract(unittest.TestCase):
    """
    Independent test suite verifying TASK.md synthetic reader contract.
    """

    def setUp(self):
        self.reader = CANDIDATE
        self.assertTrue(
            hasattr(self.reader, "read_batch"),
            "Candidate module must define read_batch(records, checkpoints)"
        )

    def test_checkpoint_key_encoding_format(self):
        """
        Verify checkpoint keys are compact JSON arrays of [account, generation, shard]
        using ensure_ascii=False and separators=(',', ':').
        """
        key1 = make_checkpoint_key("acct-1", 1, "shard-a")
        self.assertEqual(key1, '["acct-1",1,"shard-a"]')

        records = [
            {
                "account": "acct-1",
                "generation": 1,
                "shard": "shard-a",
                "seq": 5,
                "message_id": "m1",
                "send_time": "2026-10-13T10:00:00Z",
                "text": "hello"
            }
        ]
        res = self.reader.read_batch(records, {})
        self.assertIn("checkpoints", res)
        self.assertIn(key1, res["checkpoints"])
        self.assertEqual(res["checkpoints"][key1], 5)
        # Verify no bogus keys like 'global' or python tuples
        self.assertNotIn("global", res["checkpoints"])
        self.assertEqual(len(res["checkpoints"]), 1)

    def test_cross_partition_same_message_id_preserved(self):
        """
        Records across different accounts, generations, or shards having the same
        message_id must NOT be deduplicated across partitions.
        (Exposes baseline demo_reader.py flaw of global seen set).
        """
        shared_msg_id = "shared-uuid-001"
        records = [
            {
                "account": "acct-A",
                "generation": 1,
                "shard": "s1",
                "seq": 10,
                "message_id": shared_msg_id,
                "send_time": "2026-10-13T10:00:00Z",
                "text": "record from A/1/s1"
            },
            {
                "account": "acct-B",
                "generation": 1,
                "shard": "s1",
                "seq": 10,
                "message_id": shared_msg_id,
                "send_time": "2026-10-13T10:00:01Z",
                "text": "record from B/1/s1"
            },
            {
                "account": "acct-A",
                "generation": 2,
                "shard": "s1",
                "seq": 10,
                "message_id": shared_msg_id,
                "send_time": "2026-10-13T10:00:02Z",
                "text": "record from A/2/s1"
            },
            {
                "account": "acct-A",
                "generation": 1,
                "shard": "s2",
                "seq": 10,
                "message_id": shared_msg_id,
                "send_time": "2026-10-13T10:00:03Z",
                "text": "record from A/1/s2"
            },
        ]
        res = self.reader.read_batch(records, {})
        self.assertEqual(len(res["records"]), 4, "All cross-partition records must be preserved")
        returned_ids = [r["message_id"] for r in res["records"]]
        self.assertEqual(returned_ids, [shared_msg_id] * 4)

        # Checkpoints for each partition must be advanced independently
        k_a1s1 = make_checkpoint_key("acct-A", 1, "s1")
        k_b1s1 = make_checkpoint_key("acct-B", 1, "s1")
        k_a2s1 = make_checkpoint_key("acct-A", 2, "s1")
        k_a1s2 = make_checkpoint_key("acct-A", 1, "s2")

        for k in (k_a1s1, k_b1s1, k_a2s1, k_a1s2):
            self.assertIn(k, res["checkpoints"])
            self.assertEqual(res["checkpoints"][k], 10)

    def test_exact_duplicate_replay_within_partition_deduplicated(self):
        """
        Deduplicate exact replay within partition by (account, generation, shard, message_id, seq).
        However, records with same message_id but DIFFERENT seq within the same partition
        must BOTH be preserved.
        """
        # Exact duplicate replay: identical partition + message_id + seq
        rec1 = {
            "account": "acct-1",
            "generation": 1,
            "shard": "s0",
            "seq": 10,
            "message_id": "m1",
            "send_time": "2026-10-13T10:00:00Z",
            "text": "first attempt"
        }
        rec1_replay = {
            "account": "acct-1",
            "generation": 1,
            "shard": "s0",
            "seq": 10,
            "message_id": "m1",
            "send_time": "2026-10-13T10:00:05Z",
            "text": "replayed attempt"
        }
        # Same message_id, different seq (e.g. retry / subsequent event)
        rec2_diff_seq = {
            "account": "acct-1",
            "generation": 1,
            "shard": "s0",
            "seq": 12,
            "message_id": "m1",
            "send_time": "2026-10-13T10:01:00Z",
            "text": "new message with same id"
        }

        records = [rec1, rec1_replay, rec2_diff_seq]
        res = self.reader.read_batch(records, {})

        # Should contain exactly 2 records: one for seq 10, one for seq 12
        self.assertEqual(len(res["records"]), 2)
        seqs = [r["seq"] for r in res["records"]]
        self.assertEqual(seqs, [10, 12])

        k = make_checkpoint_key("acct-1", 1, "s0")
        self.assertEqual(res["checkpoints"][k], 12)

    def test_unicode_delimiters_and_large_identifiers(self):
        """
        Verify handling of Unicode characters, punctuation/delimiters, and very large
        string identifiers in partition keys, message_ids, and texts.
        """
        unicode_acct = "用户/org:北京_123,{\"tag\":\"vip\"}"
        unicode_shard = "分片#0:east-1[α/β]"
        large_msg_id = "msg_" + "x" * 2000 + "_🔥🚀_,"
        large_text = "Emoji: 🌟 🚀 " + ("Data payload delimiter ,:[]{}\n\t" * 50)

        key = make_checkpoint_key(unicode_acct, 42, unicode_shard)
        # Ensure json.dumps with ensure_ascii=False keeps Unicode literal
        self.assertIn("用户", key)
        self.assertIn("分片", key)
        self.assertNotIn("\\u", key)

        records = [
            {
                "account": unicode_acct,
                "generation": 42,
                "shard": unicode_shard,
                "seq": 999999999999,
                "message_id": large_msg_id,
                "send_time": "2026-10-13T12:00:00.123456Z",
                "text": large_text
            }
        ]

        res = self.reader.read_batch(records, {})
        self.assertEqual(len(res["records"]), 1)
        out_rec = res["records"][0]
        self.assertEqual(out_rec["account"], unicode_acct)
        self.assertEqual(out_rec["shard"], unicode_shard)
        self.assertEqual(out_rec["message_id"], large_msg_id)
        self.assertEqual(out_rec["text"], large_text)
        self.assertIn(key, res["checkpoints"])
        self.assertEqual(res["checkpoints"][key], 999999999999)

    def test_old_send_time_with_new_seq(self):
        """
        Ordering and filtering is dominated by seq, independent of send_time.
        Older send_time with higher seq must not be filtered out or misordered.
        """
        k = make_checkpoint_key("acct", 1, "s0")
        incoming_checkpoints = {k: 5}

        records = [
            # Older send_time but higher seq: should be accepted and sorted after seq 10
            {
                "account": "acct",
                "generation": 1,
                "shard": "s0",
                "seq": 20,
                "message_id": "m-seq20",
                "send_time": "1999-01-01T00:00:00Z",
                "text": "ancient timestamp"
            },
            # Newer send_time but seq <= incoming checkpoint (5): must be filtered
            {
                "account": "acct",
                "generation": 1,
                "shard": "s0",
                "seq": 5,
                "message_id": "m-seq5",
                "send_time": "2026-10-13T12:00:00Z",
                "text": "recent timestamp but old seq"
            },
            # Intermediate seq > 5
            {
                "account": "acct",
                "generation": 1,
                "shard": "s0",
                "seq": 10,
                "message_id": "m-seq10",
                "send_time": "2026-10-13T10:00:00Z",
                "text": "valid seq"
            }
        ]

        res = self.reader.read_batch(records, incoming_checkpoints)
        self.assertEqual(len(res["records"]), 2)
        # Deterministic order: seq 10 before seq 20, despite seq 20 having 1999 timestamp
        self.assertEqual([r["seq"] for r in res["records"]], [10, 20])
        self.assertEqual([r["message_id"] for r in res["records"]], ["m-seq10", "m-seq20"])
        self.assertEqual(res["checkpoints"][k], 20)

    def test_restart_and_checkpoint_reuse(self):
        """
        Batch 1 establishes checkpoints. Batch 2 reuses those checkpoints.
        Only records with seq > incoming checkpoint are accepted.
        Unrelated partition checkpoints are preserved.
        """
        k1 = make_checkpoint_key("acct-1", 1, "s0")
        k2 = make_checkpoint_key("acct-2", 1, "s0")
        k3 = make_checkpoint_key("acct-idle", 1, "s0")

        existing_checkpoints = {
            k1: 100,
            k2: 50,
            k3: 999
        }

        # Records: some replayed / older seqs, some new seqs
        records = [
            {"account": "acct-1", "generation": 1, "shard": "s0", "seq": 99, "message_id": "m1", "send_time": "t", "text": "old"},
            {"account": "acct-1", "generation": 1, "shard": "s0", "seq": 100, "message_id": "m2", "send_time": "t", "text": "boundary"},
            {"account": "acct-1", "generation": 1, "shard": "s0", "seq": 101, "message_id": "m3", "send_time": "t", "text": "new"},
            {"account": "acct-1", "generation": 1, "shard": "s0", "seq": 105, "message_id": "m4", "send_time": "t", "text": "newest"},
            {"account": "acct-2", "generation": 1, "shard": "s0", "seq": 50, "message_id": "m5", "send_time": "t", "text": "boundary"},
            {"account": "acct-2", "generation": 1, "shard": "s0", "seq": 55, "message_id": "m6", "send_time": "t", "text": "new"}
        ]

        res = self.reader.read_batch(records, existing_checkpoints)

        # Accepted: acct-1 seq 101, 105; acct-2 seq 55
        self.assertEqual(len(res["records"]), 3)
        self.assertEqual([r["seq"] for r in res["records"]], [101, 105, 55])

        # Checkpoints: k1 -> 105, k2 -> 55, k3 -> 999 (idle partition preserved!)
        self.assertEqual(res["checkpoints"][k1], 105)
        self.assertEqual(res["checkpoints"][k2], 55)
        self.assertEqual(res["checkpoints"][k3], 999)

    def test_empty_source_input_preserves_checkpoints(self):
        """
        Empty records list preserves incoming checkpoints, returns empty records,
        and never mutates caller's checkpoint dict.
        """
        k1 = make_checkpoint_key("acct-A", 1, "s0")
        k2 = make_checkpoint_key("acct-B", 2, "s1")
        incoming_checkpoints = {k1: 42, k2: 88}
        checkpoints_copy = copy.deepcopy(incoming_checkpoints)

        res = self.reader.read_batch([], incoming_checkpoints)

        self.assertEqual(res["records"], [])
        self.assertEqual(res["checkpoints"], incoming_checkpoints)
        # Ensure caller's input was not mutated
        self.assertEqual(incoming_checkpoints, checkpoints_copy)

    def test_input_immutability(self):
        """
        Verify that caller's input records list, record dictionaries, and incoming
        checkpoints dictionary are never mutated by read_batch.
        """
        k = make_checkpoint_key("acct", 1, "s0")
        original_checkpoints = {k: 5}
        checkpoints_param = copy.deepcopy(original_checkpoints)

        original_records = [
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 10, "message_id": "m1", "send_time": "t1", "text": "msg1"},
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 8, "message_id": "m2", "send_time": "t2", "text": "msg2"},
        ]
        records_param = copy.deepcopy(original_records)

        res = self.reader.read_batch(records_param, checkpoints_param)

        # Check that caller's arguments remain identical to the originals
        self.assertEqual(records_param, original_records, "Input records list or dicts were mutated")
        self.assertEqual(checkpoints_param, original_checkpoints, "Input checkpoints dict was mutated")

        # Mutating result should not affect caller inputs
        res["records"].append({"account": "bogus"})
        res["checkpoints"]["bogus"] = 999
        self.assertEqual(records_param, original_records)
        self.assertEqual(checkpoints_param, original_checkpoints)

    def test_deterministic_ordering_multidimensional(self):
        """
        Records must be sorted deterministically by (account, generation, shard, seq, message_id).
        """
        # Create records scrambled across dimensions
        raw_tuples = [
            ("beta", 1, "s0", 1, "m-1"),
            ("alpha", 2, "s0", 1, "m-1"),
            ("alpha", 1, "s1", 1, "m-1"),
            ("alpha", 1, "s0", 2, "m-1"),
            ("alpha", 1, "s0", 1, "m-2"),
            ("alpha", 1, "s0", 1, "m-1"),
        ]
        # In reverse order
        records = [
            {
                "account": t[0],
                "generation": t[1],
                "shard": t[2],
                "seq": t[3],
                "message_id": t[4],
                "send_time": "2026-10-13T10:00:00Z",
                "text": f"text-{t[4]}"
            }
            for t in reversed(raw_tuples)
        ]

        res = self.reader.read_batch(records, {})
        observed_tuples = [
            (r["account"], r["generation"], r["shard"], r["seq"], r["message_id"])
            for r in res["records"]
        ]

        expected_tuples = sorted(raw_tuples)
        self.assertEqual(observed_tuples, expected_tuples)

    def test_no_checkpoint_overrun(self):
        """
        Only returned records advance checkpoint.
        If all records for a partition have seq <= incoming checkpoint,
        the checkpoint must NOT advance or be overwritten with a lower seq.
        Checkpoint value is the max accepted seq.
        """
        k = make_checkpoint_key("acct", 1, "s0")
        incoming_checkpoints = {k: 50}

        # Records below and equal to checkpoint 50
        records = [
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 20, "message_id": "m1", "send_time": "t", "text": "old"},
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 50, "message_id": "m2", "send_time": "t", "text": "at_cp"},
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 35, "message_id": "m3", "send_time": "t", "text": "old2"},
        ]

        res = self.reader.read_batch(records, incoming_checkpoints)
        self.assertEqual(res["records"], [])
        self.assertEqual(res["checkpoints"][k], 50, "Checkpoint must remain 50 when no records accepted")

        # Now input with accepted records arriving out-of-order: 70, 90, 60
        records_accepted = [
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 70, "message_id": "m4", "send_time": "t", "text": "a"},
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 90, "message_id": "m5", "send_time": "t", "text": "b"},
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 60, "message_id": "m6", "send_time": "t", "text": "c"},
        ]
        res2 = self.reader.read_batch(records_accepted, incoming_checkpoints)
        self.assertEqual(len(res2["records"]), 3)
        self.assertEqual(res2["checkpoints"][k], 90, "Partition checkpoint must be max accepted seq (90)")

    def test_out_of_order_seq_within_partition(self):
        """
        Records arriving out of seq order within a partition:
        Baseline demo_reader.py updates position immediately during loop,
        incorrectly skipping seq 5 after seeing seq 10.
        Oracle requires both seq 5 and seq 10 to be accepted when incoming cp is 0.
        """
        records = [
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 10, "message_id": "m10", "send_time": "t", "text": "ten"},
            {"account": "acct", "generation": 1, "shard": "s0", "seq": 5, "message_id": "m5", "send_time": "t", "text": "five"},
        ]
        res = self.reader.read_batch(records, {})
        self.assertEqual(len(res["records"]), 2, "Both seq 10 and seq 5 must be accepted")
        self.assertEqual([r["seq"] for r in res["records"]], [5, 10], "Must be sorted by seq")
        k = make_checkpoint_key("acct", 1, "s0")
        self.assertEqual(res["checkpoints"][k], 10)

    def test_negative_control_baseline_flaws_exposed(self):
        """
        Explicit red negative control that definitively fails on baseline demo_reader.py:
        1. Multi-partition isolation: different partitions must maintain separate checkpoints
        2. Checkpoint key format: json array string vs baseline 'global'
        3. Cross-partition duplicate message_id: must not be dropped by global seen set
        4. Preservation of untouched incoming checkpoints
        """
        k1 = make_checkpoint_key("acct-1", 1, "s0")
        k2 = make_checkpoint_key("acct-2", 1, "s0")
        incoming_checkpoints = {k1: 5, k2: 20}

        records = [
            # acct-1 has record with seq 6 (accepted, advances k1 to 6)
            {"account": "acct-1", "generation": 1, "shard": "s0", "seq": 6, "message_id": "dup-id", "send_time": "t", "text": "p1"},
            # acct-2 has record with seq 21 and SAME message_id (must be accepted!)
            {"account": "acct-2", "generation": 1, "shard": "s0", "seq": 21, "message_id": "dup-id", "send_time": "t", "text": "p2"},
        ]

        res = self.reader.read_batch(records, incoming_checkpoints)

        # Baseline demo_reader fails here in multiple ways:
        # - returns {'checkpoints': {'global': 21}} instead of partitioned JSON keys
        # - drops the second record because message_id 'dup-id' is in seen
        self.assertEqual(len(res["records"]), 2)
        self.assertIn(k1, res["checkpoints"])
        self.assertIn(k2, res["checkpoints"])
        self.assertEqual(res["checkpoints"][k1], 6)
        self.assertEqual(res["checkpoints"][k2], 21)
        self.assertNotIn("global", res["checkpoints"])


if __name__ == "__main__":
    unittest.main()
