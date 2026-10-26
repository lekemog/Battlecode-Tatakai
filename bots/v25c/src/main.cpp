// SUBMISSION NOTE (v25c, 2026-10-21 22:14 UTC)
// Scrim test: v24z + health item build for every champion (top-4 had 1700-3100 max HP vs our 900-1000 at r300-770). Revert to v24z unless scrims improve.
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
