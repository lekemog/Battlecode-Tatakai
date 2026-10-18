"""Submit a bot with a brief comment. usage: submit.py BOT ["comment"]
- comment defaults to data/bot_notes.json[BOT]; required one way or the other
- writes the comment as a header block in src/main.cpp (visible in the platform's source view)
- logs version, bot, time and comment to data/submissions.json and the repo's SUBMISSIONS.md"""
import json,os,re,subprocess,sys,time
PROJ='/home/claude/proj';NOTES='/home/claude/data/bot_notes.json';LOG='/home/claude/data/submissions.json'
REPO='/home/claude/battlecodeconversation/SUBMISSIONS.md'
bot=sys.argv[1];notes=json.load(open(NOTES)) if os.path.exists(NOTES) else {}
comment=sys.argv[2] if len(sys.argv)>2 else notes.get(bot)
if not comment:sys.exit(f'no comment for {bot}: pass one or add it to {NOTES}')
notes[bot]=comment;json.dump(notes,open(NOTES,'w'),indent=1)
mp=f'{PROJ}/bots/{bot}/src/main.cpp';src=open(mp).read()
src=re.sub(r'^// SUBMISSION NOTE.*?// END NOTE\n','',src,flags=re.S)
open(mp,'w').write(f'// SUBMISSION NOTE ({bot}, {time.strftime("%Y-%m-%d %H:%M UTC",time.gmtime())})\n// {comment}\n// END NOTE\n'+src)
for t in range(6):
    r=subprocess.run(['cambc','submit',f'bots/{bot}'],capture_output=True,text=True,cwd=PROJ)
    m=re.search(r'version (\d+)',r.stdout+r.stderr)
    if m:break
    w=re.search(r'retry after (\d+)',r.stdout+r.stderr);time.sleep(int(w.group(1))+1 if w else 10)
ver=int(m.group(1)) if m else None
print(f'Submitted bot version {ver} ({bot}): {comment}',flush=True)
log=json.load(open(LOG)) if os.path.exists(LOG) else []
log.append({'version':ver,'bot':bot,'at':time.strftime('%Y-%m-%dT%H:%MZ',time.gmtime()),'comment':comment});json.dump(log,open(LOG,'w'),indent=1)
if not os.path.exists(REPO):open(REPO,'w').write('# Submission log\n\n| Version | Bot | Time (UTC) | Comment |\n|---|---|---|---|\n')
open(REPO,'a').write(f'| {ver} | {bot} | {log[-1]["at"]} | {comment} |\n')
