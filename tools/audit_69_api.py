"""Non-normative read-only public API probes for #69; requires authenticated gh.
Run tools/audit_69.py --output docs/research/astra-audit-69/evidence first.
No token values or private resources are read or exported.
"""
import argparse,datetime,json,pathlib,subprocess,re,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=pathlib.Path,default=ROOT/'docs/research/astra-audit-69/evidence',help='Receipt directory containing the frozen inventory.json; use a separate directory to preserve earlier observations')
out=parser.parse_args().output
def gh(*args):
 p=subprocess.run(['gh',*args],capture_output=True,text=True,encoding='utf-8');
 if p.returncode and 'HTTP 304' not in p.stderr: raise RuntimeError(p.stderr)
 return p.stdout
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
rest=[]; pages=[]; page=1
while True:
 d=json.loads(gh('api',f'repos/youling/ai-use/labels?per_page=2&page={page}'));rest.extend(x['node_id'] for x in d);pages.append(len(d))
 if len(d)<2:break
 page+=1
 if page>20:raise RuntimeError('bounded page budget exceeded; incomplete')
q='query($after:String) { repository(owner:"youling",name:"ai-use") { labels(first:2,after:$after) { totalCount nodes { id } pageInfo { hasNextPage endCursor } } } }'
g=[]; gp=[];cursor=None
while True:
 args=['api','graphql','-f','query='+q]
 if cursor:args+=['-f','after='+cursor]
 d=json.loads(gh(*args))['data']['repository']['labels'];g.extend(x['id'] for x in d['nodes']);gp.append({'count':len(d['nodes']),'hasNextPage':d['pageInfo']['hasNextPage']})
 if not d['pageInfo']['hasNextPage']:break
 cursor=d['pageInfo']['endCursor']
 if len(gp)>20:raise RuntimeError('bounded cursor budget exceeded; incomplete')
assert len(rest)==len(set(rest))==len(g)==d['totalCount'] and set(rest)==set(g)
h=gh('api','repos/youling/ai-use','--include');etag=re.search(r'(?im)^etag:\s*(.+)$',h).group(1).strip()
conditional=gh('api','repos/youling/ai-use','--include','-H','If-None-Match: '+etag)
statuses=re.findall(r'HTTP/\S+\s+(\d+)',conditional);assert statuses[-1]=='304'
search=json.loads(gh('api','-X','GET','search/code','-f','q="Capability != Authority" repo:youling/ai-use','-f','per_page=100'))
tree=json.loads(gh('api','repos/youling/ai-use/git/trees/345184f19bc5e1546c86e6c9e234d5c653437747?recursive=1'));inventory=json.loads((out/'inventory.json').read_text(encoding='utf-8'))
api_blobs={(x['path'],x['sha']) for x in tree['tree'] if x['type']=='blob'}
assert not tree['truncated'] and api_blobs=={(x['path'],x['blob_sha']) for x in inventory}
result={'schema_version':'1.0.0','started_at':start,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tree':{'evidence_class':'MEASURED','truncated':tree['truncated'],'blob_count':len(api_blobs),'matches_local_git':True},'pagination':{'evidence_class':'REAL_REPO_CANARY','scope':'public repository labels only','rest_pages':pages,'graphql_pages':gp,'count':len(rest),'ids_match':True,'negative_first_page_is_complete':len(rest)==pages[0],'first_page_size':pages[0],'limits':'Small stable collection; no concurrent mutation/rate-limit recovery/private ACL coverage'},'etag':{'evidence_class':'REAL_REPO_CANARY','conditional_http':int(statuses[-1]),'validator_sha256':hashlib.sha256(etag.encode()).hexdigest(),'limits':'One identical authenticated repository metadata GET; not universal cache freshness proof'},'code_search':{'evidence_class':'OBSERVED_AVAILABLE','total_count':search['total_count'],'incomplete_results':search['incomplete_results'],'returned':len(search['items']),'paths':[x['path'] for x in search['items']],'limits':'Search index is a discovery aid, not exact Git tree or complete semantic inventory'}}
(out/'api-canaries.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result,ensure_ascii=False))
