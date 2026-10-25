// SUBMISSION NOTE (v25j, 2026-10-25 01:24 UTC)
// SCRIM TEST (Leke approved scrim-testing bench-failing fight changes, 25 Oct): v24z + fight threshold 0.9 (was 0.6). Local bench 438/560 (v24z-level 458) - bench opponents are weaker than ranked. Baseline v24z vs 5 mid-ladder teams on 5 maps: 5/25. Revert to v24z right after unless clearly better.
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
