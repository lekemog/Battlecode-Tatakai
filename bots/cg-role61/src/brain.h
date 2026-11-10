#pragma once
// Per-turn decisions for one champion.
//
// Decision order: channels -> spawn healing/shopping -> enemy threats -> low-health recall
// -> tribute -> capture -> farm (target choice with ally commitments from shared memory).
#include "combat.h"
#include "ctx.h"

namespace mb {

class Brain
{
public:
    void turn();

private:
    void turn_inner(FuelTrace& trace);
    void warm_fields(const Ctx& ctx);
    bool handle_threats(Ctx& ctx, TurnActions& acts);
    void observe_roles(const Ctx& ctx);
    bool handle_role_combat(Ctx& ctx, TurnActions& acts);
    bool handle_role_guard(Ctx& ctx, TurnActions& acts);
    vec2 role_carry_pos_{ -1, -1 };
    int role_carry_seen_{ -1000 }, role_carry_group_{ -1 };
    float role_carry_hp_{ 1.0f };
    int role_retreat_until_{ -1 }, role_wait_since_{ -1 };
    bool role_carry_channel_{};
    bool handle_low_health(Ctx& ctx, TurnActions& acts);
    bool handle_tribute(Ctx& ctx, TurnActions& acts);
    // #45: a carrier shut out of a sealed altar attacks the next camp on the breach path.
    bool handle_breach(Ctx& ctx, TurnActions& acts);
    bool handle_farm(Ctx& ctx, TurnActions& acts);
    int choose_target(const Ctx& ctx, float* out_score);
    int plan_target(const Ctx& ctx, float* out_score);
    int choose_chained(const Ctx& ctx, float* out_score, std::vector<float>& bound);
    float score_group(const Ctx& ctx, int group, int* need_out) const;
    bool blocked_respawn(const Ctx& ctx, int group) const;
    bool go_capture(Ctx& ctx, TurnActions& acts, int group);
    bool go_stage(Ctx& ctx, TurnActions& acts, int group);
    bool handoff_capture(const Ctx& ctx, int group, bool on_tile) const;
    bool leave_capture(Ctx& ctx, TurnActions& acts);
    bool force_sufficient(const Ctx& ctx, int group) const;
    bool group_contested(const Ctx& ctx, int group) const;
    void leave_camp_tiles(Ctx& ctx, TurnActions& acts);
    static float gem_weight(const Ctx& ctx);
    static float trip_pool(const Ctx& ctx);
    static float ally_trip_share();
    static float full_trip_pool(const Ctx& ctx);
    static int effective_travel(const Ctx& ctx, const cambc::distance_field* field, int walk, vec2 center);
    int hold_since_{ -1 };  // first round of the current hold on our spawn
    int tribute_end_round_{ -1 };  // expected completion of our tribute channel
    int tribute_stuck_{};          // v51c: consecutive tribute turns that could not step toward the altar
    int detour_altar_{ -1 };       // v51c: index of the altar a blocked carrier walks to instead
    int detour_until_{ -1000 };
    bool pick_detour(Ctx& ctx);
    bool yield_altar_access(Ctx& ctx, TurnActions& acts);
    int last_hit_round_{ -1 };  // last round an engagement landed an attack or spell
    bool retreat(Ctx& ctx, TurnActions& acts);
    // Committed homeward retreat (cfg::retreat_mode 2): walk the spawn field until on spawn or out
    // of sight of every enemy, then recall or retarget away from the last sighting.
    bool continue_homeward(Ctx& ctx, TurnActions& acts);
    bool step_home(Ctx& ctx, TurnActions& acts);
    bool homeward_{};
    int retreat_streak_{};  // consecutive turns retreat() ran
    int last_enemy_round_{ -1000 };  // last round an enemy (off its spawn) was within 8
    vec2 last_enemy_pos_{ -1, -1 };
    bool travel_to_group(Ctx& ctx, TurnActions& acts, int group);
    void publish(int group, int status);

    int target_{ -1 };
    vec2 breach_target_{ -1, -1 };                        // #45: camp tile the approach field leads to
    std::unique_ptr<cambc::distance_field> breach_field_;  // #45: tiles within attack range of it
    int breach_log_round_{ -100 };
    int ring_gate_{ -1 };       // cfg::p5_ring: group whose siege opens the way to a ringed altar
    int ring_round_{ -1000 };   // round it was last wanted
    int ring_gate(const Ctx& ctx, const cambc::distance_field& open_field);  // -2: path not walked yet
    std::vector<int> ring_groups_;  // groups on the open path spawn -> altar, in order
    vec2 ring_walk_{ -1, -1 };
    bool ring_done_{};
    float gold_mult_{ 1.0f };  // our gold gain multiplier (cfg::passive_rewards: Vesper, Treasure)
    float gem_gold_{ 0.0f };   // gold we gain per gem we tribute (cfg::passive_rewards: Marcella)
    float target_score_{};
    int target_need_{ 1 };
    int chosen_round_{ -1000 };
    int staged_since_{ -1 };
    bool capturing_{};
    std::vector<int> banned_until_;  // per group: skip until this round
    int warm_next_{};
    bool initialised_{};
    bool engaged_{};
    int spawn_turns_{};  // consecutive turns started on our spawn
    int time_use_[9]{};  // pvp, heal, tribute, capture, fight, stage, travel, idle, await
    int idle_use_[6]{};
    int blocked_logs_{};
    int travel_recalls_{};  // recalls used as transport (cfg::travel_recall_margin)
    bool travel_blocked_{};  // last travel turn could not move (no field): compute it next turn
    int last_retreat_round_{ -100 };
    int wards_placed_{};
    int ward_errors_{};
    vec2 ward_try_{ -1, -1 };  // diagnostics: the tile of the last placement attempt
    void maybe_place_ward(const Ctx& ctx);
    bool try_tp_shortcut(Ctx& ctx, TurnActions& acts, const cambc::distance_field& field);
    bool place_lock(const Ctx& ctx, vec2 altar);
    void lock_enemy_tribute(const Ctx& ctx);
    int lock_range_{ 2 };  // rule text; narrowed when the engine reports a placement out of range
    int locks_placed_{};
    int calm_retreats_{};  // consecutive retreat turns without losing health
    int capture_stall_{};  // consecutive go_capture turns without a step or a capture tile
    int capture_hold_turns_{};  // consecutive turns holding a capture tile
    int last_hold_round_{ -100 };
    int standoff_recalls_{};
    int lock_errors_{};
    int tp_jumps_{};
    int tp_errors_{};
    int standoff_turns_{};  // travel turns right after a retreat (cfg::standoff_ban_after)
    // Death report: the last turns before dying (diagnostics only).
    struct TurnNote
    {
        int round{ -1 };
        int hp{};
        const char* mode{ "" };
        const char* why{ "" };
        int enemies{}, enemy_dist{ 99 }, allies_near{};
        float our_loss{ -1.0f }, their_loss{ -1.0f };
    };
    static constexpr int kNotes = 10;
    TurnNote notes_[kNotes]{};
    int note_count_{};
    bool death_reported_{ true };
    void note_turn(const Ctx& ctx, const char* mode);
    // Threat memory: awake camps that left our view, and our health at the end of last turn.
    struct RememberedCamp
    {
        vec2 pos{};
        int range{};
        float strength{};
        int round{};
    };
    RememberedCamp camp_memory_[8]{};
    int n_camp_memory_{};
    float last_hp_{ -1.0f };
    // Enemies seen recently (by roster index): hidden ones (bushes, just out of sight) still fight.
    struct EnemyMemory
    {
        int round{ -1000 };
        vec2 pos{};
        float hp{}, max_hp{}, strength{}, focus{};
        std::uint32_t gems{};
        cambc::champion_type type{};
        int range{ 1 };
    };
    EnemyMemory enemy_memory_[8]{};
    void remember_threats(Ctx& ctx);
    void share_sightings(Ctx& ctx);
    void share_pack(const Ctx& ctx);  // cfg::phantom_mode 2
    // cfg::carrier_capture: should this champion capture `group` rather than the allies beside it?
    bool designated_capturer(const Ctx& ctx, int group) const;
    int escort(Ctx& ctx, TurnActions& acts);  // cfg::escort_until
    int pick_opening_group() const;  // cfg::opening_party
    int opening_group_{ -2 };        // -2: not chosen yet, -1: none
    bool opening_done_{};
    bool pack_checked_{};  // v53d: spawn walk tested for the pack gate
    int capture_recall_group_{ -1 };  // cfg::capture_recall: the capture our recall channel overlaps
    // cfg::tactics_s: the local-power response replacing handle_threats.
    bool handle_threats_s(Ctx& ctx, TurnActions& acts);
    bool flee_s(Ctx& ctx, TurnActions& acts, bool allow_recall);
    const ChampView* focus_s(const Ctx& ctx, bool* killable) const;
    int disengage_until_{ -1 };   // committed disengage: farming may not resume before this round
    int last_threat_round_{ -1000 };
    vec2 last_threat_pos_{ -1, -1 };
    int spawn_hold_since_{ -1 };
    void report_death(int round);
    // The shop's measurements of this champion (cfg::shop_plan 100 / cfg::shop_recall_mode 1 only).
    void note_shop_signals(const Ctx& ctx, bool alive);
    float last_sim_[2]{ -1.0f, -1.0f };
    int none_logs_{};
    mutable int last_reject_{};  // diagnostics: idle causes (fuel, no target, respawn wait, stall, blocked, other) // diagnostics: turns per activity (pvp, heal, tribute, capture, fight, stage, travel, idle)
    const char* why_{ "-" };  // diagnostics: last farm branch
    int progress_best_{ 1 << 20 };
    int progress_round_{};
    // cfg::learned: the learned factor on a group's target score, given the travel used for
    // it (the same in the bound and the full score, so pruning stays exact), and the banked-gem
    // gap the features read (enemy minus ours over 300, clamped to [-1, 1]; read once per turn).
    // Their state lives in brain.cpp, so with the layer off this class is unchanged.
    float group_factor(const Ctx& ctx, int group, int travel) const;
    float gem_gap(const Ctx& ctx) const;
    void learn_setup() const;  // per-game tables, built at the end of the first turn with fuel to spare
    bool hold_on_spawn(const Ctx& ctx);  // spawn block: wait on our spawn this turn
    void share_news(const Ctx& ctx);     // cfg::group_news: read and post respawning-group news
};

} // namespace mb
