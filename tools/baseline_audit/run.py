"""Fail-closed all-map baseline execution audit. Preserve logs, stats and replays."""
import argparse, concurrent.futures, hashlib, json, pathlib, subprocess, time


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--project', type=pathlib.Path, required=True)
    p.add_argument('--out', type=pathlib.Path, required=True)
    p.add_argument('--jobs', type=int, default=2)
    args = p.parse_args()
    root = pathlib.Path(__file__).resolve().parents[2]
    names = (root / 'bench/pool6.txt').read_text().strip().split(',')
    assert len(names) == len(set(names)) == 40, 'Expected exactly 40 distinct maps'
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    project = args.project.resolve()
    for name in names:
        assert (project / 'maps' / (name + '.map26a')).is_file(), name
    for bot in ['v25u', 'x_daniel8']:
        subprocess.run(['cambc', 'build', str(project / 'bots' / bot), '--release'], cwd=project, check=True)
    def run(name, side):
        dest = out / (name + '_' + side); dest.mkdir()
        a, b = ('v25u', 'x_daniel8') if side == 'teamA' else ('x_daniel8', 'v25u')
        cmd = ['cambc', 'run', str(project/'bots'/a), str(project/'bots'/b),
               '--map', str(project/'maps'/(name+'.map26a')), '--release', '--json',
               '--statistics', str(dest/'summary.json'), '--out-dir', str(dest/'replay'),
               '--log-limit', '1048576']
        started=time.monotonic()
        with (dest/'runner.log').open('w') as log:
            try:
                rc=subprocess.run(cmd,cwd=project,stdout=log,stderr=subprocess.STDOUT,timeout=900).returncode
            except subprocess.TimeoutExpired:
                rc=-1
        row={'map':name,'side':side,'returncode':rc,'seconds':round(time.monotonic()-started,2)}
        try:
            d=json.loads((dest/'summary.json').read_text())
            row.update(outcome=d['match']['outcome'], rounds=d['match']['roundsStarted'],
                       scores={t['team']:t['submittedGems'] for t in d['teams']})
            # Do not silently treat missing diagnostics as zero faults.
            row['match_metadata']=d['match']
            row['summary_keys']=list(d)
        except (OSError,ValueError,KeyError,TypeError) as e:
            row['error']=str(e)
        row['complete']=rc==0 and 'outcome' in row
        print(json.dumps(row),flush=True)
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        jobs=[ex.submit(run,n,s) for n in names for s in ['teamA','teamB']]
        rows=[f.result() for f in concurrent.futures.as_completed(jobs)]
    report={'expected_games':80,'completed_games':sum(r['complete'] for r in rows),'games':rows,
            'map_sha256':{n:hashlib.sha256((project/'maps'/(n+'.map26a')).read_bytes()).hexdigest() for n in names},
            'note':'Completion is not proof of no idle or fuel failures; inspect retained summaries, fuel logs and replays.'}
    (out/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('AUDIT_COMPLETED',report['completed_games'],'/80',flush=True)
    if report['completed_games']!=80: raise SystemExit(1)

if __name__=='__main__': main()
