#include "../../bots/cg-ci-pair/src/pair_model.h"
#include <cassert>
int main() {
 using namespace mb::pair_model;
 assert(fresh(100,97)); assert(!fresh(101,97)); assert(!fresh(99,100));
 assert(vulnerable(1.0f,0.2f)); assert(vulnerable(0.2f,1.0f)); assert(!vulnerable(.8f,.8f));
 assert(regroup(5,0,false,false)); assert(!regroup(5,4,false,false));
 assert(!regroup(5,0,true,false)); assert(!regroup(5,0,false,true));
 assert(!regroup(9,0,false,false)); assert(!regroup(3,0,false,false));
 assert(prefer_stun(false,true,true,true,false));
 assert(prefer_stun(false,true,true,false,true));
 assert(!prefer_stun(true,true,true,true,true));
 assert(!prefer_stun(false,true,false,true,true));
 assert(!prefer_stun(false,false,true,true,true));
 assert(!prefer_stun(false,true,true,false,false));
}
