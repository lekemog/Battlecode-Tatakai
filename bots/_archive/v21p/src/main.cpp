// SUBMISSION NOTE (v21m, 2026-10-20 04:33 UTC)
// v21h + whole-cycle camp cost + C&I in 3-pick drafts (new-pool bench 337/420 vs v21h 310; v21h ranked 25-15). Stop rule <45% after 30 -> v21h
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
