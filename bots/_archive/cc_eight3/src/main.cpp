// SUBMISSION NOTE (v20o, 2026-10-19 14:51 UTC)
// #30: Ryth replaces Tavi in the draft (opponents' core, Ryth in 50/60 of their games). Built on v19n; v20n's contest and eight changes both failed scrim acceptance and are dropped. Local all-map bench 67/102 vs v19n 66/102.
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
