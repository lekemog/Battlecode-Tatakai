// SUBMISSION NOTE (v20i, 2026-10-19 04:10 UTC)
// #25 role fixes: corners sweep pair never merges (local: 22s 0.4->9.6/game, 36s and 96s kept); packs pair on centre 48s + solo on home 44s (local centre time 8%->15%, 48s ~3->6.2; first tribute r63, slower). Scrim behaviour test.
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
