#pragma once
// v51p profiler (behaviour-neutral apart from the few fuel units each fuel() read costs): per champion it accumulates fuel by turn
// phase, fuel and turns by decision (mode/why), fuel gates that deferred work, and decision latency (bags waiting above the bank
// threshold, low-health turns not yet healing, first leave-spawn / fight / capture / bank round). Printed as P/D/G/L lines.
#include <cstdint>
#include <cstdio>
#include <cstring>
#include "config.h"
#include "util.h"

namespace mb::prof {

struct Acc { const char* a{}; const char* b{}; unsigned long long sum{}, max{}, n{}, aux{}; };

struct State
{
    Acc phase[16]; int nphase{};
    Acc dec[64]; int ndec{};
    Acc gate[24]; int ngate{};
    unsigned long long turns{}, fuel_sum{}, fuel_max{}, heavy{}, suspended{}, start_sum{}, start_min{ ~0ull }, early{};
    // current-turn decision
    bool valid{}; const char* mode{}; const char* why{}; int gems{}; float hp{}; bool on_spawn{}; int round{}; int kind{};
    // latency
    unsigned long long bag_turns{}, bag_wait{}, bag_wait_pvp{}, bag_wait_farm{}, bag_gems_wait{}, lowhp_turns{}, lowhp_wait{}, lowhp_wait_fight{}, lowhp_wait_travel{}, lowhp_wait_spawnfar{};
    int first_off{ -1 }, first_fight{ -1 }, first_capture{ -1 }, first_bank{ -1 };
    int last_print{ -1 };
};
inline State& S() { static State s; return s; }

inline Acc* find(Acc* arr, int& n, int cap, const char* a, const char* b)
{
    for (int i = 0; i < n; ++i)
        if (arr[i].a == a || (arr[i].a && std::strcmp(arr[i].a, a) == 0))
            if ((!b && !arr[i].b) || (b && arr[i].b && std::strcmp(arr[i].b, b) == 0)) return &arr[i];
    if (n >= cap) return nullptr;
    arr[n].a = a; arr[n].b = b;
    return &arr[n++];
}

inline void begin_turn() { if constexpr (cfg::profile) S().valid = false; }

// A fuel gate: records how often the work was reachable and how often fuel deferred it.
inline bool gate(const char* name, bool ok)
{
    if constexpr (cfg::profile)
    {
        auto& s = S();
        if (auto* g = find(s.gate, s.ngate, 24, name, nullptr)) { ++g->n; if (!ok) ++g->aux; }
    }
    return ok;
}

inline void note(const char* mode, const char* why, int gems, float hp_frac, bool on_spawn, int round, int kind, std::uint32_t bag, float recall_frac)
{
    if constexpr (cfg::profile)
    {
        auto& s = S();
        s.valid = true; s.mode = mode; s.why = why; s.gems = gems; s.hp = hp_frac; s.on_spawn = on_spawn; s.round = round; s.kind = kind;
        const bool tribute = std::strcmp(mode, "tribute") == 0, pvp = std::strcmp(mode, "pvp") == 0;
        if (!on_spawn && s.first_off < 0) s.first_off = round;
        if (s.first_fight < 0 && (pvp || std::strcmp(why, "fight") == 0 || std::strcmp(why, "fight-travel") == 0)) s.first_fight = round;
        if (s.first_capture < 0 && std::strcmp(mode, "capture") == 0) s.first_capture = round;
        if (s.first_bank < 0 && tribute) s.first_bank = round;
        if (gems >= static_cast<int>(bag))
        {
            ++s.bag_turns;
            if (!tribute)
            {
                ++s.bag_wait; s.bag_gems_wait += static_cast<unsigned>(gems);
                if (pvp) ++s.bag_wait_pvp; else if (std::strcmp(mode, "farm") == 0 || std::strcmp(mode, "capture") == 0) ++s.bag_wait_farm;
            }
        }
        if (!on_spawn && hp_frac < recall_frac)
        {
            ++s.lowhp_turns;
            if (std::strcmp(mode, "lowhp") != 0 && std::strcmp(mode, "heal") != 0 && !pvp)
            {
                ++s.lowhp_wait;
                if (std::strcmp(why, "fight") == 0 || std::strcmp(why, "fight-travel") == 0 || std::strcmp(mode, "capture") == 0) ++s.lowhp_wait_fight;
                else if (std::strcmp(why, "travel") == 0) ++s.lowhp_wait_travel;
            }
        }
    }
}

inline void print(int round)
{
    auto& s = S();
    if (s.turns == 0) return;
    const double t = static_cast<double>(s.turns);
    std::printf("P r%d k%d turns %llu fuel avg %.0f max %llu start_avg %.0f start_min %llu heavy60k %llu susp %llu early %llu |", round, s.kind, s.turns,
                static_cast<double>(s.fuel_sum) / t, s.fuel_max, static_cast<double>(s.start_sum) / t, s.start_min, s.heavy, s.suspended, s.early);
    for (int i = 0; i < s.nphase; ++i) std::printf(" %s=%.0f/%llu", s.phase[i].a, static_cast<double>(s.phase[i].sum) / t, s.phase[i].max);
    std::printf("\nG r%d k%d", round, s.kind);
    for (int i = 0; i < s.ngate; ++i) std::printf(" %s=%llu/%llu", s.gate[i].a, s.gate[i].aux, s.gate[i].n);
    std::printf("\nL r%d k%d first_off %d first_fight %d first_capture %d first_bank %d bag_turns %llu bag_wait %llu (pvp %llu farm %llu) bag_gems_wait %llu lowhp_turns %llu lowhp_wait %llu (fight %llu travel %llu)\n",
                round, s.kind, s.first_off, s.first_fight, s.first_capture, s.first_bank, s.bag_turns, s.bag_wait, s.bag_wait_pvp, s.bag_wait_farm, s.bag_gems_wait,
                s.lowhp_turns, s.lowhp_wait, s.lowhp_wait_fight, s.lowhp_wait_travel);
    std::printf("D r%d k%d", round, s.kind);
    for (int i = 0; i < s.ndec; ++i)
        if (s.dec[i].n * 200 >= s.turns)  // decisions with at least 0.5% of turns
            std::printf(" %s/%s:%llu:%.0f:%llu", s.dec[i].a, s.dec[i].b ? s.dec[i].b : "-", s.dec[i].n, static_cast<double>(s.dec[i].sum) / static_cast<double>(s.dec[i].n), s.dec[i].max);
    std::printf("\n");
}

template <class Trace>
inline void end_turn(const Trace& trace, int round)
{
    if constexpr (cfg::profile)
    {
        auto& s = S();
        const unsigned long long total = trace.start > trace.last ? trace.start - trace.last : 0;
        ++s.turns; s.fuel_sum += total; if (total > s.fuel_max) s.fuel_max = total;
        if (total > 60000) ++s.heavy;
        if (trace.suspended) ++s.suspended;
        s.start_sum += trace.start; if (trace.start < s.start_min) s.start_min = trace.start;
        for (int i = 0; i < trace.n; ++i)
            if (auto* a = find(s.phase, s.nphase, 16, trace.names[i], nullptr)) { a->sum += trace.used[i]; if (trace.used[i] > a->max) a->max = trace.used[i]; ++a->n; }
        const char* m = s.valid ? s.mode : "early-return"; const char* w = s.valid ? s.why : "-";
        if (!s.valid) ++s.early;
        if (auto* d = find(s.dec, s.ndec, 64, m, w)) { ++d->n; d->sum += total; if (total > d->max) d->max = total; }
        if (round > 0 && round % 250 == 0 && s.last_print != round) { s.last_print = round; print(round); }
        else if (round == 100 && s.last_print < 100) { s.last_print = 100; print(round); }
    }
}

} // namespace mb::prof
