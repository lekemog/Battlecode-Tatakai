// SUBMISSION NOTE (v25m, 2026-10-25 09:31 UTC)
// v25k + siege-bot 5-pick draft (Vendetta, Vesper, Ryth, Tavi, Marcella) on maps without a per-map draft. Bench 482/560 +3700 (v25k 468 +3512). Sparring vs Marcus 29/80 (v25k 25), vs siege 16/80 (v25k 11). Guard: revert to v25k if ranked worse.
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
