from pathlib import Path
import json
root=Path(__file__).parent
data=json.loads((root/'fish-series-evidence.json').read_text())
for game in data:
    for state in game['snapshots']:
        state.pop('items',None)
        state.pop('hp',None)
    decoded=json.loads((root/game['id']/'decoded.json').read_text())
    wanted=800 if game['id'].startswith('d148') else 300
    state=next(r for r in decoded['rounds'] if r['round']==wanted)
    game['build_check']={'r':wanted,'champions':[{'id':c['entity']['index'],'team':c['team'],'type':c['type'],'focus':c['focus']['effective'],'max_health':c['maxHealth'],'items':{str(i):n for i,n in enumerate(c['items'])if n}} for c in state['champions']]}
(root/'series_evidence.json').write_text(json.dumps(data,separators=(',',':')))
history=json.loads(Path('/workspace/scratch/fish-ranked-history-snapshots-20261021.json').read_text())
inventory={'team_id':'1890540d-1ffc-4847-adbf-d0d08772f268','series_entries_loaded':868,'end_of_history_observed':True,'unique_series_urls_captured':len(history['groupUrls']),'profile_url':history['profileUrl'],'series_urls':history['groupUrls'],'limitation':'The history list is virtualized; URL capture is incomplete. These are not all decoded or watched games.'}
(root/'history_inventory.json').write_text(json.dumps(inventory,indent=2))
print('Evidence bytes', (root/'series_evidence.json').stat().st_size)
print('Inventory URL count',len(inventory['series_urls']))
