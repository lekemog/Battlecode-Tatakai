// SUBMISSION NOTE (v20d, 2026-10-19 03:03 UTC)
// #25 packs: 3-champion pack drops the elk x1.5 clear penalty on the central 48s (small 6-altar map only). Local packs 13/16 (+158) vs v19n 8/14 (+10). All other maps byte-identical to v19n.
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
