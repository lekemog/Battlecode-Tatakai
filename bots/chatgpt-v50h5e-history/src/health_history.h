#pragma once
#include <array>
#include <algorithm>
#include <cstddef>

namespace mb::hazard {
struct HealthHistory {
    std::array<float, 4> hp{};
    std::array<int, 4> round{{-1, -1, -1, -1}};
    void clear() noexcept { round.fill(-1); }
    void record(int at, float health) noexcept {
        if (at < 0) return;
        const auto slot = static_cast<std::size_t>(at) & 3u;
        hp[slot] = health;
        round[slot] = at;
    }
    float loss3(int at, float health, float max_health) const noexcept {
        if (at < 3) return 0.0f;
        const auto slot = static_cast<std::size_t>(at - 3) & 3u;
        if (round[slot] != at - 3) return 0.0f;
        return (hp[slot] - health) / std::max(1.0f, max_health);
    }
};
}
