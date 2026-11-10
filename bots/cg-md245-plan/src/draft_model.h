#pragma once
#include "model.h"
#include <array>
#include <bit>
#include <cmath>
#include <vector>

namespace mb::draft_model {
struct Pick {
    model::ChampionSummary body[2];
    int bodies{1};
    float control{}, gold_bonus{};
};
struct Camp {
    float hp{}, strength{}, weighted_hp{}, neighbours{}, gold{}, gems{};
    int walk{}, enemy_walk{}, respawn{};
};
struct Features { int size{}, spawn_walk{60}, capture_rounds{5}; float gold_share{}, wall_share{}; };
struct Candidate { unsigned mask{}; float score{}; };
inline bool contains(unsigned mask, unsigned picks) { return (mask & picks)==picks; }
inline bool valid(unsigned mask, int size, const std::array<Pick,12>& picks) {
    if (std::popcount(mask)!=size) return false;
    int melee=0,ranged=0;
    for (int p=0;p<12;++p) if (mask&(1u<<p))
        for (int b=0;b<picks[p].bodies;++b)
            (picks[p].body[b].attack_range>1 ? ranged : melee)++;
    // Keep a viable frontline; do not mistake an extra linked body for two draft slots.
    return melee >= (size>=4 ? 2 : 1) && ranged<=2;
}
inline float utility(unsigned mask, const Features& f, const std::array<Pick,12>& picks,
                     const std::vector<Camp>& camps, unsigned baseline) {
    if (!valid(mask,f.size,picks) || camps.empty()) return -1e9f;
    float health=0,control=0,bonus=0; int ranged=0;
    for (int p=0;p<12;++p) if (mask&(1u<<p)) {
        const auto& k=picks[p];control+=k.control;bonus+=k.gold_bonus;
        if (k.bodies==2) health+=std::min(k.body[0].health,k.body[1].health); // shared-death exposure
        else health+=k.body[0].health*(k.body[0].attack_range>1 ? .55f : 1.f);
        for (int b=0;b<k.bodies;++b) ranged+=k.body[b].attack_range>1;
    }
    std::array<float,6> top{};
    for (const auto& g:camps) {
        float dps=0;
        for (int p=0;p<12;++p) if (mask&(1u<<p))
            for (int b=0;b<picks[p].bodies;++b)
                dps+=model::camp_dps(picks[p].body[b],g.neighbours,true);
        if (dps<=0) continue;
        const float clear=g.hp/dps;
        const float hurt=std::max(0.f,g.weighted_hp/dps-.5f*g.strength);
        const float contested=g.enemy_walk<=g.walk+8 ? 1.f : 0.f;
        const float overhead=12.f*hurt/std::max(1.f,health*.6f);
        const float reward=g.gold*(1.f+bonus/std::max(1,f.size))+g.gems*4.f;
        const float travel=std::max(0.f,static_cast<float>(g.walk)-ranged*.4f);
        float value=reward/(travel+clear+f.capture_rounds+overhead);
        value*=1.f+120.f/std::max(40.f,g.respawn+clear+f.capture_rounds);
        value/=1.f+contested*hurt/std::max(1.f,health);
        for (auto& v:top) if (value>v) std::swap(value,v);
    }
    float score=0;
    for (int i=0;i<6;++i) score+=top[i]/(1.f+i*.25f);
    // Modest, explicit heuristics; not fitted win probabilities or perfect simulations.
    score*=1.f+std::min(.08f,control*.005f)*(f.spawn_walk<45 ? 1.f : .5f);
    score*=1.f+.02f*ranged*std::clamp((f.spawn_walk-45)/60.f,0.f,1.f);
    // Penalize unimplemented gem-battery/support roles and deviation from the proven base.
    if(mask&(1u<<5)) score*=.88f; // Prism gem retention not modeled by v245
    if(mask&(1u<<7)) score*=.92f; // Willow coordinated heal/reset value not modeled
    score*=1.f-.015f*std::popcount(mask & ~baseline);
    return score;
}
inline float reaction(unsigned mask, unsigned enemy, const std::array<Pick,12>& picks) {
    int melee=0,seen=0,range=0;float control=0;
    for(int p=0;p<12;++p) {
        if(enemy&(1u<<p)) for(int b=0;b<picks[p].bodies;++b) { ++seen;melee+=picks[p].body[b].attack_range<=1; }
        if(mask&(1u<<p)) {control+=picks[p].control;for(int b=0;b<picks[p].bodies;++b)range+=picks[p].body[b].attack_range>1;}
    }
    if(!seen) return 1.f;
    return 1.f+std::min(.04f,.008f*range*melee/seen+.002f*control);
}
}
