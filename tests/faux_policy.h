#pragma once
#include <algorithm>

// Pure policy arithmetic used by every faux v2 bot and tested without an engine.
namespace faux {
inline double remaining_hp(double total, double visible_base, double visible_hp) {
    return std::max(0.0,total-std::max(0.0,visible_base-visible_hp));
}
inline bool cancel_allowed(bool threatened,int cancels,int gems,int channel) {
    return threatened&&channel>1&&cancels<(gems>=60?20:3);
}
inline bool pursuit_budget(unsigned elapsed,int own_bag,bool channel,int enemy_bag) {
    // A hunt must not postpone our own valuable tribute indefinitely.
    if(own_bag>=40&&!channel)return false;
    return elapsed<static_cast<unsigned>(channel?12:enemy_bag>=30?10:6);
}
}
