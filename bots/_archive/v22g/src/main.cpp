// SUBMISSION NOTE (v21p, 2026-10-20 06:26 UTC)
// v21m + out-of-reach camp fix (expanse Varg stuck on a chest 2 tiles away). Bench 343/420 vs v21m 337; ranked v21m expanse 0/4. Stop rule <45% after 30 -> v21m
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
