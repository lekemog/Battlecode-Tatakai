#pragma once
// Map features for the learned draft (v54m). Computed once in the draft turn (100x fuel), from the immutable map only,
// so training (tools/draftml) and play use the same numbers. Order is fixed: add features only at the end.
#include <array>
#include <cambc.h>
#include <cmath>

namespace mb {

inline constexpr int kMapFeatures = 22;

inline std::array<float, kMapFeatures> compute_map_features()
{
    using namespace cambc;
    std::array<float, kMapFeatures> f{};
    const int w = map::width(), h = map::height();
    const auto& walls = map::walls();
    const auto& holes = map::holes();
    const auto& bushes = map::bushes();
    const auto& altars = map::altars();
    const auto& ours = map::spawn_region(team::ally);
    const auto& theirs = map::spawn_region(team::enemy);
    const float area = static_cast<float>(w * h);
    // Distance fields from each spawn, camps passable (they die) and walls/holes/altars blocked.
    bitboard blocked = walls | holes | altars;
    distance_field from_us, from_them;
    bitboard v1, v2;
    from_us.compute_with_expansion_count(blocked & ~ours, ours, v1);
    from_them.compute_with_expansion_count(blocked & ~theirs, theirs, v2);
    auto walk_to = [&](const distance_field& d, const bitboard& target) {
        int best = 1 << 20;
        for (int x = 0; x < w; ++x)
            for (int y = 0; y < h; ++y)
            {
                const vec2 p{ x, y };
                if (!target.is_set(p)) continue;
                for (int dx = -1; dx <= 1; ++dx)
                    for (int dy = -1; dy <= 1; ++dy)
                    {
                        const vec2 n{ x + dx, y + dy };
                        if (!map::is_in_bounds(n)) continue;
                        const auto v = d.get(n);
                        if (v != distance_field::unreachable) best = std::min(best, static_cast<int>(v));
                    }
            }
        return best >= (1 << 20) ? 300 : best;
    };
    const int spawn_walk = walk_to(from_us, theirs);
    const int altar_walk = walk_to(from_us, altars);
    int free_tiles = 0;
    for (int x = 0; x < w; ++x)
        for (int y = 0; y < h; ++y)
            if (!blocked.is_set(vec2{ x, y })) ++free_tiles;

    float gems = 0, gold = 0, wolves = 0, elks = 0, gemc = 0, goldc = 0, mono = 0, golem = 0, neigh = 0, members = 0;
    float near_gems = 0, mid_gems = 0, walk_sum = 0, groups = 0, biggest = 0;
    for (const auto& g : map::camp_groups())
    {
        groups += 1;
        gems += static_cast<float>(g.gem_value());
        gold += static_cast<float>(g.gold_value());
        biggest = std::max(biggest, static_cast<float>(g.gem_value()));
        const auto camps = g.camps();
        int du = 1 << 20, dt = 1 << 20;
        for (std::size_t i = 0; i < camps.size(); ++i)
        {
            const auto& c = camps[i];
            members += 1;
            wolves += c.is_wolf(); elks += c.is_elk(); gemc += c.is_gem_cluster(); goldc += c.is_gold_cluster();
            mono += c.is_monolith(); golem += c.is_golem();
            for (std::size_t j = 0; j < camps.size(); ++j)
                if (i != j && c.spawn_position().chebyshev_distance(camps[j].spawn_position()) <= 1) neigh += 1;
            const auto a = from_us.get(c.spawn_position()), b = from_them.get(c.spawn_position());
            if (a != distance_field::unreachable) du = std::min(du, static_cast<int>(a));
            if (b != distance_field::unreachable) dt = std::min(dt, static_cast<int>(b));
        }
        if (du < (1 << 20) && dt < (1 << 20))
        {
            walk_sum += static_cast<float>(du);
            if (du + 4 < dt) near_gems += static_cast<float>(g.gem_value());
            else if (std::abs(du - dt) <= 4) mid_gems += static_cast<float>(g.gem_value());
        }
    }
    const float team = static_cast<float>(draft::team_size());
    f[0] = team;
    f[1] = area / 1000.0f;
    f[2] = static_cast<float>(free_tiles) / area;
    f[3] = static_cast<float>(holes.count()) / area;
    f[4] = static_cast<float>(bushes.count()) / area;
    f[5] = static_cast<float>(altars.count());
    f[6] = groups;
    f[7] = gems / 100.0f;
    f[8] = gold / 1000.0f;
    f[9] = gold > 0 ? gems / (gold / 10.0f) : 0.0f;
    f[10] = wolves; f[11] = elks; f[12] = gemc; f[13] = goldc; f[14] = mono; f[15] = golem;
    f[16] = members > 0 ? neigh / members : 0.0f;
    f[17] = static_cast<float>(spawn_walk) / 10.0f;
    f[18] = groups > 0 ? walk_sum / groups / 10.0f : 0.0f;
    f[19] = gems > 0 ? mid_gems / gems : 0.0f;
    f[20] = gems > 0 ? near_gems / gems : 0.0f;
    f[21] = static_cast<float>(altar_walk) / 10.0f;
    return f;
}

} // namespace mb
