"""Small follow-up arms after v2 lost its parent checks. Do not overwrite the controls."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]

def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b)

def build():
    for name in ('solo','hunt','herd'):
        p=ROOT/'bots'/('fz_'+name+'_v3')
        shutil.copytree(ROOT/'bots'/('fz_'+name),p,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.cambc'))
        f=p/'src/bot.cpp';s=f.read_text()
        if name=='solo':
            s=replace(s,'me.gold_count()>=180&&me.gem_count()==0&&capturing<0',
                      'me.gold_count()>=120&&me.gem_count()<=22&&capturing<0')
        if name=='hunt':
            s=replace(s,'double need=.45;   // FAUX: aggressive',
                      'double need=.85;   // v3: require a closer local fight before hunting')
        f.write_text(s)
        if name=='herd':
            f=p/'src/draft.cpp';s=f.read_text()
            s=replace(s,'order = {C::varg, C::stellar, C::tavi, C::ren}',
                      'order = {C::cassi_and_issac, C::stellar, C::varg, C::ren}')
            s=replace(s,'order = {C::varg, C::stellar, C::tavi, C::cassi_and_issac, C::ren, C::ryth}',
                      'order = {C::cassi_and_issac, C::stellar, C::tavi, C::prism, C::ren, C::varg}')
            f.write_text(s)

if __name__=='__main__':build()
