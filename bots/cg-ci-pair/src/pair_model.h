#pragma once
#include <algorithm>

namespace mb::pair_model {
// No host calls. A stale position must never become a permanent follow objective.
inline bool fresh(int now, int seen) { return now >= seen && now - seen <= 3; }
inline bool vulnerable(float self_hp, float partner_hp) {
    return std::min(self_hp, partner_hp) < 0.35f;
}
inline bool regroup(int distance, int steps, bool channeling, bool contact) {
    return !channeling && !contact && distance > 4 && distance <= 8 && steps < 4;
}
// Damage first for an estimated finisher; otherwise stop a real dive/channel.
inline bool prefer_stun(bool damage_finisher, bool stun_ready, bool can_stun,
                        bool diving, bool channeling) {
    return !damage_finisher && stun_ready && can_stun && (diving || channeling);
}
}
