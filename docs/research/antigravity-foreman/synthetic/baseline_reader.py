"""Deliberately flawed, synthetic negative control; no private source data."""
def read_batch(records, checkpoints):
    position = max(checkpoints.values(), default=0)
    seen = set()
    output = []
    for record in records:
        if record['seq'] <= position or record['message_id'] in seen:
            continue
        output.append(record)
        seen.add(record['message_id'])
        position = record['seq']
    return {'records': output, 'checkpoints': {'global': position}}
