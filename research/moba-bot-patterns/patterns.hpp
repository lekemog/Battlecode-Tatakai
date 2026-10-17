#pragma once
// Original research examples for Polaris, not Riot/OpenAI/Valve source or SDK bindings.
// All quantities and thresholds are caller supplied, uncalibrated hypotheses.
#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <optional>
#include <stdexcept>
#include <vector>

namespace moba {
enum class Kind { Farm, Bank, Shop, Support, Fight, Retreat };
struct Option {
    int id;
    Kind kind;
    double team_value;       // Same units across ALL options; not individual farm score.
    double expected_loss;    // Same units; includes carried gems/opportunity cost if relevant.
    double uncertainty_cost;
    double turns;
    bool legal;
    bool emergency = false;
};
inline double utility(const Option& o) {
    if (!o.legal || !std::isfinite(o.team_value) || !std::isfinite(o.expected_loss)
        || !std::isfinite(o.uncertainty_cost) || !std::isfinite(o.turns)
        || o.expected_loss < 0 || o.uncertainty_cost < 0 || o.turns <= 0)
        return -std::numeric_limits<double>::infinity();
    return (o.team_value-o.expected_loss-o.uncertainty_cost)/o.turns;
}
struct Commitment {
    int id = -1;
    int until = 0;
    bool running_channel = false;
};
// Behaviours expose whether they are running rather than silently swallowing a turn.
// Caller invalidates a commitment on death, stalled progress, or changed assumptions.
// Invalid options cannot be preserved. Only a legal emergency overrides a running channel.
inline std::optional<int> select(const std::vector<Option>& opts, Commitment c,
                                 int round, double switch_margin) {
    if (!std::isfinite(switch_margin) || switch_margin < 0)
        throw std::invalid_argument("negative/nonfinite switch margin");
    const Option *best=nullptr, *current=nullptr, *urgent=nullptr;
    for (const auto& o:opts) {
        const double u=utility(o);
        if (!std::isfinite(u)) continue;
        if (o.id==c.id) current=&o;
        if (!best || u>utility(*best)) best=&o;
        if (o.emergency && (!urgent || u>utility(*urgent))) urgent=&o;
    }
    if (urgent) return urgent->id;
    if (current && (c.running_channel || round<c.until)) {
        if (c.running_channel || !best || utility(*best)<=utility(*current)+switch_margin)
            return current->id;
    }
    if (!best || utility(*best)<=0) return std::nullopt; // explicit idle/fallback
    return best->id;
}

struct Allocation {
    std::array<int,6> job{{-1,-1,-1,-1,-1,-1}};
    double value=0;
};
// Exact maximum additive assignment for <=6 agents, <=16 single-owner jobs.
// Negative/nonfinite entries mean undesirable/invalid; idle is always available.
// O(jobs * agents * 2^agents). NOT a solver for multi-champion siege synergies.
inline Allocation assign(const std::vector<std::vector<double>>& value) {
    const int n=static_cast<int>(value.size());
    if (n>6) throw std::invalid_argument("at most six agents");
    if (n==0) return {};
    const int m=static_cast<int>(value[0].size());
    if (m>16) throw std::invalid_argument("at most sixteen jobs");
    for (const auto& row:value) if (static_cast<int>(row.size())!=m)
        throw std::invalid_argument("ragged matrix");
    constexpr double neg=-std::numeric_limits<double>::infinity();
    std::vector<double> dp(1<<n,neg); dp[0]=0;
    std::vector<Allocation> plan(1<<n);
    for (int j=0;j<m;++j) {
        auto next=dp; auto next_plan=plan; // skip job j
        for (int mask=0;mask<(1<<n);++mask) if (std::isfinite(dp[mask])) {
            for (int a=0;a<n;++a) if (!(mask&(1<<a))) {
                const double v=value[a][j];
                if (!std::isfinite(v) || v<=0) continue;
                const int nm=mask|(1<<a);
                if (dp[mask]+v>next[nm]) {
                    next[nm]=dp[mask]+v; next_plan[nm]=plan[mask];
                    next_plan[nm].job[a]=j; next_plan[nm].value=next[nm];
                }
            }
        }
        dp=std::move(next); plan=std::move(next_plan);
    }
    const auto it=std::max_element(dp.begin(),dp.end());
    return plan[static_cast<int>(it-dp.begin())];
}

struct CampCycle {
    double travel, wait_at_arrival, clear, capture, bank_travel, tribute;
    double gems, gold_score_value, predicted_damage, remaining_hp, hp_reserve;
    double expected_loss_score, uncertainty_score;
    bool reachable;
};
// Arrival-aware wait must be max(0, respawn_round - (now + travel)).
// Damage includes the full known group plus conservative unknown-member allowance.
inline double cycle_rate(const CampCycle& c) {
    for (double x:{c.travel,c.wait_at_arrival,c.clear,c.capture,c.bank_travel,c.tribute,
                   c.gems,c.gold_score_value,c.predicted_damage,c.remaining_hp,c.hp_reserve,
                   c.expected_loss_score,c.uncertainty_score})
        if (!std::isfinite(x) || x<0) return -std::numeric_limits<double>::infinity();
    if (!c.reachable || c.remaining_hp-c.predicted_damage<c.hp_reserve)
        return -std::numeric_limits<double>::infinity();
    const double time=c.travel+c.wait_at_arrival+c.clear+c.capture+c.bank_travel+c.tribute;
    if (time<=0) return -std::numeric_limits<double>::infinity();
    return (c.gems+c.gold_score_value-c.expected_loss_score-c.uncertainty_score)/time;
}

struct Enemy {
    int id;
    bool visible, legal_target;
    double hp, effective_damage, allied_reserved_damage, interruption_value;
};
// Examples of a marginal-action score, NOT a calibrated combat simulator.
// Damage is post-mitigation, in HP units; interruption_value must use those units too.
inline std::optional<int> focus(const std::vector<Enemy>& enemies) {
    double best=0; std::optional<int> id;
    for (const auto& e:enemies) {
        if (!e.visible || !e.legal_target) continue;
        if (!std::isfinite(e.hp)||!std::isfinite(e.effective_damage)
            ||!std::isfinite(e.allied_reserved_damage)||!std::isfinite(e.interruption_value)
            ||e.hp<=0||e.effective_damage<0||e.allied_reserved_damage<0
            ||e.interruption_value<0) continue;
        const double left=std::max(0.0,e.hp-e.allied_reserved_damage);
        const double score=std::min(left,e.effective_damage)
            +(left>0?e.interruption_value:0);
        if (score>best) { best=score; id=e.id; }
    }
    return id;
}

struct VisionTile {
    double relevance; // How likely observing it changes a current decision, not generic area.
    bool already_seen;
};
inline double vision_gain(const std::vector<VisionTile>& covered) {
    double value=0;
    for (const auto& t:covered)
        if (!t.already_seen && std::isfinite(t.relevance) && t.relevance>0)
            value+=t.relevance;
    return value;
}
// Evaluate existing ward coverage as an option too: relocate only for net benefit.
// Geometry, legal placement, duration, shared vision and cast costs belong in an SDK adapter.
} // namespace moba
