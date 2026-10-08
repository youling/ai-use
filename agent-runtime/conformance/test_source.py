import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).parents[1]
def test_recipe_pins_and_context_allowlist():
    docker=(ROOT/'opencode/Dockerfile').read_text()
    assert len(re.findall(r'@sha256:[a-f0-9]{64}',docker))==2
    assert '20261007T140000Z' in docker and 'USER 1000:1000' in docker
    assert 'check-valid-until=no' in docker and 'trusted=yes' not in docker
    assert 'COPY LICENSE.opencode ' in docker
    assert (ROOT/'opencode/.dockerignore').read_text().splitlines()==['*','!Dockerfile','!LICENSE.opencode']
    assert 'MIT License' in (ROOT/'opencode/LICENSE.opencode').read_text()

def test_public_source_has_no_instance_or_raw_secret():
    forbidden=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:gh[pousr]_[A-Za-z0-9]{30,}|(?i:github_pat_)[A-Za-z0-9_]{20,}|sk-proj-[A-Za-z0-9_-]{30,})')
    for p in ROOT.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
        value=p.read_bytes()
        secret_found=forbidden.search(value) is not None
        assert not secret_found,p
        assert ('D:'+chr(92)).encode() not in value and ('C:'+chr(92)+'Users'+chr(92)).encode() not in value,p
        assert ('youling-'+'jige-agent').encode() not in value,p

def test_ledger_targets_match_reviewed_migration():
    ledger=json.loads((ROOT/'migration-ledger.json').read_text())
    for row in ledger['files']:
        assert hashlib.sha256((ROOT.parent/row['target']).read_bytes()).hexdigest()==row['target_sha256']

def test_document_local_links_resolve():
    for p in [*ROOT.rglob('*.md'),ROOT.parent/'90_HISTORY/ADR-0016_PUBLIC_AGENT_RUNTIME.md']:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):continue
            assert (p.parent/target.split('#')[0]).exists(),(p,target)
