#include "../../bots/chatgpt-v50h5e-history/src/health_history.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <type_traits>
static_assert(std::is_trivially_copyable_v<mb::hazard::HealthHistory>);
static_assert(sizeof(mb::hazard::HealthHistory) == 32);
int main() {
    mb::hazard::HealthHistory h;
    auto equal=[](float a,float b){assert(std::fabs(a-b)<0.000001f);};
    equal(h.loss3(0,600,1000),0);
    h.record(4,1000); equal(h.loss3(7,600,1000),.4f);
    // Old modulo buffer mistakes r4 for r8 when queried at r11.
    equal(h.loss3(11,600,1000),0);
    h.clear(); equal(h.loss3(7,600,1000),0);
    h.record(8,400); equal(h.loss3(11,700,1000),-.3f);
    h.clear();
    std::array<float,4> old{};
    for(int r=0;r<20000;++r) {
        const float hp=100+float((r*37)%1400);
        h.record(r,hp);old[static_cast<unsigned>(r)&3u]=hp;
        if(r>=3) equal(h.loss3(r,hp,1500),(old[static_cast<unsigned>(r+1)&3u]-hp)/1500);
    }
    // Independent sparse reference, including observation gaps and resets.
    h.clear(); std::array<float,20000> values{}; std::array<bool,20000> observed{};
    int generation_start=0;
    for(int r=0;r<20000;++r) {
        if(r%97==0) {h.clear();generation_start=r;}
        if(r%5!=0 && r%7!=0) {values[r]=float(r%1500);observed[r]=true;h.record(r,values[r]);}
        const float expected=r>=3 && r-3>=generation_start && observed[r-3] ? (values[r-3]-700)/1000 : 0;
        equal(h.loss3(r,700,1000),expected);
    }
    h.clear();h.record(-1,999);equal(h.loss3(3,1,1),0);
    h.record(0,100); equal(h.loss3(3,90,0),10);
    std::cout<<"PASS: stale-gap, reset, signed healing, 20000 continuous and 20000 sparse reference rounds; 32-byte fixed storage\n";
}
