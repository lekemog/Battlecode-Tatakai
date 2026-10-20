#include "src/cycle_score.h"
#include "src/task_state.h"
#include "src/capture_owner.h"
#include "src/siege_tiles.h"
#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <iostream>
#include <limits>

using namespace polaris_draft;
bool near(double a,double b) { return std::abs(a-b)<1e-9; }
int main() {
    Cycle base;
    base.travel=8; base.ready_in=5; base.clear=10; base.capture=5;
    base.delivery=6; base.channel=3; base.gems=30; base.gold=90;
    assert(near(score_cycle(base,0.1).body_rounds,32));
    assert(near(score_cycle(base,0.1).value,39));
    Cycle wait=base; wait.ready_in=12;
    assert(near(score_cycle(wait,0.1).body_rounds,36));
    Cycle helpers=base; helpers.workers=3;
    assert(near(score_cycle(helpers,0.1).body_rounds,68));
    Cycle far=base; far.delivery=60;
    assert(score_cycle(far,0.1).rate<score_cycle(base,0.1).rate);
    Cycle risk=base; risk.delivery_probability=.5;
    risk.existing_bag=80; risk.bag_loss_probability=.5;
    assert(score_cycle(risk,0.1).rate<0);
    Cycle bad=base; bad.travel=std::numeric_limits<double>::quiet_NaN();
    assert(!score_cycle(bad,0.1).feasible);
    bad=base; bad.carriers=0; assert(!score_cycle(bad,0.1).feasible);
    // 400 monotonicity checks: longer delivery must not improve equal-reward rate.
    for (int travel=0;travel<20;++travel) for(int delivery=0;delivery<20;++delivery) {
        Cycle a=base; a.travel=travel; a.delivery=delivery;
        Cycle b=a; b.delivery+=1;
        assert(score_cycle(a,.1).rate>score_cycle(b,.1).rate);
    }
    assert(!switch_target(1,1.05,.1,0));
    assert(switch_target(1,1.2,.1,0));
    assert(!switch_target(1,std::numeric_limits<double>::infinity(),.1,0));

    Task task; task.start(7,Stage::capture,10);
    assert(retain_task(task,{11,true,false,false,false,true,15},3));
    // A repeated observation cannot slide the deadline forward indefinitely.
    assert(retain_task(task,{15,true,false,false,false,true,20},3));
    assert(!retain_task(task,{16,true,false,false,false,true,21},3));
    task.start(7,Stage::travel,20);
    assert(retain_task(task,{22,true,false,false,true,false,-1},3));
    assert(!retain_task(task,{23,false,false,false,false,false,-1},3));
    assert(!task.active());
    assert(!consumes_policy_turn(Result::no_action));
    assert(!consumes_policy_turn(Result::failed));
    assert(consumes_policy_turn(Result::holding));
    CampMemory memory; memory.observe(CampState::reward,10);
    assert(memory.estimate(17,6)==CampState::unknown);
    assert(memory.ready_round==-1); // no fabricated respawn from unseen reward
    memory.observe(CampState::respawning,20,10);
    assert(memory.estimate(29,6)==CampState::respawning);
    assert(memory.estimate(30,6)==CampState::unknown);

    std::array<Capturer,3> candidates{{{2,true,2,0},{1,true,2,0},{3,false,0,0}}};
    assert(capture_owner(7,10,{},false,candidates)==1);
    std::reverse(candidates.begin(),candidates.end());
    assert(capture_owner(7,10,{},false,candidates)==1);
    Lease lease{7,5,12}; // owner5 is outside local vision, but lease is still fresh
    assert(capture_owner(7,11,lease,false,candidates)==5);
    assert(capture_owner(7,11,lease,true,candidates)==1);
    assert(capture_owner(7,13,lease,false,candidates)==1);
    assert(!release_helper(false,1,2,false));
    assert(release_helper(true,1,2,false));
    assert(!release_helper(true,1,2,true));

    const std::array<ThreatArea,1> monsters{{{{0,0},3}}};
    const std::array<Point,4> tiles{{{4,0},{3,3},{4,1},{0,-4}}};
    const auto positions=siege_positions(tiles,monsters,
        [](Point){return true;},
        [](Point p){return p.x*p.x+p.y*p.y<=16;});
    assert(positions.size()==2); // cardinal4 yes, diagonal3,3 unsafe,4,1 uncastable
    const std::array<ThreatArea,2> two{{{{0,0},3},{{5,0},1}}};
    assert(!outside_monster_ranges({4,0},two));
    std::cout<<"Draft scenario and invariant checks passed. No engine matches run.\n";
}

