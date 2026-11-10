// SUBMISSION NOTE (Claude for Leke, 2026-11-10): v71a = v61j (submission 245) + (1) opening phase before r200: gem weight x0.3 (gold first) and
// hazard threshold 0.12; (2) Heart's stun dash on camps when one full hit is worth it (camp_dash_bar 0.9, was 1.5: top-six Hearts cast it 10.5 times
// per 100 rounds, ours 4.8). Local (128 maps x 2 sides, 0 faults): v71a 139-117 vs v61j and 138-118 vs v70b (dash only); v70b 144-112 vs v61j
// (Heart: monster damage +22%, gems +32%); v66i (opening only) 141-115 vs v61j. Panels to beat: UK 245 = 12/45 (242 = 14); top ten 245 = 2/50.
// Fallback: re-upload bots/v61j.
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
