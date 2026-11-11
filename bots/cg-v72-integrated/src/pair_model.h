#pragma once
#include <algorithm>

namespace mb::pair_model {
inline int caster_escape_score(bool safe,int distance) { return safe ? 100000-distance*10 : -10000000; }
inline bool caster_exposed(int caster_distance,int camp_range,float damage,int front_distance) {
    return damage>0 && caster_distance<=camp_range && front_distance>=caster_distance;
}
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
