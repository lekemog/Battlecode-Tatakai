// SUBMISSION NOTE (v24n, 2026-10-21 16:21 UTC)
// v24k + per-map smaller banks (rows, pilgrimage, gold_rush, split) and bolder pack (shortcut, starvation), from 13-map 7-opponent benches. Full 7-opp bench 387/490 margin +3012 (v24i 378 +2713; v24k ~382). Guard <40% after 30 -> v24k
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
