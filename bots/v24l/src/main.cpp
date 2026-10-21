// SUBMISSION NOTE (v24k, 2026-10-21 15:24 UTC)
// v24i + pack farming forced on contest (fingerprint 50x50, 2 altars, 14 groups, 34 camps). Contest vs 7 bench opponents: 12/14 (v24i 8/14; always-pack diag 12/14). All other maps unchanged. Guard <40% after 30 -> v24i
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
