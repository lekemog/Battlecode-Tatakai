// Polaris V9 — adaptive squads, map-type rules, carrier safety, bag hunting, invasion-aware posture, map-aware draft. Cambridge Battlecode 2026a.
#include "bot.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <span>
#include <variant>

using namespace cambc;

namespace {
int dist(vec2 a,vec2 b){return a.chebyshev_distance(b);}
unsigned id(const champion& c){return static_cast<unsigned>(static_cast<handle_champion_t>(c));}
bitboard disk(vec2 p,int r){bitboard b;b.clear();b.draw_chebyshev(p,r);return b;}
// Chebyshev dilation with separable shifts: far cheaper than drawing a disk per tile.
bitboard grow(bitboard b,int r){
    for(int i=0;i<r;++i){b|=b.shift_right(1)|b.shift_right(-1);b|=b.shift_up(1)|b.shift_up(-1);}
    return b;
}
// Documented base stats per camp type; avoids a host query per camp at start-up.
void camp_stats_for(camp_type k,double& hp,double& str){
    switch(k){
    case camp_type::wolf:hp=1350;str=20;break;
    case camp_type::elk:hp=2400;str=60;break;
    case camp_type::monolith:hp=20000;str=200;break;
    default:hp=500;str=0;break;
    }
}
float spell_range(const ability& a){return std::visit([](const auto& x)->float{
    if constexpr(requires{x.range;})return x.range;else return 0;},*a.info());}
float spell_modifier(const ability& a){return std::visit([](const auto& x)->float{
    if constexpr(requires{x.modifier;})return x.modifier;else return 0;},*a.info());}
// Shared memory (pack mode): 0-2 squad targets, 3-5 capture claim, 6 aggression estimate,
// 7 last capturer. Solo mode: 0..n-1 per-champion targets, 6 aggression, 7 threat cell.
constexpr std::uint8_t kTarget=0,kClaimGroup=3,kClaimSlot=4,kClaimStamp=5,kAggression=6,kAltarSeen=7;
#ifndef POLARIS_SIEGE_R
#define POLARIS_SIEGE_R 600
#endif
#ifndef POLARIS_SQUADS
#define POLARIS_SQUADS 3
#endif
#ifndef POLARIS_MIN_SQUAD
#define POLARIS_MIN_SQUAD 2
#endif
bool is_carry(champion_type t){return t==champion_type::stellar||t==champion_type::tavi||t==champion_type::prism||t==champion_type::cassi||t==champion_type::willow||t==champion_type::vesper_vale;}
bool has_stun_kit(champion_type t){return t==champion_type::tavi||t==champion_type::ren||t==champion_type::ryth||t==champion_type::prism||t==champion_type::cassi||t==champion_type::marcella;}
unsigned age(unsigned now,std::uint8_t stamp){return (now-stamp)&0xFFu;}
}

void Bot::write_byte(int index,std::uint8_t value){
    shared[index]=value;
    try{shared_memory.write(index,std::span{&value,1});}catch(const error&){}
}

void Bot::init(){
    // Set-up is split into resumable phases: on big maps the whole thing costs more than
    // one turn of fuel, and a restarted set-up must never duplicate state.
    auto& me=self();
    auto room=[&](std::uint64_t need){return fuel_remaining()>need;};
    while(!initialized){
        switch(init_phase){
        case 0:{
            terrain=map::walls()|map::holes()|map::altars()|map::spawn_region(team::enemy);
            roster=champions(team::ally);enemy_roster=champions(team::enemy);
            std::sort(roster.begin(),roster.end(),[](const auto&a,const auto&b){return id(a)<id(b);});
            team_size=static_cast<int>(roster.size());
            for(unsigned i=0;i<roster.size();++i)if(id(roster[i])==id(me))slot=static_cast<int>(i);
            altar_goals.clear();
            for(auto p:map::altars().positions())altar_goals|=disk(p,constants::submit_gems_range);
            altar_goals&=~terrain;
            enemy_base=grow(map::spawn_region(team::enemy),1);
            init_phase=1;break;}
        case 1:{if(!room(45000))return;bitboard seen;altar_distance.compute(terrain,altar_goals,seen);init_phase=2;break;}
        case 2:{if(!room(45000))return;bitboard seen;home_distance.compute(terrain,map::spawn_region(team::ally),seen);init_phase=3;break;}
        case 3:{if(!room(45000))return;bitboard seen;enemy_distance.compute(map::walls()|map::holes()|map::altars(),map::spawn_region(team::enemy),seen);init_phase=4;break;}
        case 4:{if(!room(45000))return;pending_groups=map::camp_groups();groups.clear();all_spawns.clear();init_next=0;init_phase=5;break;}
        case 5:{
            while(init_next<pending_groups.size()){
                if(!room(15000))return;
                auto g=pending_groups[init_next++];
                Group v{g,g.spawn_tiles()};
                all_spawns|=v.spawns;
                int x=0,y=0;
                for(auto c:g.camps()){
                    double hp,str;const auto k=c.kind();camp_stats_for(k,hp,str);
                    v.hp+=hp;v.str+=str;
                    const auto p=c.spawn_position();
                    x+=p.x;y+=p.y;v.probes.push_back(p);
                    if(k==camp_type::monolith)v.monolith=true;
                    if(k==camp_type::elk)++v.elks;
                }
                int n=std::max<int>(1,static_cast<int>(g.camps().size()));
                v.center={x/n,y/n};
                v.gems=static_cast<int>(g.gem_value());v.gold=static_cast<int>(g.gold_value());
                v.respawn=g.max_respawn_timer();
                v.home_d=v.enemy_d=v.altar_d=100000;
                for(auto p:v.probes){
                    v.home_d=std::min<int>(v.home_d,home_distance.get(p));
                    v.enemy_d=std::min<int>(v.enemy_d,enemy_distance.get(p));
                    v.altar_d=std::min<int>(v.altar_d,altar_distance.get(p));
                }
                groups.push_back(v);
            }
            pending_groups.clear();init_phase=6;break;}
        default:{
    // Pack play only pays when there are gem camps a group can clear; otherwise spread out on gold.
    // Reference champion (shared by every teammate so all agree on the mode): 800 HP, 60 DPS.
    double solo_gems=0,pack_gems=0;
    for(auto& g:groups){
        if(g.gems<=0||g.monolith)continue;
        bool solo=g.str<=0||g.str*(g.hp/60.0)*.6<800*.6;
        (solo?solo_gems:pack_gems)+=g.gems*60.0/std::max(30,g.respawn);
    }
    pack_mode=pack_gems>0&&(pack_gems>solo_gems||team_size>=4);
    if(solo_gems+pack_gems>0&&team_size>=4)pack_mode=true;
    // Big open maps are farming races: top-100 teams split up and solo camps in parallel (corners:
    // 42 captures vs our 14 with zero deaths either side). Farm solo there.
    // v24i: per-map farming mode. A 7-opponent bench of always-solo vs the default (490 games each, data/p5_bench.txt)
    // lost clearly fewer games solo on these maps (losses default -> solo, of 14): yellow_brick_road 11->5,
    // ambush 6->2, rushbait_v2 7->4, fracture 9->7, elk_arena 2->0. Ranked uses a fixed 35-map pool; the
    // fingerprint (width, height, altars, camp groups, camps) is unique across it (data/mapfp.txt).
    {const int W=map::width(),H=map::height(),A=static_cast<int>(map::altars().count());
     int G=0,C=0;for(auto g:map::camp_groups()){++G;for(auto c:g.camps()){(void)c;++C;}}
     struct FP{int w,h,a,g,c;};
     static const FP solo_maps[]={{40,30,10,28,160},{100,100,4,12,46},{30,80,2,18,44},{61,71,3,28,86},{50,50,2,29,62},{35,31,3,34,78},{50,40,4,17,80},{40,40,2,51,132}};   // v24z: + road_of_riches (new map)   // v24w: + lost_world, great_wall (new maps)
     for(auto& f:solo_maps)if(f.w==W&&f.h==H&&f.a==A&&f.g==G&&f.c==C){forced_solo=true;break;}}
    if(forced_solo)pack_mode=false;
    // v24n: per-map tuning from 7-opponent benches on the 13 weakest maps (losses of 14, v24k -> variant):
    // smaller banks: rows 6->3, pilgrimage 5->2, gold_rush 6->5, split 5->4; bolder pack: shortcut 7->6, starvation 4->3.
    {const int W=map::width(),H=map::height(),A=static_cast<int>(map::altars().count());
     int G=0,C=0;for(auto g:map::camp_groups()){++G;for(auto c:g.camps()){(void)c;++C;}}
     struct FP{int w,h,a,g,c;};
     static const FP small_bank_maps[]={{50,50,2,9,54},{50,65,4,23,70},{31,31,4,15,41},{45,35,3,32,86}};
     static const FP bold_pack_maps[]={{40,40,2,21,86},{80,80,2,14,40}};
     for(auto& f:small_bank_maps)if(f.w==W&&f.h==H&&f.a==A&&f.g==G&&f.c==C)small_banks=true;
     for(auto& f:bold_pack_maps)if(f.w==W&&f.h==H&&f.a==A&&f.g==G&&f.c==C)bold_pack=true;
     // v24v: GPT's opponent-response idea, fixed-caution arm (Claude-tuned), only where it won on the 7-opp bench:
     // split 5->1 and corners 4->2 losses of 14 (elsewhere neutral or worse, e.g. gold_rush 5->8).
     static const FP caution_maps[]={{45,35,3,32,86},{71,71,5,30,74}};
     for(auto& f:caution_maps)if(f.w==W&&f.h==H&&f.a==A&&f.g==G&&f.c==C)opp_on=true;}
    // v24k: contest (gem-less, siege map) plays far better as a pack: always-pack bench lost 2/14 vs 6/14 (7 opponents).
    if(map::width()==50&&map::height()==50&&map::altars().count()==2){int G=0,C=0;for(auto g:map::camp_groups()){++G;for(auto c:g.camps()){(void)c;++C;}}if(G==14&&C==34)forced_pack=true;}
    {const int W=map::width(),H=map::height();if(std::max(W,H)>=75&&std::max(W,H)<100&&W*H>=2500)pack_mode=false;}
    if(forced_pack)pack_mode=true;   // expanse, lanes (W11: corners was worse)
    // Gem-less maps with a monolith: gems beat gold at the round limit, so one monolith wins.
    if(pack_gems<=0&&solo_gems<=0){
        int best=100000;
        for(unsigned i=0;i<groups.size();++i)if(groups[i].monolith&&groups[i].gems>0&&groups[i].home_d<best){best=groups[i].home_d;siege_group=static_cast<int>(i);}
    }
    // Spend gold on whichever stat adds more damage per round for this champion.
    auto st=me.base_stats();double resets=0,spells=0;
    for(auto a:me.abilities()){
        if(!a.info())continue;
        if(a.is_attack_reset())resets+=1;
        if(a.is_damage()||a.is_cc())spells+=spell_modifier(a);
        if(a.is_aoe_damage())spells+=spell_modifier(a)*1.6; // camps come in clusters
    }
    double strength_value=st.strength_growth*(1+resets/8.0);
    double focus_value=st.focus_growth*spells/8.0;
    // Passives change the maths: Ren retaliates 0.2 x focus against every attacker (camps
    // come in packs of 3-4), and Varg's basic attacks splash onto neighbouring camps.
    if(me.champion_name()==champion_type::ren)focus_value+=st.focus_growth*.2*2.5;
    if(me.champion_name()==champion_type::varg)strength_value*=1.8;
    focus_build=focus_value>strength_value*1.05;
    frontline=!is_carry(me.champion_name());
    plan_team();
    last_pos=me.position();initialized=true;
            break;}
        }
    }
}


// Every champion computes the same plan from the same inputs, so no communication is needed.
void Bot::plan_team(){
    // Enemy composition: identified at round 0 from their roster.
    for(const auto& c:enemy_roster){
        champion_type t=champion_type::ryth;
        try{t=c.champion_name();}catch(const error&){continue;}
        if(t==champion_type::cassi)enemy_has_cassi=true;
        if(has_stun_kit(t))++enemy_stuns;
    }
    // Stun-heavy or dive comps (several stuns, or Ren/Tavi/Ryth together) tend to invade early.
    enemy_aggressive_comp=enemy_stuns>=4;
    // Roles: on pack maps with harmless gold clusters, one champion farms them alone (as the
    // top teams do) while the rest move as the gem squad.
    squad_members.clear();
    int farmer=-1;
    if(pack_mode&&team_size>=4){
        // Only worth a body if harmless gold near home pays roughly a champion's share.
        double rate=0;
        for(auto& g:groups)if(g.str<=0&&g.gold>0&&g.gems==0&&g.home_d<=g.enemy_d&&g.home_d<=22)
            rate+=g.gold/static_cast<double>(std::max(30,g.respawn)+g.home_d/2);
        const bool safe_gold=rate>=3.0;
        if(safe_gold){
            // Prefer Issac (the top teams' choice: sturdy, mobile), otherwise the last slot.
            // Audit (cycles 1-2): a lone Issac picked off kills Cassi too (17% of deaths were linked).
            // The farmer is the sturdiest non-carry outside the Cassi & Issac pair.
            farmer=-1;
            for(int k=team_size-1;k>=0&&farmer<0;--k){try{auto t=roster[k].champion_name();
                if(t!=champion_type::issac&&t!=champion_type::cassi&&!is_carry(t))farmer=k;}catch(const error&){}}
            if(farmer<0)farmer=team_size-1;
        }
    }
    // Gem squads: the top teams farm several camps at once with small squads and only group
    // up for big camps or fights. Squad count comes from the map: how much of the gem income a
    // pair can clear on its own (reference pair: 1600 HP, 120 DPS).
    std::vector<int> pool;
    for(int k=0;k<team_size;++k)if(k!=farmer)pool.push_back(k);
    auto type_of=[&](int k){try{return roster[k].champion_name();}catch(const error&){return champion_type::ryth;}};
    std::sort(pool.begin(),pool.end(),[&](int a,int b){
        bool ca=is_carry(type_of(a)),cb=is_carry(type_of(b));
        if(ca!=cb)return !ca;            // frontline first
        return a<b;
    });
    double duo_rate=0,big_rate=0;
    for(auto& g:groups){
        if(g.gems<=0||g.monolith)continue;
        const double clear=g.hp/120.0;
        const double rate=g.gems*60.0/std::max(30,g.respawn);
        (g.str*clear*.3<1600*.8?duo_rate:big_rate)+=rate;
    }
    int k_squads=POLARIS_SQUADS;
    k_squads=std::min<int>(k_squads,static_cast<int>(pool.size())/POLARIS_MIN_SQUAD);
    if(!pack_mode)k_squads=1;
    // Small maps (longest side under 50) are brawl maps: the enemy is never far, so the team
    // stays together as one pack.
    if(std::max(map::width(),map::height())<50)k_squads=1;
    k_squads=std::clamp(k_squads,1,3);
    if(k_squads>1)farmer=-1,pool.clear();
    if(k_squads>1){for(int k=0;k<team_size;++k)pool.push_back(k);
        std::sort(pool.begin(),pool.end(),[&](int a,int b){
            bool ca=is_carry(type_of(a)),cb=is_carry(type_of(b));
            if(ca!=cb)return !ca;
            return a<b;});}
    for(auto& v:all_squads)v.clear();
    if(k_squads>1){
        int ci=-1,ii=-1;
        for(int k:pool){if(type_of(k)==champion_type::cassi)ci=k;if(type_of(k)==champion_type::issac)ii=k;}
        for(int k:pool){
            if(k==ii&&ci>=0)continue;                     // placed with Cassi below
            int t=0;
            for(int s2=1;s2<k_squads;++s2)if(all_squads[s2].size()<all_squads[t].size())t=s2;
            all_squads[t].push_back(k);
            if(k==ci&&ii>=0)all_squads[t].push_back(ii);
        }
    } else all_squads[0]=pool;
    squads=k_squads;
    // Territories: our-side gem groups are split by angle around our spawn into one sector per
    // squad with equal gem income, so squads loop their own camps instead of crossing paths.
    if(k_squads>1){
        double hx=0,hy=0;int hn=0;
        for(auto p:map::spawn_region(team::ally).positions()){hx+=p.x;hy+=p.y;++hn;}
        hx/=std::max(1,hn);hy/=std::max(1,hn);
        std::vector<std::pair<double,int>> ang;double total=0;
        for(unsigned i=0;i<groups.size();++i){auto& g=groups[i];g.sector=-1;
            if(g.gems<=0||g.monolith||g.home_d>g.enemy_d+6)continue;
            ang.push_back({std::atan2(g.center.y-hy,g.center.x-hx),static_cast<int>(i)});
            total+=g.gems*60.0/std::max(30,g.respawn);}
        std::sort(ang.begin(),ang.end());
        // Start the sweep at the largest angular gap so a sector never wraps around behind spawn.
        int start=0;double gap=-1;
        for(unsigned j=0;j<ang.size();++j){double a=ang[j].first,b=j?ang[j-1].first:ang.back().first-2*M_PI;if(a-b>gap){gap=a-b;start=static_cast<int>(j);}}
        double acc=0;
        for(unsigned j=0;j<ang.size();++j){auto& g=groups[ang[(start+j)%ang.size()].second];
            const double r=g.gems*60.0/std::max(30,g.respawn);
            g.sector=std::min(k_squads-1,static_cast<int>((acc+r*.5)/std::max(1e-9,total)*k_squads));acc+=r;}
    }
    team_pool=pool;std::sort(team_pool.begin(),team_pool.end());
    role=slot==farmer?1:0;
    squad=0;
    for(int s2=0;s2<squads;++s2)for(int k:all_squads[s2])if(k==slot)squad=s2;
    for(auto& v:all_squads)std::sort(v.begin(),v.end());
    squad_members=all_squads[squad];
}

// Squads merge into one pack against invaders, and when starved of score.
bool Bot::merged() const {
    return squads<=1||!split_ok||defensive||(round>last_score_round+200&&round>300);
}

// Squads split only once each one is strong enough to farm most of our home income alone,
// judged from the members' current stats (the top teams open as five and split later).
bool Bot::ally_alive(int k) const {
    if(k==slot)return true;
    if(alive_round[k]!=round+1){alive_round[k]=round+1;bool a=true;try{a=roster[k].is_alive();}catch(const error&){}alive_val[k]=a;}
    return alive_val[k];
}

// Estimated damage per round of a set of roster slots, from their last seen stats.
double Bot::group_dps(const std::vector<int>& members,double& hp,double& tank) const {
    double d=0;hp=0;tank=0;
    for(int k:members){
        auto& st=ally_stats[k];
        if(st[2]<=0)continue;
        if(!ally_alive(k))continue;
        d+=st[0]+st[1]*.3;hp+=st[2];tank=std::max(tank,st[2]);
    }
    return d;
}

// Share of our home gem income a set of champions can farm without being forced home.
double Bot::farmable_share(const std::vector<int>& members,bool lenient) const {
    double hp,tank;const double d=group_dps(members,hp,tank);
    double total=0,can=0;
    for(auto& g:groups){
        if(g.gems<=0||g.monolith||g.home_d>g.enemy_d+6)continue;
        const double rate=g.gems*60.0/std::max(30,g.respawn);
        total+=rate;
        if(d<=0)continue;
        const double clear=g.hp/(d*.9);
        const double hit=g.probes.size()==1?1.0:g.probes.size()>=8?.45:g.elks>=1?.75:.3;
        const double budget=g.probes.size()==1?tank*(lenient?.75:.62):hp*(lenient?.85:.75);
        if(g.str*clear*hit<budget)can+=rate;
    }
    return total>0?can/total:-1;
}

// Squads split once each one can farm most of our home income alone (the top teams open as a
// pack and split later). When even the whole team cannot take our gem camps yet (one huge
// central group), squads split to farm gold for items, then regroup to take it.
void Bot::update_split(){
    if(squads<=1||(round<split_checked+5&&split_checked))return;
    split_checked=round;
    bool squads_can=true;
    for(int s2=0;s2<squads;++s2)if(farmable_share(all_squads[s2],split_ok)<.5)squads_can=false;
    const double team=farmable_share(team_pool,!split_ok);
    if(team<0){split_ok=true;return;}   // no regular gem camps: farm gold in pairs
    split_ok=squads_can||(team>=0&&team<.5);
}

int Bot::active_squad() const {return merged()?0:squad;}
const std::vector<int>& Bot::active_members() const {return merged()?team_pool:squad_members;}

int Bot::squad_leader() const {
    for(int k:active_members()){
        if(k==slot)return k;
        if(ally_alive(k))return k;
    }
    return slot;
}

void Bot::observe(){
    enemies.clear();monsters.clear();allies.clear();
    auto& me=self();visible=vision::visible_tiles();
    occupied=vision::champion_tiles()|vision::camp_tiles()|vision::teleport_tiles();
    occupied.set(me.position(),false);
    try{shared_memory.read(0,std::span{shared});}catch(const error&){}
    for(const auto& c:enemy_roster){
        if(!c.is_visible()||c.health()<=0)continue;
        if(enemy_base.is_set(c.position()))continue;
        enemies.push_back({c,c.position(),c.health(),c.max_health(),c.strength(),c.attack_range(),
            static_cast<int>(c.gem_count()),c.is_submitting_gems()});
        try{enemies.back().type=c.champion_name();}catch(const error&){}
        try{enemies.back().stunned=c.buffs().has_stun();}catch(const error&){}
        try{enemies.back().focus=c.focus();}catch(const error&){}
    }
    for(auto c:roster)if(id(c)!=id(me)&&c.is_visible()&&c.health()>0)allies.push_back(c);
    // Altar watch: the killer of a gem carrier takes the bag, so enemies near an altar make it
    // a kill zone. Sightings are shared in byte 7: altar index (3 bits) + 4-round stamp (5 bits).
    if(altar_pos.empty())for(auto a:map::altars().positions())altar_pos.push_back(a);
    if(altar_seen.size()!=altar_pos.size())altar_seen.assign(altar_pos.size(),0);
    if(pack_mode&&shared[kAltarSeen]){
        const int ai=(shared[kAltarSeen]>>5)-1;const unsigned st=shared[kAltarSeen]&31;
        if(ai>=0&&ai<static_cast<int>(altar_pos.size())){
            const unsigned now4=(round>>2)&31,ago=((now4-st)&31)*4;
            if(round>=ago)altar_seen[ai]=std::max(altar_seen[ai],round-ago);
        }
    }
    for(auto& e:enemies)for(unsigned a=0;a<altar_pos.size()&&a<7;++a)if(dist(e.pos,altar_pos[a])<=6){
        altar_seen[a]=round;
        if(pack_mode)write_byte(kAltarSeen,static_cast<std::uint8_t>(((a+1)<<5)|((round>>2)&31)));
    }
    threat_fresh=false;
    if(!pack_mode&&team_size<=6){
        // Solo threat marker in byte 7; freshness is tracked locally from when it last changed.
        const int W=static_cast<int>(map::width()),H=static_cast<int>(map::height());
        if(shared[7]!=last_threat_cell){last_threat_cell=shared[7];threat_cell_round=round;}
        if(shared[7]&&round-threat_cell_round<=8){
            threat_fresh=true;threat_x=((shared[7]>>4)&15)*W/16+W/32;threat_y=(shared[7]&15)*H/16+H/32;
        }
        if(!enemies.empty()){
            auto p=enemies.front().pos;
            std::uint8_t cell=static_cast<std::uint8_t>(((p.x*16/std::max(1,W))<<4)|(p.y*16/std::max(1,H)));
            if(cell==0)cell=1;
            if(cell!=shared[7]){write_byte(7,cell);last_threat_cell=cell;threat_cell_round=round;}
        }
    }
    // ---- Opponent model ----------------------------------------------------------------
    // Evidence that the enemy plays an invading / hunting style. Each champion adds what it
    // observes to a shared, slowly decaying score; the whole team switches posture on it.
    {
        double ev=0;
        for(auto& e:enemies){
            const int hd=home_distance.get(e.pos),ed=enemy_distance.get(e.pos);
            // Deep in our third of the map (not merely past the midline).
            if(hd<distance_field::unreachable&&ed<distance_field::unreachable&&hd*2+4<ed)ev+=.4;
            // Issue #17: "in our half" no longer counts: contesting a central altar is not invading.
            if(dist(e.pos,me.position())<=e.range+1)last_enemy_round=round;
        }
        const float hp=me.health();
        if(prev_hp>=0&&hp<prev_hp-1&&round-last_enemy_round<=1)ev+=.25;                         // hit by a champion
        prev_hp=hp;
        my_evidence+=ev;
        int a=shared[kAggression];
        // Prior from the draft: a stun-heavy comp starts us in the defensive posture.
        // Issue #17: the stun-draft prior (most top-100 drafts) started us defensive; dropped.
        if(my_evidence>=1){int add=static_cast<int>(my_evidence);my_evidence-=add;a=std::min(255,a+add);}
        if(slot==0&&round%2==0&&a>0)--a;                                                        // forget
        if(a!=shared[kAggression])write_byte(kAggression,static_cast<std::uint8_t>(a));
        aggression=a;defensive=a>=40;
        // Opponent style (735 top-100 games: 71% are passive farmers - ~1 kill each by r250, 5% of
        // their time on our half - and we lose those farming races 84% of the time; we spend 4% of
        // our time on their half). Passive + ahead of us on pace -> RAID: contest their camps and
        // hunt their carriers. Aggressive (invasion score) -> the existing defensive posture.
        // A raid that costs us 3 deaths is called off for the rest of the game.
        max_aggr=std::max(max_aggr,a);
        const int deaths=static_cast<int>(team_deaths.size());
        if(raid){
            if(defensive||deaths>=raid_deaths0+3){raid=false;raid_failed=true;std::cout<<"RAID off r="<<round<<" s="<<slot<<'\n';}
        } else if(!raid_failed&&round>=120&&max_aggr<25&&deaths<=2&&std::max(map::width(),map::height())>=50&&
                  static_cast<int>(global_submitted_gems(team::enemy))>=static_cast<int>(global_submitted_gems(team::ally))+40){
            raid=true;raid_deaths0=deaths;std::cout<<"RAID on r="<<round<<" s="<<slot<<'\n';
        }
    }
    {const unsigned scored=global_submitted_gems(team::ally);if(scored!=last_score){last_score=scored;last_score_round=round;}}
    if(round%5==0||!stats_ready){stats_ready=true;for(int k=0;k<team_size&&k<8;++k)try{auto c=roster[k];if(k==slot||c.is_visible()){ally_stats[k]={c.strength(),c.focus(),c.max_health()};}}catch(const error&){}}
    update_split();
    for(unsigned i=0;i<groups.size();++i){
        auto& g=groups[i];
        // Visible if any of its camp tiles is: a few bit tests instead of a full-map AND.
        bool seen_now=false;for(auto p:g.probes)if(visible.is_set(p)){seen_now=true;break;}
        if(!seen_now){
            // A reward we walked away from is assumed taken once it has been out of sight a while.
            if(g.reward&&round>g.seen_round+6){g.reward=false;g.ready_round=g.seen_round+g.respawn;}
            continue;
        }
        g.seen_round=round;
        try{
            auto state=g.handle.state();
            g.reward=std::holds_alternative<map::camp_group_reward_available>(state);
            if(auto s=std::get_if<map::camp_group_respawning>(&state))g.ready_round=round+s->timer;
            else g.ready_round=0;
        }catch(const error&){}
        for(auto c:g.handle.camps())
            if(visible.is_set(c.spawn_position())&&c.is_visible()&&c.is_alive())
                monsters.push_back({c,c.position(),c.health(),c.strength(),static_cast<int>(i),c.is_awake()});
    }
}

double Bot::dps() const {
    auto& me=self();double burst=0;
    for(auto a:me.abilities()){
        if(!a.info())continue;
        if(a.is_attack_reset())burst+=me.strength();
        if(a.is_damage()||a.is_aoe_damage())burst+=spell_modifier(a)*me.focus();
    }
    return me.strength()+burst/8.0;
}

double Bot::threat(vec2 p) const {
    double d=0;
    for(const auto& e:enemies){
        int r=dist(p,e.pos);
        const double pw=e.strength+focus_w()*e.focus;   // v19n: focus counts only on single-altar contested maps
        if(r<=e.range+1)d+=pw*1.6;     // basic plus a share of spell burst
        else if(r<=e.range+3)d+=pw*.5;
    }
    for(const auto& m:monsters)if(m.awake&&dist(p,m.pos)<=3)d+=m.strength;
    return d;
}

void Bot::shop(){
    auto& me=self();
    // Build order copied from the top ladder teams: frontliners open with a Bruiser emblem of
    // Health (farm camps without recalling), carries open on Power; everyone adds a Durability
    // emblem of Health, then stacks Power of their best stat.
    const auto ps=focus_build?item_type::power_shard_of_focus:item_type::power_shard_of_strength;
    const auto pe=focus_build?item_type::power_emblem_of_focus:item_type::power_emblem_of_strength;
    struct Step{item_type shard,emblem;};
    const Step P{ps,pe},B{item_type::bruiser_shard_of_health,item_type::bruiser_emblem_of_health},
        D{item_type::durability_shard_of_health,item_type::durability_emblem_of_health};
    std::vector<Step> order;
    // Ladder teams around us all open with a Monster emblem (+10% damage to camps), then stack
    // Power; a Durability emblem of the main stat follows the second Power emblem.
    const Step M{focus_build?item_type::monster_shard_of_focus:item_type::monster_shard_of_strength,focus_build?item_type::monster_emblem_of_focus:item_type::monster_emblem_of_strength},
        DS{focus_build?item_type::durability_shard_of_focus:item_type::durability_shard_of_strength,focus_build?item_type::durability_emblem_of_focus:item_type::durability_emblem_of_strength};
    (void)B;(void)DS;(void)M;
    // Cycles 3-4 item audit (80 top-100 games, round 300): opponents' max HP grows 909 -> 1126 while
    // ours stays at 830. Their emblems: Power, Durability of Health (~100), Bruiser of Health (~83),
    // Jungle (~120, 30% less camp damage); almost no Monster. Copy that: Jungle, Power, Durability-Health.
    const Step J{focus_build?item_type::jungle_shard_of_focus:item_type::jungle_shard_of_strength,focus_build?item_type::jungle_emblem_of_focus:item_type::jungle_emblem_of_strength};
    order={J,P,D,P};
    // v22w: Ryth is the tank. Elite contest replay (team rated 1907): their Ryth stacked health emblems (Power, Durability,
    // Treasure, Jungle of Health) to 10,600 max HP, stood nearest the monolith (it hits only the nearest champion) and
    // let the carries kill it ~5x a game with 6 deaths in total.
    const bool tank=me.champion_name()==champion_type::ryth;
    const Step PH{item_type::power_shard_of_health,item_type::power_emblem_of_health},DH{item_type::durability_shard_of_health,item_type::durability_emblem_of_health},
        JH{item_type::jungle_shard_of_health,item_type::jungle_emblem_of_health},TH{item_type::treasure_shard_of_health,item_type::treasure_emblem_of_health};
    if(tank)order={PH,DH,JH,TH};
    auto counts=me.item_count();
    for(unsigned j=0;j<order.size();++j){
        const auto& st=order[j];
        unsigned need=0;for(unsigned k=0;k<=j;++k)if(order[k].emblem==st.emblem)++need;
        if(counts[st.emblem]>=need)continue;
        // This emblem is the next one to finish: buy its shards (5 combine into the emblem).
        unsigned have=counts[st.shard];
        unsigned n=std::min<unsigned>(5-std::min(5u,have),me.gold_count()/st.shard.cost());
        if(n>0)try{if(me.can_buy(st.shard,n))me.buy(st.shard,n);}catch(const error&){}
        return;
    }
    const auto extra=tank?item_type::power_shard_of_health:ps;
    unsigned n=me.gold_count()/extra.cost();
    while(n>0){
        try{if(me.can_buy(extra,n)){me.buy(extra,n);break;}}catch(const error&){}
        n=n>1?n/2:0;
    }
}

bool Bot::move_to(bitboard goals,bool flee){
    auto& me=self();
    goals&=~(terrain|occupied);
    if(goals.is_empty()||goals.is_set(me.position()))return false;
    bitboard walls=terrain|occupied,visited;
    auto here=me.position();
    // Search outward from the goals only until our neighbourhood is reached (dash range 2).
    bitboard near=disk(here,2)&~walls;near.set(here,true);
    distance_field field;field.compute_to(walls,goals,near,visited);
    auto here_d=field.get(here);
    // Allies or camps standing in a corridor can cut every path to the goal; path through
    // them instead (they move) rather than freezing in place.
    if(here_d==distance_field::unreachable){
        walls=terrain;visited.clear();field.compute_to(walls,goals,near,visited);here_d=field.get(here);
        walls=terrain|occupied;
    }
    vec2 best=here;double best_v=1e18;
    for(auto p:walls.reachable_tiles(here,1).positions()){
        if(p==here||field.get(p)==distance_field::unreachable)continue;
        if(!flee&&field.get(p)>=here_d)continue;
        double v=field.get(p)+threat(p)*(flee?.08:.01);
        if(flee){int near=99;for(auto& e:enemies)near=std::min(near,dist(p,e.pos));if(near<99)v-=2.0*near;}
        if(stalled>3&&p==last_pos)v+=3;
        if(v<best_v){best_v=v;best=p;}
    }
    if(me.can_cast()&&(flee||here_d>2)){
        for(auto a:me.abilities())if(a.info()&&a.is_dash()&&a.is_ready()){
            vec2 jump=here;double jv=best==here?1e18:best_v-.5;
            for(auto p:(a.valid_tiles()&~walls).positions()){
                if(field.get(p)==distance_field::unreachable)continue;
                double v=field.get(p)+threat(p)*(flee?.08:.01);
                if(v<jv){jv=v;jump=p;}
            }
            if(jump!=here)try{if(a.use(jump))return true;}catch(const error&){}
        }
    }
    if(best!=here&&me.can_move())try{if(me.move_absolute(best))return true;}catch(const error&){}
    return false;
}

bool Bot::combat(int group,bool players){
    auto& me=self();
    const auto pos=me.position();const float strength=me.strength(),focus=me.focus();
    const int range=me.attack_range();
    const bool splash=me.champion_name()==champion_type::varg;
    const auto camp_mask=vision::camp_tiles();
    int target=-1;bool on_enemy=false;double best=-1e18;
    // Team focus: every champion ranks enemies with the same matchup rules, so they converge
    // on one target. Cassi first (Issac dies with her), then squishy carries, stunned or
    // channelling targets, low health.
    auto matchup=[&](int i)->double{
        const auto& e=enemies[i];double b=0;
        if(e.type==champion_type::cassi)b+=140;
        else if(e.type==champion_type::issac)b+=40;
        else if(is_carry(e.type))b+=70;
        if(e.stunned)b+=90;
        return b;
    };
    int scoring_enemy=-1;
    auto score=[&](vec2 p,float hp,int gems,bool enemy,bool channel){
        int d=dist(pos,p);if(d>4)return -1e18;
        double s=(enemy?60+gems*.8+(channel?80:0)+(scoring_enemy>=0?matchup(scoring_enemy):0):10)+120/(1+hp/std::max(1.f,strength));
        if(hp<=strength)s+=100;
        if(d>range)s-=(enemy?30:1000)*(d-range);   // v21p: 150 was not enough (expanse: Varg next to a wolf kept picking a 75-HP chest 2 tiles away for 200 rounds)   // v21h: a camp out of reach must not outrank one in reach (broken_curve: melee stood next to a camp hitting nothing for 400 rounds)
        if(splash)s+=25*std::max(0,static_cast<int>((disk(p,1)&camp_mask).count())-1);
        return s;
    };
    if(players)for(unsigned i=0;i<enemies.size();++i){auto& e=enemies[i];scoring_enemy=static_cast<int>(i);
        double v=score(e.pos,e.hp,e.gems,true,e.channel);if(v>best){best=v;target=static_cast<int>(i);on_enemy=true;}}
    scoring_enemy=-1;
    for(unsigned i=0;i<monsters.size();++i){auto& m=monsters[i];
        if(group>=0&&m.group!=group)continue;
        double v=score(m.pos,m.hp,0,false,false);if(v>best){best=v;target=static_cast<int>(i);on_enemy=false;}}
    if(target<0)return false;
    const vec2 tp=on_enemy?enemies[target].pos:monsters[target].pos;
    const float thp=on_enemy?enemies[target].hp:monsters[target].hp;
    auto spells=me.abilities();
    struct Cast{int slot=-1,ally=-1;bool self=false,ground=false;vec2 p{0,0};double v=0;}cast;
    for(int s=0;s<2;++s){
        auto& a=spells[s];
        if(!a.info()||!a.is_ready())continue;
        if(a.is_heal())for(unsigned j=0;j<allies.size();++j){auto c=allies[j];
            if(dist(pos,c.position())>spell_range(a))continue;
            double v=std::min(static_cast<double>(a.heal_amount()),static_cast<double>(c.max_health()-c.health()))*.7;
            if(v>cast.v)cast={s,static_cast<int>(j),false,false,c.position(),v};}
        if(a.is_shield()&&threat(pos)>0){double v=std::min(static_cast<double>(a.shield_amount()),threat(pos)*3)*.6;
            if(v>cast.v)cast={s,-1,true,false,pos,v};}
        if(a.is_attack_reset()&&dist(pos,tp)<=range){
            double v=std::min(thp,strength);
            if(splash)v+=strength*std::max(0,static_cast<int>((disk(tp,1)&camp_mask).count())-1);
            if(v>cast.v)cast={s,-1,true,false,tp,v};}
        if((a.is_damage()||a.is_cc())&&dist(pos,tp)<=spell_range(a)){
            if(on_enemy&&!a.can_target_enemies())continue;
            if(!on_enemy&&!a.can_target_camps())continue;
            double v=std::min(static_cast<double>(thp),static_cast<double>(spell_modifier(a)*focus));
            // Chain stuns instead of stacking them: no stun on a target that is already
            // stunned, and none on Marcella (immune).
            const bool stun_useful=on_enemy&&!enemies[target].stunned&&enemies[target].type!=champion_type::marcella;
            if(a.is_cc())v+=on_enemy?(stun_useful?(enemies[target].channel?250:enemies[target].strength*1.5+60):0):monsters[target].strength;
            if(v>cast.v)cast={s,-1,false,a.can_target_ground(),tp,v};}
        if(a.is_aoe_damage()){
            auto meta=a.get<ability_aoe_damage>();
            auto centers=disk(tp,1)&disk(pos,static_cast<int>(meta.range));
            for(auto c:centers.positions()){
                double v=0;
                for(auto& m:monsters)if((group<0||m.group==group)&&dist(c,m.pos)<=meta.radius)v+=std::min(m.hp,meta.modifier*focus);
                if(players)for(auto& e:enemies)if(dist(c,e.pos)<=meta.radius)v+=std::min(e.hp,meta.modifier*focus);
                if(v>cast.v)cast={s,-1,false,true,c,v};
            }
        }
    }
    bool acted=false;
    auto basic=[&]{
        if(!me.can_attack())return false;
        try{
            if(on_enemy){auto& e=enemies[target];
                if(e.handle.is_visible()&&e.handle.health()>0&&dist(me.position(),e.handle.position())<=me.attack_range()){me.attack(e.handle);return true;}}
            else{auto& m=monsters[target];
                if(m.handle.is_visible()&&m.handle.is_alive()&&dist(me.position(),m.handle.position())<=me.attack_range()){me.attack(m.handle);return true;}}
        }catch(const error&){}
        return false;
    };
    if(cast.slot>=0&&spells[cast.slot].is_attack_reset())acted=basic();
    if(cast.slot>=0&&me.can_cast()){
        auto& a=spells[cast.slot];
        try{
            bool ok=false;
            if(cast.self)ok=a.use();
            else if(cast.ally>=0)ok=a.use(allies[cast.ally]);
            else if(cast.ground)ok=a.use(cast.p);
            else if(on_enemy&&enemies[target].handle.is_visible())ok=a.use(enemies[target].handle);
            else if(!on_enemy&&monsters[target].handle.is_visible()&&monsters[target].handle.is_alive())ok=a.use(monsters[target].handle);
            acted=ok||acted;
        }catch(const error&){}
    }
    acted=basic()||acted;
    return acted;
}

int Bot::choose_group(vec2 from,double pack_dps,double pack_hp,std::array<int,3> exclude,double tank_hp){
    bitboard seen;distance_field travel_field;
    travel_field.compute(terrain,disk(from,0),seen,cg_far?static_cast<std::uint16_t>(400):static_cast<std::uint16_t>(70));
    bool any_gems=false;for(auto& g:groups)if(g.gems>0)any_gems=true;
    double gold_w=!any_gems?1.0:1.0;   // v22f: patch 3.0 - gold decides fights and the r2000 tiebreak (post-patch ranked losses: gold@600 1767 vs 2702)
    int best=-1;double best_s=-1e18;
#if POLARIS_OPP_MODEL > 0
    int opp_base_best=-1;double opp_base_score=-1e18;
#endif
    for(unsigned i=0;i<groups.size();++i){
        if(best>=0&&fuel_remaining()<25000)break;
        auto& g=groups[i];
        if(!g.reward&&std::find(exclude.begin(),exclude.end(),static_cast<int>(i))!=exclude.end())continue;   // another squad has it
        if(banned(i))continue;
        double value=g.gems+gold_w*g.gold;
        if(value<=0)continue;
        int travel=100000;
        for(auto p:g.probes)travel=std::min<int>(travel,travel_field.get(p));
        if(travel>=static_cast<int>(distance_field::unreachable))continue;
        int wait=g.ready_round>round?static_cast<int>(g.ready_round-round):0;
        if(wait>travel+10)continue;
        double hp=g.hp,str=g.str;
        if(g.reward){hp=0;str=0;
            // Someone else is already capturing it.
            if(g.gems<150&&shared[kClaimGroup]==i+1&&shared[kClaimSlot]!=slot+1&&age(round,shared[kClaimStamp])<=5)continue;
        } else {
            // Unseen camps are assumed at full health, so partial vision cannot make a
            // big group look nearly dead (which made the pack flip between targets).
            for(auto& m:monsters)if(m.group==static_cast<int>(i)){
                double base,unused;camp_stats_for(m.handle.kind(),base,unused);
                hp-=std::max(0.0,base-m.hp);
            }
            hp=std::max(hp,g.hp*.1);
        }
        double clear=hp/std::max(1.0,pack_dps);
        // Camps only hit champions within range 3 and wake one at a time as we engage, so the
        // damage actually taken is a fraction of their summed strength.
        // Big groups wake piecemeal (only camps within range 3 of us act), so their effective
        // damage share is smaller still.
        // A lone camp hits every round and focuses one champion; it must not force a recall.
        // Measured on the ladder maps: in multi-camp elk groups nearly every camp engages, and the
        // retreats this forces make clears take several times the naive estimate.
        const bool elk_pack=g.probes.size()>=2&&g.probes.size()<8&&g.elks>=1;
        if(!g.reward&&elk_pack)clear*=1.5;
        double incoming=str*clear*(g.probes.size()>=8?.45:g.probes.size()==1?1.0:elk_pack?.75:.3);
        if(!g.reward&&g.probes.size()==1&&incoming>tank_hp*.62&&round<last_score_round+150)continue;
        if(g.monolith&&(clear>110||incoming>pack_hp*.55))continue;
        // Starved: nothing banked for a long time means every gem source looked too risky
        // (e.g. one huge elk group); grow bolder the longer we go without scoring.
        const unsigned scored=global_submitted_gems(team::ally);
        if(scored!=last_score){last_score=scored;last_score_round=round;}
        const double starved=round>last_score_round+150?std::min(3.0,1.0+(round-last_score_round-150)/120.0):1.0;
        // Herd vulture (ladder stampede vs Gem Simons: they cleared the 360-gem herd from r75 in ~75
        // rounds, three times, while our herd ward watched). A seen herd below 50% is cheap to
        // finish and denies them 360: always worth taking, top priority.
        const bool weak_herd=g.probes.size()>=8&&!g.reward&&hp<g.hp*.5;
        if(!weak_herd&&incoming>pack_hp*(bold_pack?1.1:.8)*(g.probes.size()>=8?std::min(starved,1.15):starved))continue;
        double side=static_cast<double>(g.enemy_d)/std::max(1,g.home_d+g.enemy_d); // 1 = deep in our half
        double side_w=defensive?std::clamp(.6+.6*side,.7,1.15):raid?std::clamp(1.15-.3*side,.85,1.15):std::clamp(.7+.5*side,.8,1.1);
        double death_w=1;
        for(auto& d:deaths)if(dist(d.first,g.center)<=6&&round-d.second<400)death_w*=.7;
        // Idle waiting is pure loss; the capturer banks alone, so altar distance matters less.
        // v21k: charge the whole cycle (walk to altar + bank channel for our share), not 15% of the altar walk.
        const double share_gems=static_cast<double>(g.gems)/std::max(1,static_cast<int>(active_members().size()));
        double cost=travel+std::max(0,wait-travel)*2.0+clear+constants::capture_time+(g.gems>0?g.altar_d+std::ceil(share_gems/10.0):0)+4;
        double s=value*side_w*death_w/cost;
        if(weak_herd)s*=3.0;
        if(!merged()&&g.sector>=0&&g.sector!=active_squad())s*=.55;
        if(static_cast<int>(i)==objective)s*=1.2;
#if POLARIS_OPP_MODEL > 0
        if(s>opp_base_score){opp_base_score=s;opp_base_best=static_cast<int>(i);}
        const double opp_weight=opponent_camp_multiplier(static_cast<int>(i),travel);
#if POLARIS_OPP_MODEL >= 2
        s*=opp_weight;
#else
        (void)opp_weight;
#endif
#endif
        if(s>best_s){best_s=s;best=static_cast<int>(i);}
    }
#if POLARIS_OPP_MODEL > 0
    if(best>=0&&best!=opp_base_best){++opp_choice_changes;
        std::cout<<"OPP_CHOICE r="<<round<<" slot="<<slot<<" kind=pack baseline="<<opp_base_best<<" model="<<best<<'\n';}
#endif
    // v23v: ranked starvation losses - from our spawn every camp group is >70 steps away (winding map), so the
    // pack idled at spawn for 1800 rounds (log: 14/14 groups unreachable). Retry once with no distance cap.
    if(best<0&&!cg_far&&fuel_remaining()>60000){cg_far=true;best=choose_group(from,pack_dps,pack_hp,exclude,tank_hp);cg_far=false;}
    return best;
}

int Bot::leader_target(){
    // The lowest living slot in the squad decides the target every turn (even while it is
    // itself banking or recalling), and the others read it.
    auto& me=self();
    const int leader=squad_leader();
    const int sq=active_squad();
    int current=shared[kTarget+sq]?shared[kTarget+sq]-1:-1;
    if(current>=static_cast<int>(groups.size()))current=-1;
    if(leader!=slot&&current>=0){
        auto& g=groups[current];
        if(!(g.ready_round>round+12))return current;   // follow unless we can see it is gone
    }
    int alive=0;
    for(int k:active_members())if(ally_alive(k))++alive;
    alive=std::max(1,alive);
    double pack_hp,tank_hp;
    double pack_dps=group_dps(active_members(),pack_hp,tank_hp)*.85;
    pack_hp*=.9;
    if(pack_dps<=0){pack_dps=dps()*alive*.85;pack_hp=me.max_health()*alive*.9;tank_hp=me.max_health();}
    if(current>=0)objective=current;
    const bool target_ok=current>=0&&groups[current].ready_round<=round+12;
    if(target_ok&&(fuel_remaining()<45000||round-last_choose<3))return current;
    // Re-planning needs a travel field over the whole map: only when this turn can afford it.
    if(fuel_remaining()<40000&&current>=0)return current;
    last_choose=round;
    std::array<int,3> other{-1,-1,-1};
    if(!merged())for(int s2=0;s2<squads;++s2)if(s2!=sq&&shared[kTarget+s2])other[s2]=shared[kTarget+s2]-1;
    int choice=choose_group(me.position(),pack_dps,pack_hp,other,tank_hp);
    // Nothing this squad can take safely on its own: join the nearest other squad.
    if(choice<0){int bd=1<<30;for(int o:other)if(o>=0&&o<static_cast<int>(groups.size())){int d=dist(me.position(),groups[o].center);if(d<bd){bd=d;choice=o;}}}
    objective=choice;
    if(leader==slot)write_byte(kTarget+sq,static_cast<std::uint8_t>(choice+1));
    return choice;
}

int Bot::solo_target(){
    // Split play: each champion takes camps it can clear alone and publishes its
    // choice in shared[slot] so teammates spread out.
    auto& me=self();
    bool any_gems=false;for(auto& g:groups)if(g.gems>0)any_gems=true;
    const double gold_w=!any_gems?1.0:(round<250?.15:round<700?.08:.04);
    const double my_dps=std::max(1.0,dps()),my_hp=me.health();
    // Issac shadows Cassi in solo play: split up, one pick kills both.
    if(me.champion_name()==champion_type::issac&&!pack_mode){
        for(int k=0;k<std::min(team_size,6);++k){try{if(k!=slot&&roster[k].champion_name()==champion_type::cassi&&ally_alive(k)
            &&shared[k]>0&&shared[k]<=groups.size()){objective=shared[k]-1;return objective;}}catch(const error&){}}
    }
    // Commit: straight-line distances jump around walls, so rescoring every turn made solo
    // champions flip between far camps. Keep a valid target and rescore every 8 rounds.
    if(objective>=0&&objective<static_cast<int>(groups.size())&&round<solo_choose+8){
        auto& g=groups[objective];
        bool taken=false;
        if(!pack_mode)for(int k=0;k<std::min(team_size,6);++k)if(k<slot&&shared[k]==objective+1)taken=true;
        const int wait=g.ready_round>round?static_cast<int>(g.ready_round-round):0;
        if(!taken&&wait<=dist(me.position(),g.center)+20)return objective;
    }
    solo_choose=round;
    int best=-1;double best_s=-1e18;
    int fb=-1;double fb_s=-1e18;
#if POLARIS_OPP_MODEL > 0
    int opp_base_best=-1;double opp_base_score=-1e18;
#endif
    for(unsigned i=0;i<groups.size();++i){
        auto& g=groups[i];
        if(g.monolith&&!g.reward)continue;
        if(banned(i))continue;
        if(role==1&&(g.str>0||g.home_d>g.enemy_d+4))continue;     // farmer: harmless home-side camps only
        // Audit, contest (10 games, ~50 deaths each, 2 wins): most deaths were lone farmers caught by
        // 1-2 enemies; kills feed their gold tiebreak. On gold-only maps farm our half only.
        if(siege_group>=0&&g.home_d>g.enemy_d)continue;
        double value=g.gems+(role==1?1.0:gold_w)*g.gold;
        if(value<=0)continue;
        double hp=g.hp;
        // Remaining group HP = full HP minus damage seen on visible members (was: the single weakest
        // visible member's HP, which made a herd with one hurt elk look nearly dead; ChatGPT review).
        for(auto& m:monsters)if(m.group==static_cast<int>(i)){double base,unused;camp_stats_for(m.handle.kind(),base,unused);hp-=std::max(0.0,base-m.hp);}
        hp=std::max(hp,g.hp*.05);
        double clear=g.reward?0:hp/my_dps;
        const bool weak_herd_s=g.probes.size()>=8&&!g.reward&&hp<g.hp*.5;
        if(!weak_herd_s&&!g.reward&&g.str*clear*.6>my_hp*(pack_mode?.6:forced_solo?1.3:.85))continue;   // solo farmers recall to heal anyway
        int travel=dist(me.position(),g.center);
        int wait=g.ready_round>round?static_cast<int>(g.ready_round-round):0;
        if(wait>travel+10){   // v23v: respawning - remember the soonest one to pre-position at instead of idling
            const double fs=value/(wait+clear+constants::capture_time+.3*g.altar_d+2);
            if(wait<400&&fs>fb_s){fb_s=fs;fb=static_cast<int>(i);}
            continue;}
        int taken=0;
        if(!pack_mode)for(int k=0;k<std::min(team_size,6);++k)if(k!=slot&&shared[k]==i+1)++taken;
        double sc=value/(std::max(travel,wait)+clear+constants::capture_time+.3*g.altar_d+2);
        if(taken)sc*=.15;
        if(static_cast<int>(i)==objective)sc*=1.6;
        double enemy_side=static_cast<double>(g.home_d)/std::max(1,g.home_d+g.enemy_d);
        if(enemy_side>.62&&!raid)sc*=.6;
        if(raid&&enemy_side>.5)sc*=1.15;
        if(defensive&&enemy_side>.6)sc*=.6;
        if(threat_fresh&&dist(g.center,{threat_x,threat_y})<=5)sc*=.6;
        for(auto& d:deaths)if(dist(d.first,g.center)<=6&&round-d.second<400)sc*=.7;
#if POLARIS_OPP_MODEL > 0
        if(sc>opp_base_score){opp_base_score=sc;opp_base_best=static_cast<int>(i);}
        const double opp_weight=opponent_camp_multiplier(static_cast<int>(i),travel);
#if POLARIS_OPP_MODEL >= 2
        sc*=opp_weight;
#else
        (void)opp_weight;
#endif
#endif
        if(sc>best_s){best_s=sc;best=static_cast<int>(i);}
    }
#if POLARIS_OPP_MODEL > 0
    if(best>=0&&best!=opp_base_best){++opp_choice_changes;
        std::cout<<"OPP_CHOICE r="<<round<<" slot="<<slot<<" kind=solo baseline="<<opp_base_best<<" model="<<best<<'\n';}
#endif
    if(best<0)best=fb;   // v23v: ranked starvation/shortcut audit - champions idled 100s of rounds while every camp respawned
    objective=best;
    if(!pack_mode&&slot<6)write_byte(slot,static_cast<std::uint8_t>(best+1));
    return best;
}

void Bot::ban(int g,int rounds){if(g<0)return;if(ban_until.size()<groups.size())ban_until.resize(groups.size(),0);ban_until[g]=round+rounds;}
bool Bot::banned(unsigned g) const{return g<ban_until.size()&&round<ban_until[g];}
bool Bot::bank(){
    auto& me=self();
    const int gems=static_cast<int>(me.gem_count());
    if(gems<100&&slot<6&&shared[slot]==255)write_byte(slot,0);   // clear our rally flag
    if(gems<=0){bag_since=-1;bank_alone_since=-1;convoy_recalled=false;return false;}
    const int ad=altar_distance.get(me.position());
    const int ticks=std::max(1,(gems+9)/10);
    const bool win=static_cast<int>(global_submitted_gems(team::ally))+gems>=static_cast<int>(constants::winning_gems);
    const bool endgame=round+ad+ticks+10>=constants::max_rounds;
    const bool rush=global_submitted_gems(team::enemy)>=850;
    int nearest_group=100000;
    for(auto& g:groups)if(g.gems>0)nearest_group=std::min(nearest_group,dist(me.position(),g.center));
    int carry=defensive?std::clamp(20+ad-nearest_group,20,50):std::clamp(20+ad-nearest_group,25,60);
    if(small_banks)carry=defensive?std::clamp(15+ad-nearest_group,15,35):std::clamp(15+ad-nearest_group,18,40);   // v23m: bank like the ladder #1 team (34 submits/game, median bag 22; we: 17/game, median 37)
    // Issue #18: on contested-altar maps our lost bags were the ones we kept farming with (collision:
    // lost bags median 58 gems held 71 rounds; theirs banked at 22 gems after 20 rounds, 95% banked vs
    // our 63%). Bank as soon as a camp's worth is in hand.
    if(contested_altars==1&&siege_group<0)carry=std::clamp(22+ad-nearest_group,22,60);
    my_danger=danger_at(me.position(),gems);
    const bool risky_bag=gems>=22&&my_danger*gems>=6.0;
    const bool go=win||endgame||rush||gems>=carry||(gems>=20&&ad<=6)||me.health()<me.max_health()*.4f||risky_bag;
    if(!go)return false;
    // v24c: boss battle - the only altar sits between two monoliths (they wake within 2 tiles), so every submit tile
    // is guarded. Carriers walked to it and stood for the whole game (952 bank turns, 0 gems banked) instead of
    // farming gold for the r2000 tiebreak. While every submit tile is within 2 of a live monolith, keep farming.
    if(!win&&!endgame&&!altar_goals.is_empty()){
        bool guarded=true;
        for(auto q:altar_goals.positions()){
            bool g2=false;
            for(auto& gg:groups){if(!gg.monolith||gg.reward||gg.ready_round>round)continue;
                for(auto pr:gg.probes)if(dist(pr,q)<=2){g2=true;break;}
                if(g2)break;}
            if(!g2){guarded=false;break;}
        }
        if(guarded)return false;
    }
    if(pack_mode)write_byte(kClaimGroup,0);
    // Do not start a long tribute with enemies close and no more allies than enemies nearby:
    // stepping back keeps the bag; dying hands it to them.
    const double fw=focus_w();
    int foes_near=0,friends_near=0;double their=0,our=fw>0?(me.strength()+fw*me.focus())*1.5*me.health():dps()*me.health();
    for(auto& e:enemies)if(dist(e.pos,me.position())<=e.range+3){++foes_near;their+=(e.strength+fw*e.focus)*1.5*e.hp;}
    for(auto c:allies)if(dist(c.position(),me.position())<=5){++friends_near;our+=(c.strength()+fw*c.focus())*1.5*c.health();}
    if(foes_near==0){bank_wait=0;tribute_cancels=0;}
    // Waiting is capped: an enemy idling by the altar must not freeze our scoring.
    // Audit (39 ranked games): deaths at the altar lost 1728 of 4364 gems. The 12-round cap
    // forced big tributes through enemies; for big bags there is no cap and the learned danger counts.
    // Monolith bag convoy (ladder contest c8w: 200-gem carriers walked alone from the monolith to the
    // central altar and died to 2 enemies; 0 tributes in 9 games while they banked 5 x 200). The carrier
    // goes home first (full heal, safe), raises a rally flag (shared[slot]=255) that pulls the team to
    // spawn, and walks to the altar only with 2+ allies within 3. Budget: 60 rounds, then go anyway.
    if(siege_group>=0&&gems>=100&&!win&&!endgame){
        if(bag_since<0)bag_since=round;
        if(slot<6)write_byte(slot,255);
        int with_me=0;for(auto c:allies)if(dist(c.position(),me.position())<=3)++with_me;
        int alive=0;for(int k=0;k<team_size;++k)if(ally_alive(k))++alive;
        const bool home=map::spawn_region(team::ally).is_set(me.position());
        if(round<bag_since+60&&with_me<std::min(2,alive-1)){
            if(!home){
                if(threat(me.position())<1&&!convoy_recalled){convoy_recalled=true;try{me.recall();log("convoy-recall");return true;}catch(const error&){}}
                move_to(map::spawn_region(team::ally),true);combat(-1,true);log("convoy-home");return true;
            }
            log("convoy-wait");return true;
        }
    }
    if(contested_altars==1&&siege_group<0&&gems>=40&&!win&&!endgame){
        if(friends_near==0&&foes_near>0){
            if(bank_alone_since<0)bank_alone_since=round;
            if(round<bank_alone_since+12){move_to(map::spawn_region(team::ally),true);combat(-1,true);log("bank-regroup");return true;}
        } else bank_alone_since=-1;
    }
    const bool big=gems>=60;
    const bool unsafe=foes_near>0&&(our<their||(big&&danger_at(me.position(),gems)>.25))&&(bank_wait<(big?80:12));   // bounded even for big bags
    if(unsafe)++bank_wait;
    for(auto altar:map::altars().positions()){
        if(dist(me.position(),altar)>constants::submit_gems_range)continue;
        if(unsafe&&ticks>2)break;
        if(vision::has_altar_lock(altar)){
            auto lock=vision::altar_lock_at(altar);
            if(lock.is_enemy()){if(me.can_attack())try{me.attack(lock);}catch(const error&){}log("unlock");return true;}
            continue;
        }
        try{me.submit_gems(altar);log("tribute");return true;}catch(const error&){}
    }
    // A recall is a free heal and shop; take it when spawn is nearly as close to an altar.
    int home_to_altar=100000;
    for(auto p:map::spawn_region(team::ally).positions())home_to_altar=std::min<int>(home_to_altar,altar_distance.get(p));
    bool close=false;for(auto& e:enemies)if(dist(e.pos,me.position())<=e.range+2)close=true;
    const int detour=me.gold_count()>=150?12:-2;
    if(!close&&threat(me.position())<1&&home_to_altar+constants::recall_time<ad+detour
        &&!map::spawn_region(team::ally).is_set(me.position())){
        try{me.recall();log("bank-recall");return true;}catch(const error&){}
    }
    if(unsafe&&ticks>2){move_to(map::spawn_region(team::ally),true);log("bank-wait");return true;}
    // Head for the nearest reachable altar that is not a kill zone: recently watched altars,
    // and contested ones when carrying a big bag alone. The path field picks among the rest.
    // Per-altar geometry is computed once (maps can have 18 altars).
    if(altar_contested.size()!=altar_pos.size()){
        altar_contested.assign(altar_pos.size(),false);altar_disk.assign(altar_pos.size(),bitboard{});
        for(unsigned a=0;a<altar_pos.size();++a){
            int hd=1<<20,ed=1<<20;
            for(auto q:disk(altar_pos[a],1).positions()){
                if(q.x<0||q.y<0||q.x>=static_cast<int>(map::width())||q.y>=static_cast<int>(map::height()))continue;
                hd=std::min<int>(hd,home_distance.get(q));ed=std::min<int>(ed,enemy_distance.get(q));
            }
            altar_contested[a]=ed<=hd+6;
            altar_disk[a]=disk(altar_pos[a],constants::submit_gems_range);
        }
    }
    bitboard goals;goals.clear();
    bool need_check=false;
    // Issue #16 (corners): opponents farm next to the central altar, so a "seen within 20 rounds" rule
    // flagged it permanently and our carriers walked to the corner altars (96% of our tributes, bags
    // held 79 rounds vs their 21 at the centre). An altar is now avoided only when enemies are near it
    // NOW and the learned danger there for this bag is high.
    std::vector<char> risky_a(altar_pos.size(),0);
    for(unsigned a=0;a<altar_pos.size();++a){
        int near_now=0;for(auto& e:enemies)if(dist(e.pos,altar_pos[a])<=6)++near_now;
        const bool hot=near_now>0&&danger_at(altar_pos[a],gems)>.25;
        const bool alone_big=altar_contested[a]&&gems>=80&&friends_near==0&&altar_pos.size()>1&&near_now>0;
        risky_a[a]=hot||alone_big;
        if(risky_a[a])need_check=true;
    }
    bitboard any=altar_goals;
    if(!need_check)goals=altar_goals;
    else for(unsigned a=0;a<altar_pos.size();++a)if(!risky_a[a])goals|=altar_disk[a];
    goals&=altar_goals;
    // Altars with our own lock are never targets; enemy-locked ones we will unlock.
    if(goals.is_empty())goals=any;
    // v23v: shortcut audit - a carrier stood 2 steps from a camp-ringed altar for 250+ rounds with every move failing
    // (an enemy champion in the one-tile gap). Fight whatever blocks after 3 failed moves; after 10, use another altar.
    if(bank_block_until>round&&bank_block_idx>=0&&bank_block_idx<static_cast<int>(altar_disk.size())){
        bitboard g2=goals&~altar_disk[bank_block_idx];if(!g2.is_empty())goals=g2;}
    bool mv=move_to(goals.is_empty()?altar_goals:goals);
    if(!mv&&!(goals==altar_goals)&&bank_block_until<=round)mv=move_to(altar_goals);
    if(mv)bank_fail=0;
    else if(++bank_fail>=3){
        combat(-1,true);
        if(bank_fail>=10&&altar_pos.size()>1){
            int bi=-1,bd=1<<20;for(unsigned a2=0;a2<altar_pos.size();++a2){int d=dist(me.position(),altar_pos[a2]);if(d<bd){bd=d;bi=static_cast<int>(a2);}}
            bank_block_idx=bi;bank_block_until=round+60;bank_fail=0;log("bank-switch");return true;}
    }
    log("bank");
    return true;
}

bool Bot::handle_enemies(){
    auto& me=self();
    if(enemies.empty())return false;
    const auto pos=me.position();
    const double fw2=focus_w();
    double ours=fw2>0?(me.strength()+fw2*me.focus())*1.5*me.health():dps()*me.health(),theirs=0;
    int near_enemies=0;
    for(auto c:allies)if(dist(c.position(),pos)<=6)ours+=(c.strength()+fw2*c.focus())*1.5*c.health();
    for(auto& e:enemies)if(dist(e.pos,pos)<=e.range+4){theirs+=(e.strength+fw2*e.focus)*1.5*e.hp;++near_enemies;}
    int near_allies=0;for(auto c:allies)if(dist(c.position(),pos)<=6)++near_allies;
    if(!near_enemies)return false;
    // Posture: against invaders we only take even fights, except next to our spawn where we
    // heal fully every round and they cannot follow (the "tower" advantage in LoL terms).
    int home_d=home_distance.get(pos);
    // Issue #17: defensive windows on eight/contest/swirl had worse kill ratios (eight 3.3 vs 0.7 deaths
    // per 100 rounds) - turtling did not protect us. Grouped fights at need .7 instead of 1.05.
    double need=defensive?(home_d<=5?.6:(near_allies>=2?.9:1.2)):1.1;   // v25i: take only fights we are ahead in (was .6 = fights 40% behind; ranked lanes: we reach low HP 1.4-1.8x as often)
    // Audit: 26% of deaths were fights taken while outnumbered, 18% Cassi&Issac linked deaths
    // (losing Cassi kills Issac too): Cassi needs a clearer edge, and 2+ extra enemies means leave.
    if(raid&&me.gem_count()<30)need=std::min(need,.5);
    if(me.champion_name()==champion_type::cassi)need*=1.3;

    tr_ratio=theirs>0?ours/theirs:9.99;
    bool favourable=ours>=theirs*need&&(near_enemies<near_allies+3||home_d<=5);
    // Alone (no ally within 6) against 1+ enemies on a gold-only map: never take it, kills are their tiebreak.
    if(siege_group>=0&&near_allies==0&&home_d>5&&round<POLARIS_SIEGE_R)favourable=false;
    bool in_range=false;
    for(auto& e:enemies)if(dist(e.pos,pos)<=me.attack_range()||(e.channel&&dist(e.pos,pos)<=4))in_range=true;
    if(favourable){
        if(in_range&&combat(-1,true)){log("fight");return true;}
        // Chase only a real kill: a tribute channel, or a target our side can burst down.
        double burst=dps()*3;for(auto c:allies)if(dist(c.position(),pos)<=5)burst+=c.strength()*3;
        // Bag hunting: the killer takes the victim's gems, so a carrier with a real bag is worth
        // a longer chase when the local fight is already ours.
        for(auto& e:enemies)if((dist(e.pos,pos)<=5&&(e.channel||e.hp<burst))||(dist(e.pos,pos)<=(raid?11:7)&&e.gems>=(raid?30:60)&&e.hp<burst*(raid?3.0:2.5))){
            move_to(disk(e.pos,me.attack_range()));combat(-1,true);log("chase");return true;}
        // Audit (cycle 2, 326 deaths): most "caught farming" deaths logged action=farm against 1-2
        // enemies: the fight was favourable but the enemy stood outside our range and poked us while
        // we kept hitting the camp. If an enemy can hit us, step in and fight it instead of farming.
        {const Enemy* tgt=nullptr;int bd=1000;
         for(auto& e:enemies){const int d=dist(e.pos,pos);if(d<=e.range+1&&d<bd){bd=d;tgt=&e;}}
         if(tgt){move_to(disk(tgt->pos,me.attack_range()));combat(-1,true);log("engage");return true;}}
        return false;
    }
    bool pressed=false;
    for(auto& e:enemies)if(dist(e.pos,pos)<=e.range+3)pressed=true;   // audit: 21% of deaths were champions still farming as enemies closed in
    if(pressed||(me.gem_count()>=30&&threat(pos)>0)){
        move_to(map::spawn_region(team::ally),true);
        combat(-1,true);
        log("evade");
        return true;
    }
    return false;
}

// ---- Opponent model (v15) -------------------------------------------------------------
// Danger: logistic model of P(this champion dies within 30 rounds), trained on 58k
// champion-rounds from 39 decoded top-50 replays (held-out AUC .725 vs .69 for "enemies near").
// Inputs are things we observe: visible enemies/allies near a tile, our HP/strength/bag, the
// map side, the opponent's kill rate on us so far and the score gap.
static constexpr double DW[22]={-0.108542,0.247151,0.143958,-0.2733,0.0672788,-0.0426196,-0.135759,0.261219,-0.49745,0.0369206,0.0607475,0.168013,0.461194,0.32944,-0.0399152,0.130066,0.194174,0.143728,0.161338,-0.110564,-0.225438,0.154939};
static constexpr double DMU[22]={0.697242,1.03308,0.913506,0.865059,0.123791,1.26475,3.48835,0.840437,0.951746,1.53257,0.128278,0.340046,0.849648,7.41744,-0.0214677,0.421497,0.228438,0.170204,0.282128,2.44915,0.379039,0.347916};
static constexpr double DSD[22]={1.15376,2.00089,0.174554,0.219038,0.431596,1.22036,3.10096,0.229949,0.434027,0.951353,0.258954,0.160792,1.1537,9.09723,0.432669,0.396316,0.398642,0.456549,0.43746,3.37047,0.906513,0.47631};
static constexpr double DB=-2.93144;

double Bot::danger_at(vec2 p,int carry) const {
    auto& me=self();
    int n8=0,n4=0,n5=0;double es=0,ehp=0,emax=0,near=9;
    for(auto& e:enemies){const int d=dist(e.pos,p);if(d<=8){++n8;es+=e.strength+.5*e.focus;ehp+=e.hp;emax+=e.maxhp;near=std::min<double>(near,d);}if(d<=4)++n4;}
    double as=me.strength()+.5*me.focus();
    for(auto c:allies){if(dist(c.position(),p)<=5){++n5;try{as+=c.strength()+.5*c.focus();}catch(const error&){}}}
    const double hd=home_distance.get(p),ed=enemy_distance.get(p);
    const double side=(hd>=60000||ed>=60000)?.5:hd/std::max(1.0,hd+ed);
    const double my_hp=me.health()/std::max(1.f,me.max_health());
    double f[22];
    f[0]=n8;f[1]=es/100;f[2]=n8?ehp/std::max(1.0,emax):1.0;f[3]=near/9;f[4]=n4;f[5]=n5;f[6]=as/100;f[7]=my_hp;f[8]=me.health()/1000.0;
    f[9]=(me.strength()+.5*me.focus())/100;f[10]=carry/100.0;f[11]=side;f[12]=kills_rate;f[13]=6.76;f[14]=pace_gap;f[15]=round/1000.0;
    f[16]=std::log1p(es/std::max(1.0,as));f[17]=n8*(1-my_hp);f[18]=side*kills_rate;f[19]=side*6.76;f[20]=(es/100)/(as/100+.1);f[21]=n8>0;
    double z=DB;for(int k=0;k<22;++k)z+=DW[k]*(f[k]-DMU[k])/DSD[k];
    return 1/(1+std::exp(-z));
}

// Profile + counter-strategy. Every champion derives the same numbers (global scores and roster
// alive flags), so the team agrees. A mode needs two consecutive readings 25 rounds apart and is
// held at least 75 rounds, so one skirmish does not flip the plan.
//   1 TURTLE  (opponent kills us fast: top-quartile kill rate)  -> group, home side, small banks
//   2 DISRUPT (out-farmed by a calm opponent)                   -> farm/steal on their side, bigger risks
//   3 SAFE    (we lead clearly)                                  -> bank sooner, take only good fights
void Bot::update_profile(){
    for(int k=0;k<team_size&&k<8;++k){
        bool alive=true;
        if(k==slot)alive=self().is_alive();
        else try{alive=roster[k].is_alive();}catch(const error&){alive=prev_alive[k];}
        if(prev_alive[k]&&!alive&&round>5)team_deaths.push_back(round);
        prev_alive[k]=alive;
    }
    const int ours=static_cast<int>(global_submitted_gems(team::ally)),theirs=static_cast<int>(global_submitted_gems(team::enemy));
    if(theirs>last_enemy_score){last_enemy_score=theirs;last_enemy_gain_round=round;}
    const int idx=std::min(81,static_cast<int>(round/25));
    if(idx<=s_last)return;
    for(int k=s_last+1;k<=idx;++k){s_ours[k]=ours;s_theirs[k]=theirs;}
    s_last=idx;
    kills_rate=round>0?static_cast<double>(team_deaths.size())/round*100:0;
    pace_gap=(theirs-ours)/500.0;
    if(round<125)return;
    int want=0;
    if(kills_rate>=1.8)want=1;
    else if(pace_gap>=.18&&kills_rate<1.0)want=2;
    else if(pace_gap<=-.24)want=3;
    if(want==mode_pending)++mode_votes;else{mode_pending=want;mode_votes=1;}
    if(false){
        mode=want;mode_since=round;
        std::cout<<"MODE r="<<round<<" s="<<slot<<" mode="<<mode<<" kr="<<kills_rate<<" gap="<<pace_gap<<'\n';
    }
}

void Bot::log(const char* action,int target){
#if POLARIS_OPP_MODEL > 0
    if(std::string(action)=="farm"){opp_farm_group=target;opp_farm_round=round;}
#endif
    // TRACE (diagnostic build, behaviour identical to v18f): one compact line per decision change and
    // every 5 rounds: round slot action target hp gems nearest-enemy-dist enemies<=6 allies<=5
    // defensive raid aggression fight-ratio(ours/theirs from handle_enemies, x100).
    {auto& me=self();
     if(std::string(action)!=tr_last_a||target!=tr_last_t||round>=tr_last_r+5){
        tr_last_a=action;tr_last_t=target;tr_last_r=round;
        int ne=99,e6=0,a5=0;for(auto& e:enemies){int d=dist(e.pos,me.position());ne=std::min(ne,d);if(d<=6)++e6;}
        for(auto c:allies)if(dist(c.position(),me.position())<=5)++a5;
        std::cout<<"T "<<round<<' '<<slot<<' '<<action<<' '<<target<<' '<<static_cast<int>(me.health())<<' '<<me.gem_count()<<' '<<ne<<' '<<e6<<' '<<a5<<' '<<(defensive?1:0)<<(raid?1:0)<<' '<<aggression<<' '<<static_cast<int>(tr_ratio*100)<<'\n';}}
    if(round-last_log<25)return;
    last_log=round;
    auto& me=self();
    std::cout<<"P3 r="<<round<<" s="<<slot<<" "<<action<<" t="<<target<<" hp="<<static_cast<int>(me.health())
        <<" gems="<<me.gem_count()<<" gold="<<me.gold_count()<<" e="<<enemies.size()<<" agg="<<aggression<<" fuel="<<fuel_remaining()<<'\n';
}

void Bot::play_turn(){
    auto& me=self();
    round=round_number();
    if(!initialized){init();return;}
    update_profile();
    if(!me.is_alive()){
#if POLARIS_OPP_MODEL > 0
        opp_model.tick(round,-1,0,nullptr,0);opp_farm_group=-1;
        report_opponent_response();
#endif
        if(was_alive&&round-last_enemy_round<=2){
            try{shared_memory.read(0,std::span{shared});}catch(const error&){}
            write_byte(6,static_cast<std::uint8_t>(std::min(255,shared[6]+20)));
        }
        if(was_alive&&last_pos.x>=0){deaths.push_back({last_pos,round});if(deaths.size()>10)deaths.erase(deaths.begin());}
        was_alive=false;
        try{shop();}catch(const error&){}
        return;
    }
    was_alive=true;
    observe();
#if POLARIS_OPP_MODEL > 0
    observe_opponent_response();
    report_opponent_response();
#endif
    if(me.gem_count()>last_gems||me.gold_count()>0){
        if(capturing>=0&&(me.gem_count()>last_gems)){
            auto& g=groups[capturing];g.reward=false;g.ready_round=round+g.respawn;
            if(pack_mode)write_byte(kClaimGroup,0);
            capturing=-1;
        }
    }
    last_gems=me.gem_count();
    stalled=me.position()==last_pos?stalled+1:0;
    last_pos=me.position();
    if(pack_mode&&role==0&&squad_leader()==slot&&(me.is_recalling()||me.is_submitting_gems()||me.gem_count()>0))leader_target();
    if(me.is_teleporting()||me.is_recalling())return;
    if(me.is_submitting_gems()){
        // Cancel a tribute only against a real threat (stronger enemies in reach), and only a
        // few times: an enemy idling by the altar must not stop us scoring altogether.
        const double fw3=focus_w();
        double their=0,our=fw3>0?(me.strength()+fw3*me.focus())*1.5*me.health():dps()*me.health();
        for(auto& e:enemies)if(dist(e.pos,me.position())<=e.range+2)their+=(e.strength+fw3*e.focus)*1.5*e.hp;
        for(auto c:allies)if(dist(c.position(),me.position())<=4)our+=(c.strength()+fw3*c.focus())*1.5*c.health();
        const bool outnumbered=their>our&&me.gem_count()>=30&&me.remaining_channel_time()>2&&(tribute_cancels<(me.gem_count()>=60?20:3));
        if(outnumbered)++tribute_cancels;
        if((outnumbered||threat(me.position())*std::max(1,me.remaining_channel_time())>me.health()*1.2)&&me.remaining_channel_time()>1)
            try{me.cancel_submit_gems();}catch(const error&){}
        else return;
    }
    const bool spawn=map::spawn_region(team::ally).is_set(me.position());
    if(spawn||me.champion_name()==champion_type::tavi)shop();
    // Wards. (1) Herd/monolith watch: on maps whose gems come from one huge group (stampede herd,
    // contest monoliths), the last slot plants a permanent ward next to it once, so we see it being
    // weakened and can finish it. (2) Everyone else keeps a ward pushed toward the enemy side for
    // early sight of invaders (most of our deaths are farmers caught by arriving enemies).
    if(herd_group==-2){
        herd_group=-1;int best=100000;
        for(unsigned i=0;i<groups.size();++i){auto& g=groups[i];
            if(g.gems>0&&(g.monolith||g.probes.size()>=8)&&g.home_d<best){best=g.home_d;herd_group=static_cast<int>(i);}}
    }
    const int wr=std::max(1,static_cast<int>(constants::ward_placement_radius));
    if(herd_group>=0&&slot==team_size-1&&!herd_warded&&round>=8){
        auto& hg=groups[herd_group];
        vec2 best=me.position();int bd=dist(me.position(),hg.center);
        for(auto q:disk(me.position(),wr).positions()){
            if(terrain.is_set(q)||occupied.is_set(q))continue;
            const int d=dist(q,hg.center);
            if(d>=4&&d<bd){bd=d;best=q;}
        }
        if(bd<=6&&!(best==me.position())){try{if(me.place_ward(best)){herd_warded=true;log("herd-ward");}}catch(const error&){}}
        if(herd_try_since<0)herd_try_since=round;
        if(round>herd_try_since+80)herd_warded=true;    // give up: unreachable or no charge
        if(!herd_warded&&enemies.empty()&&me.gem_count()==0){move_to(disk(hg.center,5)&~disk(hg.center,3));log("to-herd");return;}
    } else if(round>=ward_next&&!spawn&&!(herd_group>=0&&slot==team_size-1)){
        ward_next=round+6;
        vec2 best=me.position();int bd=enemy_distance.get(me.position());
        for(auto q:disk(me.position(),wr).positions()){
            if(terrain.is_set(q)||occupied.is_set(q))continue;
            const int d=enemy_distance.get(q);
            if(d<bd){bd=d;best=q;}
        }
        if(!(best==me.position()))try{if(me.place_ward(best))ward_next=round+6;}catch(const error&){}
    }
    if(spawn&&me.health()<me.max_health()*.98f&&enemies.empty())return;
    if(!me.can_move()&&!me.can_attack()&&!me.can_cast())return;

    const double danger=threat(me.position());
    // v21a (day audit 19 Oct + dpark research rule 11): walk speed is equal, so walking away from an enemy that is
    // already in range just eats free hits (65% of contest / 46% of eight first deaths died retreating at ~50% HP).
    // In contact and with no ready dash: fight back instead of turning; the retreat/evade decision is made at sight.
    bool locked=false;
    {bool dash=false;for(auto a:me.abilities())if(a.info()&&a.is_dash()&&a.is_ready())dash=true;
     if(!dash)for(auto& e:enemies)if(dist(e.pos,me.position())<=std::max(1,e.range))locked=true;}
    if(locked&&!spawn&&me.health()>me.max_health()*.12f){
        if(!combat(-1,true)){const Enemy* t=nullptr;int bd=1000;for(auto& e:enemies){int d=dist(e.pos,me.position());if(d<bd){bd=d;t=&e;}}
            if(t){move_to(disk(t->pos,me.attack_range()));combat(-1,true);}}
        log("stand");return;}
    if(!spawn&&(me.health()<me.max_health()*.3f||danger*2.5>me.health())){
        bool close=false;for(auto& e:enemies)if(dist(e.pos,me.position())<=e.range+2)close=true;
        if(!close&&danger<me.health()*.05){try{me.recall();log("recall");return;}catch(const error&){}}
        move_to(map::spawn_region(team::ally),true);combat(-1,true);log("retreat");return;
    }
    if(handle_enemies())return;
    if(bank())return;
    if(!spawn&&me.gold_count()>=(round<250?110u:180u)&&me.gem_count()==0&&capturing<0){   // early first items: top teams own 2x our items at r50
        bool close=false;for(auto& e:enemies)if(dist(e.pos,me.position())<=e.range+3)close=true;
        if(!close&&threat(me.position())<1){try{me.recall();log("shop-recall");return;}catch(const error&){}}
    }

    // A claimed capture is finished regardless of where the pack is heading next.
    if(capturing>=0){
        auto& c=groups[capturing];
        const bool visible_reward=!(c.spawns&visible).is_empty()&&c.reward;
        if(capture_since<0||capture_group!=capturing){capture_since=round;capture_group=capturing;}
        // v24i: yellow brick road - each road is one 30-camp group spanning the map; an enemy on the far end contests
        // the capture out of sight and it never completes (we stood on a spawn tile r21-r180). Only for groups too
        // big to see whole (>=20 camps): v24e applied this to every group and lost 17 of 490 bench games.
        if(visible_reward&&c.probes.size()>=20&&c.spawns.is_set(me.position())){if(on_spawn_since<0)on_spawn_since=static_cast<int>(round);}
        else on_spawn_since=-1;
        if(on_spawn_since>=0&&static_cast<int>(round)>on_spawn_since+12){
            ban(capturing,120);capturing=-1;capture_since=-1;on_spawn_since=-1;log("capture-contested");}
        else if(visible_reward&&round>capture_since+150){   // only a truly stuck capture
            ban(capturing,60);capturing=-1;capture_since=-1;log("capture-giveup");}
        else if(visible_reward){
            if(pack_mode){
                write_byte(kClaimGroup,static_cast<std::uint8_t>(capturing+1));
                write_byte(kClaimSlot,static_cast<std::uint8_t>(slot+1));
                write_byte(kClaimStamp,static_cast<std::uint8_t>(round&0xFF));
            }
            if(!c.spawns.is_set(me.position()))move_to(c.spawns);
            combat(-1,false);
            log("capture",capturing);return;
        }
        capturing=-1;
    }
    int target=(pack_mode&&role==0)?leader_target():solo_target();
    // Never fight a monolith down ourselves, but take one that someone left uncaptured nearby.
    for(unsigned i=0;i<groups.size();++i){
        auto& m=groups[i];
        if(m.monolith&&m.reward&&!(m.spawns&visible).is_empty()&&dist(me.position(),m.center)<=10){target=static_cast<int>(i);break;}
    }
    // Contested-altar maps (eight: one central altar; collision: both altars on the mirror line).
    // Audit: on eight we lost 15055 gems in bags over 42 games, mostly carriers alone at the altar
    // (81 "bank" deaths, no ally within 5 in most). Bag carriers get an escort from bag-less allies.
    if(contested_altars<0){
        // Altars are blocked tiles: measure from their walkable neighbours. Strict: every altar within
        // 3 steps of equidistant, and at most 2 altars (eight, collision, contest-style maps).
        bool all=!altar_pos.empty()&&altar_pos.size()<=2;int unreach=0;
        for(auto a:altar_pos){int hd=1<<20,ed=1<<20;
            for(auto q:disk(a,1).positions()){if(terrain.is_set(q))continue;hd=std::min<int>(hd,home_distance.get(q));ed=std::min<int>(ed,enemy_distance.get(q));}
            if(hd>=60000||ed>=60000){++unreach;continue;}   // walled-off altar (collision): ignore
            if(std::abs(ed-hd)>3)all=false;}
        if(unreach>=static_cast<int>(altar_pos.size()))all=false;
        contested_altars=all?1:0;
    }
    if(contested_altars==1&&siege_group<0&&me.gem_count()==0&&capturing<0){
        const cambc::champion* carrier=nullptr;int bd=9;
        for(auto& c:allies){int d=dist(c.position(),me.position());if(c.gem_count()>=40&&d<bd){bd=d;carrier=&c;}}
        if(carrier&&!enemies.empty()&&round>=escort_block_until){
            if(++escort_rounds>80){escort_rounds=0;escort_block_until=round+30;}
            if(bd>2)move_to(disk(carrier->position(),2));
            combat(-1,true);log("escort");return;
        }
    }
    // Siege (gold-only maps, e.g. contest). Audit of 28 top-100 contest games: we never scored; the
    // opponent killed a 200-gem monolith from round ~420-1000, then every ~150 rounds, to 1000.
    // From round 300 the whole team gathers at our monolith, attacks once most of us are there,
    // and the capture/bank logic takes the reward (a killed monolith nearby is always captured).
    // Escort: a teammate carrying a monolith bag walks to the central altars, where a lone carrier
    // was killed and the bag handed to the enemy (local test). Everyone stays with the carrier.
    if(siege_group>=0&&me.gem_count()<100){
        int rk=-1;for(int k=0;k<std::min(team_size,6);++k)if(k!=slot&&shared[k]==255&&ally_alive(k))rk=k;
        if(rk>=0){if(rally_since<0)rally_since=round;}else rally_since=-1;
        if(rk>=0&&round<rally_since+70){
            const cambc::champion* cr=nullptr;for(auto& c:allies){try{if(c.champion_name()==roster[rk].champion_name()){cr=&c;break;}}catch(const error&){}}
            if(cr){if(dist(me.position(),cr->position())>2)move_to(disk(cr->position(),2));}
            else move_to(map::spawn_region(team::ally));
            combat(-1,true);log("rally");return;
        }
    }
    if(siege_group>=0){
        // A 200-gem reward split between capturers leaves several sub-100 bags (ChatGPT review).
        const cambc::champion* carrier=nullptr;
        for(auto& c:allies)if(c.gem_count()>=40&&c.gem_count()>=2*me.gem_count()+1&&(!carrier||c.gem_count()>carrier->gem_count()))carrier=&c;
        if(carrier&&round>=escort_block_until){
            if(++escort_rounds>80){escort_rounds=0;escort_block_until=round+30;}
            if(dist(me.position(),carrier->position())>2)move_to(disk(carrier->position(),2));
            combat(-1,true);log("escort");return;
        } else escort_rounds=0;
    }
    // Ladder contest (v17i vs "y", 73a00a9e): our siege from r300 took ~350 rounds per kill, we died
    // constantly and fed gold, and the opponent (who never sieged) took each reward: 0-600 gems,
    // 2345-13225 gold. Now: (1) vulture any visible monolith under 50% HP, whoever softened it;
    // (2) siege only from r600 (top teams' first kill: median ~r750, after farming gold for items);
    // (3) abandon a siege that has not killed within 150 rounds, and farm gold for 150 rounds.
    if(siege_group>=0){
        int vul=-1;
        for(unsigned i=0;i<groups.size();++i){auto& g=groups[i];if(!g.monolith||g.gems<=0||g.reward)continue;
            double hp=g.hp;bool seen=false;
            for(auto& m:monsters)if(m.group==static_cast<int>(i)){double base,unused;camp_stats_for(m.handle.kind(),base,unused);hp-=std::max(0.0,base-m.hp);seen=true;}
            if(seen&&hp<g.hp*.5&&dist(me.position(),g.center)<=25){vul=static_cast<int>(i);break;}}
        if(vul>=0){target=vul;log("vulture",vul);}
    }
    if(siege_group>=0&&siege_started>=0&&round>siege_started+150&&!groups[siege_group].reward){siege_cooldown=round+150;siege_started=-1;}
    if(target<0||!groups[target].monolith)
    if(siege_group>=0&&round>=POLARIS_SIEGE_R&&round>=siege_cooldown){
        int st=siege_group;
        for(unsigned i=0;i<groups.size();++i)if(groups[i].monolith&&groups[i].gems>0&&groups[i].reward&&dist(me.position(),groups[i].center)<=14){st=static_cast<int>(i);break;}
        auto& sg=groups[st];
        if(sg.reward){target=st;siege_started=-1;}
        else if(sg.ready_round>round+25){}   // respawning: farm gold meanwhile
        else{
            int here=0;for(auto c:allies)if(dist(c.position(),sg.center)<=7)++here;
            if(dist(me.position(),sg.center)<=7)++here;
            int alive=0;for(int k=0;k<team_size;++k)if(ally_alive(k))++alive;
            // Vision is short, so the head-count only sees a few allies: go at 3, or after 12 rounds staged.
            if(dist(me.position(),sg.center)<=7){if(staged_since<0)staged_since=round;}else staged_since=-1;
            if(siege_wait_since<0)siege_wait_since=round;
            if(here>=std::min(3,std::max(2,alive-2))||(staged_since>=0&&round>=staged_since+12)||round>=siege_wait_since+40){target=st;siege_wait_since=-1;if(siege_started<0)siege_started=round;}
            else{   // stage just outside its reach until the team has gathered
                bitboard stage=disk(sg.center,6)&~disk(sg.center,4)&~terrain;
                if(!stage.is_set(me.position()))move_to(stage);
                combat(-1,false);log("siege-wait",st);return;
            }
        }
    }
    {bool gem_camps=false;for(auto& gg:groups)if(gg.gems>0&&!gg.monolith)gem_camps=true;
     if(!forced_solo&&!pack_mode&&gem_camps&&round>=120&&global_submitted_gems(team::ally)==0&&me.gem_count()==0){pack_mode=true;log("to-pack");}}
    if(target<0){
        if(!spawn&&me.health()<me.max_health()*.9f&&enemies.empty()){try{me.recall();return;}catch(const error&){}}
        // v23v: ranked starvation/shortcut losses - the pack sat in a pocket for 1800 rounds with every camp group
        // unreachable by walking (log: 14/14 unreachable). Nothing to do here for a while: recall home and re-plan.
        if(idle_since<0||round>idle_since+60)idle_since=round;
        if(!spawn&&enemies.empty()&&me.gem_count()==0&&round>=idle_since+8){try{me.recall();idle_since=-1;log("idle-recall");return;}catch(const error&){}}
        combat(-1,false);log("idle");return;
    }
    idle_since=-1;
    auto& g=groups[target];
    if(g.reward&&(!pack_mode||role==1)){
        capturing=target;
        if(!g.spawns.is_set(me.position()))move_to(g.spawns);
        log("capture",target);return;
    }
    if(g.reward){
        const bool claimed_by_other=shared[kClaimGroup]==target+1&&shared[kClaimSlot]!=slot+1&&age(round,shared[kClaimStamp])<=5;
        // Rotate captures so every champion earns gold to spend; the last capturer yields if anyone else is here.
        bool others_here=false;
        for(auto c:allies)if(dist(c.position(),g.center)<=4)others_here=true;
        const bool my_turn=shared[kClaimSlot]!=slot+1||!others_here||g.gems>=150;
        if(g.gems>=150){   // split a big reward: every squad member stands on the region
            capturing=target;
            if(!g.spawns.is_set(me.position()))move_to(g.spawns);
            log("capture",target);return;
        }
        if(!claimed_by_other&&my_turn){
            capturing=target;
            write_byte(kClaimGroup,static_cast<std::uint8_t>(target+1));
            write_byte(kClaimSlot,static_cast<std::uint8_t>(slot+1));
            write_byte(kClaimStamp,static_cast<std::uint8_t>(round&0xFF));
            if(!g.spawns.is_set(me.position()))move_to(g.spawns);
            log("capture",target);return;
        }
    }
    // Not the capturer: get off the region so the reward is not split into small bags.
    if(g.reward&&capturing!=target&&g.spawns.is_set(me.position())&&me.can_move()){
        bitboard off=grow(g.spawns,1)&~g.spawns&~terrain;
        if(move_to(off)){log("step-off",target);return;}
    }
    bool acted=combat(target,false);
    if(!acted&&me.can_move()){
        bitboard goals;goals.clear();
        bool found=false;
        for(auto& m:monsters)if(m.group==target){goals|=disk(m.pos,me.attack_range());found=true;}
        if(!found)goals=grow(g.spawns,1);   // v21h: camps unseen (walls block vision) -> walk up to them; range-3 champions idled outside walled pockets
        goals&=~terrain;
        if(g.reward)goals&=~g.spawns; // leave the capture to the claimant
        move_to(goals);
        combat(target,false);
    }
    log("farm",target);
}

// v19n: v19i's eight result without v18z/v19h resets. Focus valuation only on single-central-altar contested maps.
double Bot::focus_w() const{return contested_altars==1&&altar_pos.size()==1?.5:0.0;}

