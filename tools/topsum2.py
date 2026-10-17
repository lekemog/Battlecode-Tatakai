import json, subprocess, os, time, re
TM = json.load(open('/home/claude/data/top/topmatches.json'))
ids = open('/home/claude/data/top/ids.txt').read().split()
pri = [k for k, m in TM.items() if m['map'] in ('contest', 'swirl', 'fragment', 'collision', 'rushbait_v2')][:30]
order = pri + [i for i in ids if i not in pri]
for i in order:
    p = f'/home/claude/data/top/sum/{i}.json'
    if os.path.exists(p) and os.path.getsize(p) > 0:
        continue
    for t in range(6):
        try:
            r = subprocess.run(['cambc', 'matches', 'summary', i, '--json', '-o', p], capture_output=True, text=True, timeout=150)
        except subprocess.TimeoutExpired:
            continue
        if r.returncode == 0:
            break
        m = re.search(r'retry after (\d+)', r.stderr + r.stdout)
        time.sleep(int(m.group(1)) + 1 if m else 5)
    print(i, TM[i]['map'], os.path.exists(p), flush=True)
