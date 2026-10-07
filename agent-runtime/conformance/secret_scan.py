"""Material signatures, not bare PEM parser delimiters in compiled programs."""
import re

MATERIAL=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\r?\n(?:Proc-Type: [^\r\n]+\r?\nDEK-Info: [^\r\n]+\r?\n\r?\n)?[A-Za-z0-9+/=]{20,}\r?\n|(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,})')

def contains_material(value):
    return MATERIAL.search(value) is not None
