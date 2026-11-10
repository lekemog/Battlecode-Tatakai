#include "brain.h"
#include "config.h"
#include "knowledge.h"
#include "nav.h"
#include "world.h"
#include <algorithm>
#include <cmath>

namespace mb {
namespace {
template<class F> bool role_use(const char* label, F action)
{
    try { return action(); }
    catch (const cambc::error& e) { MB_LOG("%s rejected: %s\n", label, e.what()); return false; }
}
bool carry_type(cambc::champion_type t) { return t == cambc::champion_type::vesper_vale; }
bool guard_type(cambc::champion_type t) { return t == cambc::champion_type::heart_of_ruin; }
// Position risk includes awake camps and live enemy reach (including ready dashes).
int role_risk(const Ctx& ctx, vec2 p)
{
    int risk = static_cast<int>(camp_threat_at(ctx, p) * 12.0f);
    for (const auto& e : ctx.enemies)
    {
        if (e.hp <= 0.0f) continue;
        const int d = cheb(p, e.pos), reach = enemy_reach(e);
        if (d <= reach) risk += 3000 + static_cast<int>(e.dps * 8.0f);
        if (d <= e.range) risk += 3000;
    }
    return risk;
}
}

void Brain::observe_roles(const Ctx& ctx)
{
    role_carry_group_ = -1;
    const auto& kn = Knowledge::get();
    bool alive_carry = false;
    const auto& slots = kn.slots();
    const auto& rr = roster(cambc::team::ally);
    for (std::size_t i = 0; i < rr.types.size(); ++i)
        if (carry_type(rr.types[i]))
            for (std::size_t j = 0; j < kn.allies.size(); ++j)
                if (static_cast<cambc::handle_champion_t>(rr.champs[i]) == static_cast<cambc::handle_champion_t>(kn.allies[j]))
                {
                    alive_carry = j < kn.alive.size() && kn.alive[j];
                    if (alive_carry && j < slots.size() && (slots[j].status == SlotStatus::engaging || slots[j].status == SlotStatus::capturing))
                        role_carry_group_ = slots[j].group;
                }
    if (!alive_carry && !carry_type(kit().type))
    {
        role_carry_seen_ = -1000;
        role_wait_since_ = -1;
        return;
    }
    if (carry_type(kit().type))
    {
        role_carry_pos_ = ctx.pos;
        role_carry_seen_ = ctx.round;
        role_carry_hp_ = ctx.hp_frac();
        role_carry_channel_ = false;
    }
    else for (const auto& a : ctx.allies)
        if (carry_type(a.type))
        {
            role_carry_pos_ = a.pos;
            role_carry_seen_ = ctx.round;
            role_carry_hp_ = a.hp / std::max(1.0f, a.max_hp);
            role_carry_channel_ = a.channeling;
        }
}

bool Brain::handle_role_combat(Ctx& ctx, TurnActions& acts)
{
    const bool carry = carry_type(kit().type);
    if (ctx.enemies.empty()) return false;
    const bool known = ctx.round - role_carry_seen_ <= 6;
    if (!carry && !cfg::role_peel) return false;
    if (!carry && (!known || cheb(ctx.pos, role_carry_pos_) > 7)) return false;
    const vec2 anchor = carry ? ctx.pos : role_carry_pos_;
    const ChampView* focus = nullptr;
    int best = -1000000, nearest = 100, divers = 0;
    for (const auto& e : ctx.enemies)
    {
        if (e.hp <= 0.0f) continue;
        const int dc = cheb(anchor, e.pos);
        nearest = std::min(nearest, dc);
        if (dc <= enemy_reach(e) + 1) ++divers;
        // All nearby roles prioritise the same diver; deterministic identity breaks ties.
        const int score = (dc <= enemy_reach(e) + 1 ? 20000 : 0) - dc * 1000 - static_cast<int>(e.hp) - std::max(0, e.index);
        if (score > best) { best = score; focus = &e; }
    }
    if (!focus || nearest > 7) return false;
    int support = carry ? 0 : 1;
    for (const auto& a : ctx.allies)
        if (!a.channeling && a.range <= 1 && cheb(a.pos, anchor) <= 4) ++support;
    if (carry && nearest > kit().attack_range && divers == 0) return false;
    if (!carry && nearest > 4) return false;
    const bool losing = (divers >= support + 2 && power_ratio(ctx, 6) < 0.9f) ||
                        (role_carry_hp_ < 0.30f && nearest <= 4) || ctx.hp_frac() < 0.25f;
    if (losing) role_retreat_until_ = ctx.round + 5;
    if (cfg::role_trace && ctx.round % 20 == 0)
        MB_LOG("ROLE r%d k%d near%d divers%d cover%d retreat%d\n", ctx.round, static_cast<int>(kit().type), nearest, divers, support, ctx.round <= role_retreat_until_);
    if (ctx.round <= role_retreat_until_)
    {
        publish(-1, static_cast<int>(SlotStatus::idle));
        why_ = "role-disengage";
        // Use the same home rally direction for every role, preferring safety
        // over distance. Melee can retaliate without spending its walk.
        if (!carry) fight_retreat_counters(ctx, acts, true);
        use_support(ctx, acts, true);
        const auto* home = World::get().spawn_field(true);
        auto score = [&](vec2 p) {
            const int d = World::distance(home, p, World::get().ally_spawn_center);
            return -role_risk(ctx, p) * 10 - d * 200;
        };
        if (cambc::self().can_move() && step_best(score, score(ctx.pos)))
        { acts.moved = true; ctx.refresh_self(); }
        // If an escape is blocked, retain the established dash/recall logic.
        if (!acts.moved) return retreat(ctx, acts);
        return true;
    }
    if (carry)
    {
        const int danger_now = role_risk(ctx, ctx.pos);
        bool immediate = false;
        for (const auto& e : ctx.enemies)
            if (cheb(ctx.pos, e.pos) <= e.range + 1 ||
                (support == 0 && cheb(ctx.pos, e.pos) <= enemy_reach(e))) immediate = true;
        const bool lethal = focus->hp <= ctx.strength && cheb(ctx.pos, focus->pos) <= kit().attack_range;
        // Ranged movement and basics share an allowance: move BEFORE attacking only
        // when contact risk demands it. Otherwise hold range and spend the attack.
        if (immediate && !lethal && cambc::self().can_move())
        {
            auto score = [&](vec2 p) {
                int cover = 0;
                for (const auto& a : ctx.allies)
                    if (a.range <= 1 && !a.channeling && cheb(a.pos, p) <= 3 && cheb(a.pos, focus->pos) < cheb(p, focus->pos)) ++cover;
                const int range = cheb(p, focus->pos);
                return -role_risk(ctx, p) * 10 + std::min(range, kit().attack_range + 1) * 100 + cover * 100 - cheb(p, World::get().ally_spawn_center);
            };
            if (nearest <= 2 && !acts.cast && cambc::self().can_cast())
            {
                const auto abilities = cambc::self().abilities();
                for (int i = 0; i < 2 && !acts.moved; ++i)
                {
                    const auto& slot = kit().slot[i];
                    if (slot.kind != model::AbilityKind::dash || abilities[static_cast<std::size_t>(i)].cooldown() > 0) continue;
                    vec2 best_tile = ctx.pos;
                    int best_score = score(ctx.pos);
                    for (auto p : dash_landings(ctx.pos, static_cast<int>(slot.range)))
                        if (score(p) > best_score) { best_score = score(p); best_tile = p; }
                    if (best_tile != ctx.pos && role_use("role carry dash", [&] { return abilities[static_cast<std::size_t>(i)].use(best_tile); }))
                    { acts.cast = true; acts.moved = true; invalidate_obstacles(); ctx.refresh_self(); }
                }
            }
            if (!acts.moved && step_best(score, score(ctx.pos))) { acts.moved = true; ctx.refresh_self(); }
        }
        use_support(ctx, acts, danger_now > 0);
        fight_enemies(ctx, acts, false, focus); // no gap-closing or solo initiation
        publish(target_, static_cast<int>(SlotStatus::engaging));
        why_ = "role-kite";
        return acts.moved || acts.cast || acts.attacked;
    }
    // Finisher attacks are allowed only inside the carry's protection radius.
    if (kit().type == cambc::champion_type::vendetta)
    {
        const ChampView* lethal = nullptr;
        for (const auto& e : ctx.enemies)
            if (e.hp > 0 && e.hp <= ctx.strength && cheb(e.pos, ctx.pos) <= 2 && cheb(e.pos, anchor) <= 4 &&
                (!lethal || e.hp < lethal->hp)) lethal = &e;
        if (lethal) focus = lethal;
    }
    // Heart's area-stun dash is a peel tool: land beside the carry's diver,
    // not beyond the protection leash to initiate an unrelated fight.
    if (guard_type(kit().type) && nearest <= 3 && !acts.cast && cambc::self().can_cast())
    {
        const auto abilities = cambc::self().abilities();
        for (int i = 0; i < 2 && !acts.cast; ++i)
        {
            const auto& slot = kit().slot[i];
            if (slot.kind != model::AbilityKind::dash || slot.duration <= 0 || abilities[static_cast<std::size_t>(i)].cooldown() > 0) continue;
            vec2 best_tile = ctx.pos;
            int best_distance = 100;
            for (auto p : dash_landings(ctx.pos, static_cast<int>(slot.range)))
                if (cheb(p, anchor) <= 3 && cheb(p, focus->pos) <= static_cast<int>(slot.radius) &&
                    role_risk(ctx, p) <= role_risk(ctx, ctx.pos) + 3000 && cheb(p, focus->pos) < best_distance)
                { best_tile = p; best_distance = cheb(p, focus->pos); }
            if (best_distance < 100 && role_use("role peel dash", [&] { return abilities[static_cast<std::size_t>(i)].use(best_tile); }))
            { acts.cast = true; acts.moved = true; invalidate_obstacles(); ctx.refresh_self(); }
        }
    }
    use_support(ctx, acts, enemy_threat_at(ctx, ctx.pos) > 0.0f);
    fight_enemies(ctx, acts, false, focus);
    if (cambc::self().can_move())
    {
        const bool peel = cheb(focus->pos, anchor) <= enemy_reach(*focus) + 2;
        auto score = [&](vec2 p) {
            const int leash = cheb(p, anchor);
            const int to_enemy = cheb(p, focus->pos);
            // Intercept a diver while keeping a retreat path to the carry. Do not
            // launch a chase across the map because the local sim says favourable.
            return -std::max(0, leash - 3) * 5000 - to_enemy * (peel ? 600 : 100) -
                   static_cast<int>(camp_threat_at(ctx, p) * 20.0f) - std::max(0, leash - 1) * 50;
        };
        if (step_best(score, score(ctx.pos))) { acts.moved = true; ctx.refresh_self(); }
    }
    fight_enemies(ctx, acts, false, focus);
    publish(target_, static_cast<int>(SlotStatus::engaging));
    why_ = "role-peel";
    return true;
}

bool Brain::handle_role_guard(Ctx& ctx, TurnActions& acts)
{
    if (!guard_type(kit().type) || ctx.on_spawn || ctx.hp_frac() < 0.5f || capturing_) return false;
    // One bodyguard only, after health and banking handlers. Other champions farm
    // normally unless the combat handler needs them; this is not an all-game ball.
    if (ctx.round - role_carry_seen_ > 6 || role_carry_channel_)
    {
        role_wait_since_ = -1;
        return false;
    }
    const int distance = cheb(ctx.pos, role_carry_pos_);
    if (distance > 10) return false; // no unsupported cross-map recovery chase
    if (distance > 3)
    {
        auto score = [&](vec2 p) { return -cheb(p, role_carry_pos_) * 1000 - role_risk(ctx, p); };
        if (step_best(score, score(ctx.pos))) { acts.moved = true; ctx.refresh_self(); }
        publish(role_carry_group_, static_cast<int>(SlotStatus::engaging));
        why_ = "role-follow";
        role_wait_since_ = -1;
        return acts.moved;
    }
    if (role_carry_group_ >= 0 && role_carry_group_ < static_cast<int>(World::get().groups.size()))
    {
        const auto st = Knowledge::get().groups[static_cast<std::size_t>(role_carry_group_)].status;
        if (st == GroupStatus::alive)
        {
            if (target_ != role_carry_group_)
            {
                engaged_ = false;
                staged_since_ = -1;
                progress_best_ = 1 << 20;
                progress_round_ = ctx.round;
            }
            target_ = role_carry_group_;
            chosen_round_ = ctx.round;
            role_wait_since_ = -1;
            return false; // normal farm/camp logic supplies attacks, spells and staging
        }
        if (st == GroupStatus::reward)
        {
            if (role_wait_since_ < 0) role_wait_since_ = ctx.round;
            if (ctx.round - role_wait_since_ <= 8)
            {
                leave_camp_tiles(ctx, acts);
                use_support(ctx, acts, false);
                publish(-1, static_cast<int>(SlotStatus::idle));
                why_ = "role-capture-cover";
                return true;
            }
        }
    }
    role_wait_since_ = -1;
    return false;
}
} // namespace mb
