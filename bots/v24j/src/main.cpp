// SUBMISSION NOTE (v24i, 2026-10-21 15:13 UTC)
// v24c + per-map farming mode: solo (bolder) on yellow_brick_road, ambush, rushbait_v2, fracture, elk_arena by map fingerprint (7-opp bench: solo lost clearly fewer there); leave contested captures of >=20-camp groups after 12 rounds. 7-opp bench 378/490 (v24c 366): screen 84/140, held-out 294/350 (v24c 81, 285); yellow brick losses 11->4, fracture 8->5, ambush 5->2. Guard <40% after 30 -> v24c
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
