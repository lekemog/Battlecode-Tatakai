#pragma once
// Review sketches only: no SDK calls, no integration and no strength claim.
// Inputs must come from legal observations and engine-valid action/path queries.
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <optional>
#include <span>

namespace field_study {
struct LandingTarget {
    double health = 0;
    double mitigated_damage = 0; // adapter supplies predicted net landing damage
    double damage_per_turn = 0;  // damage prevented if this target is disabled
    double value_weight = 1;     // champion/camp opportunity value, calibrated separately
    bool in_landing_area = false;
    bool stun_immune = false;
    int existing_stun_turns = 0;
};
struct Landing {
    int token = -1;              // adapter maps this token to a valid landing tile
    bool engine_legal = false;   // includes path and destination legality
    double effective_health = 0; // current HP plus applicable shield, not max HP
    double incoming_after_landing = 0;
    double escape_option_cost = 0;
    double followup_value = 0;   // reachable follow-up only
    int stun_turns = 0;
    std::span<const LandingTarget> targets;
};
// Score *incremental* control, not overlapping stun. The adapter must use the
// engine's damage formula (HoR passive, mitigation, shields) rather than multiply
// already-effective stats twice. A profitable dash still competes with cast/basic,
// channel, movement and holding the cooldown.
inline std::optional<double> landing_value(const Landing& a) {
    if (!a.engine_legal || a.token < 0 || !std::isfinite(a.effective_health)
        || !std::isfinite(a.incoming_after_landing)
        || !std::isfinite(a.escape_option_cost) || !std::isfinite(a.followup_value)
        || a.effective_health <= 0 || a.incoming_after_landing < 0
        || a.incoming_after_landing >= a.effective_health) return std::nullopt;
    double gain = a.followup_value - a.incoming_after_landing - a.escape_option_cost;
    bool affects_target = false;
    for (const auto& t : a.targets) {
        if (!t.in_landing_area || t.health <= 0) continue;
        if (!std::isfinite(t.health) || !std::isfinite(t.mitigated_damage)
            || !std::isfinite(t.damage_per_turn) || !std::isfinite(t.value_weight)
            || t.mitigated_damage < 0 || t.damage_per_turn < 0 || t.value_weight < 0)
            return std::nullopt;
        const double damage = std::min(t.health, t.mitigated_damage);
        // A killed target cannot contribute an additional stun benefit.
        const int extra_stun = t.stun_immune || damage >= t.health ? 0
            : std::max(0, a.stun_turns - std::max(0, t.existing_stun_turns));
        gain += t.value_weight * (damage + extra_stun * t.damage_per_turn);
        affects_target = affects_target || damage > 0 || extra_stun > 0;
    }
    if (!affects_target || !std::isfinite(gain)) return std::nullopt;
    return gain;
}
inline int choose_landing(std::span<const Landing> legal_candidates,
                          double best_non_dash_value) {
    int selected = -1;
    if (!std::isfinite(best_non_dash_value)) return selected;
    for (const auto& c : legal_candidates) {
        auto v = landing_value(c);
        if (v && *v > best_non_dash_value) {
            selected = c.token; best_non_dash_value = *v;
        }
    }
    return selected;
}

struct Delivery {
    unsigned gems = 0;
    unsigned completion_turns = 0; // full travel + queue + channel, not altar distance
    bool jointly_feasible = false;
    bool safe = false;
};
struct FinishPlan { std::uint16_t carriers = 0; unsigned turns = 0, gems = 0; };
// The adapter must account for altar locks, reservations, simultaneous channels,
// escorts and legal routes BEFORE setting jointly_feasible. This small planner
// does not invent shared memory, transfer gems, or assume unknown enemy bags.
inline std::optional<FinishPlan> earliest_finish(
    unsigned submitted, unsigned target, std::span<const Delivery> delivery) {
    if (submitted >= target) return FinishPlan{};
    if (delivery.size() > 8) return std::nullopt;
    const unsigned needed = target - submitted;
    std::optional<FinishPlan> best;
    for (unsigned mask = 1; mask < (1u << delivery.size()); ++mask) {
        unsigned sum = 0, end = 0, bodies = 0; bool ok = true;
        for (unsigned i = 0; i < delivery.size(); ++i) if (mask & (1u << i)) {
            const auto& d = delivery[i];
            if (!d.safe || !d.jointly_feasible) { ok = false; break; }
            // Saturate at needed to avoid overflow on malformed external inputs.
            sum += std::min(d.gems, needed - sum);
            end = std::max(end, d.completion_turns); ++bodies;
        }
        if (!ok || sum < needed) continue;
        unsigned best_bodies = best ? __builtin_popcount(best->carriers) : 9;
        if (!best || end < best->turns || (end == best->turns && bodies < best_bodies))
            best = FinishPlan{static_cast<std::uint16_t>(mask), end, sum};
    }
    return best;
}
} // namespace field_study
