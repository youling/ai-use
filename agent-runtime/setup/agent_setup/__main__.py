"""Noninteractive phase CLI and lazy Textual entrypoint."""
import argparse
import json
from pathlib import Path
import sys
from .engine import SetupEngine,FixtureAdapter,SetupError,atomic_json,safe_path
from .windows import WindowsAdapter

def main():
    parser=argparse.ArgumentParser(description='Agent Runtime setup (probe/dry-run first)')
    parser.add_argument('mode',choices=['cli','tui'])
    parser.add_argument('phase',nargs='?',default='probe',choices=['probe','plan','apply','verify','repair','rollback'])
    parser.add_argument('--fixture');parser.add_argument('--sandbox');parser.add_argument('--plan');parser.add_argument('--output')
    parser.add_argument('--host-authorized',action='store_true');parser.add_argument('--approve',action='store_true')
    parser.add_argument('--runtime',action='store_true');parser.add_argument('--github-ref',default='');parser.add_argument('--helper',default='')
    parser.add_argument('--model-ref',default='');parser.add_argument('--free-route',action='store_true');parser.add_argument('--locale',default='zh',choices=['zh','en'])
    parser.add_argument('--github-work',default='');parser.add_argument('--approve-helper',action='store_true');parser.add_argument('--authorize-github-work',action='store_true')
    parser.add_argument('--durable-destination',default='');parser.add_argument('--authorize-durable',action='store_true');parser.add_argument('--require-recovery',action='store_true')
    args=parser.parse_args()
    if args.fixture:
        sandbox=safe_path(args.sandbox or str(Path.cwd()/'.setup-fixture'))
        marker=safe_path(sandbox/'.fixture-owner')
        if sandbox.exists() and not marker.is_file():raise SetupError('UNOWNED_FIXTURE_SANDBOX')
        sandbox.mkdir(parents=True,exist_ok=True)
        if not marker.exists():
            with marker.open('x',encoding='utf-8') as owner:owner.write('explicit-fixture-sandbox-v1\n')
        data=json.loads(Path(args.fixture).read_text(encoding='utf-8'))
        data=json.loads(json.dumps(data).replace('{sandbox}',sandbox.as_posix()))
        adapter=FixtureAdapter(data,sandbox)
        adapter.validate_owned_path(data['documents'])
        for volume in data.get('volumes',[]):adapter.validate_owned_path(volume['mount'])
        Path(data['documents']).mkdir(parents=True,exist_ok=True)
    else:adapter=WindowsAdapter(apply_authorized=args.host_authorized)
    engine=SetupEngine(adapter)
    if args.mode=='tui':
        from .tui import run_tui
        run_tui(engine,locale=args.locale,host_authorized=args.host_authorized);return
    if args.phase=='probe':result=engine.probe()
    elif args.phase=='plan':result=engine.plan(engine.probe(),overrides={'host_authorized':args.host_authorized,'runtime':args.runtime},
        github={'ref':args.github_ref,'helper':args.helper,'work':args.github_work,'helper_approved':args.approve_helper,'authorized':args.authorize_github_work,'recovery_requested':args.require_recovery},
        model={'ref':args.model_ref,'free_route':args.free_route},durable={'destination':args.durable_destination,'authorized':args.authorize_durable})
    else:
        if not args.plan:raise SetupError('REVIEWED_PLAN_FILE_REQUIRED')
        plan=json.loads(Path(args.plan).read_text(encoding='utf-8'))
        if args.phase in {'apply','rollback'} and not args.host_authorized:raise SetupError('EXPLICIT_HOST_APPROVAL_REQUIRED')
        method=getattr(engine,args.phase)
        result=method(plan,approved=args.approve) if args.phase in {'apply','rollback'} else method(plan)
    if args.output:atomic_json(safe_path(args.output),result)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps({'status':'BLOCKED','reason':str(error) if isinstance(error,SetupError) else type(error).__name__,'raw_error':'SUPPRESSED'}))
        sys.exit(2)
