// SUBMISSION NOTE (Claude for Leke, 2026-11-10): v66i = v61j (submission 245) + an opening phase (rounds before 200): the gem weight is
// multiplied by 0.3 (gold first: it compounds through items) and the hazard alarm threshold is 0.12 instead of 0.2.
// Local vs v61j (128 maps x 2 sides): 141-115, margin +44, 0 faults. Related settings: x0.3 alone 144-112, x0.6 alone 137-119, x0.3 to r150 143-113,
// x0.1 137-119, x0.6 to r350 126-130; caution alone 127-129. Panels to beat: UK 245 = 12/45 (242 = 14); top ten 245 = 2/50.
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
