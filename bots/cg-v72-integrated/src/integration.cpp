#include "pair.h"
#include "pair_model.h"
#include "world.h"
#include "config.h"
#include <algorithm>
#include <cstddef>
#include <cstdio>

namespace mb {
bool integrated_camp_safe(const Ctx& ctx,vec2 p,int group) {
    for(const auto& c:ctx.camps) {
        if(c.hp<=0 || (c.group!=group && !c.awake))continue;
        const int distance=cheb(p,c.pos);
        if(c.strength<=0 || distance>c.range)continue;
        int front=100000;
        for(const auto& a:ctx.allies)
            if(a.range<=1 && a.hp>=.5f*a.max_hp && !a.channeling)
                front=std::min(front,cheb(a.pos,c.pos));
        if(pair_model::caster_exposed(distance,c.range,c.strength,front))return false;
    }
    for(int i=0;i<ctx.n_unseen;++i)
        if(cheb(p,ctx.unseen[i].pos)<=ctx.unseen[i].range)return false;
    return true;
}
float integrated_region(const Ctx& ctx,vec2 p) {
    if(ctx.round>=cfg::phase_early_until || !ctx.enemies.empty())return 1.f;
    static const int anchor=[] {
        const auto& d=cambc::draft_memory;
        if(d.size()<10 || std::to_integer<int>(d[0])!=0xD4 || std::to_integer<int>(d[1])!=1)return -1;
        const int group=std::to_integer<int>(d[8])+(std::to_integer<int>(d[9])<<8);
        std::printf("REGION anchor%d capacity%zu\n",group,d.size());
        return group;
    }();
    const auto& w=World::get();
    if(anchor<0 || anchor>=static_cast<int>(w.groups.size()))return 1.f;
    return cheb(p,w.groups[anchor].center)<=10 ? 1.12f : 1.f;
}
}
