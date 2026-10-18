#include "faux_policy.h"
#include <cassert>
int main(){
    // Four wolves, one visible at 50 HP: not a 50-HP group.
    assert(faux::remaining_hp(5400,1350,50)==4100);
    assert(faux::remaining_hp(4100,1350,1000)==3750);
    assert(faux::remaining_hp(500,500,600)==500);
    assert(faux::remaining_hp(500,500,0)==0);
    assert(faux::cancel_allowed(true,2,40,3));
    assert(!faux::cancel_allowed(true,3,40,3));
    assert(!faux::cancel_allowed(true,20,80,3));
    assert(!faux::cancel_allowed(true,0,80,1));
    assert(!faux::cancel_allowed(false,0,80,3));
    assert(faux::pursuit_budget(9,0,false,40));
    assert(!faux::pursuit_budget(10,0,false,40));
    assert(!faux::pursuit_budget(0,60,false,40));
    assert(faux::pursuit_budget(11,60,true,40));
    assert(!faux::pursuit_budget(12,60,true,40));
}
