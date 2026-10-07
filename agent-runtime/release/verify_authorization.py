"""Fail-closed input/current-main authorization and exact conformance guard."""
import json
import os
from pathlib import Path
import re
import urllib.request

def main():
    assert os.environ.get('RELEASE_ENABLED')=='true','RELEASE_DISABLED'
    doc=json.loads(Path('agent-runtime/release/authorization.json').read_text())
    revision=os.environ['RELEASE_REVISION']
    tag=os.environ['RELEASE_TAG']
    run_id=os.environ['CONFORMANCE_RUN_ID']
    repository=os.environ['GITHUB_REPOSITORY']
    assert re.fullmatch(r'[a-f0-9]{40}',revision)
    assert re.fullmatch(r'[0-9]+',run_id)
    assert re.fullmatch(r'2\.0\.22-runtime\.1-candidate-[a-f0-9]{7,40}',tag)
    assert tag.endswith(revision[:len(tag.rsplit('-',1)[1])])
    assert doc['schema']=='1.0.0' and doc['action']=='PUBLISH_CANDIDATE'
    assert doc['revision']==revision and doc['tag']==tag
    assert re.fullmatch(r'https://github\.com/'+re.escape(repository)+r'/(?:issues|pull)/[1-9][0-9]*(?:#issuecomment-[0-9]+)?',doc['authority_pointer'])
    req=urllib.request.Request('https://api.github.com/repos/'+repository+'/actions/runs/'+run_id,
        headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'})
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args):raise ValueError('REDIRECT_DENIED')
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as response:
        evidence=json.load(response)
    assert evidence['head_sha']==revision and evidence['conclusion']=='success'
    assert evidence['name']=='Agent runtime conformance'
    assert evidence['repository']['full_name']==repository
    assert evidence['event'] in {'pull_request','push','workflow_dispatch'}
    print(json.dumps({'authorized_candidate':revision,'conformance_run_id':run_id,'publication':'NOT_YET'}))

if __name__=='__main__':main()
