// SUBMISSION NOTE (v22f, 2026-10-20 12:45 UTC)
// Patch 3.0: v21p + gold weight 1.0 (post-patch ranked losses: gold@600 1767 vs 2702; games now go ~1700 rounds, gold decides fights and the tiebreak). 3.0 bench 307/420 vs v21p 299, both sets up. Stop rule <45% after 30 -> v21p
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
