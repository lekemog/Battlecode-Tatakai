#pragma once
#include <algorithm>
#include <cmath>
#include <limits>

namespace polaris_draft {
// All durations are rounds; costs are occupied champion-rounds.
// Inputs are estimates assembled from legal observations, not SDK calls here.
struct Cycle {
    double travel = 0, ready_in = 0, clear = 0, capture = 0;
    double delivery = 0, channel = 0, recovery_body_rounds = 0;
    int workers = 1, capturers = 1, carriers = 1;
    double gems = 0, gold = 0;
    // Only incremental score denied AND never already counted in gems.
    double denied_score = 0;
    double delivery_probability = 1, reward_probability = 1;
    double existing_bag = 0, bag_loss_probability = 0;
    bool feasible = true;
};
struct CycleScore {
    bool feasible = false;
    double value = 0, body_rounds = 0;
    double rate = -std::numeric_limits<double>::infinity();
};
inline CycleScore score_cycle(const Cycle& c, double gold_value) {
    const double fields[]{c.travel,c.ready_in,c.clear,c.capture,c.delivery,c.channel,
        c.recovery_body_rounds,c.gems,c.gold,c.denied_score,c.existing_bag,gold_value};
    for (double x : fields) if (!std::isfinite(x) || x < 0) return {};
    const double probabilities[]{c.delivery_probability,c.reward_probability,c.bag_loss_probability};
    for (double x : probabilities) if (!std::isfinite(x) || x < 0 || x > 1) return {};
    if (!c.feasible || c.workers < 1 || c.capturers < 1 || c.carriers < 0
        || (c.gems>0 && c.carriers==0) || c.delivery_probability>c.reward_probability
        || c.capturers > c.workers || c.carriers > c.workers) return {};
    // Travel overlaps respawn waiting. Do not charge travel twice.
    // Helpers released after clearing do not pay the carrier's delivery cost.
    const double cost = c.workers * (std::max(c.travel,c.ready_in) + c.clear)
        + c.capturers * c.capture + c.carriers * (c.delivery + c.channel)
        + c.recovery_body_rounds;
    if (!std::isfinite(cost) || cost <= 0) return {};
    // Gold is earned at reward receipt; gems require completed delivery.
    // Denial is separately supplied; no automatic double-value kill heuristic.
    const double value = c.reward_probability * gold_value * c.gold
        + c.delivery_probability * c.gems + c.denied_score
        - c.bag_loss_probability * c.existing_bag;
    if (!std::isfinite(value)) return {};
    return {true,value,cost,value/cost};
}
inline bool switch_target(double incumbent_rate, double challenger_rate,
                          double relative_margin, double absolute_margin) {
    if (!std::isfinite(challenger_rate) || challenger_rate <= 0) return false;
    if (!std::isfinite(incumbent_rate) || incumbent_rate <= 0) return true;
    if (relative_margin < 0 || absolute_margin < 0) return false;
    return challenger_rate > incumbent_rate
        + std::max(absolute_margin,std::abs(incumbent_rate)*relative_margin);
}
} // namespace polaris_draft
