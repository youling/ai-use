"""Bounded actual private GitHub canary; no model sessions or secret output."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request
from github_credential import current

def git(*args):
    result=subprocess.run(['git','-c','credential.helper=!python3 /exchange/in/github_credential.py',
        '-c','credential.useHttpPath=true',*args],cwd='/workspace',capture_output=True,text=True,timeout=45)
    if result.returncode:
        raise RuntimeError('GIT_OPERATION_FAILED')
    return result.stdout.strip()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):
        raise RuntimeError('API_REDIRECT_DENIED')

def api(path,body=None,method=None):
    value=current()
    req=urllib.request.Request('https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+path,
        data=None if body is None else json.dumps(body).encode(),method=method,
        headers={'Authorization':'Bearer '+value['token'],'Accept':'application/vnd.github+json',
        'X-GitHub-Api-Version':'2022-11-28','User-Agent':'agent-container-canary'})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as r:
        blob=r.read(2*1024*1024)
        return json.loads(blob) if blob else {}

def validate_work(spec):
    if (type(spec['issue']) is not int or spec['issue']<=0 or spec['phase'] not in {'a','b'}
        or spec['work']!=spec['repo']+'#'+str(spec['issue'])
        or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',spec['repo'])):
        raise ValueError('WORK_ISSUE_BINDING_MISMATCH')
    if not re.fullmatch(r'[a-f0-9]{40}',spec['source_sha']) or not re.fullmatch(r'[a-f0-9]{16}',spec['nonce']):
        raise ValueError('INVALID_WORK_BINDING')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./-]*',spec['source_ref']) or '..' in spec['source_ref']:
        raise ValueError('INVALID_SOURCE_REF')
    relative=Path(spec['canary_path'])
    if (relative.is_absolute() or '..' in relative.parts or '.git' in relative.parts
        or spec['canary_path']!=spec['allowed_canary_path']):
        raise ValueError('CANARY_WRITE_SET_DENIED')

def main():
    spec=json.loads(Path('/exchange/in/work.json').read_text())
    validate_work(spec)
    os.environ.update(GITHUB_WORK=spec['work'],GITHUB_REPOSITORY=spec['repo'],
        GIT_TERMINAL_PROMPT='0',GIT_CONFIG_NOSYSTEM='1')
    host=Path('/host-context/HOST_AGENT.md').read_bytes()
    if hashlib.sha256(host).hexdigest()!=spec['host_agent_sha256']:
        raise ValueError('HOST_AGENT_HASH_MISMATCH')
    if b'host_agent_version: 1.0.0' not in host or b'recovery_required: true' not in host:
        raise ValueError('HOST_AGENT_REQUIRED')
    issue=api('/issues/'+str(spec['issue']))
    if issue['number']!=spec['issue'] or issue['state']!='open' or not api('')['private']:
        raise ValueError('PRIVATE_WORK_MISMATCH')
    if Path('/home/foreman/.local/share/opencode/opencode.db').exists():
        raise ValueError('OLD_SESSION_STATE_PRESENT')
    branch='canary/host-agent-'+spec['nonce']
    git('clone','--no-checkout','https://github.com/'+spec['repo']+'.git','repo')
    git('-C','repo','fetch','origin',spec['source_ref'])
    base=git('-C','repo','rev-parse','FETCH_HEAD')
    if base!=spec['source_sha']:
        raise ValueError('SOURCE_HEAD_MOVED')
    git('-C','repo','checkout','--detach',base)
    if spec['phase']=='a':
        git('-C','repo','switch','-c',branch)
        target=Path('/workspace/repo')/spec['canary_path']
        relative=Path(spec['canary_path'])
        if (relative.is_absolute() or '..' in relative.parts or '.git' in relative.parts
            or spec['canary_path']!=spec['allowed_canary_path'] or target.exists()):
            raise ValueError('CANARY_WRITE_SET_DENIED')
        target.write_text(json.dumps({'work':spec['work'],'nonce':spec['nonce'],'base_sha':base,'host_agent_sha256':spec['host_agent_sha256']})+'\n')
        git('-C','repo','add','--',spec['canary_path'])
        git('-C','repo','-c','user.name=Agent container canary','-c','user.email=agent-canary@users.noreply.github.com','commit','-m','bounded Host recovery canary')
        sha=git('-C','repo','rev-parse','HEAD')
        git('-C','repo','push','origin','HEAD:refs/heads/'+branch)
        if api('/git/ref/heads/'+branch)['object']['sha']!=sha:
            raise ValueError('REMOTE_WRITEBACK_MISMATCH')
    else:
        comments=api('/issues/'+str(spec['issue'])+'/comments?per_page=100')
        rows=[json.loads(c['body'].split('```json\n')[1].split('\n```')[0]) for c in comments
            if 'HOST_AGENT_CONTAINER_CHECKPOINT' in c['body'] and spec['nonce'] in c['body']]
        previous=next(r for r in rows if r['phase']=='a' and r['work']==spec['work'])
        sha=previous['canary_sha']
        if not re.fullmatch(r'[a-f0-9]{40}',sha):
            raise ValueError('INVALID_DURABLE_SHA')
        git('-C','repo','fetch','origin',branch)
        if git('-C','repo','rev-parse','FETCH_HEAD')!=sha:
            raise ValueError('RECOVERY_SHA_MISMATCH')
        git('-C','repo','checkout','--detach',sha)
        receipt=json.loads((Path('/workspace/repo')/spec['canary_path']).read_text())
        if receipt['nonce']!=spec['nonce'] or receipt['base_sha']!=base:
            raise ValueError('RECOVERY_BINDING_MISMATCH')
    receipt={'work':spec['work'],'phase':spec['phase'],'nonce':spec['nonce'],'source_sha':base,
        'canary_sha':sha,'branch':branch,'uid':os.getuid(),'workspace':'LINUX_NATIVE',
        'host_agent_sha256':spec['host_agent_sha256'],'private_issue_read':True,
        'private_repo_fetch':True,'private_push':spec['phase']=='a','fresh_recovery':spec['phase']=='b',
        'prior_container_required':False,'prior_session_db_required':False,'secret_output':'NONE'}
    comment=api('/issues/'+str(spec['issue'])+'/comments',{'body':'## HOST_AGENT_CONTAINER_CHECKPOINT\n\n```json\n'+json.dumps(receipt,indent=2)+'\n```'})
    receipt['comment_url']=comment['html_url']
    receipt['actor']=comment['user']['login']
    Path('/exchange/out/receipt-'+spec['phase']+'.json').write_text(json.dumps(receipt,indent=2))
    if spec['phase']=='a':
        initial=current()['generation']
        for _ in range(45):
            time.sleep(2)
            if current()['generation']!=initial:
                api('/issues/'+str(spec['issue']))
                receipt['live_atomic_refresh_visible']=True
                Path('/exchange/out/receipt-a.json').write_text(json.dumps(receipt,indent=2))
                break
        else:
            raise ValueError('REFRESH_NOT_OBSERVED')
    else:
        api('/git/refs/heads/'+branch,method='DELETE')
        receipt['owned_branch_deleted_after_durable_readback']=True
        Path('/exchange/out/receipt-b.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt))

if __name__=='__main__':
    try:
        main()
    except urllib.error.HTTPError as e:
        print(json.dumps({'status':'FAILED','category':'HTTP_'+str(e.code),'secret_output':'NONE'}))
        raise SystemExit(2)
    except Exception as e:
        print(json.dumps({'status':'FAILED','category':type(e).__name__,'secret_output':'NONE'}))
        raise SystemExit(2)
