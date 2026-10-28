// SUBMISSION NOTE (v18x, 2026-10-18 15:05 UTC)
// Revert from v19b/v19c: on identical top-100 weak-map games v18x won 6, v19b 3, v19c 1 (the fight recalibration made us evade 17% of the time vs 10% and lost stampede races).
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
