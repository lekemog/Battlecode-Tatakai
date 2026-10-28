#include "bot.h"
#if POLARIS_OPP_MODEL > 0
#include <iostream>

int Bot::opp_radius(int group) const {
    if(group<0||group>=static_cast<int>(groups.size()))return -1;
    const auto& g=groups[group];
    // Large/dispersed objectives have a different approach geometry. Leave
    // them to the baseline until we have a separate, tested model for them.
    if(g.monolith||g.reward||g.probes.empty()||g.probes.size()>=8)return -1;
    int radius=0;
    for(auto p:g.probes)radius=std::max(radius,static_cast<int>(p.chebyshev_distance(g.center)));
    return radius<=4?radius+2:-1;
}

void Bot::observe_opponent_response(){
    auto& me=cambc::self();
    int group=opp_farm_group;
    int radius=opp_radius(group);
    // An episode describes ongoing nearby farming, not a stale selected task.
    if(opp_farm_round+1!=round||radius<0||capturing>=0||
       me.is_recalling()||me.is_submitting_gems()||me.is_teleporting()||
       (group>=0&&me.position().chebyshev_distance(groups[group].center)>radius+2)){
        group=-1;radius=0;
    }
    std::array<opponent_response::Observation,opponent_response::capacity> obs{};
    int count=0;
    if(group>=0)for(const auto& e:enemies){
        if(count==opponent_response::capacity)break;
        obs[count++]={static_cast<unsigned>(static_cast<cambc::handle_champion_t>(e.handle)),
                      static_cast<int>(e.pos.chebyshev_distance(groups[group].center)),!e.stunned&&!e.channel};
    }
    opp_model.tick(round,group,radius,obs.data(),count);
}

double Bot::opponent_camp_multiplier(int group,int travel){
    if(!opp_on)return 1;
    const int radius=opp_radius(group);
    // No long-range forecasts, score bonuses, bans, or commitment overrides.
    // Query only in the local geometry in which the model is trained.
    // Claude tune: the v1 gate (we already stand by the camp, travel<=6) meant the discount never changed a choice
    // (choices=0 in full games). Re-rank any compact group within 15 steps; the estimate is still per visible enemy.
    if(radius<0||travel>15)
        return 1;
    ++opp_evaluated;
    double pressure=0;
    for(const auto& e:enemies){
        if(e.stunned||e.channel)continue;
        const int d=e.pos.chebyshev_distance(groups[group].center);
        const unsigned enemy_id=static_cast<unsigned>(static_cast<cambc::handle_champion_t>(e.handle));
        const auto prediction=opp_model.estimate(enemy_id,d,radius,round);
        double value=prediction.pressure;
#if POLARIS_OPP_MODEL == 3
        // Same eligible current sightings, but no learned tendency. Distinguish
        // a benefit from generic local caution from a benefit from learning.
        value=d>radius&&d<=radius+7?.5:0;
#endif
        pressure=std::max(pressure,value); // Never multiply fear by enemy count.
    }
    if(pressure>0)++opp_discounted;
    return opponent_response::Model::multiplier(pressure);
}

void Bot::report_opponent_response(){
    for(int i=0;i<opp_model.event_count();++i){
        const auto& e=opp_model.event(i);
        std::cout<<"OPP_SAMPLE slot="<<slot<<" enemy="<<e.enemy<<" group="<<e.group
            <<" band="<<e.band<<" start="<<e.start<<" end="<<e.end<<" label="<<e.label
            <<" prediction="<<e.predicted<<" evidence="<<e.evidence<<'\n';
    }
    if(round<opp_last_report+50)return;
    opp_last_report=round;
    const auto& n=opp_model.counts();
    std::cout<<"OPP r="<<round<<" slot="<<slot<<" mode="<<POLARIS_OPP_MODEL
        <<" started="<<n.started<<" completed="<<n.completed<<" approach="<<n.approached
        <<" censored="<<n.censored<<" evaluated="<<opp_evaluated
        <<" discounted="<<opp_discounted<<" choices="<<opp_choice_changes<<'\n';
}
#endif
