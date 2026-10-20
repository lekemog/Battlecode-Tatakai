#pragma once
#include <algorithm>

namespace polaris_draft {
enum class Stage { none, travel, clear, capture, deliver };
enum class Result { no_action, progress, holding, complete, failed };
struct Task {
    int target = -1;
    Stage stage = Stage::none;
    int last_progress = 0, hold_until = -1;
    bool active() const { return target >= 0 && stage != Stage::none; }
    void clear() { *this = {}; }
    void start(int group, Stage next, int now) {
        target=group; stage=next; last_progress=now; hold_until=-1;
    }
    void transition(Stage next, int now) {
        stage=next; last_progress=now; hold_until=-1;
    }
};
struct TaskObservation {
    int round = 0;
    bool alive = true, target_invalid = false, unsafe_to_continue = false;
    bool actual_progress = false;
    // Current legal observation confirms capture/tribute/respawn waiting is useful.
    // Caller supplies a bounded completion deadline, not a fresh timer every turn.
    bool productive_hold = false;
    int hold_deadline = -1;
};
inline bool retain_task(Task& t, const TaskObservation& o, int stall_limit) {
    if (!t.active()) return false;
    if (!o.alive || o.target_invalid || o.unsafe_to_continue) { t.clear(); return false; }
    if (o.actual_progress) t.last_progress=o.round;
    if (o.productive_hold && o.hold_deadline >= o.round) {
        // A new hold must be a stage transition; never extend the existing deadline.
        if (t.hold_until < 0) t.hold_until=o.hold_deadline;
        if (o.round <= t.hold_until) return true;
    }
    if (o.round - t.last_progress >= std::max(1,stall_limit)) { t.clear(); return false; }
    return true;
}
// Holding is a useful consumed turn, although no SDK action was issued.
inline bool consumes_policy_turn(Result r) {
    return r==Result::progress || r==Result::holding || r==Result::complete;
}

enum class CampState { unknown, alive, reward, respawning };
struct CampMemory {
    CampState state = CampState::unknown;
    int observed_round = -1, ready_round = -1;
    void observe(CampState next, int now, int respawn_remaining = -1) {
        state=next; observed_round=now;
        ready_round=(next==CampState::respawning && respawn_remaining>=0)
            ? now+respawn_remaining : -1;
    }
    CampState estimate(int now, int reward_freshness) const {
        if (state==CampState::reward && now-observed_round>reward_freshness)
            return CampState::unknown; // no invented capture time or ownership
        if (state==CampState::respawning && ready_round>=0 && now>=ready_round)
            return CampState::unknown; // deadline reached, not proof of a living camp
        return state;
    }
};
} // namespace polaris_draft
