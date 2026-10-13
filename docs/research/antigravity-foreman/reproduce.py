"""Replay frozen synthetic controls; no provider calls or global config writes."""
import hashlib,json,os,pathlib,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parent
def main():
    e=json.loads((ROOT/'evidence.json').read_text(encoding='utf-8'))
    for name,digest in e['test_hashes'].items():
        assert hashlib.sha256((ROOT/'synthetic'/name).read_bytes()).hexdigest()==digest,name
    results={}
    with tempfile.TemporaryDirectory(prefix='ag-fm-replay-') as scratch:
        for label in ['baseline','builder']:
            env={k:v for k,v in os.environ.items() if not any(x in k.upper() for x in ['TOKEN','SECRET','API_KEY','PASSWORD'])}
            env.update(CANARY_CANDIDATE_FILE=str(ROOT/'synthetic'/(label+'_reader.py')),PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1')
            p=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'synthetic'),'-p','test_reader.py','-v'],cwd=scratch,env=env,capture_output=True,text=True,encoding='utf-8',timeout=30)
            expected=1 if label=='baseline' else 0
            text=p.stdout+p.stderr
            assert p.returncode==expected,(label,p.returncode,text)
            assert 'Ran 12 tests' in text,(label,text)
            assert ('failures=10, errors=1' in text) if label=='baseline' else text.rstrip().endswith('OK')
            results[label]={'exit_code':p.returncode,'tests':12,'matched_frozen_expectation':True}
    print(json.dumps({'fixed_test_replay':'PASS','native_runtime_retested':False,'results':results}))
if __name__=='__main__':main()
