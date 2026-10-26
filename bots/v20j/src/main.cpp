// SUBMISSION NOTE (v20j, 2026-10-19 05:03 UTC)
// #25: corners-only change kept (v20i scrims: gems@400 484 vs v19n 450, deaths 3.4 vs 3.8, our 22s 6.0, their 22s 15.4 vs 19.7). Packs reverted to v19n: v20i packs first tribute r62 vs r39, deaths 2.8 vs 1.4, gems@400 513 vs 582.
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
