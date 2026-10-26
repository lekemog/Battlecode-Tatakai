// SUBMISSION NOTE (v24p, 2026-10-21 17:09 UTC)
// v24n + per-map draft: Vesper/Willow-led order on quadrants, reverse_spiral, fracture, contest (map read during draft). Full 7-opp bench 396/490 margin +3137 (v24n 387 +3012); only those 4 maps changed: quadrants 7->4, reverse_spiral 5->3, fracture 5->3, contest 2->0 losses. Guard <40% after 30 -> v24n
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
