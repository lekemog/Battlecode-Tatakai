// SUBMISSION NOTE (v24c, 2026-10-21 13:08 UTC)
// v23v + no banking while every altar submit tile is within 2 of a live monolith (boss battle: carriers stood by the monolith-ringed altar all game, 0 banked; now the pack kills the monoliths and banks). Boss battle vs DE41H/Mohnish/Apex: 0-0 x3 -> wins 1147-920, 1008-8, 1612-0. Screen 81/140 +263 (v23v 80 +234); held-out 285/350 (v23v 283). Guard <40% after 30 -> v23v
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
