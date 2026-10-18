"""Reproducibly build isolated local-only opponents from the preserved fz_* parents."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]

def replace(s, old, new):
    assert old in s, old[:100]
    return s.replace(old, new)

def build(profile):
    parent = ROOT / 'bots' / ('fz_' + profile)
    dest = ROOT / 'bots' / ('fz_' + profile + '_v2')
    shutil.copytree(parent, dest, dirs_exist_ok=True,ignore=shutil.ignore_patterns('.cambc'))
    p = dest / 'src/bot.cpp'
    s = p.read_text()
    s = replace(s, '#include "bot.h"', '#include "bot.h"\n#include "faux_policy.h"')
    # Correct the group estimate using the same legal visible monster snapshots already collected.
    s = replace(s, 'for(auto& m:monsters)if(m.group==static_cast<int>(i))hp=std::min(hp,static_cast<double>(m.hp));', '''for(auto& m:monsters)if(m.group==static_cast<int>(i)){
            double base,unused;camp_stats_for(m.handle.kind(),base,unused);
            hp=faux::remaining_hp(hp,base,m.hp);
        }''')
    # Unseen members remain at full HP. Do not erase dead/hidden members by guessing.
    s = replace(s, 'if(leader!=slot&&current>=0){', 'if(current>=0&&banned(current))current=-1;\n    if(leader!=slot&&current>=0){')
    s = replace(s, '&&round<solo_choose+8){', '&&round<solo_choose+8&&!banned(objective)){')
    s = replace(s, 'if(sg.reward){target=st;}', 'if(banned(st)){}\n        else if(sg.reward){target=st;}')
    s = replace(s, 'if(target<0){', 'if(target>=0&&banned(target))target=-1;\n    if(target<0){')
    # Lifecycle reset precedes every channel/combat/healing early return.
    s = replace(s, '    update_profile();\n    if(!me.is_alive()){', '''    update_profile();
    if(!me.is_alive()||me.gem_count()==0){bag_since=-1;bank_alone_since=-1;bank_wait=0;tribute_cancels=0;}
    if(!me.is_alive()){capturing=-1;capture_since=-1;capture_group=-1;objective=-1;
        pursuit_target=0;pursuit_since=-1;pursuit_block_until=round+10;
        siege_committed=-1;siege_started=-1;''')
    s = replace(s, '            capturing=-1;\n        }', '            capturing=-1;capture_since=-1;capture_group=-1;\n        }')
    s = replace(s, '        capturing=-1;\n    }\n    int target=', '        capturing=-1;capture_since=-1;capture_group=-1;\n    }\n    int target=')
    s = replace(s, 'if(spawn&&me.health()<me.max_health()*.98f&&enemies.empty())return;', 'if(spawn&&me.health()<me.max_health()*.98f&&threat(me.position())<=0)return;')
    # A distant enemy ward sighting must not strand a low-HP ward runner away from healing.
    s = replace(s, 'if(!herd_warded&&enemies.empty()&&me.gem_count()==0)', 'if(!herd_warded&&!spawn&&me.health()>=me.max_health()*.7f&&enemies.empty()&&me.gem_count()==0)')
    # Count only successful cancellations; both reasons share the bound.
    start=s.index('        const bool outnumbered=their>our', s.index('if(me.is_submitting_gems())'))
    end=s.index('\n    }\n    const bool spawn=',start)
    s=s[:start]+'''        const bool danger=their>our&&me.gem_count()>=30&&me.remaining_channel_time()>2;
        const bool lethal=threat(me.position())*std::max(1,me.remaining_channel_time())>me.health()*1.2;
        if(faux::cancel_allowed(danger||lethal,tribute_cancels,me.gem_count(),me.remaining_channel_time())){
            bool cancelled=false;try{me.cancel_submit_gems();cancelled=true;}catch(const error&){}
            if(cancelled)++tribute_cancels;else return;
        }else return;'''+s[end:]
    # Do not let a generic fight routine divert to camp damage when asked to engage a player.
    s = replace(s, '    scoring_enemy=-1;\n    for(unsigned i=0;i<monsters.size();++i)', '    scoring_enemy=-1;\n    if(!players||target<0)for(unsigned i=0;i<monsters.size();++i)')
    # Bound target episodes, including blocked approaches. Carrying a valuable bag takes priority.
    s = replace(s, '            move_to(disk(e.pos,me.attack_range()));combat(-1,true);log("chase");return true;', '''            if(!pursuit_allowed(e))continue;
            bool moved=move_to(disk(e.pos,me.attack_range()));
            bool hit=combat(-1,true);
            if(moved||hit){log("chase");return true;}
            pursuit_block_until=round+8;
            break;''')
    s = replace(s, '         if(tgt){move_to(disk(tgt->pos,me.attack_range()));combat(-1,true);log("engage");return true;}', '''         if(tgt&&pursuit_allowed(*tgt)){
             bool moved=move_to(disk(tgt->pos,me.attack_range()));bool hit=combat(-1,true);
             if(moved||hit){log("engage");return true;}
             pursuit_block_until=round+8;
         }}
        // No blind farming while a blocked approach leaves us in immediate threat.
        if(threat(pos)>0){move_to(map::spawn_region(team::ally),true);log("disengage");return true;''')
    # Travel through walls is not distance. Reuse the existing eight-round commitment budget.
    s = replace(s, '    solo_choose=round;\n    int best=', '''    solo_choose=round;
    if(fuel_remaining()<45000&&objective>=0&&!banned(objective))return objective;
    bitboard reachable;distance_field solo_field;
    solo_field.compute(terrain,disk(me.position(),0),reachable,100);
    int best=''')
    s = replace(s, '        int travel=dist(me.position(),g.center);', '''        int travel=100000;
        for(auto q:g.probes)travel=std::min<int>(travel,solo_field.get(q));
        if(travel>=static_cast<int>(distance_field::unreachable))continue;''')
    # Keep observation, pursuit state and helpers local: no extra shared-memory bytes.
    where=s.index('bool Bot::handle_enemies()')
    s=s[:where]+'''bool Bot::pursuit_allowed(const Enemy& e){
    const unsigned who=id(e.handle);
    if(round<pursuit_block_until)return false;
    if(pursuit_since<0||round>pursuit_last+1){pursuit_since=round;pursuit_target=who;}
    // Switching victims inside an active episode does not refresh its budget.
    pursuit_target=who;pursuit_last=round;
    const int bag=static_cast<int>(self().gem_count());
    if(!faux::pursuit_budget(round-pursuit_since,bag,e.channel,e.gems)){
        pursuit_since=-1;pursuit_block_until=round+12;return false;
    }
    return true;
}

'''+s[where:]
    if profile == 'solo':
        s = replace(s, 'pack_mode=false;   // FAUX: always solo', '''// Independent farmers on ordinary income; one coordinated pack for a sole huge source.
    double ordinary=0,huge=0;
    for(auto& g:groups)if(g.gems>0){if(g.monolith||g.probes.size()>=8)huge+=g.gems;else ordinary+=g.gems;}
    pack_mode=huge>0&&ordinary==0;''')
        s = replace(s, 'if(!g.reward&&g.str*clear*.6>my_hp*1.1)continue;', 'if(!g.reward&&g.str*clear*(g.probes.size()==1?1.0:.45)>my_hp*.90)continue;')
        s = replace(s, 'if(!pack_mode&&gem_camps&&round>=120', 'if(!pack_mode&&gem_camps&&round>=500')
    if profile == 'herd':
        s = replace(s, 'if(g.probes.size()<8&&incoming>pack_hp*.8*starved)continue;   // FAUX: herds always allowed', 'if(incoming>pack_hp*.8*std::min(starved,1.15))continue; // no suicidal herd exception')
        # Force the herd policy into pack play even when an open-map width override ran.
        s = replace(s, '    int k_squads=POLARIS_SQUADS;', '''    for(auto& g:groups)if(g.gems>0&&(g.monolith||g.probes.size()>=8))pack_mode=true;
    int k_squads=POLARIS_SQUADS;''')
    if profile == 'hunt':
        s = replace(s, 'double need=.45;   // FAUX: aggressive', '''// Aggressive at home, but stop converting an HP deficit into free enemy income.
    double need=home_d<=5?.50:.85;
    if(me.health()<me.max_health()*.55f||me.gem_count()>=40)need=1.15;''')
        s = replace(s, 'e.hp<burst*3.5', 'e.hp<burst*2.0')
    if profile == 'tank':
        s = replace(s, 'order={B,D,B,P}', 'order={B,P,D,P}')
    # Preserve siege commitment until capture, visible respawn, or a timed recovery, not one turn.
    s = replace(s, '        auto& sg=groups[st];', '''        auto& sg=groups[st];
        if(siege_committed==st&&siege_started>=0&&round>=static_cast<unsigned>(siege_started+150)){
            ban(st,90);siege_committed=-1;siege_started=-1;
        }
        if(sg.reward||sg.ready_round>round+25){siege_committed=-1;siege_started=-1;}
        if(siege_committed==st&&!banned(st))target=st;''')
    s = replace(s, '        else{\n            int here=0;', '        else if(siege_committed!=st){\n            int here=0;')
    s = replace(s, '{target=st;siege_wait_since=-1;}', '{target=st;siege_committed=st;siege_started=round;siege_wait_since=-1;}')
    p.write_text(s)
    h=dest/'src/bot.h'
    h.write_text(replace(h.read_text(), '    bool handle_enemies();', '''    bool handle_enemies();
    bool pursuit_allowed(const Enemy& e);
    unsigned pursuit_target=0,pursuit_last=0,pursuit_block_until=0;
    int pursuit_since=-1,siege_committed=-1,siege_started=-1;'''))
    shutil.copy(ROOT/'tests/faux_policy.h',dest/'src/faux_policy.h')

if __name__ == '__main__':
    for name in ('herd','solo','hunt','tank'):build(name)
