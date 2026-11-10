#include "map_draft.h"
#include "draft_model.h"
#include "config.h"
#include "ctx.h"
#include "world.h"
#include <algorithm>
#include <array>
#include <cstdio>
#include <exception>

namespace mb {
namespace {
using namespace draft_model;
struct Search {
    bool attempted{},ready{};
    Features features;
    std::array<Pick,12> picks{};
    std::vector<Candidate> candidates;
    unsigned baseline{};
    int evaluated{},refined{},expected{},groups{};
    std::uint64_t used{},start{};
};
Search& search() { static Search s;return s; }
unsigned mask_of(const std::vector<cambc::champion_draft>& v) {
    unsigned mask=0;for(auto p:v) mask|=1u<<static_cast<int>(p);return mask;
}
std::array<int,12> base_order(int n) {
    return n<=3 ? cfg::draft_pref3 : n==4 ? cfg::draft_pref4 : cfg::draft_pref;
}
unsigned baseline_mask(int n) {
    unsigned m=0;for(int p:base_order(n)) if(p>=0 && p<12 && std::popcount(m)<n) m|=1u<<p;return m;
}
int distance_to(const cambc::distance_field& f,vec2 t,const World& w) {
    int best=1<<20;
    for(auto d:kDirs) {
        const auto q=t+d;if(q.x<0 || q.y<0 || q.x>=w.width || q.y>=w.height)continue;
        const auto v=f.get(q);if(v!=cambc::distance_field::unreachable)best=std::min(best,static_cast<int>(v));
    }
    return best;
}
void prepare(Search& s) {
    if(s.attempted)return;
    s.attempted=true;s.start=cambc::fuel_remaining();
    s.features.size=static_cast<int>(cambc::draft::team_size());
    s.features.capture_rounds=cambc::constants::capture_time;
    s.baseline=baseline_mask(s.features.size);
    // Only the initial draft turn has the large budget. Never rebuild during gameplay
    // or begin this work in a later low-budget draft guest.
    if(s.start<2000000 || s.features.size<1 || s.features.size>5)return;
    try {
        auto& w=World::get();
        if(cambc::fuel_remaining()<1600000)return;
        auto roots=cambc::map::spawn_region(cambc::team::ally);
        auto enemy_roots=cambc::map::spawn_region(cambc::team::enemy);
        auto walls=(w.blocked|w.camp_spawns)&~roots&~enemy_roots;
        cambc::distance_field ours,theirs;cambc::bitboard visited;
        ours.compute_with_expansion_count(walls,roots,visited);
        theirs.compute_with_expansion_count(walls,enemy_roots,visited);
        s.features.spawn_walk=1<<20;
        for(auto p:w.enemy_spawn)s.features.spawn_walk=std::min(s.features.spawn_walk,distance_to(ours,p,w));
        if(s.features.spawn_walk>100000)s.features.spawn_walk=120;
        s.features.wall_share=static_cast<float>(w.blocked.count())/std::max(1,w.width*w.height);
        std::vector<Camp> camps;
        float gold=0,gems=0;
        for(const auto& g:w.groups) {
            if(cambc::fuel_remaining()<1200000)break;
            if(g.has_monolith || g.total_hp<=0 || (!g.gold&&!g.gems))continue;
            int a=1<<20,b=1<<20;
            for(auto p:g.tiles) {a=std::min(a,distance_to(ours,p,w));b=std::min(b,distance_to(theirs,p,w));}
            if(a>120 || a>b+10)continue; // accessible own/contested economy, not enemy-backline fantasies
            camps.push_back({g.total_hp,g.total_strength,g.weighted_hp,g.neighbours,static_cast<float>(g.gold),static_cast<float>(g.gems),a,b,g.respawn});
            gold+=g.gold;gems+=g.gems;
        }
        std::stable_sort(camps.begin(),camps.end(),[](const Camp&a,const Camp&b){
            return (a.gold+4*a.gems)/(a.walk+10.f)>(b.gold+4*b.gems)/(b.walk+10.f);
        });
        if(camps.size()>36)camps.resize(36);
        s.groups=static_cast<int>(camps.size());s.features.gold_share=gold/std::max(1.f,gold+4*gems);
        if(camps.empty())return;
        for(int p=0;p<12;++p) {
            auto& pick=s.picks[p];pick.bodies=p==3 ? 2 : 1;
            for(int b=0;b<pick.bodies;++b) {
                const int physical=p==3 ? 3+b : p>3 ? p+1 : p;
                const auto type=static_cast<cambc::champion_type>(physical);
                pick.body[b]=design_summary(type);
                for(const auto& a:pick.body[b].ability)if(a.kind==model::AbilityKind::cc)pick.control+=1.f;
                if(cambc::champion_designs[physical].passive()==cambc::passive_type::bonus_gold)
                    pick.gold_bonus=cambc::constants::passive_abilities::vesper_vale_bonus_gold_percent/100.f;
            }
        }
        // Coarse-to-fine: every valid composition gets the same six-camp screen.
        // Refine the strongest 32 with all selected camps; interrupted screening falls back.
        std::vector<Camp> screen;
        for(std::size_t i=0;i<std::min<std::size_t>(6,camps.size());++i)
            screen.push_back(camps[i*camps.size()/std::min<std::size_t>(6,camps.size())]);
        std::vector<Candidate> coarse;
        for(unsigned mask=1;mask<(1u<<12);++mask)if(valid(mask,s.features.size,s.picks))++s.expected;
        for(unsigned mask=1;mask<(1u<<12);++mask) {
            if(!valid(mask,s.features.size,s.picks))continue;
            if(cambc::fuel_remaining()<1600000)break;
            coarse.push_back({mask,utility(mask,s.features,s.picks,screen,s.baseline)});++s.evaluated;
        }
        if(s.evaluated!=s.expected) {
            std::printf("MDFALLBACK incomplete screen %d/%d remaining%llu\n",s.evaluated,s.expected,static_cast<unsigned long long>(cambc::fuel_remaining()));return;
        }
        std::stable_sort(coarse.begin(),coarse.end(),[](auto a,auto b){return a.score>b.score;});
        const float base_score=utility(s.baseline,s.features,s.picks,camps,s.baseline);
        s.candidates.push_back({s.baseline,base_score});
        for(const auto& candidate:coarse) {
            if(s.refined>=32 || cambc::fuel_remaining()<500000)break;
            if(candidate.mask==s.baseline)continue;
            const float value=utility(candidate.mask,s.features,s.picks,camps,s.baseline);++s.refined;
            if(value>=base_score*1.025f)s.candidates.push_back({candidate.mask,value});
        }
        std::stable_sort(s.candidates.begin(),s.candidates.end(),[](auto a,auto b){return a.score>b.score;});
        s.ready=true;s.used=s.start-cambc::fuel_remaining();
        if(cfg::map_draft_log)std::printf("MDPLAN size%d groups%d walk%d screened%d expected%d refined%d shortlist%zu used%llu start%llu best%u base%u\n",
            s.features.size,s.groups,s.features.spawn_walk,s.evaluated,s.expected,s.refined,s.candidates.size(),
            static_cast<unsigned long long>(s.used),static_cast<unsigned long long>(s.start),s.candidates[0].mask,s.baseline);
    } catch(const std::exception&e) {s.ready=false;std::printf("map draft fallback: %s\n",e.what());}
}
void record(const Search& s,unsigned target,unsigned mine) {
    std::array<std::byte,16> bytes{};bytes[0]=std::byte{0xD4};bytes[1]=std::byte{1};
    bytes[2]=static_cast<std::byte>(s.features.size);bytes[3]=static_cast<std::byte>(std::popcount(mine));
    bytes[4]=static_cast<std::byte>(target&255);bytes[5]=static_cast<std::byte>(target>>8);
    bytes[6]=static_cast<std::byte>(mine&255);bytes[7]=static_cast<std::byte>(mine>>8);
    if(cambc::constants::draft_memory_bytes>=8)
        cambc::draft_memory=std::span<const std::byte>{bytes.data(),std::min(bytes.size(),static_cast<std::size_t>(cambc::constants::draft_memory_bytes))};
}
}
bool play_map_draft() {
    auto& s=search();prepare(s);
    if(!s.ready)return false;
    const auto mine=mask_of(cambc::draft::current_draft(cambc::team::ally));
    const auto enemy=mask_of(cambc::draft::current_draft(cambc::team::enemy));
    unsigned target=0;float score=-1e30f;
    for(const auto& c:s.candidates) {
        if(cambc::fuel_remaining()<18000)break;
        if(!contains(c.mask,mine))continue;
        const float v=c.score*(cfg::map_draft_react ? reaction(c.mask,enemy,s.picks) : 1.f);
        if(v>score){score=v;target=c.mask;}
    }
    // A safe cached incumbent is essential even if a later turn has little fuel.
    if(!target)for(const auto& c:s.candidates)if(contains(c.mask,mine)){target=c.mask;break;}
    if(!target)return false;
    const std::array<int,12> priority{11,6,2,9,0,3,1,8,4,10,5,7};
    for(int p:priority)if((target&~mine)&(1u<<p)) {
        try {
            cambc::draft::pick(static_cast<cambc::champion_draft>(p));
            // A failure to write diagnostics must never cause a second pick this turn.
            try {record(s,target,mine|(1u<<p));}catch(const std::exception&){}
            if(cfg::map_draft_log)std::printf("MDPICK p%d mask%u mine%u enemy%u remaining%llu\n",p,target,mine,enemy,static_cast<unsigned long long>(cambc::fuel_remaining()));
            return true;
        } catch(const cambc::error&) {continue;}
    }
    return false;
}
}
