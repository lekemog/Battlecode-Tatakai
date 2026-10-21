#include "../../bots/chatgpt-opp-response-v1/src/opponent_response.h"
#include <cassert>
#include <iostream>

using opponent_response::Model;
using opponent_response::Observation;

void snapshot(Model& m,unsigned r,int group,int distance,bool eligible=true,unsigned id=17){
    Observation o{id,distance,eligible};m.tick(r,group,2,&o,1);
}

void episode(Model& m,unsigned start,bool approach,unsigned id=17){
    snapshot(m,start,4,7,true,id);
    for(unsigned j=1;j<=4;++j)snapshot(m,start+j,4,approach&&j==4?5:7,true,id);
}

int main(){
    // Cold start: no unseen enemy or unobserved style is declared safe/hostile.
    Model cold;
    assert(cold.estimate(17,7,2,100).pressure==0);
    assert(Model::multiplier(0)==1);

    Model approaching,stationary;
    for(unsigned r=10;r<90;r+=10){episode(approaching,r,true);episode(stationary,r,false);}
    const auto a=approaching.estimate(17,7,2,85);
    const auto b=stationary.estimate(17,7,2,85);
    assert(a.probability>.8 && a.pressure>0);
    assert(b.probability<.2 && b.pressure==0);
    assert(approaching.counts().completed==8 && approaching.counts().approached==8);
    assert(stationary.counts().completed==8 && stationary.counts().approached==0);
    assert(approaching.estimate(999,7,2,85).pressure==0); // per identity
    assert(approaching.estimate(17,4,2,85).pressure==0); // separate distance band
    assert(approaching.estimate(17,2,2,85).pressure==0); // already in contact
    assert(approaching.estimate(17,30,2,85).pressure==0); // no extrapolation
    assert(approaching.estimate(17,7,2,5000).pressure==0); // stale evidence decays

    // Every incomplete observation reason must censor, not create a negative.
    for(int reason=0;reason<6;++reason){
        Model m;snapshot(m,10,4,7);
        if(reason==0)m.tick(11,4,2,nullptr,0); // fog
        if(reason==1)snapshot(m,11,5,7); // changed objective
        if(reason==2)snapshot(m,12,4,7); // missing frame/fuel pause
        if(reason==3)snapshot(m,11,4,7,false); // stun/submit
        if(reason==4)m.tick(11,-1,0,nullptr,0); // death/abandonment
        if(reason==5){Observation o{17,7,true};m.tick(11,4,3,&o,1);} // geometry change
        assert(m.counts().censored==1 && m.counts().completed==0);
        assert(m.estimate(17,7,2,12).evidence==0);
        assert(m.event_count()==1 && m.event(0).label==-1);
    }

    // Positive on first entry, even if the next action is to fight/leave.
    Model early;snapshot(early,10,4,4);snapshot(early,11,4,2);
    assert(early.counts().approached==1 && early.counts().completed==1);
    assert(early.event(0).start==10 && early.event(0).end==11);
    assert(early.event(0).predicted==.5); // forecast made before observing label
    early.tick(12,-1,0,nullptr,0);
    assert(early.counts().censored==0);

    Model duplicates;snapshot(duplicates,10,4,7);snapshot(duplicates,10,4,2);
    assert(duplicates.counts().approached==0);
    snapshot(duplicates,11,4,7);snapshot(duplicates,12,4,7);snapshot(duplicates,13,4,7);
    assert(duplicates.counts().completed==0);
    snapshot(duplicates,14,4,7);
    assert(duplicates.counts().completed==1);

    Model few;episode(few,10,true);episode(few,20,true);
    assert(few.estimate(17,7,2,24).pressure==0); // insufficient evidence

    // Capacity and independent simultaneous observations; no allocation by raw ID.
    Model many;Observation obs[8];
    for(unsigned i=0;i<8;++i)obs[i]={1000000+i,7,true};
    for(unsigned r=10;r<=14;++r)many.tick(r,4,2,obs,8);
    assert(many.counts().started==8 && many.counts().completed==8);
    snapshot(many,20,4,7,true,42);
    assert(many.estimate(42,7,2,20).evidence==0);

    for(int i=-100;i<=200;++i){
        const double f=Model::multiplier(i/100.0);assert(f>=.75&&f<=1);
    }
    // Repeated evidence is bounded and a change in tendency can be learned.
    Model change;
    for(unsigned r=10;r<500;r+=10)episode(change,r,true);
    const double before=change.estimate(17,7,2,494).probability;
    for(unsigned r=510;r<1000;r+=10)episode(change,r,false);
    const auto after=change.estimate(17,7,2,994);
    assert(after.evidence<=32 && after.probability<before && after.pressure==0);
    std::cout<<"opponent model scenarios passed; state bytes="<<sizeof(Model)<<'\n';
}
