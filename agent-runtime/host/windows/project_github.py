"""Trusted Host-only runtime projection helper. Never print credential material."""
import argparse
import base64
import datetime as dt
import json
import os
import re
from pathlib import Path
import time
import urllib.error
import urllib.request

def b64(v):
    return base64.urlsafe_b64encode(v).rstrip(b'=').decode()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError('REDIRECT_DENIED')

def request(path, bearer, data=None, method=None):
    if not path.startswith('/') or path.startswith('//'):
        raise ValueError('API_PATH_DENIED')
    req=urllib.request.Request('https://api.github.com'+path,
        data=None if data is None else json.dumps(data).encode(),method=method,
        headers={'Authorization':'Bearer '+bearer,'Accept':'application/vnd.github+json',
                 'X-GitHub-Api-Version':'2022-11-28','User-Agent':'host-runtime-projection'})
    opener=urllib.request.build_opener(NoRedirect())
    with opener.open(req,timeout=30) as r:
        blob=r.read(1024*1024)
        return json.loads(blob) if blob else {}

def jwt(binding):
    from cryptography.hazmat.primitives import hashes,serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    now=int(time.time())
    unsigned=b64(b'{"alg":"RS256","typ":"JWT"}')+'.'+b64(json.dumps({'iat':now-60,'exp':now+480,'iss':binding['app_id']}).encode())
    # Host-native catalog consumption only. Key never copied or serialized.
    key=serialization.load_pem_private_key(Path(binding['private_key_ref']).read_bytes(),password=None)
    return unsigned+'.'+b64(key.sign(unsigned.encode(),padding.PKCS1v15(),hashes.SHA256()))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--binding',required=True)
    p.add_argument('--mode',choices=['probe','project','revoke'],required=True)
    p.add_argument('--directory')
    p.add_argument('--generation',default='one')
    a=p.parse_args()
    binding=json.loads(Path(a.binding).read_text(encoding='utf-8-sig'))
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,40}',a.generation):
        raise ValueError('INVALID_GENERATION')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',binding['repo']):
        raise ValueError('INVALID_REPOSITORY')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*',binding['work']):
        raise ValueError('INVALID_WORK')
    if a.mode=='revoke':
        cred=json.loads((Path(a.directory)/'credential.json').read_text())
        request('/installation/token',cred['token'],method='DELETE')
        print(json.dumps({'revoked':True,'secret_output':'NONE'}))
        return
    assertion=jwt(binding)
    app=request('/app',assertion)
    if app['id']!=binding['app_id'] or app['slug']!=binding['app_slug']:
        raise ValueError('APP_BINDING_MISMATCH')
    installation=request('/repos/'+binding['repo']+'/installation',assertion)
    if installation['id']!=binding['installation_id'] or installation['app_id']!=binding['app_id']:
        raise ValueError('INSTALLATION_BINDING_MISMATCH')
    if a.mode=='probe':
        print(json.dumps({'status':'READY','app_identity_bound':True,'installation_bound':True,'repo':binding['repo'],'root_custody':'HOST_CATALOG','secret_output':'NONE'}))
        return
    token=request('/app/installations/'+str(binding['installation_id'])+'/access_tokens',assertion,
        {'repository_ids':[binding['repo_id']],'permissions':{'contents':'write','issues':'write'}})
    if (token['permissions'].get('contents')!='write' or token['permissions'].get('issues')!='write'
        or set(token['permissions'])-{'contents','issues','metadata'}):
        raise ValueError('TOKEN_PERMISSION_MISMATCH')
    repos=token.get('repositories')
    if repos is not None:
        if {r['id'] for r in repos}!={binding['repo_id']}:
            raise ValueError('TOKEN_SCOPE_MISMATCH')
    inventory=request('/installation/repositories?per_page=100',token['token'])
    if inventory['total_count']!=1 or {r['id'] for r in inventory['repositories']}!={binding['repo_id']}:
        raise ValueError('TOKEN_REPOSITORY_SCOPE_MISMATCH')
    target=Path(a.directory)
    if not target.is_dir() or Path(binding['private_key_ref']).resolve().is_relative_to(target.resolve()):
        raise ValueError('PROTECTED_PROJECTION_DIRECTORY_REQUIRED')
    projection={'token':token['token'],'expires_at':token['expires_at'],'repo':binding['repo'],
                'repo_id':binding['repo_id'],'work':binding['work'],'generation':a.generation,
                'permissions':{'contents':'write','issues':'write'}}
    temporary=target/('credential.json.new-'+a.generation)
    temporary.write_text(json.dumps(projection),encoding='utf-8')
    os.replace(temporary,target/'credential.json')
    print(json.dumps({'status':'PROJECTED','repo':binding['repo'],'generation':a.generation,
                      'expires_at':token['expires_at'],'secret_output':'NONE'}))

if __name__=='__main__':
    try:
        main()
    except urllib.error.HTTPError as e:
        print(json.dumps({'status':'FAILED','category':'GITHUB_HTTP_'+str(e.code),'secret_output':'NONE'}))
        raise SystemExit(2)
    except Exception as e:
        print(json.dumps({'status':'FAILED','category':type(e).__name__,'secret_output':'NONE'}))
        raise SystemExit(2)
