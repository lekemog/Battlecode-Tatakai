// SUBMISSION NOTE (v20q, 2026-10-19 21:08 UTC)
// Bounded trial: v20p (contest central gold) + eight: carriers below 85% HP recall to heal before the altar (#32 fight study: we engage altar fights at 74-76% HP vs their 83-84%; lose 916 vs 731 HP per fight). Local eight 6/8 vs v19n 1/8, deaths 9.2 vs 15.1. Map-gated; guard: overall <45% after 30 games -> v19n.
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
