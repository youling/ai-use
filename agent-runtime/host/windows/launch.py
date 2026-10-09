"""Narrow native WSLC launcher consuming HOST_AGENT V1 and existing projections.
No Fleet/GhostFleet calls or credential minting key enters the container.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import os
import secrets
import yaml
import ctypes

def trusted_windows_powershell():
    """Windows-provided PowerShell 5.1; PATH and SystemRoot are not authority."""
    try:
        buffer=ctypes.create_unicode_buffer(32768)
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.GetSystemDirectoryW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint]
        kernel.GetSystemDirectoryW.restype=ctypes.c_uint
        count=kernel.GetSystemDirectoryW(buffer,len(buffer))
        if not 0<count<len(buffer):return None
        path=Path(buffer.value)/'WindowsPowerShell/v1.0/powershell.exe'
        if not path.is_file() or any(p.is_symlink() or (p.exists() and getattr(p.lstat(),'st_file_attributes',0)&0x400) for p in (path,*path.parents)):return None
        return str(path)
    except (OSError,AttributeError):return None

def read_host(path, *, local_only=False):
    text=Path(path).read_text(encoding='utf-8')
    match=re.search(r'```yaml\s*\n(.*?)\n```',text,re.S)
    if not match:
        raise ValueError('HOST_AGENT_V1_REQUIRED')
    value=yaml.safe_load(match[1])
    if value.get('host_agent_version')!='1.0.0' or (not local_only and not value['agents']['opencode']['enabled']):
        raise ValueError('OPENCODE_PROJECTION_DISABLED')
    if not local_only and not value['agents']['opencode']['github']['recovery_required']:
        raise ValueError('GITHUB_RECOVERY_REQUIRED')
    return value

def ordinary(path):
    path=Path(path).absolute()
    if any(p.is_symlink() or (p.exists() and getattr(p.lstat(),'st_file_attributes',0)&0x400) for p in (path,*path.parents)):
        raise ValueError('REPARSE_PATH_DENIED')
    if any(c in str(path) for c in ',\r\n\x00') or str(path).startswith(('\\\\', '//')) or '..' in path.parts:
        raise ValueError('MOUNT_PATH_INVALID')
    return path.resolve()

def local_server_auth(root):
    """Host-owned attempt auth; no external identity, secret result or reuse.

    Protect the empty directory before writing. On Windows set and read back
    a non-inherited ACL restricted to the current SID and SYSTEM, failing shut.
    """
    custody=ordinary(root/'auth')
    custody.mkdir(mode=0o700)
    if os.name=='nt':
        ps=trusted_windows_powershell()
        if not ps:
            raise ValueError('PROTECTED_HOST_AUTH_CUSTODY_UNAVAILABLE')
        script=r"""$ErrorActionPreference='Stop';
[Console]::InputEncoding=[System.Text.UTF8Encoding]::new($false);
[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false);
try {
 $p=([Console]::In.ReadToEnd()|ConvertFrom-Json).path;
 $sid=[System.Security.Principal.WindowsIdentity]::GetCurrent().User;
 $system=[System.Security.Principal.SecurityIdentifier]::new('S-1-5-18');
 $acl=[System.Security.AccessControl.DirectorySecurity]::new();
 $acl.SetAccessRuleProtection($true,$false); $acl.SetOwner($sid);
 foreach($identity in @($sid,$system)) {
  $rule=[System.Security.AccessControl.FileSystemAccessRule]::new($identity,'FullControl','ContainerInherit,ObjectInherit','None','Allow');
  $acl.AddAccessRule($rule);
 }
 Set-Acl -LiteralPath $p -AclObject $acl;
 $got=Get-Acl -LiteralPath $p;
 $rules=@($got.GetAccessRules($true,$true,[System.Security.Principal.SecurityIdentifier]));
 $ok=$got.AreAccessRulesProtected -and $got.GetOwner([System.Security.Principal.SecurityIdentifier]).Value -eq $sid.Value -and $rules.Count -eq 2;
 foreach($r in $rules) { if($r.IsInherited -or $r.IdentityReference.Value -notin @($sid.Value,'S-1-5-18') -or $r.AccessControlType -ne 'Allow' -or $r.FileSystemRights -ne [System.Security.AccessControl.FileSystemRights]::FullControl -or $r.PropagationFlags -ne [System.Security.AccessControl.PropagationFlags]::None -or $r.InheritanceFlags -ne ([System.Security.AccessControl.InheritanceFlags]::ContainerInherit -bor [System.Security.AccessControl.InheritanceFlags]::ObjectInherit)) {$ok=$false} }
 @{protected=[bool]$ok}|ConvertTo-Json -Compress
} catch { '{"protected":false}' }
"""
        try:
            check=subprocess.run([ps,'-NoLogo','-NoProfile','-NonInteractive','-Command',script],
                                 input=json.dumps({'path':str(custody)},ensure_ascii=False),capture_output=True,encoding='utf-8',errors='strict',timeout=20)
            proof=json.loads(check.stdout) if check.returncode==0 and len(check.stdout)<4096 else {}
        except (OSError,ValueError,UnicodeError,subprocess.TimeoutExpired):
            proof={}
        if not isinstance(proof,dict) or proof.get('protected') is not True:
            raise ValueError('PROTECTED_HOST_AUTH_CUSTODY_UNVERIFIED')
    elif custody.stat().st_mode & 0o077:
        raise ValueError('PROTECTED_HOST_AUTH_CUSTODY_UNVERIFIED')
    target=custody/'server.env'
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as out:
        out.write('OPENCODE_SERVER_PASSWORD='+secrets.token_urlsafe(48)+'\n')
    return target

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--host-agent',required=True)
    p.add_argument('--wslc',required=True)
    p.add_argument('--attempt',required=True)
    p.add_argument('--name',required=True)
    p.add_argument('--github-projection')
    p.add_argument('--local-only',action='store_true')
    p.add_argument('--input',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--canary',action='store_true')
    p.add_argument('--server-env')
    p.add_argument('--host-port',type=int,default=4096)
    p.add_argument('--stop',action='store_true')
    a=p.parse_args()
    source=ordinary(a.host_agent)
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    host=read_host(source, local_only=a.local_only)
    if a.local_only and (a.canary or a.github_projection or a.server_env):
        raise ValueError('LOCAL_EXTERNAL_AUTH_PROJECTION_DENIED')
    if not re.fullmatch(r'[a-z][a-z0-9-]{1,60}',a.name):
        raise ValueError('INVALID_ATTEMPT_NAME')
    image=host['agents']['opencode']['image']
    if not re.fullmatch(r'sha256:[a-f0-9]{64}',image):
        raise ValueError('IMMUTABLE_IMAGE_REQUIRED')
    root=ordinary(a.attempt)
    if a.stop:
        lease=json.loads((root/'owner.json').read_text())
        if lease['name']!=a.name or lease['image']!=image:
            raise ValueError('OWNED_ATTEMPT_MISMATCH')
        observed=subprocess.run([a.wslc,'inspect',a.name,'--format','json'],capture_output=True,text=True,timeout=10)
        if observed.returncode:
            raise ValueError('OWNED_CONTAINER_ABSENT')
        info=json.loads(observed.stdout)[0]
        if info.get('Config',{}).get('Labels',{}).get('agent.attempt')!=a.name:
            raise ValueError('FOREIGN_CONTAINER_DENIED')
        stopped=subprocess.run([a.wslc,'stop',a.name],capture_output=True,timeout=20)
        if stopped.returncode:
            raise RuntimeError('OWNED_STOP_FAILED')
        print(json.dumps({'stopped':True,'name':a.name,'secret_output':'NONE'}))
        return
    if root.exists():
        raise ValueError('ATTEMPT_EXISTS')
    temp=ordinary(host['paths']['temp']['path'])
    if not root.is_relative_to(temp):
        raise ValueError('ATTEMPT_OUTSIDE_DECLARED_ROOT')
    incoming,outgoing=map(ordinary,[a.input,a.output])
    if (not incoming.is_relative_to(ordinary(host['paths']['exchange']['in']))
        or not outgoing.is_relative_to(ordinary(host['paths']['exchange']['out']))):
        raise ValueError('EXCHANGE_OUTSIDE_DECLARED_ROOTS')
    if not incoming.is_dir() or not outgoing.is_dir() or incoming==outgoing or incoming.is_relative_to(outgoing) or outgoing.is_relative_to(incoming):
        raise ValueError('EXCHANGE_PROJECTION_INVALID')
    credential=None
    if not a.local_only:
        if not a.github_projection:
            raise ValueError('PROJECTION_NOT_READY')
        credential=ordinary(a.github_projection)
        if not (credential/'credential.json').is_file():
            raise ValueError('PROJECTION_NOT_READY')
        if len({incoming,outgoing,credential})!=3 or any(x.is_relative_to(y) for x in (incoming,outgoing,credential) for y in (incoming,outgoing,credential) if x!=y):
            raise ValueError('PROJECTION_OVERLAP')
        if any(p.name not in {'credential.json','server.env'} or not p.is_file() or p.is_symlink() for p in credential.iterdir()):
            raise ValueError('UNDECLARED_SECRET_PROJECTION_CONTENT')
        if host['paths']['secrets']['refs']['github_machine']['ref']!=host['agents']['opencode']['github']['credential_ref']:
            raise ValueError('SECRET_REFERENCE_MISMATCH')
    if a.local_only:
        # Read back the released manifest/config before creating any attempt.
        checked=subprocess.run([a.wslc,'inspect',image,'--format','json'],capture_output=True,text=True,timeout=15)
        info=json.loads(checked.stdout)[0] if checked.returncode==0 else {}
        released='ghcr.io/youling/opencode-foreman@sha256:fa92f37752ff6132b161ed4c2563897c94b014ab70d650846dcb09f354f55261'
        if info.get('Id',info.get('ID'))!=image or released not in info.get('RepoDigests',[]):
            raise ValueError('RELEASED_LOCAL_IMAGE_READBACK_REQUIRED')
    # Only declared context file is projected; never the Documents/catalog parent.
    context=root/'context'
    context.mkdir(parents=True)
    shutil.copyfile(a.host_agent,context/'HOST_AGENT.md')
    before=hashlib.sha256(Path(a.host_agent).read_bytes()).hexdigest()
    if before!=source_hash or before!=hashlib.sha256((context/'HOST_AGENT.md').read_bytes()).hexdigest():
        raise ValueError('HOST_CONTEXT_COPY_MISMATCH')
    (root/'owner.json').write_text(json.dumps({'name':a.name,'image':image,'host_agent_sha256':before}))
    argv=[a.wslc,'run','--rm','--detach','--name',a.name,'--cpus','4','--memory','4G',
          '--label','agent.attempt='+a.name,
          '--mount',f'type=bind,source={context},target=/host-context,readonly',
          '--mount',f'type=bind,source={incoming},target=/exchange/in,readonly',
          '--mount',f'type=bind,source={outgoing},target=/exchange/out']
    if credential is not None:
        argv+=['--mount',f'type=bind,source={credential},target=/run/secrets/github,readonly']
    if a.local_only:
        envfile=local_server_auth(root)
        argv+=['--user','1000:1000','--network','none','--env-file',str(envfile),
               '--label','agent.setup.profile=local-only', image,'serve','--hostname','127.0.0.1','--port','4096']
    elif a.canary:
        for name in ('work.json','github_recovery.py','github_credential.py'):
            if not (incoming/name).is_file():
                raise ValueError('CANARY_INPUT_MISSING')
        argv+=['--entrypoint','python3',image,'/exchange/in/github_recovery.py']
    else:
        envfile=ordinary(a.server_env) if a.server_env else None
        if envfile is None or not envfile.is_file() or not 1024<=a.host_port<=65535:
            raise ValueError('SERVER_CREDENTIAL_BINDING_REQUIRED')
        names={s.split('=',1)[0] for s in envfile.read_text().splitlines() if '=' in s and not s.startswith('#')}
        if 'OPENCODE_PASSWORD' not in names or names-{'OPENCODE_PASSWORD','OPENCODE_API_KEY'}:
            raise ValueError('SERVER_ENV_ALLOWLIST_REQUIRED')
        if not (incoming/'github_credential.py').is_file():
            raise ValueError('PER_OPERATION_GITHUB_HELPER_REQUIRED')
        metadata=json.loads((credential/'credential.json').read_text())
        if (not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*',metadata['work'])
            or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',metadata['repo'])):
            raise ValueError('GITHUB_BINDING_METADATA_INVALID')
        for key,value in {'GITHUB_WORK':metadata['work'],'GITHUB_REPOSITORY':metadata['repo'],
            'GITHUB_CREDENTIAL_FILE':'/run/secrets/github/credential.json','GIT_TERMINAL_PROMPT':'0',
            'GIT_CONFIG_COUNT':'2','GIT_CONFIG_KEY_0':'credential.helper',
            'GIT_CONFIG_VALUE_0':'!python3 /exchange/in/github_credential.py',
            'GIT_CONFIG_KEY_1':'credential.useHttpPath','GIT_CONFIG_VALUE_1':'true'}.items():
            argv+=['--env',key+'='+value]
        argv+=['--env-file',str(envfile),'--publish',f'127.0.0.1:{a.host_port}:4096',
               image,'serve','--hostname','0.0.0.0','--port','4096']
    result=subprocess.run(argv,capture_output=True,text=True,timeout=30)
    if result.returncode:
        raise RuntimeError('WSLC_START_FAILED')
    print(json.dumps({'started':True,'name':a.name,'image':image,'host_agent_sha256':before,'secret_output':'NONE','local_only':a.local_only,'network':'none' if a.local_only else 'default','scoped_auth':bool(a.local_only or a.server_env)}))

if __name__=='__main__':
    try:
        main()
    except Exception as e:
        print(json.dumps({'status':'FAILED','category':type(e).__name__,'secret_output':'NONE'}))
        raise SystemExit(2)
