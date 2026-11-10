#include "../../bots/cg-hci66-map/src/draft_model.h"
#include "../../bots/cg-hci66-map/src/pair_model.h"
#include <cassert>
int main(){
 using namespace mb::draft_model;
 std::array<Pick,12> p{};for(auto&k:p){k.body[0].health=1000;k.body[0].strength=50;}
 p[3].bodies=2;p[3].body[0].attack_range=3;p[3].body[1].attack_range=1;
 Features f;f.required=(1u<<11)|(1u<<3);f.allowed=4095u&~(1u<<5)&~(1u<<7);
 for(int n:{3,4,5}) {
  f.size=n;int count=0;
  for(unsigned mask=1;mask<4096;++mask)if(eligible(mask,f,p)){++count;assert(contains(mask,f.required));assert(std::popcount(mask)==n);assert((mask&~f.allowed)==0);}
  assert(count>0);
  assert(!eligible((1u<<6)|(1u<<2)|(1u<<9),f,p));
 }
 assert(mb::pair_model::vulnerable(1.f,.2f));
 assert(!mb::pair_model::fresh(10,6));
 assert(!mb::pair_model::regroup(6,4,false,false));
 assert(mb::pair_model::prefer_stun(false,true,true,true,false));
 assert(!mb::pair_model::prefer_stun(false,true,false,true,false));
}
