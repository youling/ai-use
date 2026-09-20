"""Non-normative, offline inventory of an exact Git revision for issue #69.

No repository files are executed. Bytes come from Git blobs (not checkout EOLs).
Markdown links and backtick path mentions are separate, deliberately limited scans.
This does not prove semantic consistency, complete navigation or absence of secrets.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import posixpath
import re
import subprocess
import urllib.parse

BASE = '345184f19bc5e1546c86e6c9e234d5c653437747'
NAV = {'README.md', 'START_HERE.md', 'NAMESPACE.md', 'READING_MAP.md'}
HIST = {'docs/DeepSeekPP-github-mcp-usage.md', 'docs/issue-26-mcp-injection-truncation-root-cause.md', 'human/DEPOSITOR_PROMPT_v0.1.md'}

def git(*args):
    return subprocess.check_output(['git', *args])

def classify(path):
    if path == 'AGENTS.md': return 'L0_KERNEL'
    if path in HIST or path.startswith('90_HISTORY/'): return 'L3_HISTORY'
    if '/tests/' in path or path == '40_GUIDES/PUBLIC_COLD_START_CHECKLIST.md': return 'L2_TEST_REFERENCE'
    if path in NAV or path.endswith('/README.md'): return 'NAVIGATION_MIXED'
    if path.endswith('.md'): return 'L2_NORMATIVE_OR_PLAYBOOK'
    return 'LICENSE_OR_OTHER'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--ref',default=BASE); ap.add_argument('--output',default='audit-output'); a=ap.parse_args()
    ref=git('rev-parse', a.ref+'^{commit}').decode().strip()
    rows=[]; content={}; tree=git('ls-tree','-r','-z',ref).split(b'\0')
    for entry in tree:
        if not entry: continue
        meta,name=entry.split(b'\t',1); mode,kind,oid=meta.decode().split(); path=name.decode()
        if kind != 'blob': raise ValueError('unsupported non-blob tree entry')
        b=git('cat-file','blob',oid); t=b.decode('utf-8'); content[path]=t
        rows.append({'path':path,'blob_sha':oid,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'characters':len(t),'lines':len(t.splitlines()),'class':classify(path),'version_headers':re.findall(r'^.*(?:Version:|Version\*\*|版本[:：]|ai-use v|Doctrine v).*$',t,re.M)[:5]})
    files=set(content); links=[]; mentions=[]; phrases=collections.defaultdict(set)
    def target(source,raw):
        v=urllib.parse.urlsplit(raw)
        if v.scheme or v.netloc or raw.startswith('#'): return None
        return posixpath.normpath(posixpath.join(posixpath.dirname(source),urllib.parse.unquote(v.path)))
    for p,t in content.items():
        if not p.endswith('.md'): continue
        # Only actual Markdown links outside fenced examples are counted as links.
        nofence=re.sub(r'(?ms)^(```|~~~).*?^\1[^\n]*', '', t)
        for m in re.finditer(r'\[[^\]\n]*\]\(([^\s)]+)(?:\s+[^)]*)?\)',nofence):
            raw=m.group(1).strip('<>'); dest=target(p,raw)
            if dest is None: continue
            exists=dest in files or any(f.startswith(dest.rstrip('/')+'/') for f in files)
            links.append({'source':p,'target':raw,'resolved':dest,'exists':exists})
        for raw in re.findall(r'`([^`\n]+\.md)`',nofence):
            if any(x in raw for x in ('<','>','*','|')): continue
            dest=target(p,raw)
            if dest is None: continue
            mentions.append({'source':p,'target':raw,'relative_exists':dest in files,'root_exists':raw in files})
        for line in nofence.splitlines():
            normalized=re.sub(r'\s+',' ',line.strip())
            if len(normalized)>=45 and not normalized.startswith('|'): phrases[normalized].add(p)
    edges=collections.defaultdict(set)
    for x in links:
        if x['exists'] and x['resolved'] in files: edges[x['source']].add(x['resolved'])
    for x in mentions:
        dest=target(x['source'],x['target'])
        if x['relative_exists']: edges[x['source']].add(dest)
        elif x['root_exists']: edges[x['source']].add(x['target'])
    seen=set(); todo=['AGENTS.md','START_HERE.md','READING_MAP.md','NAMESPACE.md']
    while todo:
        p=todo.pop()
        if p in seen: continue
        seen.add(p); todo.extend(edges[p]-seen)
    route=['AGENTS.md','NAMESPACE.md','READING_MAP.md']
    paths={'kernel_only':route[:1],'kernel_and_router':route,'fresh_executor':route+['10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md','docs/AGENT_INTERFACE.md'],'material_architect':route+['10_BOOT/BOOTSTRAP_CHECK_PROTOCOL.md','docs/AGENT_INTERFACE.md','docs/ARCHITECT_RECONNAISSANCE.md','CONSTITUTION.md','30_PROTOCOLS/CHANGE_LIFECYCLE.md']}
    lookup={r['path']:r for r in rows}
    stats={'schema_version':'1.0.0','evidence_class':'MEASURED','source_revision':ref,'method':'Git blob bytes; manual file-role rubric; syntactic references; no model token counter','file_count':len(rows),'markdown_count':sum(p.endswith('.md') for p in files),'total_bytes':sum(r['bytes'] for r in rows),'class_counts':dict(collections.Counter(r['class'] for r in rows)),'markdown_links':len(links),'broken_markdown_links':[x for x in links if not x['exists']],'path_mentions':len(mentions),'unresolved_path_mentions':[x for x in mentions if not x['relative_exists'] and not x['root_exists']],'reachable_files':len(seen),'not_reached':sorted(files-seen),'exact_duplicate_lines':[{'text':line,'files':sorted(fs)} for line,fs in phrases.items() if len(fs)>1],'reading_paths':{k:{'files':v,'file_count':len(v),'bytes':sum(lookup[p]['bytes'] for p in v),'characters':sum(lookup[p]['characters'] for p in v),'limits':'whole-file upper-bound scenario, excludes owner-local rules and Work Order; not a measured fresh-agent run'} for k,v in paths.items()},'limits':['No anchor validation','Backtick mentions may be illustrative/root-relative','Reachability is not mandatory reading','Historical documents may include former normative text','No semantic or secret-clearance verdict']}
    out=pathlib.Path(a.output); out.mkdir(parents=True,exist_ok=True)
    for name,data in [('inventory',rows),('measurements',stats),('links',links)]:
        (out/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:stats[k] for k in ['source_revision','file_count','markdown_count','total_bytes','class_counts','markdown_links','reachable_files']},ensure_ascii=False))

if __name__=='__main__': main()
