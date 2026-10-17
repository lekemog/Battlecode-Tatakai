"""Regenerate Polaris_Testing_Results.xlsx from live ladder data (scrim groups + ranked matches)."""
import json,subprocess,time,collections,datetime,sys
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table,TableStyleInfo
ME='9c16b699-cad2-453e-8042-dae23ff934d8';OUT='/mnt/user-data/outputs/Polaris_Testing_Results.xlsx'
META=json.load(open('/home/claude/data/ab/meta.json'))
def cambc(args):
    for _ in range(4):
        r=subprocess.run(['cambc']+args,capture_output=True,text=True,cwd='/home/claude/proj')
        try:return json.loads(r.stdout)
        except Exception:time.sleep(3)
    return None
# scrims
rows=[]
for g in json.load(open('/home/claude/data/ab/groups.json')):
    d=cambc(['match-groups','show',g['group'],'--json'])
    if not d:continue
    for m in d['matches']:
        us=[t for t in m['teams'] if t['teamId']==ME][0]
        rows.append({'test':g['tag'],'label':META['labels'].get(g['tag'],g['tag']),'opp':g['name'],'map':m['map'],'result':us['result'] or m['status'],'created':m['createdAt'][:16].replace('T',' ')})
# ranked
rl=cambc(['matches','list','--team',ME,'--kind','ranked','--limit','100','--json']) or {'matches':[]}
rr=[m for m in rl['matches'] if m['status']=='finished']
def ver(ch):
    if '5' in ch or ch==['9','4','3']:return 'V8 onwards'
    if ch[:3]==['8','4','3']:return 'V7 (checkpoints 1-2)'
    return 'Other'
names={'0':'Ryth','3':'Cassi & Issac','4':'Stellar','5':'Prism','8':'Ren','9':'Varg','10':'Tavi'}
lad=cambc(['ladder','--json','--page','1','--limit','1'])
q=cambc(['match-groups','quota','--json']) or {}
rank=q.get('requesterRank','?')
F='Arial';H=Font(name=F,bold=True,color='FFFFFF');HF=PatternFill('solid',fgColor='1F3864');B=Font(name=F);BB=Font(name=F,bold=True);BLUE=Font(name=F,color='0000FF')
wb=Workbook()
def header(ws,row,cols):
    for i,c in enumerate(cols,1):
        x=ws.cell(row=row,column=i,value=c);x.font=H;x.fill=HF;x.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
def widths(ws,w):
    for i,v in enumerate(w,1):ws.column_dimensions[get_column_letter(i)].width=v
ws2=wb.active;ws2.title='Ladder scrims'
header(ws2,1,['Test tag','Version','Opponent','Map','Result','Win (1/0)','Queued (UTC)'])
for i,r in enumerate(rows,2):
    for j,v in enumerate([r['test'],r['label'],r['opp'],r['map'],r['result']],1):ws2.cell(row=i,column=j,value=v).font=B
    ws2.cell(row=i,column=6,value=f'=IF(E{i}="win",1,IF(E{i}="loss",0,""))').font=B
    ws2.cell(row=i,column=7,value=r['created']).font=B
n2=max(2,len(rows)+1);widths(ws2,[11,26,22,13,9,10,17]);ws2.freeze_panes='A2'
t=Table(displayName='Scrims',ref=f'A1:G{n2}');t.tableStyleInfo=TableStyleInfo(name='TableStyleLight9',showRowStripes=True);ws2.add_table(t)
ws3=wb.create_sheet('Ranked games')
header(ws3,1,['Played (UTC)','Version','Opponent','Map','Our draft','Result','Win (1/0)'])
for i,m in enumerate(rr,2):
    us=[t for t in m['teams'] if t['teamId']==ME][0];th=[t for t in m['teams'] if t['teamId']!=ME][0]
    for j,v in enumerate([m['createdAt'][:16].replace('T',' '),ver(us['characters']),th['name'],m['map'],', '.join(names.get(c,c) for c in us['characters']),us['result']],1):ws3.cell(row=i,column=j,value=v).font=B
    ws3.cell(row=i,column=7,value=f'=IF(F{i}="win",1,IF(F{i}="loss",0,""))').font=B
n3=max(2,len(rr)+1);widths(ws3,[17,20,24,13,40,8,10]);ws3.freeze_panes='A2'
t=Table(displayName='Ranked',ref=f'A1:G{n3}');t.tableStyleInfo=TableStyleInfo(name='TableStyleLight9',showRowStripes=True);ws3.add_table(t)
# local tests (static benchmark results)
ws4=wb.create_sheet('Local tests')
header(ws4,1,['Version','Change tested','Opponent','Wins','Games','Win rate'])
local=json.load(open('/home/claude/data/ab/local.json'))
for i,(v,c,o,w) in enumerate(local['rows'],2):
    for j,x in enumerate([v,c,o],1):ws4.cell(row=i,column=j,value=x).font=B
    ws4.cell(row=i,column=4,value=w).font=BLUE;ws4.cell(row=i,column=5,value=34).font=BLUE
    x=ws4.cell(row=i,column=6,value=f'=IF(E{i}=0,"",D{i}/E{i})');x.font=B;x.number_format='0%'
r=len(local['rows'])+3
ws4.cell(row=r,column=1,value='Source: local cambc run-batch benchmarks, all 17 pool maps from both sides (34 games per row). Blue = hardcoded results.').font=Font(name=F,italic=True)
r+=2;ws4.cell(row=r,column=1,value='Uncontested speed vs starter bot').font=BB
header(ws4,r+1,['Version','Mean rounds to 1000 gems','','','',''])
for k,(v,s) in enumerate(local['speed'],r+2):
    ws4.cell(row=k,column=1,value=v).font=B;ws4.cell(row=k,column=2,value=s).font=BLUE
widths(ws4,[16,42,16,8,8,10]);ws4.freeze_panes='A2'
# summary
ws=wb.create_sheet('Summary',0)
ws['A1']='Polaris testing results';ws['A1'].font=Font(name=F,bold=True,size=14)
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).strftime('%H:%M')
ws['A2']=f'Team LionelMSISS, ladder rank {rank}. Updated {now} (UK). Live submission: {META["live"]}.';ws['A2'].font=Font(name=F,italic=True)
ws['A4']='Real-ladder scrims by version';ws['A4'].font=BB
header(ws,5,['Test tag','Version','Matches finished','Wins','Win rate','Note'])
order=list(dict.fromkeys(r['test'] for r in rows))
for i,tg in enumerate(order,6):
    ws.cell(row=i,column=1,value=tg).font=B;ws.cell(row=i,column=2,value=META['labels'].get(tg,tg)).font=B
    ws.cell(row=i,column=3,value=f"=COUNTIFS('Ladder scrims'!$A$2:$A${n2},A{i},'Ladder scrims'!$F$2:$F${n2},\">=0\")").font=B
    ws.cell(row=i,column=4,value=f"=SUMIFS('Ladder scrims'!$F$2:$F${n2},'Ladder scrims'!$A$2:$A${n2},A{i})").font=B
    x=ws.cell(row=i,column=5,value=f'=IF(C{i}=0,"",D{i}/C{i})');x.font=B;x.number_format='0%'
    ws.cell(row=i,column=6,value=META['notes'].get(tg,'')).font=B
e=6+len(order)
ws.cell(row=e+1,column=1,value='Ranked ladder record by version').font=BB
header(ws,e+2,['Version','','Matches','Wins','Win rate','Note'])
for k,(v,nt) in enumerate([('V7 (checkpoints 1-2)','Earlier, at lower rank'),('V8 onwards','Later, against stronger opponents')],e+3):
    ws.cell(row=k,column=1,value=v).font=B
    ws.cell(row=k,column=3,value=f"=COUNTIFS('Ranked games'!$B$2:$B${n3},A{k},'Ranked games'!$G$2:$G${n3},\">=0\")").font=B
    ws.cell(row=k,column=4,value=f"=SUMIFS('Ranked games'!$G$2:$G${n3},'Ranked games'!$B$2:$B${n3},A{k})").font=B
    x=ws.cell(row=k,column=5,value=f'=IF(C{k}=0,"",D{k}/C{k})');x.font=B;x.number_format='0%'
    ws.cell(row=k,column=6,value=nt).font=B
m=e+6
ws.cell(row=m,column=1,value='Real-ladder results by map (all scrims)').font=BB
header(ws,m+1,['Map','','Matches','Wins','Win rate',''])
for k,mp in enumerate(sorted(set(r['map'] for r in rows)),m+2):
    ws.cell(row=k,column=1,value=mp).font=B
    ws.cell(row=k,column=3,value=f"=COUNTIFS('Ladder scrims'!$D$2:$D${n2},A{k},'Ladder scrims'!$F$2:$F${n2},\">=0\")").font=B
    ws.cell(row=k,column=4,value=f"=SUMIFS('Ladder scrims'!$F$2:$F${n2},'Ladder scrims'!$D$2:$D${n2},A{k})").font=B
    x=ws.cell(row=k,column=5,value=f'=IF(C{k}=0,"",D{k}/C{k})');x.font=B;x.number_format='0%'
widths(ws,[22,28,17,8,10,52])
# top teams vs us (per-team averages from match summaries)
try:
    import statistics as _st
    FR=json.load(open('/home/claude/data/feat.json'))
    def _g(r):
        if r['label']=='US':return 'Us (LionelMSISS)'
        if r['label']=='OPP':return 'Our opponents'
        return 'Top-10 teams' if int(r['label'][3:])<=10 else 'Top 11-50 teams'
    G={}
    for r in FR:G.setdefault(_g(r),[]).append(r)
    cols=[c for c in ['Top-10 teams','Top 11-50 teams','Us (LionelMSISS)','Our opponents'] if c in G]
    ws5=wb.create_sheet('Top teams vs us')
    ws5['A1']='How the top-50 teams play compared with us (average per team per game)';ws5['A1'].font=BB
    header(ws5,2,['Metric']+cols+['What it means'])
    MET=[('Games','n',''),('Win rate','win','Fraction of games won'),('Gems by round 200','g200','Early farming pace'),('Gems by round 400','g400','Mid-game pace'),
         ('First tribute (round)','first_score','Lower = banks earlier'),('First item bought (round)','first_buy','Lower = shops earlier'),('Gold by round 200','gold200','Early economy'),
         ('Deaths','deaths','Each death gives the killer 50 gold and our carried gems'),('Kills','kills',''),('Gems lost on death','lost_gems',''),
         ('Big-camp captures (30+ gems)','big_camps',''),('Ward placements','wards','Wards can be moved every round'),('Altar locks bought','locks','10 gold: blocks enemy tributes'),
         ('Teleport crystals bought','tps',''),('Damage to champions','champ_dmg','How much they fight'),('Damage to camps','mon_dmg','')]
    for i,(lab,k,why) in enumerate(MET,3):
        ws5.cell(row=i,column=1,value=lab).font=B
        for j,c in enumerate(cols,2):
            v=len(G[c]) if k=='n' else _st.mean([float(r[k]) for r in G[c] if r[k] is not None] or [0])
            x=ws5.cell(row=i,column=j,value=round(v,2));x.font=BLUE;x.number_format='0' if k!='win' else '0%'
        ws5.cell(row=i,column=2+len(cols),value=why).font=B
    rr5=3+len(MET)+1
    ws5.cell(row=rr5,column=1,value='Source: cambc match summaries. Top teams = ranked games between two top-50 teams (sample weighted to contest, swirl, fragment, collision, rushbait_v2); us = our last 100 ranked games. Blue = computed values.').font=Font(name=F,italic=True)
    widths(ws5,[30,16,16,18,16,52]);ws5.freeze_panes='B3'
except Exception as _e:
    print('top tab skipped',_e)
wb.save(OUT)
r=subprocess.run(['python3','scripts/recalc.py',OUT,'60'],capture_output=True,text=True,cwd='/root/.claude/skills/synced/49bc620a-f9f3-4fbf-9988-71b28a07cb10_7ff86389-32d3-4974-9613-23bcacef32c0/xlsx')
res=json.loads(r.stdout)
print('rows',len(rows),'ranked',len(rr),'rank',rank,'recalc',res.get('status'),res.get('total_errors'))
