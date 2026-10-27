// Polaris v27 (core rebuilt 25 Oct; see the v27 core section below). Was: Polaris V9 — adaptive squads, map-type rules, carrier safety, bag hunting, invasion-aware posture, map-aware draft. Cambridge Battlecode 2026a.
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
    // v25n: golems (5000 HP, 120 str, range 4; 6 ranked maps) fell to the default and looked like harmless 500-HP
    // camps, and gem/gold clusters have 120 HP, not 500 (SDK camp_type docs).
    case camp_type::golem:hp=5000;str=120;break;
    case camp_type::gem_cluster:case camp_type::gold_cluster:hp=120;str=0;break;
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
    pack_mode=false;   // v27: one planner for every map (squad target + cluster claims); shared bytes are re-assigned
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
    // v25o: Heart of Ruin's dash (1.5x focus area hit + stun) and shield scale with focus (growth 12 vs strength 3.5);
    // the #1 team's HoR (300 games) builds Treasure-focus, Home-health, Durability-health, then Power-focus.
    if(me.champion_name()==champion_type::heart_of_ruin)focus_build=true;
    frontline=!is_carry(me.champion_name());
    last_pos=me.position();initialized=true;
            break;}
        }
    }
}

// Squads split only once each one is strong enough to farm most of our home income alone,
// judged from the members' current stats (the top teams open as five and split later).
bool Bot::ally_alive(int k) const {
    if(k==slot)return true;
    if(alive_round[k]!=round+1){alive_round[k]=round+1;bool a=true;try{a=roster[k].is_alive();}catch(const error&){}alive_val[k]=a;}
    return alive_val[k];
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
    if(false){   // v27: byte 7 is no longer the threat cell
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
        int a=0;   // v27: byte 6 is the team focus target, not an aggression score
        // Prior from the draft: a stun-heavy comp starts us in the defensive posture.
        // Issue #17: the stun-draft prior (most top-100 drafts) started us defensive; dropped.
        if(my_evidence>=1){int add=static_cast<int>(my_evidence);my_evidence-=add;a=std::min(255,a+add);}
        if(slot==0&&round%2==0&&a>0)--a;                                                        // forget
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
        } else if(false&&!raid_failed&&round>=120&&max_aggr<25&&deaths<=2&&std::max(map::width(),map::height())>=50&&
                  static_cast<int>(global_submitted_gems(team::enemy))>=static_cast<int>(global_submitted_gems(team::ally))+40){
            raid=true;raid_deaths0=deaths;std::cout<<"RAID on r="<<round<<" s="<<slot<<'\n';
        }
    }
    {const unsigned scored=global_submitted_gems(team::ally);if(scored!=last_score){last_score=scored;last_score_round=round;}}
    if(round%5==0||!stats_ready){stats_ready=true;for(int k=0;k<team_size&&k<8;++k)try{auto c=roster[k];if(k==slot||c.is_visible()){ally_stats[k]={c.strength(),c.focus(),c.max_health()};}}catch(const error&){}}
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

constexpr unsigned kCaptureGiveUp=25;   // v29a: a capture takes 5 rounds (3 with the emblem); 60 let a blocked one eat a minute
void Bot::shop(){
    auto& me=self();
    // v25s: carry an altar lock (10 gold). Placing one cancels an enemy tribute in progress and blocks their tributes
    // there until they spend 5 basic attacks; we can still tribute at it. Opponents use ~3 a game; we never had one.
    try{if(me.consumables()[consumable_type::altar_lock].count()==0&&me.can_buy(consumable_type::altar_lock))me.buy(consumable_type::altar_lock);}catch(const error&){}
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
    // v25k (idea from the public "siege" bot's README, re-implemented): ranged carries open with a Treasure emblem of their
    // stat (+20% gold), melee with Monster; both then Jungle Health (-30% camp damage) and Durability Health, and stack
    // Bruiser of their stat for good (5 stat shards + 1 of each other = 7 shards' worth for the price of Power's 6).
    const Step T{focus_build?item_type::treasure_shard_of_focus:item_type::treasure_shard_of_strength,focus_build?item_type::treasure_emblem_of_focus:item_type::treasure_emblem_of_strength},
        JH2{item_type::jungle_shard_of_health,item_type::jungle_emblem_of_health};
    order={me.attack_range()>=3?T:M,JH2,D};
    // v22w: Ryth is the tank. Elite contest replay (team rated 1907): their Ryth stacked health emblems (Power, Durability,
    // Treasure, Jungle of Health) to 10,600 max HP, stood nearest the monolith (it hits only the nearest champion) and
    // let the carries kill it ~5x a game with 6 deaths in total.
    const bool tank=me.champion_name()==champion_type::ryth;
    const Step PH{item_type::power_shard_of_health,item_type::power_emblem_of_health},DH{item_type::durability_shard_of_health,item_type::durability_emblem_of_health},
        JH{item_type::jungle_shard_of_health,item_type::jungle_emblem_of_health},TH{item_type::treasure_shard_of_health,item_type::treasure_emblem_of_health};
    if(tank)order={PH,DH,JH,TH};
    const bool hor=me.champion_name()==champion_type::heart_of_ruin;
    const Step HOME{item_type::home_shard_of_health,item_type::home_emblem_of_health};
    if(hor)order={T,HOME,D};
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
    const auto extra=tank?item_type::power_shard_of_health:hor?item_type::power_shard_of_focus:(focus_build?item_type::bruiser_shard_of_focus:item_type::bruiser_shard_of_strength);   // v25k: Bruiser, not Power
    unsigned n=me.gold_count()/extra.cost();
    while(n>0){
        try{if(me.can_buy(extra,n)){me.buy(extra,n);break;}}catch(const error&){}
        n=n>1?n/2:0;
    }
}

bool Bot::move_to(bitboard goals,bool flee){
    auto& me=self();
    if(flee)flee_round=round+1;
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
        for(auto a:me.abilities())if(a.info()&&a.is_dash()&&a.is_ready()&&(flee||spell_modifier(a)<=0)){   // v25o: a damaging dash is kept for fights
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
        if(focus_idx>=0&&enemy_index(e)==focus_idx)b+=300;   // v27: team focus
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
        // v25o: damaging dashes (Heart of Ruin: 1.5x focus to every target within 1 of the landing tile, 1-turn stun)
        // were only ever spent on travel. Land where the hit is worth most; never while fleeing this turn.
        if(a.is_dash()&&spell_modifier(a)>0&&flee_round!=round+1){
            auto meta=a.get<ability_dash>();
            const double hit=meta.modifier*focus;
            for(auto c:(a.valid_tiles()&~(terrain|occupied)).positions()){
                double v=0;
                for(auto& m:monsters)if((group<0||m.group==group)&&dist(c,m.pos)<=meta.radius)v+=std::min(static_cast<double>(m.hp),hit);
                if(players)for(auto& e:enemies)if(dist(c,e.pos)<=meta.radius){
                    v+=std::min(static_cast<double>(e.hp),hit);
                    if(meta.duration>0&&!e.stunned&&e.type!=champion_type::marcella)v+=e.channel?250:e.strength*1.5+60;}
                if(v>cast.v)cast={s,-1,false,true,c,v};
            }
        }
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


void Bot::ban(int g,int rounds){if(g<0)return;if(ban_until.size()<groups.size())ban_until.resize(groups.size(),0);ban_until[g]=round+rounds;}
bool Bot::banned(unsigned g) const{return g<ban_until.size()&&round<ban_until[g];}
static int g_guard_try_until=-1,g_guard_next_try=0;
static int g_nobank_until=0;static std::vector<int> g_walk_pos;   // v29e: oscillation detector for the bank walk
bool Bot::bank(){
    auto& me=self();
    const int gems=static_cast<int>(me.gem_count());
    if(gems<100&&slot<6&&shared[slot]==255)write_byte(slot,0);   // clear our rally flag
    if(gems<=0){bag_since=-1;bank_alone_since=-1;convoy_recalled=false;g_walk_pos.clear();return false;}
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
    if(carry_override>0)carry=carry_override;   // v27: careful mode banks at 10
    my_danger=danger_at(me.position(),gems);
    const bool risky_bag=gems>=22&&my_danger*gems>=6.0;
    const bool go=win||endgame||rush||gems>=carry||(gems>=20&&ad<=6)||me.health()<me.max_health()*.4f||risky_bag;
    if(!go)return false;
    if(round<g_nobank_until&&!win&&!endgame)return false;   // v29e: the altar was unreachable; farm instead of walking in circles
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
        // v29b: 01shortcut - the guard held a 170-355 gem bag from round 250 to the end (0 gems submitted, opponents banked 1000).
        // A big bag is worth a bounded attempt: try for 60 rounds, then back off 400 rounds (boss-battle's stuck carrier is bounded too).
        if(guarded&&gems>=80){
            if(g_guard_try_until<0&&round>=g_guard_next_try){g_guard_try_until=round+60;g_guard_next_try=round+460;}
            if(g_guard_try_until>=0&&round<g_guard_try_until)guarded=false;
            else if(g_guard_try_until>=0)g_guard_try_until=-1;
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
                if(threat(me.position())<1&&!convoy_recalled){convoy_recalled=true;if(!unsafe_recall)try{me.recall();log("convoy-recall");return true;}catch(const error&){}}
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
            // v25s: our own lock: tribute as normal
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
        if(!unsafe_recall)try{me.recall();log("bank-recall");return true;}catch(const error&){}
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
    // v29e: 02the-pack - the only altar is ringed by 17 sleeping camps, so no submit tile is reachable; two champions oscillated
    // between 2-3 tiles 6 steps from it for 1900 rounds (0 gems, 486 gold earned, lost the gold tiebreak). A walk that has visited
    // at most 3 distinct tiles in its last 40 bank turns, still outside the submit range, is a loop: stop banking for 150 rounds and farm.
    // (v29c/d used 'no progress in N rounds' and also fired on legitimate waits.)
    g_walk_pos.push_back(me.position().x*256+me.position().y);
    if(g_walk_pos.size()>40)g_walk_pos.erase(g_walk_pos.begin());
    if(g_walk_pos.size()==40&&ad>constants::submit_gems_range+2&&!win&&!endgame){
        std::vector<int> u=g_walk_pos;std::sort(u.begin(),u.end());u.erase(std::unique(u.begin(),u.end()),u.end());
        if(u.size()<=3){g_nobank_until=round+150;g_walk_pos.clear();log("bank-loop");return false;}
    }
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
// ======================================================================================================================
// v27 core (25 Oct). Mid-rank scrims: v25u won 4/100 vs ranks 55-136 and every tweak since was neutral, so the decision
// core is rebuilt around the design the stronger public bots describe (siege/warlord README; re-implemented, no code
// copied): one squad target the team agrees on through shared memory, engaged only when the champions present can clear
// it; harmless clusters claimed by single champions; camp scores that charge the trips home to heal; multi-trip sieges of
// groups too strong for one fight; a careful mode after repeated deaths; team-wide fight decisions with a shared focus.
// Shared memory: 0 squad target (group+1), 1-5 cluster claim per slot (group+1), 6 focus enemy (idx+1 | stamp<<3).
// ======================================================================================================================
namespace {
constexpr int kSquad=0,kClaim0=1,kFocus=6;
constexpr double kEff=.6;          // share of paper damage a group really deals (travel, retreats, stragglers)
constexpr int kSiegeFrom=500;
constexpr double kSiegeKill=.8;   // v27m: squad only for a monolith siege the team's forecast kills within this share of its HP
constexpr bool solo_only=false;
constexpr double kSquadBias=.8;
constexpr double kGoldW=.10;   // v27m: gold weight .15->.10     // gold counts 0.15 of a gem in target choice (gems win; first test at 0.3 farmed gold clusters all game)
}

// v27m: v25u's solo farm targeting (claims moved to the v27 claim bytes 1-5).
int Bot::solo_target(){
    // Split play: each champion takes camps it can clear alone and publishes its
    // choice in shared[slot] so teammates spread out.
    auto& me=self();
    bool any_gems=false;for(auto& g:groups)if(g.gems>0)any_gems=true;
    const double gold_w=!any_gems?1.0:(round<250?.15:round<700?.08:.04);
    const double my_dps=std::max(1.0,dps()),my_hp=me.health();
    // Issac shadows Cassi in solo play: split up, one pick kills both.
    if(me.champion_name()==champion_type::issac&&!pack_mode){
        for(int k=0;k<std::min(team_size,5);++k){try{if(k!=slot&&roster[k].champion_name()==champion_type::cassi&&ally_alive(k)
            &&shared[kClaim0+k]>0&&shared[kClaim0+k]<=groups.size()){objective=shared[kClaim0+k]-1;return objective;}}catch(const error&){}}
    }
    // Commit: straight-line distances jump around walls, so rescoring every turn made solo
    // champions flip between far camps. Keep a valid target and rescore every 8 rounds.
    if(objective>=0&&objective<static_cast<int>(groups.size())&&round<solo_choose+8){
        auto& g=groups[objective];
        bool taken=false;
        for(int k=0;k<std::min(team_size,5);++k)if(k<slot&&shared[kClaim0+k]==objective+1&&ally_alive(k))taken=true;
        const int wait=g.ready_round>round?static_cast<int>(g.ready_round-round):0;
        if(!taken&&wait<=dist(me.position(),g.center)+20)return objective;
    }
    solo_choose=round;
    bitboard sseen;distance_field sfield;bool use_field=false;
    if(fuel_remaining()>60000){sfield.compute(terrain,disk(me.position(),0),sseen,static_cast<std::uint16_t>(260));use_field=true;}
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
        if(use_field){   // v27n: walking distance (water/walls make straight lines useless); unreachable groups are skipped
            int t=100000;for(auto p:g.probes)t=std::min<int>(t,sfield.get(p));
            if(t>=static_cast<int>(distance_field::unreachable))continue;
            travel=t;}
        int wait=g.ready_round>round?static_cast<int>(g.ready_round-round):0;
        if(wait>travel+10){   // v23v: respawning - remember the soonest one to pre-position at instead of idling
            const double fs=value/(wait+clear+constants::capture_time+.3*g.altar_d+2);
            if(wait<400&&fs>fb_s){fb_s=fs;fb=static_cast<int>(i);}
            continue;}
        int taken=0;
        for(int k=0;k<std::min(team_size,5);++k)if(k!=slot&&shared[kClaim0+k]==i+1&&ally_alive(k))++taken;
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
    objective=best;solo_score=best>=0?best_s:0;
    return best;
}

bool Bot::harmless(const Group& g) const{return g.str<=0;}

double Bot::rem_hp(int i) const{
    const auto& g=groups[i];double hp=g.hp;
    for(auto& m:monsters)if(m.group==i){double base,unused;camp_stats_for(m.handle.kind(),base,unused);hp-=std::max(0.0,base-m.hp);}
    return std::max(hp,g.hp*.05);
}

// Damage a group deals while `dps` worth of champions clears it, and the rounds it takes.
void Bot::forecast(int i,double dps,double& dmg,double& rounds) const{
    const auto& g=groups[i];
    rounds=rem_hp(i)/std::max(1.0,dps*kEff);
    const bool elk_pack=g.probes.size()>=2&&g.probes.size()<8&&g.elks>=1;
    const double share=g.probes.size()==1?1.0:g.probes.size()>=8?.45:elk_pack?.75:.4;
    dmg=harmless(g)?0:g.str*rounds*share;
}

// Value per round of the squad target for the team, estimated cheaply from here (no path search), so every champion,
// not only the leader, can weigh its own cluster against its share of the squad's income.
double Bot::squad_rate(int i) const{
    if(i<0||i>=static_cast<int>(groups.size()))return 0;
    const auto& g=groups[i];
    double tdps,thp;team_power(tdps,thp);
    double dmg,rounds;forecast(i,tdps,dmg,rounds);
    const int travel=static_cast<int>(dist(self().position(),g.center)*1.3);
    const int wait=g.ready_round>round?static_cast<int>(g.ready_round-round):0;
    const double heal=dmg/std::max(1.0,thp)*(2.0*g.home_d+10);
    const double cost=std::max(travel,wait)+rounds+heal+constants::capture_time+(g.gems>0?g.altar_d+g.gems/10.0:0)+4;
    return (g.gems+kGoldW*g.gold)/cost;
}

bool Bot::careful() const{
    int n=0;for(unsigned r:team_deaths)if(round<r+150)++n;
    return n>=3;
}

void Bot::team_power(double& dps,double& hp) const{
    dps=0;hp=0;
    for(int k=0;k<team_size&&k<8;++k){
        if(!ally_alive(k))continue;
        auto& st=ally_stats[k];
        dps+=st[0]+st[1]*.3;hp+=std::max(st[2],1.0);
    }
    if(dps<=0){dps=dps_self*team_size;hp=1000.0*team_size;}
}

bool Bot::guards_altar(int i) const{
    if(!groups[i].monolith)return false;
    for(auto q:altar_goals.positions())for(auto p:groups[i].probes)if(dist(p,q)<=2)return true;
    return false;
}
bool Bot::altars_walled() const{
    if(altar_goals.is_empty())return false;
    for(auto q:altar_goals.positions()){
        bool g2=false;
        for(auto& gg:groups){if(!gg.monolith||gg.reward||gg.ready_round>round)continue;   // v27e: only monoliths wall an altar (starfish: 6 elks beside the altar made v27b siege them from r23)
            for(auto pr:gg.probes)if(dist(pr,q)<=2){g2=true;break;}
            if(g2)break;}
        if(!g2)return false;
    }
    return true;
}

// Team plan: the best dangerous group for the whole squad (value per round, all costs charged).
int Bot::squad_target(){
    auto& me=self();
    double tdps,thp;team_power(tdps,thp);
    bitboard seen;distance_field field;
    field.compute(terrain,disk(me.position(),0),seen,static_cast<std::uint16_t>(220));
    const bool walled=altars_walled();
    const bool cf=careful();
    int best=-1;double best_s=0;
    for(unsigned i=0;i<groups.size();++i){
        auto& g=groups[i];
        if(harmless(g)||banned(i))continue;
        const double value=g.gems+kGoldW*g.gold+(walled&&guards_altar(i)?1000:0);
        if(value<=0)continue;
        int travel=100000;for(auto p:g.probes)travel=std::min<int>(travel,field.get(p));
        if(travel>=static_cast<int>(distance_field::unreachable))continue;
        const int wait=g.ready_round>round?static_cast<int>(g.ready_round-round):0;
        if(wait>travel+40)continue;
        double dmg,rounds;forecast(i,tdps,dmg,rounds);
        const bool unlock=walled&&guards_altar(i);
        double extra=0;
        if(dmg>thp*(unlock?.8:.55)){
            if(!unlock&&round<kSiegeFrom)continue;
            const double trips=dmg/std::max(1.0,thp*.45);
            if(trips>(unlock?8:2))continue;
            extra=(std::ceil(trips)-1)*(2.0*g.home_d+15);
        }
        const double heal=dmg/std::max(1.0,thp)*(2.0*g.home_d+10);
        const double bank_t=g.gems>0?g.altar_d+g.gems/10.0:0;
        const double cost=std::max(travel,wait)+rounds+heal+extra+constants::capture_time+bank_t+4;
        const double side=static_cast<double>(g.home_d)/std::max(1,g.home_d+g.enemy_d);
        const double sw=side>.55?(cf?.15:.7):1.0;
        double s=value*sw/cost;
        for(auto& d:deaths)if(dist(d.first,g.center)<=6&&round<d.second+300)s*=.75;
        if(static_cast<int>(i)==squad_goal)s*=1.25;   // keep the plan unless clearly better
        if(s>best_s){best_s=s;best=static_cast<int>(i);}
    }
    squad_score=best_s;
    return best;
}

// My own work: the best harmless cluster nobody else has claimed.
int Bot::cluster_target(double& score){
    auto& me=self();score=0;
    if(fuel_remaining()<30000)return cluster_goal;
    bitboard seen;distance_field field;
    field.compute(terrain,disk(me.position(),0),seen,static_cast<std::uint16_t>(90));
    const bool cf=careful();
    int best=-1;
    for(unsigned i=0;i<groups.size();++i){
        auto& g=groups[i];
        if(banned(i)||g.monolith)continue;
        // v27b: also any group I can clear alone without being forced home (corners: single-elk 15-22 gem groups were
        // all left to the 5-champion squad; the top teams kill ~19 elks a game, mostly one champion per elk).
        double sdmg=0,srounds=0;
        if(!harmless(g)){if(g.probes.size()>4)continue;forecast(static_cast<int>(i),dps_self/kEff*.9,sdmg,srounds);
            if(sdmg>self().health()*.7)continue;}
        const double value=g.gems+kGoldW*g.gold;
        if(value<=0)continue;
        bool taken=false;for(int k=0;k<5&&k<team_size;++k)if(k!=slot&&shared[kClaim0+k]==i+1&&ally_alive(k))taken=true;
        if(taken)continue;
        int travel=100000;for(auto p:g.probes)travel=std::min<int>(travel,field.get(p));
        if(travel>=static_cast<int>(distance_field::unreachable))continue;
        const int wait=g.ready_round>round?static_cast<int>(g.ready_round-round):0;
        if(wait>travel+10)continue;
        const double clear=g.reward?0:rem_hp(i)/std::max(1.0,dps_self*.9);
        const double heal=sdmg/std::max(1.0,static_cast<double>(self().max_health()))*(2.0*g.home_d+10);
        const double cost=std::max(travel,wait)+clear+heal+constants::capture_time+.3*g.altar_d+2;
        const double side=static_cast<double>(g.home_d)/std::max(1,g.home_d+g.enemy_d);
        double s=value*(side>.55?(cf?.1:.6):1.0)/cost;
        // v27f: the contested middle is where both teams fight; a lone champion there is the one picked off (starfish: lone
        // champions farmed single 4-gem wolves at the centre and died 31 times vs Marcus; v25u, which penalised it, won 1039-92).
        if(side>=.4&&side<=.6)s*=cf?.2:.5;
        for(auto& d:deaths)if(dist(d.first,g.center)<=6&&round<d.second+300)s*=.6;
        if(static_cast<int>(i)==cluster_goal)s*=1.3;
        if(s>score){score=s;best=static_cast<int>(i);}
    }
    return best;
}

int Bot::enemy_index(const Enemy& e) const{
    for(unsigned k=0;k<enemy_roster.size();++k)if(id(enemy_roster[k])==id(e.handle))return static_cast<int>(k);
    return -1;
}

// Team fight decision: one shared focus, fight unless clearly outmatched, leave when outnumbered.
bool Bot::fight(){
    auto& me=self();
    if(enemies.empty()){focus_idx=-1;return false;}
    const auto pos=me.position();
    int e6=0,a6=0,beside=0;double ours=0,theirs=0;
    ours+=(me.strength()+.5*me.focus())*me.health();
    for(auto c:allies){const int d=dist(c.position(),pos);
        if(d<=8)ours+=(c.strength()+.5*c.focus())*c.health();
        if(d<=6)++a6;
        if(d<=2)++beside;}
    int nearest=1000;
    for(auto& e:enemies){const int d=dist(e.pos,pos);nearest=std::min(nearest,d);
        if(d<=8)theirs+=(e.strength+.5*e.focus)*e.hp;
        if(d<=6)++e6;}
    if(nearest>7){focus_idx=-1;return false;}
    const double need=careful()?1.3:1.6;
    const bool lost=ours*need<theirs;
    const bool outnum=e6>a6+2||(e6>a6+1&&ours<theirs);
    const bool danger=me.health()<threat(pos)*2.5+me.max_health()*.1f;
    tr_ratio=theirs>0?ours/theirs:9.99;
    // Shared focus: keep a fresh team focus if it is in sight, otherwise pick the weakest enemy in reach and publish it.
    focus_idx=-1;
    {const std::uint8_t b=shared[kFocus];
     if(b){const int idx=(b&7)-1;const unsigned st=(b>>3)&31,now=(round>>1)&31;
         if(((now-st)&31)<=3)for(auto& e:enemies)if(enemy_index(e)==idx&&dist(e.pos,pos)<=8)focus_idx=idx;}}
    if(focus_idx<0){
        const Enemy* t=nullptr;double bv=1e18;
        for(auto& e:enemies){if(dist(e.pos,pos)>6)continue;
            double v=e.hp*(is_carry(e.type)?.75:1.0)*(e.stunned?.7:1.0)*(e.channel?.5:1.0);
            if(v<bv){bv=v;t=&e;}}
        if(t){focus_idx=enemy_index(*t);
            if(focus_idx>=0&&focus_idx<7)write_byte(kFocus,static_cast<std::uint8_t>((focus_idx+1)|(((round>>1)&31)<<3)));}
    }
    if(danger||lost||outnum){
        if(beside>=2&&!lost&&!danger){/* two teammates beside me and the fight is not lost: stay */}
        else{
            combat(-1,true);   // hit whatever is in reach on the way out (melee can walk and hit)
            move_to(map::spawn_region(team::ally),true);
            log(danger?"pvp-hurt":lost?"pvp-lost":"pvp-outnum");return true;
        }
    }
    if(nearest>5&&!(me.gem_count()==0&&nearest<=7))return false;
    if(combat(-1,true)){hold_since=-1;log("pvp-fight");return true;}
    const Enemy* t=nullptr;
    for(auto& e:enemies)if(enemy_index(e)==focus_idx)t=&e;
    if(!t){int bd=1000;for(auto& e:enemies){int d=dist(e.pos,pos);if(d<bd){bd=d;t=&e;}}}
    if(!t)return false;
    const bool ranged=me.attack_range()>=3;
    if(ranged){
        bool mate_on=false;for(auto c:allies)if(dist(c.position(),t->pos)<=1)mate_on=true;
        if(!mate_on&&t->hp>t->maxhp*.25f&&dist(t->pos,pos)<=me.attack_range()+2){
            if(hold_since<0)hold_since=static_cast<int>(round);
            if(static_cast<int>(round)<hold_since+6){log("pvp-hold");return true;}
        }
        bitboard ring=disk(t->pos,me.attack_range())&~disk(t->pos,me.attack_range()-1)&~terrain;
        if(ring.is_empty())ring=disk(t->pos,me.attack_range());
        if(!ring.is_set(pos))move_to(ring);
    } else move_to(disk(t->pos,1));
    combat(-1,true);log("pvp-engage");return true;
}

void Bot::play_turn(){
    auto& me=self();
    round=round_number();
    if(!initialized){init();return;}
    update_profile();
    if(!me.is_alive()){
        if(was_alive&&last_pos.x>=0){deaths.push_back({last_pos,round});if(deaths.size()>10)deaths.erase(deaths.begin());}
        if(was_alive&&slot<5)write_byte(kClaim0+slot,0);
        was_alive=false;
        try{shop();}catch(const error&){}
        return;
    }
    if(!was_alive)respawn_round=round;
    was_alive=true;
    observe();
    dps_self=std::max(1.0,dps());
    if(capturing>=0&&me.gem_count()>last_gems){
        auto& g=groups[capturing];g.reward=false;g.ready_round=round+g.respawn;capturing=-1;}
    last_gems=me.gem_count();
    stalled=me.position()==last_pos?stalled+1:0;
    last_pos=me.position();
    if(me.is_teleporting()||me.is_recalling()){turn_hp=me.health();return;}
    {const float hp=me.health();const bool hit=turn_hp>=0&&hp<turn_hp-1;turn_hp=hp;
     camp_reach.clear();bool in_reach=false;
     for(auto& m:monsters){if(!m.awake||m.strength<=0)continue;const int d=dist(m.pos,me.position());if(d>6)continue;
        int r=1;try{r=m.handle.attack_range();}catch(const error&){}
        camp_reach|=disk(m.pos,r+1);if(d<=r+1)in_reach=true;}
     unsafe_recall=hit||in_reach;}
    const bool cf=careful();
    // Tribute guard: cancel a channel the enemies in reach would win before it completes, unless the bag wins the game.
    if(me.is_submitting_gems()){
        const bool win=static_cast<int>(global_submitted_gems(team::ally)+me.gem_count())>=static_cast<int>(constants::winning_gems);
        double t=threat(me.position());
        if(!win&&me.remaining_channel_time()>1&&t*me.remaining_channel_time()>me.health()*.9)
            try{me.cancel_submit_gems();}catch(const error&){}
        else return;
    }
    const bool spawn=map::spawn_region(team::ally).is_set(me.position());
    if(spawn||me.champion_name()==champion_type::tavi)shop();
    if(!spawn)try{auto lk=me.consumables()[consumable_type::altar_lock];
        if(lk.count()>0)for(auto a:altar_pos){
            if(dist(a,me.position())>2||vision::has_altar_lock(a))continue;
            bool channeling=false;for(auto& e:enemies)if(e.channel&&dist(e.pos,a)<=1)channeling=true;
            const bool their_side=enemy_distance.get(me.position())<home_distance.get(me.position());
            if(!channeling&&!their_side&&altar_pos.size()>2)continue;
            if(lk.use(a)){log(channeling?"lock-cancel":"lock");break;}
        }}catch(const error&){}
    // Ward: drop the free ward where we farm or bank, so respawns and arrivals there stay in sight.
    if(round>=ward_next&&!spawn){
        bool spot=false;for(auto a:altar_pos)if(dist(a,me.position())<=2)spot=true;
        if(capturing>=0)spot=true;
        if(spot){for(auto q:disk(me.position(),1).positions())if(!terrain.is_set(q)&&!occupied.is_set(q)){
            try{if(me.place_ward(q)){ward_next=round+10;break;}}catch(const error&){} }}
    }
    if(spawn&&me.health()<me.max_health()*.98f&&enemies.empty())return;
    // Escort after respawn: after two team deaths in 120 rounds, wait on spawn (up to 40 rounds) for a teammate.
    if(spawn&&enemies.empty()&&round<respawn_round+40){
        int recent=0;for(unsigned r:team_deaths)if(round<r+120)++recent;
        bool mate=false;for(auto c:allies)if(dist(c.position(),me.position())<=3)mate=true;
        if(recent>=2&&!mate&&round>respawn_round+1){log("respawn-wait");return;}
    }
    if(!me.can_move()&&!me.can_attack()&&!me.can_cast())return;
    // In contact with no dash: a lone duel is fought, a gang-up is not (top-10 replays: 3-6 enemies on one of ours).
    bool locked=false;int e6=0,a5=0;
    {bool dash=false;for(auto a:me.abilities())if(a.info()&&a.is_dash()&&a.is_ready())dash=true;
     if(!dash)for(auto& e:enemies)if(dist(e.pos,me.position())<=std::max(1,e.range))locked=true;
     for(auto& e:enemies)if(dist(e.pos,me.position())<=6)++e6;
     for(auto c:allies)if(dist(c.position(),me.position())<=5)++a5;}
    if(locked&&!spawn&&e6<=a5+2&&me.health()>me.max_health()*.3f){   // v35a: was .12f (Szymon v25z: fatal retreats started at median 6% HP, 73% after stand)
        if(!combat(-1,true)){const Enemy* t=nullptr;int bd=1000;for(auto& e:enemies){int d=dist(e.pos,me.position());if(d<bd){bd=d;t=&e;}}
            if(t){move_to(disk(t->pos,me.attack_range()));combat(-1,true);}}
        log("stand");return;}
    if(fight())return;
    // Camps: step out before a hit could kill; a teammate nearby takes over (camps hit the nearest champion).
    const double heal_at=cf?.55:.4;
    {double incoming=0;int steps=1;std::vector<std::pair<vec2,int>> hitters;const auto here=me.position();
     for(auto& m:monsters){if(!m.awake||m.strength<=0)continue;const int d=dist(m.pos,here);if(d>5)continue;
        int r=1;try{r=m.handle.attack_range();}catch(const error&){}
        if(d>r)continue;
        bool nearest=true;for(auto& c:allies)if(dist(c.position(),m.pos)<d){nearest=false;break;}
        if(!nearest)continue;
        incoming+=m.strength;steps=std::max(steps,r+1-d);hitters.push_back({m.pos,r});}
     const double buffer=incoming*std::max(me.attack_range()>=3?2.5:3.5,steps*.9)+me.max_health()*.08;
     if(incoming>0&&me.health()<buffer){
        bitboard safe=disk(here,3)&~terrain;for(auto& h:hitters)safe&=~disk(h.first,h.second);
        if(!safe.is_empty()&&move_to(safe)){combat(-1,false);log("camp-out");return;}
     }}
    const double danger=threat(me.position());
    if(!spawn&&(me.health()<me.max_health()*heal_at||danger*2.5>me.health())){
        bool close=false;for(auto& e:enemies)if(dist(e.pos,me.position())<=e.range+3)close=true;
        if(!close&&!unsafe_recall){try{me.recall();log("recall");return;}catch(const error&){}}
        if(enemies.empty()&&!camp_reach.is_empty()&&camp_reach.is_set(me.position())){
            bitboard out=disk(me.position(),3)&~terrain&~camp_reach;
            if(!out.is_empty()&&move_to(out)){log("camp-out");return;}}
        move_to(map::spawn_region(team::ally),true);combat(-1,true);log("retreat");return;
    }
    carry_override=cf?10:-1;
    if(bank())return;
    if(!spawn&&me.gold_count()>=(round<250?110u:200u)&&me.gem_count()==0&&capturing<0&&enemies.empty()&&!unsafe_recall){
        try{me.recall();log("shop-recall");return;}catch(const error&){}
    }
    // Finish a capture in progress.
    if(capturing>=0){
        auto& c=groups[capturing];
        const bool vis=!(c.spawns&visible).is_empty()&&c.reward;
        if(capture_group!=capturing){capture_since=round;capture_group=capturing;}
        if(vis&&round<static_cast<unsigned>(capture_since)+kCaptureGiveUp&&dist(me.position(),c.center)<=14){
            if(!c.spawns.is_set(me.position()))move_to(c.spawns);
            combat(-1,false);log("capture",capturing);return;
        }
        if(vis&&round>=static_cast<unsigned>(capture_since)+kCaptureGiveUp)ban(capturing,90);
        capturing=-1;
    }
    // Any visible reward close by: the champion nearest to it captures, the others step off its tiles.
    for(unsigned i=0;i<groups.size();++i){
        auto& g=groups[i];
        if(!g.reward||(g.spawns&visible).is_empty()||dist(me.position(),g.center)>10)continue;
        if(banned(i))continue;   // v29a: a capture we gave up on was re-started at once, so one champion stood on an uncapturable reward for 300 rounds (02the-pond)
        const int dm=dist(me.position(),g.center);bool mine=true;
        for(auto c:allies){int d=dist(c.position(),g.center);if(d<dm||(d==dm&&id(c)<id(me))){mine=false;break;}}
        if(mine){capturing=static_cast<int>(i);capture_since=round;capture_group=capturing;
            if(!g.spawns.is_set(me.position()))move_to(g.spawns);log("capture",capturing);return;}
        if(g.spawns.is_set(me.position())){bitboard off=grow(g.spawns,1)&~g.spawns&~terrain;if(move_to(off)){log("step-off",i);return;}}
    }
    // Plan: the lowest living slot sets the squad target every 8 rounds (or when it is gone); each champion compares
    // its own best cluster with its share of the squad's value per round.
    int lead=-1;for(int k=0;k<team_size;++k)if(ally_alive(k)){lead=k;break;}
    int sq=shared[kSquad]?shared[kSquad]-1:-1;
    if(sq>=static_cast<int>(groups.size()))sq=-1;
    if(lead==slot&&(round>=squad_choose+8||sq<0||groups[sq].ready_round>round+30||banned(sq))&&fuel_remaining()>45000){
        squad_choose=round;sq=squad_target();squad_goal=sq;write_byte(kSquad,static_cast<std::uint8_t>(sq+1));
    }
    if(sq>=0)squad_goal=sq;
    int alive=0;for(int k=0;k<team_size;++k)if(ally_alive(k))++alive;
    // v27m: farm solo (v25u's solo_target) unless the squad target is an altar-guarding monolith the whole team can kill
    // now (forecast); team fights, focus and defence are handled earlier by fight().
    bool siege_now=false;
    if(sq>=0&&groups[sq].ready_round<=round+30&&!banned(sq)&&!harmless(groups[sq])){
        double tdps,thp,dmg,rounds;team_power(tdps,thp);forecast(sq,tdps,dmg,rounds);
        const bool killable=dmg<=thp*kSiegeKill&&alive>=std::min(3,team_size);
        // a group one champion can clear alone stays a solo farm; the squad takes monoliths and big groups
        double sdmg=0,sr=0;forecast(sq,dps_self/kEff*.9,sdmg,sr);
        const bool solo_ok=!groups[sq].monolith&&groups[sq].probes.size()<=4&&sdmg<=me.health()*.7;
        if(!solo_ok&&killable){
            // compare per-champion income of the squad plan with the best solo farm (solo_target caches its score)
            solo_target();
            siege_now=groups[sq].monolith||squad_rate(sq)/std::max(1,alive)>=solo_score*kSquadBias;}
    }
    bool solo=!siege_now;
    int target=siege_now?sq:solo_target();
    if(target<0){
        double cs=0;
        if(round>=cluster_choose+8||cluster_goal<0||(cluster_goal>=0&&groups[cluster_goal].ready_round>round+20)){
            cluster_choose=round;cluster_goal=cluster_target(cs);cluster_score=cs;}
        if(cluster_goal>=0){target=cluster_goal;solo=true;}
        else if(sq>=0&&!solo_only){target=sq;solo=false;}
    }
    if(slot<5){const std::uint8_t want=(solo&&target>=0)?static_cast<std::uint8_t>(target+1):0;if(shared[kClaim0+slot]!=want)write_byte(kClaim0+slot,want);}
    if(target<0){
        if(!spawn&&enemies.empty()&&me.health()<me.max_health()*.9f&&!unsafe_recall){try{me.recall();log("idle-recall");return;}catch(const error&){}}
        combat(-1,false);log("idle");return;
    }
    auto& g=groups[target];
    // Squad target: engage only when the champions present can clear it safely (or it is a siege we are wearing down);
    // otherwise wait just outside its reach for the others.
    if(!solo&&!g.reward){
        double pd=dps_self,ph=me.health();
        for(auto c:allies)if(dist(c.position(),g.center)<=7&&dist(c.position(),me.position())<=8){pd+=c.strength()+.3*c.focus();ph+=c.health();}
        double dmg,rounds;forecast(target,pd,dmg,rounds);
        bool awake=false;for(auto& m:monsters)if(m.group==target&&m.awake)awake=true;
        const bool siege=dmg>ph*.8&&(round>=static_cast<unsigned>(kSiegeFrom)||(altars_walled()&&guards_altar(target)));
        const bool go=awake||dmg<=ph*.8||(siege&&me.health()>me.max_health()*.6f);
        int near=1000;for(auto p:g.probes)near=std::min(near,dist(p,me.position()));
        if(!go&&near<=10){
            if(stage_group!=target){stage_group=target;stage_since=static_cast<int>(round);}
            // v27g: stage at most 12 rounds, then engage anyway if healthy (>70%) with an ally within 8; else ban
            bool ally8=false;for(auto c:allies)if(dist(c.position(),me.position())<=8)ally8=true;
            const bool force=me.health()>me.max_health()*.7f&&ally8;
            if(static_cast<int>(round)<stage_since+12){
                bitboard ring=disk(g.center,6)&~terrain;for(auto p:g.probes)ring&=~disk(p,3);
                if(!ring.is_empty()&&!ring.is_set(me.position()))move_to(ring);
                combat(-1,false);log("stage",target);return;
            }
            if(!force){ban(target,60);stage_group=-1;
            if(lead==slot)squad_choose=0;}
        }
    }
    bool acted=combat(target,false);
    if(!acted&&me.can_move()){
        bitboard goals;goals.clear();bool found=false;
        for(auto& m:monsters)if(m.group==target){goals|=disk(m.pos,me.attack_range());found=true;}
        if(!found&&!g.monolith&&g.spawns.is_set(me.position())){goals=grow(g.spawns,1)&~g.spawns&~terrain;if(goals.is_empty())goals=grow(g.spawns,2)&~g.spawns;}
        else if(!found)goals=grow(g.spawns,1);
        goals&=~terrain;
        if(g.reward)goals=g.spawns;
        move_to(goals);
        combat(target,false);
    }
    log(solo?"cluster":"squad",target);
}

// v19n kept for bank(): focus valuation only on single-central-altar contested maps.
double Bot::focus_w() const{return contested_altars==1&&altar_pos.size()==1?.5:0.0;}
