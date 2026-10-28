// SUBMISSION NOTE (v20p, 2026-10-19 15:51 UTC)
// Contest gold race: farm the four central 105-gold groups (either side of centre), skip far 35-gold edge singles. Vs teams at our rank, ranked contest is 3/27; they hold 38% of champion-time at the central groups vs our 13% and reach ~3x our gold by r600. Local: central time 18%->61%, opponent gold @600 1663->1298, wins 10/12 vs 8/12. v20o (Ryth draft) paused so contest is measured cleanly on v19n.
// END NOTE
// Dispatch draft and gameplay; a failed turn is logged and still yields.
#include <cambc.h>
#include <iostream>
#include "bot.h"
#include "draft.h"

int main() {
    Bot bot;
    while (true) {
        try {
            if (cambc::is_draft())
                play_draft();
            else
                bot.play_turn();
        } catch (const std::exception& error) {
            std::cout << "bot error: " << error.what() << std::endl;
        } catch (...) {
            std::cout << "bot error: unknown exception" << std::endl;
        }

        cambc::end_turn();
    }
}
