// SUBMISSION NOTE (v19f, 2026-10-18 19:36 UTC)
// Earlier first items (shop-recall at 110 gold before r250): on the identical 75 top-100 weak-map games 10 wins vs v18x 6 (corners 2, collision 3, stampede 5).
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
