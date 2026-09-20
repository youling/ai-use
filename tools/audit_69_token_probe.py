"""Bounded GitHub-hosted audit branch token probe; never prints response bodies/token."""
import json, os, pathlib, urllib.error, urllib.request

repo=os.environ['GITHUB_REPOSITORY']; sha=os.environ['GITHUB_SHA']
if repo!='youling/ai-use' or not os.environ['GITHUB_REF'].startswith('refs/heads/audit/astra-69-'):
    raise SystemExit('probe restricted to authorized audit branch push')
def request(path,data=None):
    headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json'}
    req=urllib.request.Request('https://api.github.com/repos/'+repo+path,headers=headers,data=None if data is None else json.dumps(data).encode())
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return r.status
    except urllib.error.HTTPError as e: return e.code
read=request('/contents/AGENTS.md?ref='+sha)
# Target is the synthetic audit head, never main. Unexpected success is observable but harmless.
write=request('/statuses/'+sha,{'state':'success','context':'audit-69/unexpected-token-write','description':'Synthetic negative permission probe unexpectedly wrote status'})
record={'evidence_class':'SYNTHETIC_CANARY','source_head':sha,'read_http':read,'write_status_http':write,'expected':[200,403],'limits':'Only this job token and audit branch; public read does not prove private read; no App/admin/production claim'}
pathlib.Path('audit-output/token-probe.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record)); assert (read,write)==(200,403), 'permission boundary differed'
