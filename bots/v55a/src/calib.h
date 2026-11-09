#pragma once
// v55a in-game fight calibration (online learning, per champion, per game).
//
// The fight simulation predicts how much damage enemies deal from their live strength/focus and kit.
// It misses items, passives, levels it cannot read and how well the opponent focuses. Ranked losses:
// deaths 7.7 vs 4.2 - our verdicts are too optimistic against the teams that beat us.
//
// Each round we end a turn isolated (no ally within 2, so we are the only target) with enemies able to
// hit us and no camp awake near us, we record the damage the simulation expects (basic attacks plus
// casts that are ready) and, next turn, the damage actually taken (all remaining health if we died).
// The enemy-strength multiplier is a shrunk ratio of sums:
//     m = (P * mean_exp + sum_obs) / (P * mean_exp + sum_exp),  clamped to [lo, hi]
// P pseudo-rounds of prior at m = 1, so a single unlucky round cannot swing it. The simulation then
// scales every enemy's damage by m for the rest of the game.
#include <algorithm>

namespace calib
{
struct Snapshot
{
    int x{}, y{};
    int range{};
    float dmg{};  // expected damage this enemy deals in one round if it targets us
};

struct State
{
    Snapshot snap[8]{};
    int n_snap{};
    bool armed{};        // a snapshot was taken this turn (expected computed at turn end)
    bool pending{};      // an expectation waits for next turn's observation
    float hp_before{};   // our health at the end of the armed turn
    float expected{};
    float sum_obs{}, sum_exp{};
    int n{};
    int deaths{};
};

inline State& state()
{
    static State s;
    return s;
}

inline float multiplier(float prior_rounds, float lo, float hi)
{
    const auto& s = state();
    if (s.n == 0 || s.sum_exp <= 0.0f) return 1.0f;
    const float mean = s.sum_exp / static_cast<float>(s.n);
    const float m = (prior_rounds * mean + s.sum_obs) / (prior_rounds * mean + s.sum_exp);
    return std::clamp(m, lo, hi);
}

// Next turn (alive): fold the observation in.
inline void observe_alive(float hp_now)
{
    auto& s = state();
    if (!s.pending) return;
    s.pending = false;
    const float taken = std::clamp(s.hp_before - hp_now, 0.0f, s.hp_before);
    s.sum_obs += taken;
    s.sum_exp += s.expected;
    ++s.n;
}

// Next turn (dead): we lost at least all the health we had.
inline void observe_dead()
{
    auto& s = state();
    if (!s.pending) return;
    s.pending = false;
    s.sum_obs += s.hp_before;
    s.sum_exp += s.expected;
    ++s.n;
    ++s.deaths;
}
}  // namespace calib
