// SUBMISSION NOTE (v20e, 2026-10-19 03:19 UTC)
// #25: v20d (packs elk fix) + corners: squad 3 of 3 sweeps single camps only. Map-gated changes, so packs and corners are read separately in the scrims; other 15 maps = v19n. Local corners 12/16 (+106) vs v19n 11/14 (+121): neutral.
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
