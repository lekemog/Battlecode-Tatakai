#include "../../bots/cg-md245-plan/src/draft_model.h"
#include <cassert>
int main(){
 using namespace mb::draft_model;
 std::array<Pick,12> p{};
 for(auto&x:p){x.body[0].health=1000;x.body[0].strength=70;}
 p[9].body[0].strength=50;p[9].body[0].splash=true;
 Features f;f.size=1;f.spawn_walk=60;
 Camp g;g.hp=1000;g.strength=30;g.weighted_hp=30000;g.gold=100;g.walk=5;g.enemy_walk=50;g.respawn=50;
 std::vector<Camp> sparse{g};
 assert(utility(1u<<9,f,p,sparse,0)<utility(1,f,p,sparse,0));
 g.neighbours=4;std::vector<Camp> dense{g};
 assert(utility(1u<<9,f,p,dense,0)>utility(1,f,p,dense,0));
 assert(contains(7,3));assert(!contains(7,8));
 assert(!valid(3,1,p));assert(valid(3,2,p));
 p[3].bodies=2;p[3].body[0].attack_range=3;p[3].body[1].attack_range=1;
 assert(valid(1u<<3,1,p)); // pair is one pick despite two bodies
 assert(!valid(1u<<3,2,p));
 auto fast=utility(1,f,p,dense,0);dense[0].respawn=1000;assert(utility(1,f,p,dense,0)<fast);
 assert(utility(1,f,p,{},0)<0);
 assert(reaction(1,0,p)==1.f);
}
