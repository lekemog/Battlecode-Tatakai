#include "brain.h"
#include "config.h"
#include "knowledge.h"
#include "nav.h"
#include "pair_model.h"
#include "pair.h"
#include "world.h"
#include <algorithm>
#include <exception>

namespace mb {
namespace {
bool paired() { return kit().type == cambc::champion_type::cassi || kit().type == cambc::champion_type::issac; }
template<class F> bool pair_action(F f) {
    try { if (!cambc::self().is_alive()) return false; return f(); }
    catch (const std::exception& e) { MB_LOG("pair action rejected: %s\n", e.what()); return false; }
}
int contact_risk(const Ctx& ctx, vec2 p) {
    int out = static_cast<int>(camp_threat_at(ctx,p)*10.0f);
    for (const auto& e : ctx.enemies) {
        if (e.hp <= 0) continue;
        const int d=cheb(p,e.pos);
        if (d <= e.range + (e.range <= 1 ? 1 : 0)) out += 1000 + static_cast<int>(e.dps*10);
    }
    return out;
}
bool pair_stun(Ctx& ctx, TurnActions& acts, const ChampView* focus, vec2 buddy) {
    if (!focus || acts.cast || !cambc::self().can_cast()) return false;
    const auto abilities=cambc::self().abilities();
    int damage=-1, stun=-1;
    for (int i=0;i<2;++i) {
        const auto& s=kit().slot[i];
        if (!s.enemies || abilities[i].cooldown()>0 || cheb(ctx.pos,focus->pos)>static_cast<int>(s.range) || (s.exclusive && acts.moved)) continue;
        if (s.kind==model::AbilityKind::damage) damage=i;
        if (s.kind==model::AbilityKind::cc && s.duration>0) stun=i;
    }
    const bool estimated_finish=damage>=0 && focus->hp<=abilities[damage].damage_amount();
    const bool diving=cheb(focus->pos,ctx.pos)<=focus->range+1 || cheb(focus->pos,buddy)<=focus->range+1;
    const bool stun_works=focus->champ->passive()!=cambc::passive_type::stun_immunity;
    if (!pair_model::prefer_stun(estimated_finish,stun>=0,stun_works,diving,focus->channeling)) return false;
    if (!focus->champ->is_visible()) return false;
    if (!pair_action([&] { return abilities[stun].use(*focus->champ); })) return false;
    acts.cast=true;
    return true;
}
}


const ChampView* core_focus(const Ctx& ctx, const ChampView* fallback) {
    const auto type=kit().type;
    if(type!=cambc::champion_type::heart_of_ruin && type!=cambc::champion_type::cassi && type!=cambc::champion_type::issac) return fallback;
    vec2 cassi=ctx.pos; bool seen=type==cambc::champion_type::cassi;
    for(const auto& a:ctx.allies) if(a.type==cambc::champion_type::cassi) {cassi=a.pos;seen=true;}
    if(!seen)return fallback;
    const ChampView* diver=nullptr;float best=-1;
    for(const auto& e:ctx.enemies) if(e.hp>0 && cheb(e.pos,cassi)<=e.range+1 && cheb(ctx.pos,e.pos)<=6) {
        const float score=e.dps/std::max(1.f,e.hp)+(e.channeling ? 10.f : 0.f);
        if(score>best){best=score;diver=&e;}
    }
    return diver ? diver : fallback;
}

void Brain::observe_pair(const Ctx& ctx) {
    if (!paired()) return;
    pair_group_=-1;
    const auto buddy=kit().type==cambc::champion_type::cassi ? cambc::champion_type::issac : cambc::champion_type::cassi;
    const auto& rr=roster(cambc::team::ally);
    bool alive=false;
    for (std::size_t i=0;i<rr.types.size();++i)
        if (rr.types[i]==buddy) { alive=rr.champs[i].is_alive(); break; }
    if (!alive) { pair_seen_=-1000; pair_regroup_steps_=0; return; }
    for (const auto& a : ctx.allies) if (a.type==buddy) {
        pair_pos_=a.pos; pair_hp_=a.hp/std::max(1.0f,a.max_hp);
        pair_seen_=ctx.round; pair_channel_=a.channeling;
        if (cheb(ctx.pos,pair_pos_)<=4) pair_regroup_steps_=0;
        const auto& kn=Knowledge::get();
        for (std::size_t j=0;j<kn.allies.size();++j)
            if (static_cast<cambc::handle_champion_t>(kn.allies[j])==static_cast<cambc::handle_champion_t>(*a.champ) && j<kn.slots().size()) {
                const auto& slot=kn.slots()[j];
                if (slot.status==SlotStatus::engaging) pair_group_=slot.group;
            }
        break;
    }
}

bool Brain::pair_emergency(Ctx& ctx, TurnActions& acts) {
    if (!paired() || ctx.on_spawn || !pair_model::fresh(ctx.round,pair_seen_)) return false;
    // An uncovered caster must not be the team's first contact with ready burst.
    if(kit().type==cambc::champion_type::cassi) {
        for(const auto& e:ctx.enemies)if(e.hp>0 && cheb(ctx.pos,e.pos)<=enemy_reach(e)) {
            bool cover=false;
            for(const auto& a:ctx.allies)if(a.range<=1 && a.hp>=.5f*a.max_hp && !a.channeling &&
                cheb(a.pos,ctx.pos)<=3 && cheb(a.pos,e.pos)<cheb(ctx.pos,e.pos))cover=true;
            if(!cover){publish(-1,static_cast<int>(SlotStatus::idle));why_="caster-uncovered";return retreat(ctx,acts);}
        }
    }
    // Death is shared. A healthy body must not override its wounded partner's exit.
    if (!pair_model::vulnerable(ctx.hp_frac(),pair_hp_)) return false;
    publish(-1,static_cast<int>(SlotStatus::idle));
    why_="pair-weak-link";
    if (contact_risk(ctx,ctx.pos)>0 || contact_risk(ctx,pair_pos_)>0) return retreat(ctx,acts);
    if (pair_action([&] { cambc::self().recall(); return true; })) return true;
    return retreat(ctx,acts);
}

bool Brain::pair_combat(Ctx& ctx, TurnActions& acts, const ChampView* preferred) {
    if (!paired() || ctx.enemies.empty() || !pair_model::fresh(ctx.round,pair_seen_)) return false;
    const bool cassi=kit().type==cambc::champion_type::cassi;
    if (cheb(ctx.pos,pair_pos_)>8) return false;
    const ChampView* focus=preferred; int best=-1000000;
    for (const auto& e : ctx.enemies) {
        if (e.hp<=0) continue;
        const int d=std::min(cheb(ctx.pos,e.pos),cheb(pair_pos_,e.pos));
        const int score=(d<=e.range+1 ? 10000 : 0)+(e.channeling ? 1000 : 0)-d*500-static_cast<int>(e.hp)-std::max(0,e.index);
        if (!preferred && score>best) { focus=&e; best=score; }
    }
    if (!focus) return false;
    if (cassi) {
        // Spend a legal stun/basic/nuke before considering a walk. Query actual
        // can_move afterwards: do not assume a symmetric walk/attack allowance.
        pair_stun(ctx,acts,focus,pair_pos_);
        fight_enemies(ctx,acts,false,focus);
        const int here_risk=contact_risk(ctx,ctx.pos);
        // Only immediate contact justifies surrendering a ranged basic to movement.
        // No full dash-envelope avoidance: it erased safe attack windows in role61.
        if (here_risk>0 && cambc::self().can_move() && !capturing_) {
            auto score=[&](vec2 p) {
                return -contact_risk(ctx,p)*100-std::max(0,cheb(p,pair_pos_)-4)*1000-
                       std::abs(cheb(p,focus->pos)-kit().attack_range)*10;
            };
            if (step_best(score,score(ctx.pos))) { acts.moved=true; ctx.refresh_self(); }
        }
    } else {
        // Strike/reset before a walk; do not spend Issac's escape dash to chase.
        fight_enemies(ctx,acts,false,focus);
        if (!pair_channel_ && cheb(focus->pos,pair_pos_)<=4 && cambc::self().can_move()) {
            const int before=contact_risk(ctx,ctx.pos);
            auto score=[&](vec2 p) {
                if (cheb(p,pair_pos_)>4 || contact_risk(ctx,p)>before+1500) return -1000000;
                return -cheb(p,focus->pos)*100-cheb(p,pair_pos_)*5;
            };
            if (step_best(score,score(ctx.pos))) { acts.moved=true; ctx.refresh_self(); }
            fight_enemies(ctx,acts,false,focus);
        }
    }
    const bool acted=acts.moved || acts.attacked || acts.cast;
    // Prevent a no-action sighting at spell range from blocking the farm planner.
    if (acted) { publish(target_,static_cast<int>(SlotStatus::engaging)); why_="pair-fight"; }
    return acted;
}

bool Brain::pair_farm(Ctx& ctx, TurnActions& acts) {
    if (!paired() || ctx.on_spawn || capturing_) return false;
    // Cassi joins a visible, healthy frontliner's active camp instead of wandering off.
    if(kit().type==cambc::champion_type::cassi) {
        auto& kn=Knowledge::get();auto& w=World::get();int chosen=-1,best=-100000;
        for(const auto& a:ctx.allies)if(a.range<=1 && a.hp>=.5f*a.max_hp && !a.channeling && cheb(a.pos,ctx.pos)<=8)
            for(std::size_t i=0;i<kn.allies.size();++i)if(static_cast<cambc::handle_champion_t>(kn.allies[i])==static_cast<cambc::handle_champion_t>(*a.champ) && i<kn.slots().size()) {
                const auto slot=kn.slots()[i];int g=slot.group;
                if(slot.status!=SlotStatus::engaging || g<0 || g>=static_cast<int>(w.groups.size()) || kn.groups[g].status!=GroupStatus::alive)continue;
                const int distance=cheb(a.pos,w.groups[g].center);
                if(distance>6)continue;
                const int value=(a.type==cambc::champion_type::heart_of_ruin ? 100 : 0)-distance-cheb(ctx.pos,a.pos);
                if(value>best){best=value;chosen=g;}
            }
        if(chosen>=0) {
            if(target_!=chosen){engaged_=false;staged_since_=-1;progress_best_=1<<20;progress_round_=ctx.round;}
            target_=chosen;chosen_round_=ctx.round;
        }
    }
    if(!pair_model::fresh(ctx.round,pair_seen_))return false;
    if (pair_channel_ || pair_model::vulnerable(ctx.hp_frac(),pair_hp_)) return false;
    const int distance=cheb(ctx.pos,pair_pos_);
    if (kit().type==cambc::champion_type::issac && pair_model::regroup(distance,pair_regroup_steps_,pair_channel_,!ctx.enemies.empty())) {
        auto score=[&](vec2 p) { return -cheb(p,pair_pos_)*1000-contact_risk(ctx,p)*100; };
        if (step_best(score,score(ctx.pos))) {
            ++pair_regroup_steps_; acts.moved=true; ctx.refresh_self();
            publish(-1,static_cast<int>(SlotStatus::idle)); why_="pair-regroup"; return true;
        }
        return false; // blocked routes never create a stationary follow loop
    }
    // Cassi chooses; Issac adopts only a current, nearby, living camp intent.
    // Never follow a reward/capture: one body captures while the other can farm.
    if (kit().type!=cambc::champion_type::issac || distance>4 || pair_seen_!=ctx.round) return false;
    auto& kn=Knowledge::get(); auto& world=World::get();
    if (pair_group_<0 || pair_group_>=static_cast<int>(world.groups.size()) || kn.groups[pair_group_].status!=GroupStatus::alive) return false;
    if (cheb(ctx.pos,world.groups[pair_group_].center)>8) return false;
    if (target_!=pair_group_) { engaged_=false; staged_since_=-1; progress_best_=1<<20; progress_round_=ctx.round; }
    target_=pair_group_; chosen_round_=ctx.round;
    if constexpr (cfg::ci_trace) MB_LOG("PAIR r%d camp%d distance%d\n",ctx.round,target_,distance);
    return false; // normal planner supplies camp safety, spells, capture and banking
}
}
