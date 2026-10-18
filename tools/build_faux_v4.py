"""Two small execution hypotheses; preserve all earlier arms and parents."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
for name in ('solo','herd'):
    p=ROOT/'bots'/('fz_'+name+'_v4')
    shutil.copytree(ROOT/'bots'/('fz_'+name),p,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.cambc'))
    f=p/'src/bot.cpp';s=f.read_text()
    a,b=('order={J,P,D,P};','order={J,D,P,P};') if name=='solo' else ('#define POLARIS_SIEGE_R 150','#define POLARIS_SIEGE_R 600')
    assert a in s
    f.write_text(s.replace(a,b))
