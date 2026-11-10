// SUBMISSION NOTE (Claude for Leke, 2026-11-10): v61j = v61i (submission 244) with the many-group test computed once per choose, so maps
// with at most 100 groups run the v61b chooser without extra per-group work (244 lost 01yellow_brick_road in both panels: 160 camps,
// fuel-critical). Keeps: chooser fixes above 100 groups (04gem_caverns) and the gem-starved map rule (03one_gem, 03ultrastarvation).
// Local vs v61b: all maps 127-129 (margin +3), 04gem_caverns 1003-266 and 1001-343, 03one_gem 221-0 and 214-0, 0 faults.
// Panels to compare: UK 242 = 14/45, 244 = 11/45; top ten 240 = 3/50, 244 = 2/50. Fallback: 242.
// Polaris v50e1: v50d + Prospector emblem replaces Treasure as the opener (cfg::p4_open 2)
// the bot entrypoint: dispatch draft or gameplay; any failed turn is logged and yields.
#include <cambc.h>
#include <cstdio>
#include <exception>
#include "brain.h"
#include "draft.h"
#include "config.h"
#include "util.h"

namespace mb {

namespace {
int log_lines = 0;
}

bool fuel_ok(std::uint64_t need) { return cambc::fuel_remaining() > need + cfg::fuel_reserve; }

bool log_allowed() { return ++log_lines <= 400; }

void FuelTrace::report(int round, std::uint64_t threshold) const
{
    const auto total = start > last ? start - last : 0;
    if (!suspended && total < threshold) return;
    if (!log_allowed()) return;
    std::printf("fuel r%d %s%s total %llu:", round, suspended ? "SUSPENDED in " : "", suspended ? suspended_in : "",
                static_cast<unsigned long long>(total));
    for (int i = 0; i < n; ++i) std::printf(" %s=%llu", names[i], static_cast<unsigned long long>(used[i]));
    std::printf("\n");
}

} // namespace mb

int main()
{
    mb::Brain* brain = nullptr;
    while (true)
    {
        try
        {
            if (cambc::is_draft())
                mb::play_draft();
            else
            {
                if (!brain) brain = new mb::Brain();
                brain->turn();
            }
        }
        catch (const std::exception& error)
        {
            // Killed during our own turn (retaliation after a basic attack): every later query on
            // ourselves raises, and nothing is left to do this turn (cfg::died_mid_turn_quiet).
            bool died = false;
            if constexpr (mb::cfg::died_mid_turn_quiet)
                if (!cambc::is_draft())
                    try { died = !cambc::self().is_alive(); } catch (...) { died = false; }
            if (died)
                MB_LOG("died mid-turn r%u\n", cambc::round_number());
            else
                MB_LOG("turn error r%u: %s\n", cambc::is_draft() ? 0u : cambc::round_number(), error.what());
        }
        catch (...)
        {
            MB_LOG("turn error: unknown exception\n");
        }
        cambc::end_turn();
    }
}
