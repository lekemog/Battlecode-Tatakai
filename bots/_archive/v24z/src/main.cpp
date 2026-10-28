// SUBMISSION NOTE (v24z, 2026-10-21 20:25 UTC)
// v24w + solo farming on the new map road_of_riches (40x40, 2 altars, 51 groups, 132 camps). 7-opp bench on it: 9/14 vs v24w 4/14 (margin -2173 -> +2582); other maps unchanged. Guard <40% after 30 -> v24w
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
