// SUBMISSION NOTE (v20n, 2026-10-19 12:47 UTC)
// #27 contest disengage (from v20m) + #28 eight: carrier within 5 of the altar and not outnumbered finishes the deposit instead of retreating/evading. Map-gated separately. Local eight 6/12 vs v19n 3/12, deaths 8.4 vs 12.0, gems@400 439 vs 422.
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
