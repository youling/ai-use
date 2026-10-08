"""Probe/plan/apply/verify/repair transactions. No Textual or credential values."""
from __future__ import annotations
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import uuid
import yaml

IMAGE='ghcr.io/youling/opencode-foreman@sha256:fa92f37752ff6132b161ed4c2563897c94b014ab70d650846dcb09f354f55261'
SCHEMA='1.0.0'
DOMAINS=('Execution','Workspace','Config','State','Cache','Temp','Secrets')
SECRET_PATTERN=re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{30,}|(?i:github_pat_)|sk-proj-[A-Za-z0-9_-]{30,}|(?im:^\s*(?:token|password|api_key|private_key|secret_value)\s*:)')

class SetupError(Exception):
    """Only stable codes reach UI/logs; never interpolate external exceptions."""
    def __init__(self,code,*,conflicts=None,metadata_errors=None):
        super().__init__(code)
        self.conflicts=conflicts or []
        self.metadata_errors=metadata_errors or []

ROOT_ROLES=('workspace','config','cache','temp')
METADATA_REASONS={'EXPECTED_MAPPING','INVENTORY_FLAG_TYPE','UNKNOWN_ROLE','DIRECTION_FIELDS_REQUIRED','PATH_TYPE',
    'UNKNOWN_FIELD','PATH_REQUIRED','OWNER_TYPE','RELOCATABLE_TYPE','EXISTS_TYPE','REASON_TYPE','VERSION_UNSUPPORTED',
    'UNSAFE_CONTEXT','UNREADABLE_OR_INVALID_CONTEXT','UNSAFE_PATH','PATH_NOT_ABSOLUTE','SENSITIVE_VALUE','POLICY_SENTINEL_CLASSIFICATION'}

def metadata_diagnostics(value):
    if not isinstance(value,list):return [{'role':'context','reason':'UNSAFE_CONTEXT'}]
    result=[]
    for entry in value[:8]:
        if (isinstance(entry,dict) and isinstance(entry.get('role'),str) and entry.get('role') in (*ROOT_ROLES,'state','exchange','context')
            and isinstance(entry.get('reason'),str) and entry.get('reason') in METADATA_REASONS):result.append({'role':entry['role'],'reason':entry['reason']})
        else:result.append({'role':'context','reason':'UNSAFE_CONTEXT'})
    return result

def normalize_existing_roots(value):
    """Canonical V1 plus the old Boolean inventory flag; no guessed legacy aliases."""
    def invalid(role,reason):
        raise SetupError('EXISTING_ROOT_METADATA_INVALID',metadata_errors=[{'role':role,'reason':reason}])
    if not isinstance(value,dict):invalid('context','EXPECTED_MAPPING')
    result={}
    for role,entry in value.items():
        if role=='host_agent':
            if type(entry) is not bool:invalid('context','INVENTORY_FLAG_TYPE')
            continue # Presence is metadata, never a semantic root or ownership proof.
        if role not in (*ROOT_ROLES,'state','exchange'):invalid('context','UNKNOWN_ROLE')
        if not isinstance(entry,dict):invalid(role,'EXPECTED_MAPPING')
        if role=='exchange':
            if set(entry)!={'in','out'}:invalid(role,'DIRECTION_FIELDS_REQUIRED')
            if any(not isinstance(path,str) or not path for path in entry.values()):invalid(role,'PATH_TYPE')
        else:
            if set(entry)-{'path','owner','relocatable','reason','exists'}:invalid(role,'UNKNOWN_FIELD')
            if not isinstance(entry.get('path'),str) or not entry['path']:invalid(role,'PATH_REQUIRED')
            if 'owner' in entry and (not isinstance(entry['owner'],str) or not entry['owner']):invalid(role,'OWNER_TYPE')
            if 'relocatable' in entry and type(entry['relocatable']) is not bool:invalid(role,'RELOCATABLE_TYPE')
            if 'exists' in entry and type(entry['exists']) is not bool:invalid(role,'EXISTS_TYPE')
            if 'reason' in entry and not isinstance(entry['reason'],str):invalid(role,'REASON_TYPE')
        if SECRET_PATTERN.search(json.dumps(entry)):invalid(role,'SENSITIVE_VALUE')
        for path in entry.values() if role=='exchange' else [entry['path']]:
            if role=='state' and path=='NATIVE_VENDOR_STATE':
                if entry.get('owner')!='VENDOR_OWNED' or entry.get('relocatable') is not False:invalid(role,'POLICY_SENTINEL_CLASSIFICATION')
                continue # Emitted V1 policy sentinel, not a cwd path.
            if not Path(path).is_absolute():invalid(role,'PATH_NOT_ABSOLUTE')
            try:safe_path(path)
            except SetupError:invalid(role,'UNSAFE_PATH')
        result[role]=copy.deepcopy(entry)
    return result

def root_conflicts(paths,sources):
    """Native resolved paths stay local; diagnostics contain only finite role metadata."""
    conflicts=[]
    for i,left in enumerate(ROOT_ROLES):
        a=safe_path(paths[left])
        for right in ROOT_ROLES[i+1:]:
            b=safe_path(paths[right])
            relation='SAME_DIRECTORY' if a==b else 'CONTAINS' if a.is_relative_to(b) or b.is_relative_to(a) else None
            if relation:
                conflicts.append({'roles':[left,right],'sources':[sources[left],sources[right]],'relation':relation,
                    'action':'OWNER_REVIEW_EXISTING_ROOTS' if 'EXISTING_CONTEXT' in (sources[left],sources[right]) else 'REVIEW_SEPARATE_SCOPED_ROOTS'})
    return conflicts

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None

def safe_path(value):
    text=str(value)
    if SECRET_PATTERN.search(text):raise SetupError('REFERENCE_ONLY_NO_SECRET_VALUE')
    if not text or any(c in text for c in '\r\n\x00,') or text.startswith(('\\\\','//')):
        raise SetupError('UNSAFE_PATH')
    if ':' in text and not re.fullmatch(r'[A-Za-z]:[/\\][^:]*',text):
        raise SetupError('PATH_STREAM_DENIED')
    p=Path(text).absolute()
    if '..' in Path(text).parts or p==p.anchor or p==Path.home() or p.parent==p:
        raise SetupError('UNSAFE_ROOT')
    for item in (p,*p.parents):
        if item.is_symlink() or (item.exists() and getattr(item.lstat(),'st_file_attributes',0)&0x400):
            raise SetupError('REPARSE_PATH_DENIED')
    return p.resolve()

def reference(value):
    value=str(value or '')
    if not value:return ''
    if SECRET_PATTERN.search(value) or re.search(r'(?i)(?:gh[pousr]_|sk-|-----BEGIN|password=|token=)',value) or not re.fullmatch(r'[A-Za-z0-9_.:/#-]{1,256}',value):
        raise SetupError('REFERENCE_ONLY_NO_SECRET_VALUE')
    return value

def atomic_json(path,value):
    if SECRET_PATTERN.search(json.dumps(value)):raise SetupError('REFERENCE_ONLY_NO_SECRET_VALUE')
    path=safe_path(path)
    temporary=path.with_name(path.name+'.new-'+uuid.uuid4().hex)
    with temporary.open('x',encoding='utf-8',newline='\n') as out:
        json.dump(value,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
    os.replace(temporary,path)

def version_ok(value,minimum):
    match=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)(?:\.\d+)?',str(value or ''))
    return bool(match and tuple(map(int,match.groups()))>=minimum)

def bound_root_owner(path):
    """A marker needs the same exact root/attempt/current owned journal."""
    path=safe_path(path);marker=safe_path(path/'.agent-runtime-setup-owner.json')
    if not marker.is_file():return False
    try:
        value=json.loads(marker.read_text(encoding='utf-8'))
        if (value.get('schema')!=SCHEMA or value.get('owner')!='AGENT_RUNTIME_SETUP'
            or value.get('root')!=str(path) or not re.fullmatch(r'[a-f0-9]{32}',value.get('attempt',''))
            or not re.fullmatch(r'[a-f0-9]{64}',value.get('install_binding',''))):return False
        control=safe_path(Path(value['config_root'])/'.agent-runtime-setup')
        owner=json.loads(safe_path(control/'owner.json').read_text(encoding='utf-8'))
        receipt=json.loads(safe_path(control/'receipt.json').read_text(encoding='utf-8'))
        return (owner.get('schema')==SCHEMA and owner.get('install_binding')==value['install_binding']
            and receipt.get('schema')==SCHEMA and receipt.get('install_binding')==value['install_binding']
            and receipt.get('attempt')==value['attempt'] and str(path) in receipt.get('created_roots',[])
            and receipt.get('status') in {'APPLYING','INTERRUPTED','APPLIED'})
    except (KeyError,ValueError,TypeError,OSError):return False

class FixtureAdapter:
    """Explicit fixture transport; filesystem writes stay in fixture sandbox."""
    can_apply=True
    fixture=True
    def __init__(self,data,sandbox):
        self.data=copy.deepcopy(data);self.sandbox=safe_path(sandbox)
    def probe(self):return copy.deepcopy(self.data)
    def validate_owned_path(self,path):
        if not safe_path(path).is_relative_to(self.sandbox):raise SetupError('FIXTURE_ESCAPE')
    def pull_image(self,image):
        if self.data.get('network_interruption'):raise SetupError('NETWORK_INTERRUPTED')
        return {'state':'PASS','manifest_digest':image.split('@')[1],'config_id':'sha256:'+'a'*64}
    def start_runtime(self,plan,host_path):
        return {'state':'NOT_AUTHORIZED','reason':'Fixture does not start real runtime'}
    def verify_runtime(self,plan):
        return {'state':'NOT_AUTHORIZED','reason':'Fixture is not authenticated runtime proof'}

class SetupEngine:
    def __init__(self,adapter):self.adapter=adapter
    def discover_credentials(self):
        """Discovery is metadata only; a login candidate is never runtime authority."""
        value=self.adapter.discover_credentials() if hasattr(self.adapter,'discover_credentials') else {
            kind:{'state':'REUSE_NOT_SUPPORTED','reason':'Owner-approved connection adapter required'} for kind in ('github','model')}
        return self._credential_metadata(value)

    def connect_credential(self,kind,mode,approved=False):
        if kind not in {'github','model'} or mode not in {'auto','manual','skip'}:raise SetupError('CREDENTIAL_SELECTION_INVALID')
        if mode=='skip':return {'state':'SKIPPED','reason':'May connect later; no runtime authorization granted'}
        if not approved:raise SetupError('CREDENTIAL_CONNECTION_APPROVAL_REQUIRED')
        value=self.adapter.connect_credential(kind,mode,approved=True) if hasattr(self.adapter,'connect_credential') else {
            'state':'REUSE_NOT_SUPPORTED','reason':'Owner-approved connection adapter required'}
        return self._credential_metadata(value)

    @staticmethod
    def _credential_metadata(value):
        """Bounded allowlisted metadata; arbitrary provider payloads never reach UI."""
        if not isinstance(value,dict):raise SetupError('UNSAFE_CREDENTIAL_METADATA')
        if set(value).issubset({'github','model'}) and value:
            return {kind:SetupEngine._credential_metadata(entry) for kind,entry in value.items()}
        allowed={'state','reason','reason_code','account','provider','label','reusable','next_action','plan_inputs','repo','work','permissions','action','manual_next_action','scope'}
        if set(value)-allowed:raise SetupError('UNSAFE_CREDENTIAL_METADATA')
        states={'AVAILABLE','CONNECTED','CONNECTION_PENDING_PROJECTION','PASS','BLOCKED','NEEDS_CONNECTION','REUSE_NOT_SUPPORTED','NOT_AUTHORIZED','HUMAN_GATE','SKIPPED','MISSING','UNKNOWN'}
        result={}
        for key,item in value.items():
            if key=='state':
                if not isinstance(item,str) or item not in states:raise SetupError('UNSAFE_CREDENTIAL_METADATA')
            elif key=='reusable':
                if type(item) is not bool:raise SetupError('UNSAFE_CREDENTIAL_METADATA')
            elif key=='plan_inputs':
                # No shipping custodian bridge may grant plan authority. A future
                # real bridge needs its own reviewed, scoped translation contract.
                if item!={}:raise SetupError('UNSUPPORTED_CREDENTIAL_PLAN_INPUTS')
            elif key=='permissions' and isinstance(item,dict):
                if set(item)-{'contents','issues'} or any(not isinstance(v,str) or v not in {'read','write','none'} for v in item.values()):raise SetupError('UNSAFE_CREDENTIAL_METADATA')
            elif not isinstance(item,str) or len(item)>256 or any(c in item for c in '\r\n\x00'):
                raise SetupError('UNSAFE_CREDENTIAL_METADATA')
            raw=json.dumps(item)
            if SECRET_PATTERN.search(raw) or re.search(r'(?i)(?:gh[pousr]_|sk-|private_key|access_token|refresh_token|password|api_key)',raw):raise SetupError('UNSAFE_CREDENTIAL_METADATA')
            result[key]=copy.deepcopy(item)
        return result

    def probe(self):
        observation=self.adapter.probe()
        # Adapters return allowlisted metadata only; refuse token-like input data.
        raw=json.dumps(observation)
        if SECRET_PATTERN.search(raw):
            raise SetupError('UNSAFE_PROBE_DATA')
        observation['schema']=SCHEMA
        observation.setdefault('observed_at',dt.datetime.now(dt.timezone.utc).isoformat())
        if observation.get('documents'):
            target=safe_path(observation['documents'])/'HOST_AGENT.md'
            if target.is_file():
                try:
                    content=target.read_text(encoding='utf-8')
                    if SECRET_PATTERN.search(content):raise SetupError('EXISTING_CONTEXT_SECRET_DATA_REFUSED')
                    match=re.search(r'```yaml\s*\n(.*?)\n```',content,re.S)
                    existing=yaml.safe_load(match[1]) if match else {}
                    if not isinstance(existing,dict):raise SetupError('EXISTING_ROOT_METADATA_INVALID',metadata_errors=[{'role':'context','reason':'EXPECTED_MAPPING'}])
                    if existing.get('host_agent_version')!=SCHEMA:raise SetupError('EXISTING_ROOT_METADATA_INVALID',metadata_errors=[{'role':'context','reason':'VERSION_UNSUPPORTED'}])
                    paths=existing.get('paths',{})
                    if not isinstance(paths,dict):raise SetupError('EXISTING_ROOT_METADATA_INVALID',metadata_errors=[{'role':'context','reason':'EXPECTED_MAPPING'}])
                    # Secrets are reference-only context outside root planning.
                    normalized=normalize_existing_roots({k:v for k,v in paths.items() if k!='secrets'})
                    for name,value in normalized.items():
                        if name!='exchange':value['exists']=False if name=='state' and value['path']=='NATIVE_VENDOR_STATE' else Path(value['path']).exists()
                    observation['existing_roots']=normalized
                except SetupError as error:
                    if str(error)=='EXISTING_CONTEXT_SECRET_DATA_REFUSED':raise
                    observation['existing_context_state']='STALE_REQUIRES_OWNER_REPAIR'
                    observation['existing_root_metadata_errors']=error.metadata_errors or [{'role':'context','reason':'UNSAFE_CONTEXT'}]
                except (ValueError,TypeError,AttributeError,KeyError,OSError,yaml.YAMLError):
                    observation['existing_context_state']='STALE_REQUIRES_OWNER_REPAIR'
                    observation['existing_root_metadata_errors']=[{'role':'context','reason':'UNREADABLE_OR_INVALID_CONTEXT'}]
        return observation

    def diagnose_root_plan(self,observation=None,overrides=None):
        """Read-only planning diagnostics: no paths, identities, file contents or writes."""
        try:
            plan=self.plan(observation if observation is not None else self.probe(),overrides=overrides)
            return {'status':plan['status'],'code':'NO_ROOT_OVERLAP','roles':list(ROOT_ROLES),'conflicts':[],
                'host_apply':'NOT_AUTHORIZED','boss_cause':'NOT_DETERMINED'}
        except SetupError as error:
            code=str(error)
            if not re.fullmatch(r'[A-Z][A-Z0-9_]{1,63}',code):code='OPERATION'
            return {'status':'BLOCKED','code':code,'conflicts':error.conflicts,'metadata_errors':error.metadata_errors,
                'host_apply':'NOT_AUTHORIZED','boss_cause':'NOT_DETERMINED'}
        except Exception:
            return {'status':'BLOCKED','code':'OPERATION','conflicts':[],
                'host_apply':'NOT_AUTHORIZED','boss_cause':'NOT_DETERMINED'}

    def propose_isolated_roots(self,observation):
        """Return an unselected new namespace; never mutate or move existing roots."""
        volumes=[v for v in observation.get('volumes',[]) if (v.get('free_bytes') or 0)>=8*1024**3
            and v.get('fs') in {'NTFS','ReFS'} and v.get('mount') and v.get('local',True) is not False
            and str(v.get('bus_type','')).lower() not in {'usb','iscsi','network'}]
        volumes.sort(key=lambda v:(str(v.get('bus_type','')).upper()=='NVME',str(v.get('media_type','')).upper()=='SSD',
            v.get('device_id')==observation.get('wslc_storage_device_id'),(v.get('free_bytes') or 0)/max(v.get('capacity_bytes') or 1,1),v.get('free_bytes',0)),reverse=True)
        if not volumes:raise SetupError('STORAGE_CAPACITY')
        for volume in volumes:
            scope=safe_path(Path(volume['mount'])/('AgentRuntime-Setup-'+uuid.uuid4().hex[:12]))
            try:self.plan(observation,overrides={'isolated_scope':str(scope)})
            except SetupError as error:
                if str(error)=='ISOLATED_SCOPE_OVERLAP':continue
                raise
            return {'isolated_scope':str(scope),'action':'REVIEW_ONLY_NO_HOST_CHANGES'}
        raise SetupError('ISOLATED_SCOPE_OVERLAP')

    def plan(self,observation,overrides=None,github=None,model=None,durable=None):
        overrides=overrides or {};github=github or {};model=model or {};durable=durable or {}
        gates=[]
        def gate(code,ready,reason):gates.append({'code':code,'state':'PASS' if ready else 'BLOCKED','reason':reason})
        gate('WINDOWS_V1',observation.get('platform')=='windows','Windows V1 only; other platform apply is unsupported')
        gate('PYTHON_314',str(observation.get('python_version','')).startswith('3.14.') and observation.get('python_verified') is True,'Verified stable Python 3.14.x; bootstrap never upgrades an unrelated Python')
        gate('WSL_APP_3',version_ok(observation.get('wsl_app_version'),(3,0,0)),'WSL application >=3.0.0, not WSL2/kernel version')
        gate('WSLC',observation.get('wslc_capability',{}).get('state')=='PASS','Actual native WSLC capability must pass; no upgrade/reboot/distro termination')
        gate('CONTEXT_CURRENT',not observation.get('existing_context_state'),'Stale or malformed existing discovery requires owner repair; never silently replace')
        volumes=observation.get('volumes',[])
        viable=[v for v in volumes if (v.get('free_bytes') or 0)>=8*1024**3 and v.get('fs') in {'NTFS','ReFS'} and v.get('mount') and v.get('local',True) is not False and str(v.get('bus_type','')).lower() not in {'usb','iscsi','network'}]
        viable.sort(key=lambda v:(str(v.get('bus_type','')).upper()=='NVME',str(v.get('media_type','')).upper()=='SSD',v.get('device_id')==observation.get('wslc_storage_device_id'),(v.get('free_bytes') or 0)/max(v.get('capacity_bytes') or 1,1),v.get('free_bytes',0)),reverse=True)
        gate('STORAGE_CAPACITY',bool(viable),'At least8GiB headroom on local NTFS/ReFS; respect filesystem and device locality')
        chosen=viable[0] if viable else (volumes[0] if volumes else {'mount':observation.get('documents') or str(Path.cwd())})
        base=Path(chosen['mount'])/'AgentRuntime'
        if observation.get('existing_root_metadata_errors'):
            raise SetupError('EXISTING_ROOT_METADATA_INVALID',metadata_errors=metadata_diagnostics(observation['existing_root_metadata_errors']))
        existing=normalize_existing_roots(observation.get('existing_roots',{}))
        isolated=overrides.get('isolated_scope')
        if isolated:
            base=safe_path(isolated)
            if base.exists():raise SetupError('ISOLATED_SCOPE_ALREADY_EXISTS')
            protected=[old['path'] for name,old in existing.items() if name in (*ROOT_ROLES,'state') and isinstance(old,dict) and old.get('path')]
            if isinstance(existing.get('exchange'),dict):protected.extend(existing['exchange'].values())
            for raw in protected:
                if raw=='NATIVE_VENDOR_STATE':continue
                old_path=safe_path(raw)
                if base==old_path or base.is_relative_to(old_path) or old_path.is_relative_to(base):raise SetupError('ISOLATED_SCOPE_OVERLAP')
        roots={}
        root_sources={}
        for name,leaf in [('workspace','workspaces'),('config','config'),('cache','cache'),('temp','attempts')]:
            old={} if isolated else existing.get(name,{})
            selected=overrides.get(name) or old.get('path') or str(base/leaf)
            root_sources[name]='USER_SELECTION' if overrides.get(name) else 'EXISTING_CONTEXT' if old.get('path') else 'NEW_DEFAULT'
            if old.get('path') and (old.get('exists') or Path(old['path']).exists()) and safe_path(selected)!=safe_path(old['path']):
                raise SetupError('FIRST_INSTALL_NEVER_RELOCATES_EXISTING_DATA')
            path=safe_path(selected)
            if isolated and (not path.is_relative_to(base) or path==base):raise SetupError('ISOLATED_SCOPE_TARGET_ESCAPE')
            if hasattr(self.adapter,'validate_owned_path'):self.adapter.validate_owned_path(path)
            # Parent containment alone does not make an arbitrary existing root owned.
            canonical=observation.get('canonical_classification',{})
            classified=(canonical.get('verified') is True and bool(re.fullmatch(r'[a-f0-9]{64}',str(canonical.get('sha256',''))))
                and canonical.get('sha256')==file_hash(Path(observation['documents'])/'HOST_AGENT.md') and bool(canonical.get('owner_pointer')))
            owner=old.get('owner','UNKNOWN') if classified and not isolated else 'HOST_MANAGED' if not path.exists() else 'UNKNOWN'
            marker=path/'.agent-runtime-setup-owner.json'
            if marker.exists():
                try:
                    owner='HOST_MANAGED' if bound_root_owner(path) else 'UNKNOWN'
                except (ValueError,OSError):raise SetupError('OWNERSHIP_MARKER_INVALID')
            gate('ROOT_'+name.upper(),owner=='HOST_MANAGED','Preserve classified existing roots or create explicitly owned new roots; unknown ownership blocks')
            roots[name]={'path':str(path),'owner':owner,'relocatable':old.get('relocatable',not path.exists()),
                'reason':'NO_MOVE: preserve existing root; ownership still independently verified' if old.get('path') else 'Recommended local NVMe/SSD with capacity headroom; no data migration',
                'existed':path.exists()}
        state=existing.get('state',{'path':observation.get('vendor_state','NATIVE_VENDOR_STATE'),'owner':'VENDOR_OWNED','relocatable':False})
        roots['state']={**state,'reason':'Preserve vendor/native state; never relocate on first install'}
        managed=[safe_path(roots[n]['path']) for n in ('workspace','config','cache','temp')]
        conflicts=root_conflicts({n:roots[n]['path'] for n in ROOT_ROLES},root_sources)
        if conflicts:raise SetupError('ROOT_OVERLAP',conflicts=conflicts)
        for writer in observation.get('active_workloads',[]):
            if isinstance(writer,dict) and writer.get('path'):
                active=safe_path(writer['path'])
                if any(active==p or active.is_relative_to(p) or p.is_relative_to(active) for p in managed):raise SetupError('ACTIVE_WRITER')
            elif writer:gate('ACTIVE_WORKLOAD_UNKNOWN',False,'Unknown active writer requires explicit ownership/quiescence; installer does not stop workloads')
        documents=safe_path(observation.get('documents') or str(Path.cwd()/'unsupported-documents'))
        target=documents/'HOST_AGENT.md'
        old_hash=file_hash(target)
        if target.exists():
            try:
                content=target.read_text(encoding='utf-8')
                if SECRET_PATTERN.search(content):raise SetupError('EXISTING_CONTEXT_SECRET_DATA_REFUSED')
                match=re.search(r'```yaml\s*\n(.*?)\n```',content,re.S)
                value=yaml.safe_load(match[1]) if match else {}
                if value.get('host_agent_version')!=SCHEMA:raise SetupError('EXISTING_HOST_AGENT_REPAIR_REQUIRES_OWNER')
            except (ValueError,TypeError,AttributeError,OSError):raise SetupError('EXISTING_HOST_AGENT_REPAIR_REQUIRES_OWNER')
        gh={key:github.get(key) for key in ('authorized','recovery_requested','helper','helper_approved','repo','work','projection_directory','server_env') if key in github}
        gh['ref']=reference(github.get('ref'))
        gh.setdefault('authorized',False);gh.setdefault('recovery_requested',False)
        gh.setdefault('helper','')
        if gh.get('work'):
            if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*',gh['work']):raise SetupError('WORK_COORDINATE_INVALID')
            gh['repo']=gh['work'].split('#')[0]
        for name in ('helper','projection_directory','server_env'):
            if gh.get(name):gh[name]=str(safe_path(gh[name]))
        mod={'ref':reference(model.get('ref')),'free_route':bool(model.get('free_route',False)),
            'helper':str(safe_path(model['helper'])) if model.get('helper') else '',
            'state':'NOT_AUTHORIZED','reason':'Provider metadata/helper activation has not been verified; free selection is not a price/auth proof'}
        durable_meta={'destination':str(durable.get('destination') or ''),'authorized':bool(durable.get('authorized',False))}
        if durable_meta['destination'] and not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[^\s]*)?',durable_meta['destination']):raise SetupError('DURABLE_DESTINATION_INVALID')
        recovery_authorized=gh['authorized'] and durable_meta['authorized'] and bool(durable_meta['destination'])
        exchange={'in':str(base/'exchange/in'),'out':str(base/'exchange/out')}
        if existing.get('exchange') and not isolated:exchange=copy.deepcopy(existing['exchange'])
        for key in exchange:
            exchange[key]=str(safe_path(exchange[key]))
            if hasattr(self.adapter,'validate_owned_path'):self.adapter.validate_owned_path(exchange[key])
        docs_parent=bool(observation.get('documents')) and documents.exists() and documents.is_dir()
        gate('DOCUMENTS_KNOWN_FOLDER',docs_parent,'Use resolved OS-native Documents; do not invent fallback placement')
        # Bind every selected managed root to its actual volume, including advanced overrides.
        def volume_anchor(mount):
            # Drive roots are read-only inventory anchors, not eligible install
            # destinations. Keep safe_path() root rejection for every managed
            # workspace/config/cache/temp/exchange target.
            raw=str(mount)
            if os.name=='nt' and re.fullmatch(r'[A-Za-z]:[/\\]',raw):
                root=Path(raw)
                if not root.is_absolute() or root.parent!=root:
                    raise SetupError('UNSAFE_VOLUME_ANCHOR')
                if root.is_symlink() or (root.exists() and getattr(root.lstat(),'st_file_attributes',0)&0x400):
                    raise SetupError('REPARSE_PATH_DENIED')
                return root.resolve()
            return safe_path(raw)
        def volume_for(path):
            destination=safe_path(path)
            matches=[v for v in volumes if destination.is_relative_to(volume_anchor(v['mount']))]
            return max(matches,key=lambda v:len(str(v['mount']))) if matches else None
        storage_bindings=[]
        rows=[]
        for name,path in [(n,roots[n]['path']) for n in ('workspace','config','cache','temp')]+[('exchange',exchange['in']),('host_agent',str(target))]:
            volume=volume_for(path)
            if name not in {'host_agent'}:
                gate('PLACEMENT_'+name.upper(),bool(volume and volume in viable),'Selected root needs supported local filesystem and at least 8GiB headroom')
                if volume and volume not in storage_bindings:storage_bindings.append(volume)
            rows.append({'name':name,'path':path,'media_type':volume.get('media_type','UNKNOWN') if volume else 'UNKNOWN',
                'bus_type':volume.get('bus_type','UNKNOWN') if volume else 'UNKNOWN','device_id':volume.get('device_id','UNKNOWN') if volume else 'UNKNOWN',
                'free_bytes':volume.get('free_bytes') if volume else None,'reason':roots[name]['reason'] if name in roots else 'Known Folder discovery; existing hash checked before overwrite' if name=='host_agent' else 'Bound exchange attempt; no native state migration'})
        documents_state='ONEDRIVE_REDIRECTED' if observation.get('documents_onedrive') is True or any(part.lower().startswith('onedrive') for part in documents.parts) else 'NATIVE_KNOWN_FOLDER'
        ready=all(g['state']=='PASS' for g in gates)
        result={'schema':SCHEMA,'status':'READY' if ready else 'BLOCKED','host_authorized':bool(overrides.get('host_authorized',False)),
            'gates':gates,'roots':roots,'exchange':exchange,'documents':str(documents),'host_agent':str(target),
            'expected_host_agent_sha256':old_hash,'github':gh,'model':mod,'durable':durable_meta,'image':IMAGE,
            'storage':chosen,'storage_bindings':storage_bindings,'placement_rows':rows,'documents_state':documents_state,'recovery_authorized':bool(recovery_authorized),'platform':observation.get('platform'),'observed_at':observation['observed_at'],
            'operations':[{'kind':'ENSURE_OWNED_ROOT','path':str(p),'reason':'New/preserved scoped ownership'} for p in managed]+[{'kind':'MATERIALIZE_CONTEXT','path':str(target),'reason':'Known Folder discovery projection'}],
            'domains':{name:({'owner':'VENDOR_OWNED','relocatable':False} if name in {'Execution','State'} else {'owner':'HOST_CUSTODY','reference_only':True} if name=='Secrets' else roots[name.lower()]) for name in DOMAINS},
            'placement':'NO_MOVE','runtime_requested':bool(overrides.get('runtime',False))}
        if isolated:
            result['preserved_existing_roles']=[name for name in (*ROOT_ROLES,'state','exchange') if existing.get(name)]
            result['isolated_scope_reviewed']=str(base)
        # Stable semantic binding excludes observation time; new authority must still be explicit.
        result['install_binding']=digest({'roots':{k:{key:v[key] for key in ('path','owner','relocatable') if key in v} for k,v in roots.items()},'exchange':exchange,'github':gh,'model':mod,'durable':durable_meta,'image':IMAGE})
        run_id=result['install_binding'][:12]
        result['runtime']={'name':'setup-'+run_id,'attempt':str(Path(roots['temp']['path'])/('setup-'+run_id)),
            'incoming':str(Path(exchange['in'])/('setup-'+run_id)),'outgoing':str(Path(exchange['out'])/('setup-'+run_id)),'port':4096}
        gh['durable_destination']=durable_meta['destination']
        result['fingerprint']=digest(result)
        # Interrupted transaction resumes only the full prior reviewed semantics.
        prior=self._control(result)/'plan.json'
        checkpoint=self._control(result)/'receipt.json'
        if prior.is_file() and checkpoint.is_file():
            saved=json.loads(prior.read_text(encoding='utf-8'));state=json.loads(checkpoint.read_text(encoding='utf-8'))
            if state.get('status')=='INTERRUPTED' and saved.get('install_binding')==result['install_binding'] and result['host_authorized']:
                self._validate(saved)
                return saved
        return result

    def _validate(self,plan):
        if SECRET_PATTERN.search(json.dumps(plan)):raise SetupError('REFERENCE_ONLY_NO_SECRET_VALUE')
        original=dict(plan);fingerprint=original.pop('fingerprint',None)
        if fingerprint!=digest(original) or plan.get('schema')!=SCHEMA or plan.get('image')!=IMAGE:raise SetupError('PLAN_DRIFT')
        if plan.get('platform')!='windows' or not self.adapter.can_apply:raise SetupError('UNSUPPORTED_PLATFORM')
        for name in ('workspace','config','cache','temp'):safe_path(plan['roots'][name]['path'])
        for value in plan['exchange'].values():safe_path(value)
        safe_path(plan['host_agent'])
        if hasattr(self.adapter,'validate_owned_path'):
            for value in [plan['host_agent'],*[r['path'] for k,r in plan['roots'].items() if k!='state'],*plan['exchange'].values()]:self.adapter.validate_owned_path(value)

    def _control(self,plan):return safe_path(Path(plan['roots']['config']['path'])/'.agent-runtime-setup')

    def _optional_writeback(self,plan,target,context_hash):
        """Optional private recovery failure cannot erase verified local installation."""
        if not plan.get('recovery_authorized'):
            return {'state':'NOT_AUTHORIZED','reason_code':'DURABLE_OWNER_APPROVAL_REQUIRED'}
        if not hasattr(self.adapter,'writeback_context'):
            return {'state':'BLOCKED','reason_code':'DURABLE_OWNER_ADAPTER_UNAVAILABLE'}
        try:
            proof=self.adapter.writeback_context(plan,target,context_hash)
            if isinstance(proof,dict) and proof.get('state')=='PASS' and proof.get('context_sha256')==context_hash:
                outcome={'state':'PASS','context_sha256':context_hash}
            else:outcome={'state':'BLOCKED','reason_code':'DURABLE_WRITEBACK_NOT_VERIFIED'}
        except Exception:
            outcome={'state':'BLOCKED','reason_code':'DURABLE_WRITEBACK_FAILED_SANITIZED'}
        # Optional remote failure is separable; a changed local projection is a
        # currentness/security drift and must stop before further Host effects.
        if file_hash(target)!=context_hash:raise SetupError('HOST_AGENT_STALE')
        return outcome

    def context(self,plan,config_id=None,readiness=None):
        if SECRET_PATTERN.search(json.dumps(plan)):raise SetupError('REFERENCE_ONLY_NO_SECRET_VALUE')
        readiness=readiness or {}
        enabled=bool(config_id and readiness.get('credentials')=='PASS' and readiness.get('model')=='PASS')
        paths={k:{key:v[key] for key in ('path','owner','relocatable','reason') if key in v} for k,v in plan['roots'].items()}
        paths['exchange']=plan['exchange']
        paths['secrets']={'catalog_ref':'host.native-secret-custody','runtime_root':'/run/secrets','refs':{
            'github_machine':{'ref':plan['github']['ref'] or 'host.github.not-authorized','class':'GITHUB_MACHINE_IDENTITY','custody':'HOST_OWNER','materialize':'EXISTING_APPROVED_HELPER'},
            'model_provider':{'ref':plan['model']['ref'] or 'host.model.not-authorized','class':'MODEL_PROVIDER_AUTH','custody':'HOST_OWNER','materialize':'PUBLIC_PROVIDER_ACTIVATION' if plan['model']['free_route'] else 'EXISTING_APPROVED_HELPER'}}}
        value={'host_agent_version':SCHEMA,'observed_at':plan['observed_at'],
            'durable':{'host_agent_canonical':plan['durable']['destination'] or 'NOT_CONFIGURED_OWNER_SELECTION_REQUIRED','governance':'https://github.com/youling/ai-use'},
            'paths':paths,'domains':plan['domains'],'placement':'NO_MOVE','agents':{'opencode':{
                'enabled':enabled,'readiness':'MODEL_READY' if enabled else 'CONFIGURED_PENDING_AUTH','runtime':'container','image':config_id or IMAGE,
                'oci_manifest':IMAGE,'command':'serve','workspace':'LINUX_NATIVE /workspace','state':'DISPOSABLE_GITHUB_RECOVERY',
                'exchange':plan['exchange'],'github':{'credential_ref':paths['secrets']['refs']['github_machine']['ref'],'recovery_required':True},
                'model_auth':{'credential_ref':paths['secrets']['refs']['model_provider']['ref'],'materialize':'HOST_APPROVED_RUNTIME_PROJECTION'}}}}
        return '# HOST_AGENT resolved projection\n\n```yaml\n'+yaml.safe_dump(value,allow_unicode=True,sort_keys=False)+'```\n'

    def apply(self,plan,approved=False):
        self._validate(plan)
        if not approved or not plan['host_authorized']:raise SetupError('EXPLICIT_HOST_APPROVAL_REQUIRED')
        if plan['status']!='READY':raise SetupError('PREFLIGHT_BLOCKED')
        # Reprobe critical runtime gates immediately before any effect.
        now=self.probe()
        if now.get('platform')!='windows' or not version_ok(now.get('wsl_app_version'),(3,0,0)) or now.get('wslc_capability',{}).get('state')!='PASS':raise SetupError('PREFLIGHT_DRIFT')
        if not now.get('python_verified') or not str(now.get('python_version','')).startswith('3.14.'):raise SetupError('PYTHON_PROVENANCE_DRIFT')
        if any(now.get('active_workloads',[])):raise SetupError('ACTIVE_WORKLOAD_REVIEW_REQUIRED')
        for selected in plan.get('storage_bindings',[plan['storage']]):
            if not any((v.get('free_bytes') or 0)>=8*1024**3 and v.get('device_id')==selected.get('device_id') and v.get('mount')==selected.get('mount') and v.get('fs')==selected.get('fs') for v in now.get('volumes',[])):raise SetupError('STORAGE_PRESSURE_OR_TOPOLOGY_DRIFT')
        root=safe_path(plan['roots']['config']['path'])
        control=self._control(plan)
        if not (control/'receipt.json').exists() and file_hash(plan['host_agent'])!=plan['expected_host_agent_sha256']:raise SetupError('HOST_AGENT_STALE')
        if (control/'apply.lock').exists():raise SetupError('CONCURRENT_ATTEMPT_OR_INTERRUPTED_LOCK')
        if root.exists() and not plan['roots']['config']['existed'] and not bound_root_owner(root):raise SetupError('NEW_ROOT_RACE_OR_UNKNOWN_OWNER')
        control_owner=control/'owner.json'
        if control.exists():
            if not control_owner.is_file() or json.loads(control_owner.read_text(encoding='utf-8')).get('install_binding')!=plan['install_binding']:raise SetupError('CONTROL_OWNERSHIP_UNVERIFIED')
        root_created=False
        if not root.exists():root.mkdir(parents=True);root_created=True
        control.mkdir(exist_ok=True)
        if not control_owner.exists():atomic_json(control_owner,{'schema':SCHEMA,'install_binding':plan['install_binding']})
        lock=control/'apply.lock'
        try:handle=lock.open('x',encoding='utf-8')
        except FileExistsError:raise SetupError('CONCURRENT_ATTEMPT_OR_INTERRUPTED_LOCK')
        try:
            handle.write(json.dumps({'pid':os.getpid(),'fingerprint':plan['fingerprint']}));handle.close()
            receipt_path=control/'receipt.json'
            if receipt_path.exists():
                receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
                if receipt.get('install_binding')==plan['install_binding'] and receipt.get('status')=='APPLIED':return self.verify(plan)
                if receipt.get('status')=='APPLIED':raise SetupError('EXISTING_INSTALL_REVIEW_REQUIRED')
                if receipt.get('fingerprint')!=plan['fingerprint']:raise SetupError('CHECKPOINT_PLAN_MISMATCH')
            else:
                if file_hash(plan['host_agent'])!=plan['expected_host_agent_sha256']:raise SetupError('HOST_AGENT_STALE')
                receipt={'schema':SCHEMA,'fingerprint':plan['fingerprint'],'install_binding':plan['install_binding'],'attempt':uuid.uuid4().hex,'status':'APPLYING',
                    'created_roots':[],'context_before_sha256':plan['expected_host_agent_sha256'],'context_after_sha256':None,
                    'runtime':{'state':'NOT_AUTHORIZED'},'durable':{'state':'NOT_AUTHORIZED' if plan['durable']['destination'] else 'NOT_CONFIGURED'},'image':{'state':'NOT_REQUESTED'}}
                if root_created:receipt['created_roots'].append(str(root))
                atomic_json(receipt_path,receipt)
            atomic_json(control/'plan.json',plan)
            for directory in [*[plan['roots'][n]['path'] for n in ('workspace','config','cache','temp')],*plan['exchange'].values()]:
                p=safe_path(directory)
                if p.exists() and str(p) not in receipt['created_roots'] and directory not in [r['path'] for r in plan['roots'].values() if r.get('existed')]:
                    raise SetupError('NEW_ROOT_RACE_OR_UNKNOWN_OWNER')
                if not p.exists():
                    p.mkdir(parents=True);receipt['created_roots'].append(str(p));atomic_json(receipt_path,receipt)
                if str(p) in receipt['created_roots']:
                    atomic_json(p/'.agent-runtime-setup-owner.json',{'schema':SCHEMA,'owner':'AGENT_RUNTIME_SETUP',
                        'root':str(p),'config_root':str(root),'attempt':receipt['attempt'],'install_binding':plan['install_binding']})
            config_id=None
            config_id=receipt['image'].get('config_id')
            if plan['runtime_requested'] and receipt['image'].get('state')!='PASS':
                pulled=self.adapter.pull_image(IMAGE)
                if pulled.get('state')!='PASS' or pulled.get('manifest_digest')!=IMAGE.split('@')[1]:raise SetupError('IMAGE_DIGEST_NOT_VERIFIED')
                config_id=pulled['config_id'];receipt['image']=pulled;atomic_json(receipt_path,receipt)
            target=safe_path(plan['host_agent'])
            if receipt['context_after_sha256'] is None and receipt.get('context_intended_sha256') and file_hash(target)==receipt['context_intended_sha256']:
                # Reconcile an atomic replacement that finished before checkpoint writeback.
                receipt['context_after_sha256']=receipt['context_intended_sha256'];atomic_json(receipt_path,receipt)
            if receipt['context_after_sha256'] is None:
                if file_hash(target)!=receipt['context_before_sha256']:raise SetupError('HOST_AGENT_STALE')
                readiness=self.adapter.runtime_readiness(plan) if hasattr(self.adapter,'runtime_readiness') and plan['runtime_requested'] else {}
                receipt['readiness']=readiness
                content=self.context(plan,config_id,readiness).encode('utf-8')
                if target.exists():
                    # Nonsecret old context is retained only in owned journal, never secret stores.
                    (control/'HOST_AGENT.previous').write_bytes(target.read_bytes())
                temporary=target.with_name('HOST_AGENT.setup-new')
                receipt['context_intended_sha256']=hashlib.sha256(content).hexdigest();atomic_json(receipt_path,receipt)
                with temporary.open('xb') as output:output.write(content);output.flush();os.fsync(output.fileno())
                os.replace(temporary,target)
                receipt['context_after_sha256']=hashlib.sha256(content).hexdigest();atomic_json(receipt_path,receipt)
            elif file_hash(target)!=receipt['context_after_sha256']:raise SetupError('HOST_AGENT_STALE')
            if plan['durable']['destination']:
                receipt['durable']=self._optional_writeback(plan,target,receipt['context_after_sha256']);atomic_json(receipt_path,receipt)
            if plan['runtime_requested']:
                if not plan['github']['authorized'] or receipt.get('readiness',{}).get('credentials')!='PASS' or receipt.get('readiness',{}).get('model')!='PASS':
                    if receipt['runtime'].get('state') in {'READY','PASS'}:
                        pass # Reconcile the bound prior attempt in verify; never create/start twice.
                    elif hasattr(self.adapter,'start_local_runtime'):
                        for name in ('incoming','outgoing'):
                            attempt=safe_path(plan['runtime'][name])
                            if attempt.exists():raise SetupError('RUNTIME_ATTEMPT_ALREADY_EXISTS_RECONCILE_FIRST')
                            attempt.mkdir(exist_ok=True)
                        receipt['runtime']=self.adapter.start_local_runtime(plan,target)
                        atomic_json(receipt_path,receipt)
                    else:receipt['runtime']={'state':'NOT_AUTHORIZED','reason':'Local scoped-auth adapter unavailable; no GitHub/model authority granted'}
                elif receipt['runtime'].get('state') not in {'READY','PASS'}:
                    incoming=safe_path(plan['runtime']['incoming']);outgoing=safe_path(plan['runtime']['outgoing'])
                    if incoming.exists() or outgoing.exists():raise SetupError('RUNTIME_ATTEMPT_ALREADY_EXISTS_RECONCILE_FIRST')
                    incoming.mkdir(exist_ok=True);outgoing.mkdir(exist_ok=True)
                    import shutil
                    helper_source=Path(__file__).resolve().parents[2]/'conformance/github_credential.py'
                    with (incoming/'github_credential.py').open('xb') as destination:destination.write(helper_source.read_bytes())
                    receipt['runtime']=self.adapter.start_runtime(plan,target)
                    atomic_json(receipt_path,receipt)
                if receipt['runtime'].get('state') not in {'READY','PASS'} and receipt.get('readiness',{}).get('model')=='PASS':
                    # Startup can invalidate earlier readiness. Never leave an
                    # enabled discovery projection after a denied/failed start.
                    if file_hash(target)!=receipt['context_after_sha256']:raise SetupError('HOST_AGENT_STALE')
                    disabled=self.context(plan,config_id,{}).encode('utf-8')
                    temporary=target.with_name('HOST_AGENT.setup-new')
                    with temporary.open('xb') as output:output.write(disabled);output.flush();os.fsync(output.fileno())
                    os.replace(temporary,target)
                    receipt['context_after_sha256']=hashlib.sha256(disabled).hexdigest();receipt['readiness']={}
                    atomic_json(receipt_path,receipt)
                    if plan['durable']['destination']:
                        receipt['durable']=self._optional_writeback(plan,target,receipt['context_after_sha256']);atomic_json(receipt_path,receipt)
            receipt['status']='APPLIED';atomic_json(receipt_path,receipt)
            return self.verify(plan)
        except Exception as error:
            if (control/'receipt.json').exists():
                state=json.loads((control/'receipt.json').read_text(encoding='utf-8'));state['status']='INTERRUPTED';state['failure']=str(error) if isinstance(error,SetupError) else type(error).__name__;atomic_json(control/'receipt.json',state)
            raise SetupError(str(error) if isinstance(error,SetupError) else 'APPLY_FAILED_SANITIZED') from None
        finally:
            handle.close()
            if lock.exists():lock.unlink()

    def verify(self,plan):
        self._validate(plan)
        checkpoint=self._control(plan)/'receipt.json'
        if not checkpoint.exists():return {'status':'NOT_APPLIED','checks':[],'reason':'Plan only; no Host install evidence'}
        receipt=json.loads(checkpoint.read_text(encoding='utf-8'))
        if receipt.get('install_binding')!=plan['install_binding']:raise SetupError('CHECKPOINT_PLAN_MISMATCH')
        if receipt.get('status')!='ROLLED_BACK' and any(not bound_root_owner(raw) for raw in receipt.get('created_roots',[])):
            raise SetupError('ROOT_OWNERSHIP_DRIFT')
        context=file_hash(plan['host_agent'])==receipt['context_after_sha256'] and receipt['context_after_sha256'] is not None
        runtime=receipt['runtime']
        current_readiness=self.adapter.runtime_readiness(plan) if hasattr(self.adapter,'runtime_readiness') else {}
        if runtime.get('state') in {'PASS','READY'} and not getattr(self.adapter,'fixture',False):
            verify_options={'expected_config_id':receipt['image']['config_id']}
            if runtime.get('local_only') is True:
                verify_options.update(expected_local=True,expected_mount_sources={
                    '/host-context':str(Path(plan['runtime']['attempt'])/'context'),
                    '/exchange/in':plan['runtime']['incoming'],'/exchange/out':plan['runtime']['outgoing']})
            runtime=self.adapter.verify_runtime(plan['runtime']['name'],Path(plan['host_agent']),**verify_options)
            if runtime.get('state')=='PASS' and plan['github'].get('helper_approved'):
                proof=self.adapter.helper_status(plan['github']['helper'],approved=True,operation='verify')
                if proof.get('state')=='PASS' and proof.get('repo')==plan['github'].get('repo') and proof.get('work')==plan['github'].get('work') and proof.get('context_sha256')==receipt['context_after_sha256']:
                    for key,source in {'github_read':'github_read','github_write':'github_write','github_fresh_recovery':'fresh_recovery','server_authenticated':'authenticated_api'}.items():
                        runtime[key]='PASS' if proof.get(source) is True else 'BLOCKED' if proof.get(source) is False else 'NOT_AUTHORIZED'
        checks={'local_context':'PASS' if context else 'BLOCKED','durable_context':receipt['durable']['state'],
            'credentials':'PASS' if current_readiness.get('credentials')=='PASS' else 'NOT_AUTHORIZED',
            'image':receipt['image']['state'],'runtime':runtime.get('state','UNKNOWN'),
            'github_fresh_recovery':runtime.get('github_fresh_recovery','NOT_AUTHORIZED'),
            'github_read':runtime.get('github_read','NOT_AUTHORIZED'),'github_write':runtime.get('github_write','NOT_AUTHORIZED'),
            'server_authenticated':runtime.get('server_authenticated','NOT_AUTHORIZED'),
            'model':'PASS' if current_readiness.get('model')=='PASS' else 'NOT_AUTHORIZED','workspace':'LINUX_NATIVE' if runtime.get('state')=='PASS' else 'NOT_STARTED'}
        github_ready=context and runtime.get('state')=='PASS' and receipt['durable']['state']=='PASS' and all(checks[k]=='PASS' for k in ('credentials','github_fresh_recovery','github_read','github_write','server_authenticated'))
        status='READY' if github_ready and checks['model']=='PASS' else 'RUNTIME_GITHUB_READY' if github_ready else 'CONFIGURED_PENDING_AUTH' if context else 'BLOCKED'
        capabilities={
            'local_install':{'state':'PASS' if context and checks['image']=='PASS' and checks['runtime']=='PASS' and checks['server_authenticated']=='PASS' else 'NOT_VERIFIED','reason':'Exact image, owned container, nonroot context and scoped loopback authentication required'},
            'github':{'state':'PASS' if all(checks[k]=='PASS' for k in ('credentials','github_read','github_write')) else 'NEEDS_CONNECTION','reason':'Runtime read/write and current credential proof required'},
            'model':{'state':checks['model'],'reason':'Current provider verification required; past receipts are insufficient'},
            'fresh_recovery':{'state':'PASS' if github_ready else 'NOT_VERIFIED','reason':'Private durable owner writeback and second fresh container proof required'}}
        return {'status':status,'capabilities':capabilities,
            'checks':checks,'reason':'No complete recovery claim without authenticated durable writeback/fresh-runtime proof',
            'host_agent_sha256':receipt['context_after_sha256'],'receipt':str(checkpoint)}

    def repair(self,plan):
        self._validate(plan)
        checkpoint=self._control(plan)/'receipt.json'
        state=json.loads(checkpoint.read_text(encoding='utf-8')) if checkpoint.exists() else {}
        return {'status':'REVIEW_REQUIRED','reason':'Reprobe, preserve native/vendor/secret state; approve retry of this exact plan or owned rollback',
            'checkpoint_status':state.get('status','NONE'),'operations':[],
            'reviewed_plan':str(self._control(plan)/'plan.json') if (self._control(plan)/'plan.json').is_file() else None,
            'lock_present':(self._control(plan)/'apply.lock').exists(),'reboot_or_upgrade':'NOT_AUTOMATIC'}

    def rollback(self,plan,approved=False):
        self._validate(plan)
        if not approved or not plan['host_authorized']:raise SetupError('EXPLICIT_HOST_APPROVAL_REQUIRED')
        control=self._control(plan)
        try:lease=(control/'apply.lock').open('x',encoding='utf-8')
        except FileExistsError:raise SetupError('CONCURRENT_ATTEMPT_OR_INTERRUPTED_LOCK')
        try:
            lease.write(json.dumps({'pid':os.getpid(),'action':'rollback'}));lease.close()
            return self._rollback_owned(plan)
        finally:
            lease.close();(control/'apply.lock').unlink()

    def _rollback_owned(self,plan):
        control=self._control(plan);checkpoint=control/'receipt.json'
        state=json.loads(checkpoint.read_text(encoding='utf-8'))
        if state.get('install_binding')!=plan['install_binding']:raise SetupError('CHECKPOINT_PLAN_MISMATCH')
        if state.get('status')=='ROLLED_BACK':return {'status':'ROLLED_BACK','retained_roots':state.get('retained_roots',[])}
        if state.get('runtime',{}).get('state') in {'PASS','READY'}:raise SetupError('OWNED_RUNTIME_STOP_REQUIRED_BEFORE_ROLLBACK')
        target=safe_path(plan['host_agent'])
        if state.get('context_after_sha256'):
            if file_hash(target)!=state['context_after_sha256']:raise SetupError('HOST_AGENT_STALE')
            previous=control/'HOST_AGENT.previous'
            if state['context_before_sha256']:
                if file_hash(previous)!=state['context_before_sha256']:raise SetupError('ROLLBACK_BACKUP_DRIFT')
                os.replace(previous,target)
            else:target.unlink()
        # Delete only marker-proven newly owned roots and empty directories. Never recursive GC.
        retained=[]
        for raw in reversed(state.get('created_roots',[])):
            p=safe_path(raw);marker=p/'.agent-runtime-setup-owner.json'
            if not marker.exists() or json.loads(marker.read_text(encoding='utf-8')).get('attempt')!=state['attempt']:raise SetupError('ROLLBACK_OWNERSHIP_DRIFT')
            if any(child.name not in {'.agent-runtime-setup-owner.json','.agent-runtime-setup'} for child in p.iterdir()):retained.append(str(p));continue
            if p==control.parent:retained.append(str(p));continue
            marker.unlink();p.rmdir()
        state['status']='ROLLED_BACK';state['retained_roots']=retained;atomic_json(checkpoint,state)
        return {'status':'ROLLED_BACK','retained_roots':retained,'reason':'Journal/root with evidence retained; unknown or unique bytes never deleted'}
