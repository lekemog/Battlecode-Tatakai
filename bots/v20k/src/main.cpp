// SUBMISSION NOTE (v20k, 2026-10-19 07:56 UTC)
// #26: frontliners build Bruiser-Health then Durability-Health before Power (carries unchanged). Local focus maps (32 games vs fz_hunt/tank/herd, v18x): wins 22/32 vs v19n 20/32; max HP@300 +17-30% on every map; deaths down on contest/eight/monolith.
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
