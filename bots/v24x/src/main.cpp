// SUBMISSION NOTE (v24w, 2026-10-21 19:11 UTC)
// v24v + solo farming on the two newest maps (lost_world 35x31, great_wall 50x40, by fingerprint). 7-opp bench on those maps: 18/28 vs v24v 8/28 (losses great_wall 12->5, lost_world 8->5); other maps unchanged. Guard <40% after 30 -> v24v
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
