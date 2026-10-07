import importlib.util
from pathlib import Path
import pytest

s=importlib.util.spec_from_file_location('lifecycle',Path(__file__).parents[1]/'release/lifecycle.py')
life=importlib.util.module_from_spec(s)
s.loader.exec_module(life)

def fixture(letter):
    return {'schema':'1.0.0','runtime':'opencode','platform':'linux/amd64','host_agent_major':1,
            'digest':'sha256:'+letter*64,'revision':letter*40,'conformance':'PASS'}

def test_exact_digest_update_and_rollback_keep_previous():
    proposal=life.validate(fixture('b'),fixture('a'))
    assert proposal['stable']=='sha256:'+'b'*64 and proposal['previous']=='sha256:'+'a'*64
    assert life.rollback(proposal)['stable']==proposal['previous']
    assert proposal['mutation']=='PROPOSAL_ONLY'

@pytest.mark.parametrize('field,value',[('digest','latest'),('conformance','FAIL'),('revision','main'),('host_agent_major',2),('platform','linux/arm64')])
def test_unready_or_incompatible_candidate_rejected(field,value):
    c=fixture('b');c[field]=value
    with pytest.raises(ValueError):life.validate(c,fixture('a'))

def test_missing_previous_is_not_rollback():
    with pytest.raises(ValueError):life.rollback(life.validate(fixture('b')))
