"""Read-only frozen-doc reader with append-only measurement receipts (Python stdlib)."""
import argparse, datetime, hashlib, json, pathlib

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',required=True,type=pathlib.Path)
parser.add_argument('--log',required=True,type=pathlib.Path)
sub=parser.add_subparsers(dest='command',required=True)
ls=sub.add_parser('list');ls.add_argument('prefix',nargs='?',default='')
read=sub.add_parser('read');read.add_argument('path');read.add_argument('--start',type=int,default=1);read.add_argument('--end',type=int)
sub.add_parser('summary')
args=parser.parse_args();root=args.root.resolve();log=args.log.resolve()
assert root.is_dir()

def record(event):
    log.parent.mkdir(parents=True,exist_ok=True)
    event['observed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with log.open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')

def target(path):
    p=(root/path).resolve()
    if not p.is_relative_to(root) or '.git' in p.relative_to(root).parts:raise ValueError('outside frozen document surface')
    return p

if args.command=='list':
    p=target(args.prefix)
    paths=sorted(x.relative_to(root).as_posix() for x in p.rglob('*') if x.is_file() and '.git' not in x.parts)
    text='\n'.join(paths)+'\n'
    record({'action':'list','prefix':args.prefix,'paths_returned':len(paths),'metadata_bytes':len(text.encode('utf-8'))})
    print(text,end='')
elif args.command=='read':
    p=target(args.path);raw=p.read_bytes();lines=raw.splitlines(keepends=True)
    end=args.end or len(lines)
    if not 1<=args.start<=end<=len(lines):raise ValueError('invalid exact line range')
    selected=b''.join(lines[args.start-1:end]);text=selected.decode('utf-8')
    record({'action':'read','path':p.relative_to(root).as_posix(),'start':args.start,'end':end,'file_bytes':len(raw),'bytes_read':len(selected),'file_sha256':hashlib.sha256(raw).hexdigest()})
    print(text,end='')
else:
    events=[json.loads(line) for line in log.read_text(encoding='utf-8').splitlines()] if log.exists() else []
    reads=[e for e in events if e['action']=='read'];ranges={}
    for e in reads:ranges.setdefault(e['path'],set()).update(range(e['start']-1,e['end']))
    unique_bytes=sum(sum(len(line) for i,line in enumerate(target(path).read_bytes().splitlines(keepends=True)) if i in indices) for path,indices in ranges.items())
    print(json.dumps({'files_read':list(ranges),'file_count':len(ranges),'read_operations':len(reads),'bytes_read_including_repeats':sum(e['bytes_read'] for e in reads),'unique_source_bytes_read':unique_bytes,'list_metadata_bytes':sum(e.get('metadata_bytes',0) for e in events),'limits':'UTF-8 document bytes, not tokens/time, and excludes task seed, instructions, tool envelopes, model reasoning and output.'},ensure_ascii=False,indent=2))
