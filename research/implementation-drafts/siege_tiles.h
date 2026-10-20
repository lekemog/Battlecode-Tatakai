#pragma once
#include <span>
#include <vector>

namespace polaris_draft {
struct Point { int x=0,y=0; };
struct ThreatArea { Point position; int attack_radius=0; };
inline long long abs_distance(int a,int b) {
    const long long d=static_cast<long long>(a)-b;
    return d<0?-d:d;
}
inline bool outside_monster_ranges(Point p,std::span<const ThreatArea> monsters) {
    for (const auto& m : monsters) {
        if (m.attack_radius<0) return false;
        const auto dx=abs_distance(p.x,m.position.x),dy=abs_distance(p.y,m.position.y);
        if (dx<=m.attack_radius && dy<=m.attack_radius) return false;
    }
    return true;
}
// all_remaining_damaging includes monsters that our cast could wake.
// can_cast_from must check the real ability's geometry, target type and line of sight.
// SDK-independent: caller must also ensure occupancy, path reachability and fuel budget.
template<class LegalTile,class CanCastFrom>
std::vector<Point> siege_positions(std::span<const Point> candidates,
        std::span<const ThreatArea> all_remaining_damaging,
        LegalTile legal_tile,CanCastFrom can_cast_from) {
    std::vector<Point> result;
    for (Point p : candidates)
        if (legal_tile(p) && outside_monster_ranges(p,all_remaining_damaging)
            && can_cast_from(p)) result.push_back(p);
    return result;
}
} // namespace polaris_draft
