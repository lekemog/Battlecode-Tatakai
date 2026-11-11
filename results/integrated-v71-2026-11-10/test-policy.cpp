#include "../../bots/cg-v72-integrated/src/pair_model.h"
#include "../../bots/cg-v72-integrated/src/draft_model.h"
#include <cassert>
int main(){
 using namespace mb::pair_model;
 assert(caster_escape_score(false,1)==caster_escape_score(false,100));
 assert(caster_escape_score(true,10)>caster_escape_score(false,1));
 assert(!caster_exposed(3,1,100,100));
 assert(caster_exposed(3,3,100,3));
 assert(!caster_exposed(3,3,100,2));
 assert(!caster_exposed(1,3,0,100));
 assert(!fresh(10,6));assert(vulnerable(1,.2f));assert(!regroup(6,4,false,false));
 assert(prefer_stun(false,true,true,true,false));assert(!prefer_stun(false,true,false,true,false));
 using namespace mb::draft_model;
 std::array<Pick,12> picks{};for(auto& p:picks){p.body[0].health=1000;p.body[0].strength=50;}
 picks[3].bodies=2;picks[3].body[0].attack_range=3;picks[3].body[1].attack_range=1;
 Features f;f.required=(1u<<11)|(1u<<3);f.allowed=f.required|(1u<<0)|(1u<<2)|(1u<<6)|(1u<<8)|(1u<<9);
 for(int n:{3,4,5}){f.size=n;int count=0;for(unsigned m=1;m<4096;++m)if(eligible(m,f,picks)){++count;assert(contains(m,f.required));assert(std::popcount(m)==n);}assert(count>0);}
}
