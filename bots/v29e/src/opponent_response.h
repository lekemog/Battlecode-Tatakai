#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>

// Small online model, independent of the engine API. Each Bot instance owns its
// own observations. A score is an approach tendency, NOT a death probability.
namespace opponent_response {
constexpr int horizon = 4;
constexpr int capacity = 8;

struct Observation {
    unsigned id = 0;
    int distance = 0; // Chebyshev distance to this episode's fixed camp centre
    bool eligible = true; // false for stunned/channeling enemies
};

struct Estimate {
    double probability = .5;
    double evidence = 0;
    double pressure = 0;
};

struct Counts {
    unsigned started = 0, completed = 0, approached = 0, censored = 0;
};

struct Event {
    unsigned enemy = 0, start = 0, end = 0;
    int group = -1, band = 0, label = -1; // -1=censored, 0=no approach, 1=approach
    double predicted = .5, evidence = 0;
};

class Model {
    struct Belief {
        double yes = 0, no = 0;
        unsigned updated = 0;
        void decay(unsigned now) {
            if (now > updated) {
                const double retain = std::exp2(-static_cast<double>(now - updated) / 240.0);
                yes *= retain; no *= retain;
            }
            updated = now;
        }
    };
    struct Episode {
        bool active = false;
        int group = -1, distance = 0, band = 0, radius = 0;
        unsigned start = 0, last = 0;
        double predicted = .5, evidence = 0;
    };
    struct Profile {
        bool used = false;
        unsigned id = 0, next_start = 0;
        std::array<Belief, 2> belief{};
        Episode episode{};
    };
    std::array<Profile, capacity> profiles_{};
    Counts counts_{};
    std::array<Event, capacity> events_{};
    int event_count_ = 0;
    unsigned last_tick_ = 0;
    bool ticked_ = false;

    static int band_for(int distance, int radius) {
        const int gap = distance - radius;
        return gap <= 0 || gap > 7 ? -1 : gap <= 3 ? 0 : 1;
    }
    Profile* profile(unsigned id) {
        for (auto& p : profiles_) if (p.used && p.id == id) return &p;
        for (auto& p : profiles_) if (!p.used) { p.used = true; p.id = id; return &p; }
        return nullptr; // Never evict another enemy's history or mix identities.
    }
    void censor(Profile& p, unsigned now) {
        if (p.episode.active) {
            record(p, now, -1); ++counts_.censored; p.episode.active = false;
        }
        p.next_start = now + horizon;
    }
    void record(const Profile& p, unsigned now, int label) {
        const auto& e = p.episode;
        if (event_count_ < capacity)
            events_[event_count_++] = {p.id,e.start,now,e.group,e.band,label,e.predicted,e.evidence};
    }

public:
    const Counts& counts() const { return counts_; }
    int event_count() const { return event_count_; }
    const Event& event(int index) const { return events_[index]; }

    // Supply at most one snapshot per actual game round. Every negative needs
    // four consecutive observed transitions. Losing sight is censored, not calm.
    // A positive ends at the first observed approach within that horizon.
    void tick(unsigned now, int group, int radius,
              const Observation* obs, int count) {
        event_count_ = 0;
        if (ticked_ && now <= last_tick_) return;
        ticked_ = true; last_tick_ = now;
        count = std::clamp(count, 0, capacity);
        for (auto& p : profiles_) {
            if (!p.used || !p.episode.active) continue;
            const Observation* current = nullptr;
            for (int i = 0; i < count; ++i) if (obs[i].id == p.id) current = &obs[i];
            auto& e = p.episode;
            if (group < 0 || e.group != group || e.radius != radius ||
                now != e.last + 1 || !current || !current->eligible) {
                censor(p, now); continue;
            }
            e.last = now;
            const bool approached = current->distance <= radius ||
                                    current->distance <= e.distance - 2;
            if (approached || now - e.start == horizon) {
                record(p, now, approached ? 1 : 0);
                auto& b = p.belief[e.band]; b.decay(now);
                (approached ? b.yes : b.no) += 1.0;
                // Bound effective history; all later observations still matter.
                const double n = b.yes + b.no;
                if (n > 32) { b.yes *= 32 / n; b.no *= 32 / n; }
                ++counts_.completed;
                if (approached) ++counts_.approached;
                e.active = false; p.next_start = now + horizon;
            }
        }
        if (group < 0) return;
        for (int i = 0; i < count; ++i) {
            const auto& o = obs[i];
            const int band = band_for(o.distance, radius);
            if (!o.eligible || band < 0) continue;
            auto* p = profile(o.id);
            if (!p || p->episode.active || now < p->next_start) continue;
            const auto prior = estimate(o.id,o.distance,radius,now);
            p->episode = {true, group, o.distance, band, radius, now, now,prior.probability,prior.evidence};
            ++counts_.started;
        }
    }

    // Use only with a CURRENT visible enemy in the same distance band. No
    // extrapolation to hidden enemies, no model-based permission to ignore danger.
    Estimate estimate(unsigned id, int distance, int radius, unsigned now) const {
        const int band = band_for(distance, radius);
        if (band < 0) return {};
        for (const auto& p : profiles_) if (p.used && p.id == id) {
            auto b = p.belief[band]; b.decay(now);
            const double n = b.yes + b.no;
            const double probability = (1 + b.yes) / (2 + n); // Beta(1,1)
            const double pressure = n < 2 ? 0 :   // Claude tune: 3 -> 2 samples, n/(n+6) -> n/(n+3) (v1 never fired: 0 discounts in a full game)
                std::max(0.0, 2 * probability - 1) * n / (n + 3);
            return {probability, n, pressure};
        }
        return {};
    }

    static double multiplier(double pressure) {
        // Evidence can only modestly discount a camp, never ban it or declare
        // it safe. With no evidence the baseline score is unchanged.
        return 1.0 - .35 * std::clamp(pressure, 0.0, 1.0);   // Claude tune: cap 25% -> 35%
    }
};
} // namespace opponent_response
