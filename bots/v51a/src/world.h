#pragma once
// Static map knowledge, built once per bot instance, plus a cache of distance fields.
//
// Claims: terrain, altars, spawns and camp-group membership never change during a match
// (GameRules "Map features"); camps occupy their spawn tiles while alive, so static fields
// treat every camp tile except the target's own as a wall. Fields are computed lazily and
// only when fuel allows; their cost depends on search depth, so it is measured, not guessed.
#include <cambc.h>
#include <cstdint>
#include <memory>
#include <vector>
#include "util.h"

namespace mb {

struct CampTypeStats
{
    float health{};
    float strength{};
    int range{};
};

struct GroupInfo
{
    std::vector<vec2> tiles;            // member spawn tiles
    std::vector<std::uint8_t> types;    // member camp_type values
    vec2 center{};
    int min_x{}, min_y{}, max_x{}, max_y{};
    std::uint32_t gold{}, gems{};
    int respawn{};
    float total_hp{};
    float total_strength{};
    int max_range{};
    float neighbours{};  // mean count of other members within Chebyshev radius one
    // Fight constants with members killed in Smith order (descending strength/health):
    // weighted_hp = sum_k strength_k * cumulative_health_k. Damage taken at team damage
    // rate d is about weighted_hp/d (see model::forecast_from_constants).
    float weighted_hp{};
    bool harmless{};
    bool has_monolith{};
};

class World
{
public:
    static World& get();

    int width{}, height{};
    cambc::bitboard blocked;      // never walkable: walls, holes, altars, enemy spawn
    cambc::bitboard camp_spawns;  // every camp spawn tile
    std::vector<GroupInfo> groups;
    std::vector<cambc::map::camp_group> group_objects;  // SDK objects, same order as groups
    std::vector<vec2> altars;
    std::vector<vec2> ally_spawn, enemy_spawn;
    vec2 ally_spawn_center{}, enemy_spawn_center{};
    CampTypeStats camp_stats[6]{};

    // Group index owning a camp spawn tile (or -1), and the member index within it.
    int group_at(vec2 tile) const;
    int member_at(vec2 tile) const;
    const cambc::camp& camp(int group, int member) const { return group_objects[static_cast<std::size_t>(group)].camps()[static_cast<std::size_t>(member)]; }

    // Distance fields (nullptr when not yet computed and fuel does not allow computing now).
    // `tail_margin`: fuel kept free after the search (default cfg::field_tail_margin).
    const cambc::distance_field* group_field(int group, bool allow_compute, std::uint64_t tail_margin = 0);
    const cambc::distance_field* altar_field(bool allow_compute);
    const cambc::distance_field* spawn_field(bool allow_compute);
    // v51a: distance to one altar (index into `altars`), for carriers avoiding a guarded altar.
    const cambc::distance_field* altar_field_at(std::size_t i, bool allow_compute);
    // Distance to the nearest altar with every camp tile passable (ring-gate banking).
    const cambc::distance_field* open_altar_field(bool allow_compute);
    // An altar whose submit range holds only one group's camp tiles (a gate): reachable by
    // standing on those tiles while that group is down. Field rooted at the gate tiles.
    std::vector<vec2> gate_tiles;
    int gate_group{ -1 };
    const cambc::distance_field* gate_field(bool allow_compute);
    // #45 sealed altars (02the_pack): an altar with free floor in submit range that no walk from
    // our spawn reaches while every camp tile is a wall, i.e. ringed by camps (not the gate case
    // above). Camp tiles of groups near it form the seal zone. Tiles seen there without a living
    // camp are a gap: the altar field is rebuilt with them passable, so carriers bank through any
    // gap that they have seen (made by us or the enemy). Other maps are untouched (empty zone).
    void note_seal_camps(const cambc::bitboard& visible, const cambc::bitboard& living);
    void refresh_sealed_altar_field();
    void detect_seal();  // once the altar field exists
    bool sealed() const { return seal_state_ == 1; }
    int seal_gaps() const { return static_cast<int>(seal_dead_.count()); }
    bool seal_dead(vec2 t) const { return seal_dead_.is_set(t); }
    // Living (not seen dead) seal-zone camps within Chebyshev `r` of `t`: who fires at a breacher
    // there once the ring is awake (the whole group wakes when one member is hit).
    int seal_exposure(vec2 t, int r) const
    {
        int n = 0;
        for (auto z : seal_zone_list_)
            if (cheb(z, t) <= r && !seal_dead_.is_set(z)) ++n;
        return n;
    }
    // #45 breach: fewest seal-zone camps to kill so a walk from our spawn reaches free floor in
    // submit range of the sealed altar, outermost first (seen gaps cost nothing). Searched over the
    // zone tiles only; empty when the spawn field is missing or no breach exists. Cached until a
    // gap changes.
    const std::vector<vec2>& breach_path();
    // Free floor inside a sealed altar's ring (filled by breach_path). Only the altar field knows
    // the gaps, so a champion in here cannot path to anything else.
    bool in_seal_interior(vec2 t)
    {
        breach_path();
        if (seal_interior_.empty() || t.x < 0 || t.y < 0 || t.x >= width || t.y >= height) return false;
        return seal_interior_[static_cast<std::size_t>(t.y) * width + t.x] != 0;
    }
    // Field to arbitrary roots with camps as walls except seen gaps (breach approach).
    bool approach_field(std::unique_ptr<cambc::distance_field>& slot, const cambc::bitboard& roots, vec2 center)
    {
        return compute(slot, roots, true, center, 0, true, &seal_dead_);
    }
    // Field to walk towards a group from `from`: the full group field when present, else a
    // partial one searched only until `from` is reached (cost ~ distance, not map size; full
    // fields on 100x100 maps cost ~35K and were often unaffordable, leaving travel blocked).
    // Partial fields are for stepping only, never for travel estimates.
    const cambc::distance_field* route_field(int group, vec2 from);
    // Can a group be reached on foot from our spawn? 1 yes, 0 no, -1 unknown (spawn field not
    // computed yet). A member tile counts when any neighbour has a finite spawn distance.
    int walk_reachable(int group);
    // Path distance from `from` to a field's roots, falling back to a Chebyshev estimate.
    static int distance(const cambc::distance_field* field, vec2 from, vec2 fallback_target);
    // Fuel estimate for one field rooted near `center`: measured cost per expansion step times
    // the estimated search depth (farthest corner with a detour allowance).
    std::uint64_t field_cost_at(vec2 center) const;
    int depth_estimate(vec2 center) const;
    // Typical estimate (map centre) for callers without a specific field in mind.
    std::uint64_t field_cost() const { return field_cost_at({ width / 2, height / 2 }); }
    bool calibrated() const { return measured_; }

private:
    World();
    bool compute(std::unique_ptr<cambc::distance_field>& slot, const cambc::bitboard& roots, bool allow_compute, vec2 center,
                 std::uint64_t tail_margin = 0, bool camp_walls = true, const cambc::bitboard* passable = nullptr);

    int seal_state_{ -1 };       // -1 unknown, 0 no sealed altar, 1 sealed
    bool seal_dirty_{};          // seal_dead_ changed since the altar field was built
    cambc::bitboard seal_zone_;  // camp tiles of groups ringing a sealed altar
    cambc::bitboard seal_dead_;  // zone tiles last seen without a living camp
    std::vector<vec2> sealed_altars_;
    std::vector<vec2> seal_zone_list_;
    std::vector<vec2> breach_path_;
    std::vector<std::uint8_t> seal_interior_;
    bool breach_valid_{};

    std::vector<std::unique_ptr<cambc::distance_field>> group_fields_;
    std::vector<std::unique_ptr<cambc::distance_field>> partial_fields_;
    std::unique_ptr<cambc::distance_field> altar_field_, spawn_field_, gate_field_, open_altar_field_;
    std::vector<std::unique_ptr<cambc::distance_field>> single_altar_fields_;
    std::vector<std::int8_t> reachable_;     // per group: -1 unknown, 0 no, 1 yes
    std::vector<std::int16_t> tile_group_;   // row-major tile -> group index
    std::vector<std::int16_t> tile_member_;  // row-major tile -> member index
    std::uint64_t step_cost_{};
    bool measured_{};
};

} // namespace mb
