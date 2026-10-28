// SUBMISSION NOTE (v20h, 2026-10-19 03:31 UTC)
// #25: v20e (corners sweep pair) + packs 2+1 squads (replaces v20d elk fix). Local packs behaviour: 8/8 wins, 48s 5.5/game (v19n 3.0), 44s kept 12.8, first tribute r48, gems@400 706 (v19n 692).
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
