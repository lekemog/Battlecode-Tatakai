#include "bots/v50c-hazard-history/src/hazard_history.h"
#include <cassert>
#include <cmath>
#include <iostream>
int main() {
    mb::hazard::HealthHistory h;
    auto near=[](float a,float b){assert(std::fabs(a-b)<0.00001f);};
    near(h.loss3(0,500,1000),0);
    h.record(4,1000);
    near(h.loss3(7,600,1000),.4f);
    // Legacy modulo lookup wrongly reuses r4 at r11 after a fuel/observation gap.
    near(h.loss3(11,600,1000),0);
    assert((h.hp[(11+1)%4]-600)/1000 == .4f);
    h.clear();
    near(h.loss3(7,600,1000),0);
    // Healing keeps the signed feature used during training.
    h.record(8,400); near(h.loss3(11,700,1000),-.3f);
    // For uninterrupted observations, preserve all old feature values.
    float legacy[4]{-1,-1,-1,-1};
    for(int r=0;r<10000;++r) {
        float hp=100.f+float((r*37)%1400);
        h.record(r,hp); legacy[r%4]=hp;
        if(r>=3) near(h.loss3(r,hp,1500),(legacy[(r+1)%4]-hp)/1500);
    }
    // Exact timestamp validity against a reference map with sparse observations.
    h.clear(); int stamps[4]{-1,-1,-1,-1}; float values[4]{};
    for(int r=0;r<10000;++r) {
        if(r%7==0) { h.clear(); for(int& s:stamps)s=-1; }
        if(r%5!=0) {h.record(r,float(r)); stamps[r%4]=r;values[r%4]=float(r);}
        float expected=0;
        if(r>=3&&stamps[(r-3)%4]==r-3)expected=(values[(r-3)%4]-float(r))/1000;
        near(h.loss3(r,float(r),1000),expected);
    }
    std::cout<<"PASS: stale-slot reproducer, death reset, signed healing, 10000 continuous and 10000 sparse rounds\n";
}
