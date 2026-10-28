#include <cambc.h>
#include "draft.h"
#include <algorithm>
#include <array>
#include <vector>

// Draft coach. Picks are revealed one at a time and both teams may take the same champion,
// so the draft is about our own composition, adjusted to what the enemy has shown so far.
//
// Base composition (what the strongest ladder teams converge on): Ren (frontline, retaliation,
// stun), Stellar (burst + area), Cassi & Issac (two bodies for one pick), Ryth (tank, area
// stun), then Varg or Tavi.
// Counters:
//   * enemy took Cassi & Issac -> prefer Tavi over Varg: a 2.2x focus stun-burst deletes
//     Cassi, and Issac dies with her.
//   * enemy is stun-heavy (3+ stunners) -> Marcella (immune to stuns) as a late pick.
namespace {
using C = cambc::champion_draft;

bool stunner(C c) {
    return c == C::tavi || c == C::ren || c == C::ryth || c == C::prism || c == C::cassi_and_issac || c == C::marcella;
}

struct MapPlan {
    bool ready = false;
    bool pack = true;
    bool wolf_packs = false;   // most gem income from groups of 3+ wolves: Varg's splash hits them all
};

// The map analysis runs once, on the first draft turn (which has 10x fuel); later picks
// only read the cached result, so no pick can run out of fuel and be randomised.
MapPlan& map_plan() {
    static MapPlan plan;
    if (plan.ready) return plan;
    double solo_gems = 0, pack_gems = 0, wolf_gems = 0, all_gems = 0;
    for (const auto& g : cambc::map::camp_groups()) {
        double hp = 0, str = 0;
        bool monolith = false;
        int wolves = 0;
        for (auto c : g.camps()) {
            if (c.kind() == cambc::camp_type::wolf) ++wolves;
            switch (c.kind()) {
            case cambc::camp_type::wolf: hp += 1350; str += 20; break;
            case cambc::camp_type::elk: hp += 2400; str += 60; break;
            case cambc::camp_type::monolith: hp += 20000; str += 200; monolith = true; break;
            default: hp += 500; break;
            }
        }
        if (g.gem_value() == 0 || monolith) continue;
        bool solo = str <= 0 || str * (hp / 60.0) * .6 < 800 * .6;
        const double rate = g.gem_value() * 60.0 / std::max(30, g.max_respawn_timer());
        all_gems += rate;
        if (wolves >= 3) wolf_gems += rate;
        (solo ? solo_gems : pack_gems) += g.gem_value() * 60.0 / std::max(30, g.max_respawn_timer());
    }
    plan.pack = pack_gems > 0 && pack_gems > solo_gems;
    plan.wolf_packs = all_gems > 0 && wolf_gems >= all_gems * .5;
    plan.ready = true;
    return plan;
}
}

void play_draft() {
    const auto& plan = map_plan();
    const auto ours = cambc::draft::current_draft(cambc::team::ally);
    const auto theirs = cambc::draft::current_draft(cambc::team::enemy);
    auto has = [](const auto& list, C c) { return std::find(list.begin(), list.end(), c) != list.end(); };

    int enemy_stunners = 0;
    for (auto c : theirs) if (stunner(c)) ++enemy_stunners;

    std::vector<C> order;
    if (cambc::draft::team_size() <= 3) order = {C::varg, C::vesper_vale, C::ryth, C::stellar, C::ren};   // v23r: engine 1.0.2 nerfed Stellar (750->650 HP, 85->70 focus); ladder since 06:00: Vesper 56%, Ryth 52%, Stellar 48%   // v21l: C&I in 3-picks (two bodies for one pick; every strong public bot does this)
    else order = {C::ryth, C::varg, C::vesper_vale, C::vendetta, C::ren, C::cassi_and_issac, C::stellar};   // v23r: post-1.0.2 meta (Vesper 56%, Vendetta 53%, Ryth 52%; Stellar/C&I 48%)   // v22p: elite post-patch 5-6 pick core (ryth, C&I, stellar, ren, varg) - 4 of 10 elite eight/fracture games
    // v24p: per-map draft. Vesper/Willow-led orders lost clearly fewer bench games (7 opponents, of 14) on quadrants
    // 7->4, reverse_spiral 5->3, fracture 5->3, contest 2->0 (but more on shortcut, gold_rush, expanse). Map data is
    // readable during the draft; width, height, altars and camp groups identify these maps in the 35-map pool.
    {
        static int vw = -1;
        if (vw < 0) {
            vw = 0;
            try {
                const int W = cambc::map::width(), H = cambc::map::height(), A = static_cast<int>(cambc::map::altars().count());
                int G = 0; for (auto g : cambc::map::camp_groups()) { (void)g; ++G; }
                const int fp[][4] = {{45,45,4,21},{30,30,2,14},{61,71,3,28},{50,50,2,14}};
                for (auto& f : fp) if (f[0]==W && f[1]==H && f[2]==A && f[3]==G) vw = 1;
            } catch (const cambc::error&) {}
        }
        if (vw == 1) {
            if (cambc::draft::team_size() <= 3) order = {C::vesper_vale, C::varg, C::ryth, C::willow, C::ren};
            else order = {C::vesper_vale, C::ryth, C::varg, C::vendetta, C::willow, C::ren, C::cassi_and_issac};
        }
    }
    if (cambc::draft::team_size() <= 3) order = {C::stellar, C::heart_of_ruin, C::ren, C::cassi_and_issac, C::ryth};   // DIAG v24q: Fish draft
    else order = {C::stellar, C::heart_of_ruin, C::ren, C::cassi_and_issac, C::ryth, C::varg, C::vesper_vale};
    for (C c : {C::marcella, C::prism, C::vendetta, C::willow, C::vesper_vale}) order.push_back(c);

    std::array<std::uint8_t, 16> memo{};
    memo[0] = 'P'; memo[1] = '9'; memo[2] = plan.pack;
    cambc::draft_memory = memo;
    for (auto c : order)
        if (!has(ours, c)) { cambc::draft::pick(c); return; }
}
