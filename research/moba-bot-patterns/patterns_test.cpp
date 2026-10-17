#include "patterns.hpp"
#include <cassert>
#include <iostream>
#include <random>
using namespace moba;
double brute(const std::vector<std::vector<double>>& v,int a,unsigned used) {
    if (a==static_cast<int>(v.size())) return 0;
    double best=brute(v,a+1,used);
    for (unsigned j=0;j<v[a].size();++j) if (!(used&(1u<<j)) && std::isfinite(v[a][j]))
        best=std::max(best,v[a][j]+brute(v,a+1,used|(1u<<j)));
    return best;
}
int main() {
    // Joint assignment avoids individually greedy starvation: agent 0 should take job 1.
    auto a=assign({{10,9},{9,0}});
    assert(a.value==18 && a.job[0]==1 && a.job[1]==0);
    assert(assign({{-1,-2}}).job[0]==-1);
    assert(assign({}).value==0);
    const double nan=std::numeric_limits<double>::quiet_NaN();
    assert(assign({{nan,4}}).job[0]==1);
    bool rejected=false;try{assign({{1},{1,2}});}catch(const std::invalid_argument&){rejected=true;}
    assert(rejected);
    // Compare the DP with exhaustive enumeration over many small independent inputs.
    std::mt19937 rng(20261017);
    std::uniform_int_distribution<int> val(-5,20);
    for (int t=0;t<200;++t) {
        const int n=1+static_cast<int>(rng()%4),m=1+static_cast<int>(rng()%5);
        std::vector<std::vector<double>> v(n,std::vector<double>(m));
        for(auto& row:v) for(auto& x:row) x=val(rng);
        const auto got=assign(v);
        assert(std::abs(got.value-brute(v,0,0))<1e-9);
        unsigned used=0;double sum=0;
        for(int i=0;i<n;++i) if(got.job[i]>=0) {
            assert(!(used&(1u<<got.job[i])));used|=1u<<got.job[i];sum+=v[i][got.job[i]];
        }
        assert(sum==got.value);
    }
    Option channel{1,Kind::Bank,30,0,0,3,true};
    Option farm{2,Kind::Farm,80,0,0,4,true};
    Option escape{3,Kind::Retreat,1,0,0,1,true,true};
    assert(select({channel,farm},{1,5,true},10,2)==1);
    assert(select({channel,farm,escape},{1,5,true},10,2)==3);
    channel.legal=false;assert(select({channel,farm},{1,99,true},1,2)==2);
    channel.legal=true;assert(select({channel,farm},{1,5,false},10,2)==2);
    assert(select({channel,farm},{1,5,false},1,11)==1);
    farm.team_value=nan;assert(!select({farm},{},1,0));
    CampCycle c{10,0,5,5,10,4,66,0,100,500,100,0,0,true};
    assert(cycle_rate(c)>0);c.predicted_damage=450;assert(!std::isfinite(cycle_rate(c)));
    c.predicted_damage=100;c.wait_at_arrival=20;const auto slower=cycle_rate(c);
    c.wait_at_arrival=0;assert(cycle_rate(c)>slower);
    assert(focus({{1,false,true,1,100,0,1000},{2,true,true,50,30,0,0}})==2);
    assert(focus({{1,true,true,20,30,20,50},{2,true,true,50,30,0,0}})==2);
    assert(!focus({{1,true,false,20,30,0,0}}));
    assert(vision_gain({{10,true},{3,false},{nan,false},{-2,false}})==3);
    std::cout<<"PASS: 200 assignment oracle cases; commitment, legality, cycle, focus, vision scenarios\n";
}
