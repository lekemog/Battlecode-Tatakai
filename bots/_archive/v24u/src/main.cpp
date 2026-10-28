// SUBMISSION NOTE (v24u, 2026-10-21 17:37 UTC)
// v24p + per-map draft: Varg-first/Willow 5-pick on rows and rushbait_v2 (losses vs 7 bench opponents 5->1 and 6->4 of 14; only those maps change). Projected 7-opp bench 402/490 (v24p 396). New maps gem_fields/gemfight fingerprinted, no rule collisions. Guard <40% after 30 -> v24p
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
