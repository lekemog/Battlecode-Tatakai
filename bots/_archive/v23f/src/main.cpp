// SUBMISSION NOTE (v22w, 2026-10-21 01:07 UTC)
// v22p + Ryth health-tank build (elite contest replay: Ryth 10,600 HP soaks monolith). 35-map bench: Daniel v8 34/70 (v22p 30), held-out 273/350 (258), tuning 259/350 (250). Guard <45% after 30 -> v22p
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
