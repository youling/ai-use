"""Docker deterministic smoke/provenance/history/layer checks. Never inference."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile

SOURCE='ghcr.io/anomalyco/opencode:2.0.22@sha256:11f2b6c96d380867387fbee390c06cb47efffd9fdc37009b4cd40795b45dad19'
def run(*args):
    return subprocess.check_output(['docker',*args],text=True,stderr=subprocess.PIPE).strip()

def main():
    image=sys.argv[1]
    revision=os.environ['EXPECTED_REVISION']
    info=json.loads(run('image','inspect',image))[0]
    config=info['Config']
    assert config['User']=='1000:1000' and config['WorkingDir']=='/workspace'
    assert config['Entrypoint']==['opencode'] and config['Cmd'][0]=='serve'
    labels=config['Labels']
    assert labels['org.opencontainers.image.source']=='https://github.com/youling/ai-use'
    assert labels['org.opencontainers.image.revision']==revision and revision!='unreleased'
    assert labels['org.opencontainers.image.licenses']=='Apache-2.0 AND MIT'
    assert all(not re.match(r'(?i)(GH_TOKEN|GITHUB_TOKEN|OPENCODE_API_KEY|OPENCODE_PASSWORD)=',s) for s in config['Env'])
    def shell(command):return run('run','--rm','--entrypoint','sh',image,'-ec',command)
    assert shell('id -u')=='1000'
    assert shell('opencode --version')=='opencode v2.0.22'
    shell('test -w /workspace; for x in git rg jq curl python3; do command -v "$x" >/dev/null; done; test -s /usr/share/agent-runtime/LICENSE.opencode')
    run('pull',SOURCE)
    original=run('run','--rm','--entrypoint','sh',SOURCE,'-ec','sha256sum /usr/local/bin/opencode').split()[0]
    actual=shell('sha256sum /usr/local/bin/opencode').split()[0]
    assert original==actual
    license_local=Path('agent-runtime/opencode/LICENSE.opencode').read_bytes()
    assert shell('sha256sum /usr/share/agent-runtime/LICENSE.opencode').split()[0]==hashlib.sha256(license_local).hexdigest()
    manifest=shell('cat /usr/share/agent-runtime/package-manifest.tsv')
    assert manifest.splitlines()==Path('agent-runtime/opencode/package-manifest.observed.tsv').read_text().splitlines()
    Path('package-manifest.current.tsv').write_text(manifest+'\n')
    secret=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-proj-[A-Za-z0-9_-]{30,})')
    history=run('history','--no-trunc','--format','{{json .}}',image).encode()
    assert not secret.search(history) and b'/run/secrets' not in history
    layers=0
    with tempfile.TemporaryDirectory(prefix='runtime-image-scan-') as directory:
        archive=Path(directory)/'image.tar'
        subprocess.run(['docker','save','-o',str(archive),image],check=True)
        with tarfile.open(archive) as outer:
            manifests=json.load(outer.extractfile('manifest.json'))
            layer_paths={p for manifest in manifests for p in manifest['Layers']}
            for member in outer:
                if not member.isfile():continue
                handle=outer.extractfile(member)
                if member.name in layer_paths:
                    layers+=1
                    with tarfile.open(fileobj=handle,mode='r|*') as layer:
                        for item in layer:
                            if not item.isfile():continue
                            assert not re.search(r'(^|/)(credential\.json|auth\.json|\.git-credentials|id_rsa|id_ed25519)$',item.name)
                            content=layer.extractfile(item)
                            tail=b''
                            while True:
                                chunk=content.read(1024*1024)
                                if not chunk:break
                                assert not secret.search(tail+chunk), 'secret signature in image file'
                                tail=chunk[-256:]
                elif member.size<2*1024*1024:
                    assert not secret.search(handle.read())
    assert layers==len(layer_paths) and layers>0
    evidence={'runtime':'opencode','version':'2.0.22','platform':'linux/amd64','revision':revision,
        'config_id':info['Id'],'source':SOURCE,'upstream_executable_sha256':actual,
        'non_root':True,'model_inference':False,'layer_secret_scan':'PASS','layers_scanned':layers,
        'package_manifest_sha256':hashlib.sha256((manifest+'\n').encode()).hexdigest(),
        'registry_manifest_digest':None,'publication':'NOT_PERFORMED'}
    Path('image-conformance.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence))

if __name__=='__main__':main()
