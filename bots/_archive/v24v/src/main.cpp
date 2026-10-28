// SUBMISSION NOTE (v24v, 2026-10-21 18:44 UTC)
// v24u + GPT opponent-response (fixed-caution arm, Claude-tuned gates) only on split and corners. 37-map 7-opp bench 430/518 (v24u 426); split losses 5->1 of 14 in two separate runs. Guard <40% after 30 -> v24u
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
