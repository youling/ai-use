"""Synthetic reader implementation conforming to frozen canary contract."""
import json


def read_batch(records=None, checkpoints=None):
    """Read a batch of records and update partition checkpoints.

    Contract:
    - records: list of dicts with 'account', 'generation', 'shard', 'seq', 'message_id', 'send_time', 'text'.
    - checkpoints: dict mapping partition key string to non-negative integer max accepted seq.
    - partition key: json.dumps([account, generation, shard], ensure_ascii=False, separators=(',', ':')).
    - filtering: accept record if seq > partition's incoming checkpoint (absent partition defaults to 0).
    - replay deduplication: within partition by (account, generation, shard, message_id, seq).
      Equal message_id across different partitions is NOT deduplicated.
    - deterministic order: sorted by (account, generation, shard, seq, message_id).
    - checkpoints: preserved caller checkpoints updated with newly accepted max seqs.
      Only returned records advance checkpoint.
    - caller input immutability: caller's records and checkpoints are never mutated.
    """
    new_checkpoints = dict(checkpoints) if checkpoints is not None else {}
    if records is None:
        return {'records': [], 'checkpoints': new_checkpoints}

    accepted_records = []
    seen_replays = set()
    partition_max_seq = {}

    for record in records:
        account = record['account']
        generation = record['generation']
        shard = record['shard']
        seq = record['seq']
        message_id = record['message_id']

        pk = json.dumps([account, generation, shard], ensure_ascii=False, separators=(',', ':'))
        incoming_cp = new_checkpoints.get(pk, 0)

        if seq <= incoming_cp:
            continue

        replay_key = (account, generation, shard, message_id, seq)
        if replay_key in seen_replays:
            continue
        seen_replays.add(replay_key)

        accepted_records.append(record)

        if pk not in partition_max_seq or seq > partition_max_seq[pk]:
            partition_max_seq[pk] = seq

    accepted_records.sort(
        key=lambda r: (r['account'], r['generation'], r['shard'], r['seq'], r['message_id'])
    )

    for pk, max_seq in partition_max_seq.items():
        new_checkpoints[pk] = max_seq

    return {
        'records': accepted_records,
        'checkpoints': new_checkpoints,
    }
