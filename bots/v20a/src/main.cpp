// SUBMISSION NOTE (v20a, 2026-10-19 02:28 UTC)
// #25 test: v19n + corners solo farming (big-map rule from 70) + packs two squads. Local corners margin +180 vs +121; packs equal; other 15 maps byte-identical to v19n (control for the scrim A/B).
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
