#pragma once
#include <algorithm>
namespace mb::hazard {
struct HealthHistory {
    float hp[4]{};
    int rounds[4]{-1, -1, -1, -1};
    void clear() { for (int& r : rounds) r = -1; }
    void record(int round, float health) {
        hp[round % 4] = health;
        rounds[round % 4] = round;
    }
    float loss3(int round, float health, float max_health) const {
        if (round < 3) return 0.0f;
        const int slot = (round - 3) % 4;
        return rounds[slot] == round - 3
            ? (hp[slot] - health) / std::max(1.0f, max_health) : 0.0f;
    }
};
}
