import importlib.util
import json
from pathlib import Path
import pytest

s=importlib.util.spec_from_file_location('releaseguard',Path(__file__).parents[1]/'release/verify_authorization.py')
guard=importlib.util.module_from_spec(s);s.loader.exec_module(guard)

def test_release_disabled_before_file_or_network(monkeypatch):
    monkeypatch.delenv('RELEASE_ENABLED',raising=False)
    with pytest.raises(AssertionError,match='RELEASE_DISABLED'):guard.main()

@pytest.mark.parametrize('field,value',[('revision','b'*40),('action','PROMOTE_STABLE'),('tag','latest'),('authority_pointer','https://evil.example/approval')])
def test_exact_authority_mismatch_fails_before_network(tmp_path,monkeypatch,field,value):
    monkeypatch.chdir(tmp_path)
    folder=tmp_path/'agent-runtime/release';folder.mkdir(parents=True)
    doc={'schema':'1.0.0','action':'PUBLISH_CANDIDATE','revision':'a'*40,
         'tag':'2.0.22-runtime.1-candidate-aaaaaaa','authority_pointer':'https://github.com/owner/repo/issues/123#issuecomment-123'}
    doc[field]=value
    (folder/'authorization.json').write_text(json.dumps(doc))
    for k,v in {'RELEASE_ENABLED':'true','RELEASE_REVISION':'a'*40,
        'RELEASE_TAG':'2.0.22-runtime.1-candidate-aaaaaaa','CONFORMANCE_RUN_ID':'123',
        'GITHUB_REPOSITORY':'owner/repo','GH_TOKEN':'synthetic-only'}.items():monkeypatch.setenv(k,v)
    monkeypatch.setattr(guard.urllib.request,'build_opener',lambda *_: pytest.fail('network reached before authority guard'))
    with pytest.raises(AssertionError):guard.main()
