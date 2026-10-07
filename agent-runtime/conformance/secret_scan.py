"""Material signatures, not bare PEM parser delimiters in compiled programs."""
import re
import hashlib
import json
from pathlib import Path

MATERIAL=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\r?\n(?:Proc-Type: [^\r\n]+\r?\nDEK-Info: [^\r\n]+\r?\n\r?\n)?[A-Za-z0-9+/=]{20,}\r?\n|(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,})')

def contains_material(value):
    return MATERIAL.search(value) is not None

def verify_public_vectors(name,value):
    record=json.loads(Path(__file__).with_name('public-test-vectors.json').read_text())
    if name!=record['file'] or hashlib.sha256(value).hexdigest()!=record['file_sha256']:
        raise ValueError('PUBLIC_VECTOR_FILE_DRIFT')
    spans=[]
    for match in MATERIAL.finditer(value):
        end=value.find(b'\0',match.start())
        if end<0:raise ValueError('PUBLIC_VECTOR_BLOCK_BOUNDARY')
        block=value[match.start():end]
        if hashlib.sha256(block).hexdigest() not in record['block_sha256']:
            raise ValueError('UNRECOGNIZED_MATERIAL')
        spans.append(hashlib.sha256(block).hexdigest())
    if set(spans)!=set(record['block_sha256']) or len(spans)!=len(record['block_sha256']):
        raise ValueError('PUBLIC_VECTOR_SET_DRIFT')
    return len(spans)
