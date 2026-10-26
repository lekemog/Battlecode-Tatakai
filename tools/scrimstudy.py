"""scrimstudy.py GROUP... -> download+decode unranked scrim groups; compare top team (O) vs us (S) per game. Cache data/scrim_cache.json."""
import json,os,sys,subprocess,zipfile,tempfile,shutil,importlib.util
spec=importlib.util.spec_from_file_location('fs','/home/claude/tools/fishstudy.py')
sys.argv_saved=sys.argv;sys.argv=['x']; fs=importlib.util.module_from_spec(spec); spec.loader.exec_module(fs); sys.argv=sys.argv_saved
C='/home/claude/data/scrim_cache.json';cache=json.load(open(C)) if os.path.exists(C) else {}
D='/home/claude/data/scrims';os.makedirs(D,exist_ok=True)
for g in sys.argv[1:]:
    d=json.loads(subprocess.run(['cambc','match-groups','show',g,'--json'],capture_output=True,text=True).stdout)
    for m in d['matches']:
        mid=m['matchId']
        if mid in cache or m.get('status')!='finished':continue
        me=[t for t in m['teams'] if t.get('teamId','').startswith('9c16')][0];op=[t for t in m['teams'] if t is not me][0]
        z=f'{D}/{mid}.zip'
        if not os.path.exists(z):subprocess.run(['cambc','matches','download',mid,'-o',z],capture_output=True,timeout=300)
        t=tempfile.mkdtemp(dir=D)
        try:
            zipfile.ZipFile(z).extractall(t)
            rp=[os.path.join(a,f) for a,_,fs_ in os.walk(t) for f in fs_ if f.endswith('.repl26a')][0]
            subprocess.run(['node','/home/claude/tools/replay/extract3.mjs','/home/claude/data/vis3/assets',rp,t+'/r.json'],capture_output=True,timeout=600)
            R=json.load(open(t+'/r.json'))['rounds']
            s=0 if me.get('side')=='a' else 1
            rec=fs.analyse(R,s);rec.update(map=m['map'],result=me.get('result'),opp=op.get('name'),group=g)
            cache[mid]=rec;print('ok',m['map'],op.get('name'),me.get('result'),flush=True)
        except Exception as e:print('skip',mid[:8],e)
        finally:shutil.rmtree(t,ignore_errors=True)
json.dump(cache,open(C,'w'))
