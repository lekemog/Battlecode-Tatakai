// SUBMISSION NOTE (v20l, 2026-10-19 09:46 UTC)
// #26 follow-up: frontliners Bruiser-Health replaces Jungle as first emblem, then v19n order. v20k (B,D,P,P) failed scrims: our deaths -30% but enemy deaths fell more, wins 4/60 vs v19n 8/60, gems@400 down on eight/elkring. v20l local focus maps 23/32 (v19n 20, v20k 22).
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
