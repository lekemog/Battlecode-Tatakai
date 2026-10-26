// SUBMISSION NOTE (v25k, 2026-10-25 01:49 UTC)
// v24z + siege-style item build (idea from public MathCosine/siege README, re-implemented): ranged open Treasure, melee Monster, then Jungle Health, Durability Health, then Bruiser of main stat for good (was Jungle/Power/Durability/Power + Power). Ryth tank build unchanged. Bench 468/560 +3512 (live level 458 +3138). Sparring vs Marcus bot 25/80 (v24z 17), vs siege bot 11/80 (v24z 5). Guard: revert to v24z if ranked/scrims worse.
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
