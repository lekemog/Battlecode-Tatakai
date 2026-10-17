"""Cache match-group details (matchId -> our side, tag, opponent, map) for all scrim groups."""
import json, subprocess, os, time, re
G = json.load(open('/home/claude/data/ab/groups.json'))
CF = '/home/claude/data/ab/groupcache.json'
cache = json.load(open(CF)) if os.path.exists(CF) else {}
ME = '9c16b699-cad2-453e-8042-dae23ff934d8'
for g in G:
    if g['group'] in cache:
        continue
    for t in range(6):
        r = subprocess.run(['cambc', 'match-groups', 'show', g['group'], '--json'], capture_output=True, text=True)
        if r.returncode == 0:
            break
        m = re.search(r'retry after (\d+)', r.stderr + r.stdout)
        time.sleep(int(m.group(1)) + 1 if m else 3)
    try:
        d = json.loads(r.stdout)
    except Exception:
        continue
    ms = []
    for m in d.get('matches', []):
        us = [t for t in m['teams'] if t['teamId'] == ME]
        if not us:
            continue
        ms.append({'matchId': m['matchId'], 'map': m['map'], 'side': us[0]['side'], 'status': m['status']})
    if all(x['status'] == 'finished' for x in ms) and ms:
        cache[g['group']] = {'tag': g['tag'], 'opp': g['opp'], 'name': g['name'], 'matches': ms}
    json.dump(cache, open(CF, 'w'))
print(len(cache))
