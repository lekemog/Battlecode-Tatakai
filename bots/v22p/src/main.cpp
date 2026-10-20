// SUBMISSION NOTE (v22p, 2026-10-20 23:26 UTC)
// v22f + elite post-patch draft (Ryth, C&I, Stellar, Varg, Ren, Tavi for 4+ picks). 35-map bench: held-out 258 vs 251, tuning 250 vs 249, Daniel v8 30/70 = v22f. Guard <45% after 30 -> v22f
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
