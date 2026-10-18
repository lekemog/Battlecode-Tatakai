"""Offline-only paired execution lab. Never logs in, submits, or queues platform games.

python tools/faux_lab.py --candidate v17w --opponents fz_solo_v2,fz_hunt_v2 \
    --maps corners,rows,contest --out results/local/faux-check
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('CAMBC_CACHE',str(ROOT/'.engine-cache'))
MAP_PREFIX = dict(corners='e3c2', collision='2e98', contest='3a5c', rows='25d8',
                  stampede='f2b6', eight='3e2d', lanes='9385', expanse='8192')

def save_json(path,data):
    with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False) as f:
        json.dump(data,f,indent=2);temp=Path(f.name)
    temp.replace(path)

def fingerprint(path):
    h=hashlib.sha256()
    for f in sorted(path.glob('src/*')):
        if f.is_file():h.update(f.name.encode()+b'\0'+f.read_bytes())
    return h.hexdigest()

def at(timeline, index):
    # Timelines are indexed samples. Never substitute the postgame value for a missing horizon.
    if index>=int(timeline.get('sampleCount',0)):return None
    for r in timeline.get('runs',[]):
        if index<int(r['duration']):return float(r['value'])
        index-=int(r['duration'])
    return None

def features(d, side):
    cs=[c for c in d.get('champions',[]) if c.get('team')==side]
    events=[e for e in d.get('events',[]) if e.get('owner',{}).get('team')==side]
    def entries(kind):return [v for e in events if e['kind']==kind for v in e.get('entries',[])]
    def first(kind):
        vals=[v['timestamp']['round'] for v in entries(kind)]
        return min(vals) if vals else None
    # amount is not assumed to be the gem amount; gem events encode the count in value.
    def amount(kind):return sum(float(v.get('value',0)) for v in entries(kind))
    result={'champions':len(cs),'first_purchase':first('buyItem'),
            'first_tribute':first('gemSubmission'),'deaths':len(entries('death')),
            'gem_loss_event_sum':amount('gemLoss'),'camp_clear_events':len(entries('campClear')),
            'unique_camp_clear_groups':len({e.get('target',{}).get('id') for e in entries('campClear') if isinstance(e.get('target'),dict)}),
            'wards':len(entries('wardPlacement')),'fuel_exhaustions':len(entries('fuelExhausted')),
            'bot_faults':len(entries('botFault')),
            'submitted':next(int(t['submittedGems']) for t in d['teams'] if t['team']==side),
            'earned_gold':sum(float(c.get('metrics',{}).get('earnedGold',0)) for c in cs),
            'monster_damage':sum(float(c.get('metrics',{}).get('monsterDamageDone',0)) for c in cs),
            'champion_damage':sum(float(c.get('metrics',{}).get('championDamageDone',0)) for c in cs),
            'purchases':[{'round':e['timestamp']['round'],'item':e.get('target',{}).get('name')} for e in entries('buyItem')],
            'horizon_sample_indices':{}}
    for horizon in (100,200,300,400):
        row={}
        for metric in ('gold','gems','earnedGold','maxHealth'):
            ts=[t for t in d.get('championTimelines',[]) if t.get('owner',{}).get('team')==side and t.get('metric')==metric]
            vals=[at(t,horizon) for t in ts]
            row[metric]=sum(vals) if len(ts)==len(cs) and ts and all(v is not None for v in vals) else None
        result['horizon_sample_indices'][str(horizon)]=row
    return result

def parse(d):
    # Use the engine's outcome, including gold/kill tiebreaks; never derive a winner from gem margin.
    if d['match'].get('outcome') not in ('teamA','teamB','draw'):raise ValueError('missing/unsupported outcome')
    return {'match':d['match'],'teamA':features(d,'teamA'),'teamB':features(d,'teamB')}

def resolve_map(name):
    direct=ROOT/'maps'/(name+'.map26a')
    if direct.exists():return direct
    hits=list((ROOT/'maps').glob('p_'+MAP_PREFIX.get(name,name)+'*.map26a'))
    if len(hits)!=1:raise ValueError(f'expected one map for {name}, found {len(hits)}')
    return hits[0]

def summarize(rows,candidate,opponents,map_count):
    def family(bot):return re.sub(r'_v\d+$','',bot)
    expected={family(o):sum(family(v)==family(o) for v in opponents) for o in opponents}
    cells={};per_opp={o:{'wins':0,'completed':0,'failed':0} for o in opponents}
    for r in rows:
        side='teamA' if r['a']==candidate else 'teamB'
        opp=r['b'] if side=='teamA' else r['a']
        if r['status']!='complete':per_opp[opp]['failed']+=1;continue
        win=r['match']['outcome']==side
        per_opp[opp]['completed']+=1;per_opp[opp]['wins']+=win
        cells.setdefault((family(opp),r['map'],side),[]).append(win)
    complete=[v for k,v in cells.items() if len(v)==expected[k[0]]]
    return {'per_opponent':per_opp,'family_checks_planned':len(expected)*map_count*2,
            'family_checks_completed':len(complete),'family_checks_passed':sum(all(v) for v in complete)}

def run_one(cli, out, game, timeout, keep):
    name, a, b, map_path=game
    directory=out/name
    directory.mkdir(parents=True,exist_ok=False)
    stats=directory/'stats.json'
    cmd=[cli,'run',str(ROOT/'bots'/a),str(ROOT/'bots'/b),'--map',str(map_path),
         '--out-dir',str(directory),'--release','--statistics',str(stats),'--json','--log-limit','0']
    row={'id':name,'a':a,'b':b,'map':map_path.name,'map_sha256':hashlib.sha256(map_path.read_bytes()).hexdigest(),
         'source_sha256':{a:fingerprint(ROOT/'bots'/a),b:fingerprint(ROOT/'bots'/b)},'command':cmd}
    try:
        r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=timeout)
        (directory/'runner.txt').write_text(r.stdout+r.stderr)
        if r.returncode:raise RuntimeError(f'runner exit {r.returncode}')
        row.update(parse(json.loads(stats.read_text())))
        row['status']='complete'
    except (OSError,ValueError,KeyError,RuntimeError,subprocess.TimeoutExpired) as e:
        row.update(status='failed',error=str(e))
    if not keep:
        for f in directory.rglob('*.repl26a'):f.unlink()
    return row

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',required=True)
    p.add_argument('--opponents',default='fz_herd,fz_solo,fz_hunt,fz_tank,fz_herd_v4,fz_hunt_v3,fz_tank_v2')
    p.add_argument('--maps',default='corners,collision,rows,contest,stampede,eight')
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--jobs',default=2,type=int)
    p.add_argument('--timeout',default=900,type=int)
    p.add_argument('--cli',default='cambc')
    p.add_argument('--keep-replays',action='store_true')
    args=p.parse_args()
    cli=shutil.which(args.cli)
    if not cli:p.error('official cambc executable not found')
    opps=args.opponents.split(',')
    for name in [args.candidate]+opps:
        if '/' in name or not (ROOT/'bots'/name/'src').is_dir():p.error('unknown bot '+name)
    out=args.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    version=subprocess.run([cli,'--version'],capture_output=True,text=True,check=True).stdout.strip()
    # Build sequentially so simultaneous games never race on the same compiler output.
    for name in [args.candidate]+opps:
        r=subprocess.run([cli,'build',name,'--release'],cwd=ROOT,capture_output=True,text=True)
        (out/(name+'-build.txt')).write_text(r.stdout+r.stderr)
        if r.returncode:raise SystemExit('build failed: '+name)
    games=[]
    for opp in opps:
        for m in args.maps.split(','):
            for side,(a,b) in enumerate(((args.candidate,opp),(opp,args.candidate))):
                games.append((f'{opp}-{m}-{side}',a,b,resolve_map(m)))
    rows=[]
    with ThreadPoolExecutor(max_workers=max(1,args.jobs)) as ex:
        fs=[ex.submit(run_one,cli,out,g,args.timeout,args.keep_replays) for g in games]
        for f in as_completed(fs):
            row=f.result();rows.append(row)
            save_json(out/'results.json',{'cli':version,'planned':len(games),'games':rows})
            print(row['id'],row['status'],row.get('match',{}).get('outcome',''),flush=True)
    complete=[r for r in rows if r['status']=='complete']
    wins=sum(r['match']['outcome']==('teamA' if r['a']==args.candidate else 'teamB') for r in complete)
    summary={'planned':len(games),'completed':len(complete),'failed':len(rows)-len(complete),'candidate_wins':wins,
             **summarize(rows,args.candidate,opps,len(args.maps.split(',')))}
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary))

if __name__=='__main__':main()
