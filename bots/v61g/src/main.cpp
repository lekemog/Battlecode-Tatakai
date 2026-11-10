// SUBMISSION NOTE (Claude for Leke, 2026-11-10): v61g = v61b (submission 242) + (1) the chooser's per-evaluation fuel reserve scales with
// group size, (2) above 48 groups the chooser's bound uses straight-line distance and respawning groups beyond max_respawn_wait are
// dropped before the evaluation loop, (3) gem-starved maps (winning gems / whole-game gem output > 0.5) multiply the gem weight.
// Evidence (local vs v61b): 04gem_caverns 1006-252 and 1003-231 (was 245-210 at r2000); 03one_gem 205-0 and 222-0; all maps 135-121, 0 faults.
// Ranked before: 04gem_caverns 0/12, 03one_gem 0/11. Gate: UK panel pinned to uk_i not below 14/45, deaths not worse. Revert target: 242.
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
