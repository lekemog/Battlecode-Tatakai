// SUBMISSION NOTE (v23r, 2026-10-21 09:01 UTC)
// Engine 1.0.2: v23m + post-Stellar-nerf draft (5-6 picks Ryth, Varg, Vesper, Vendetta, Ren, C&I; 3 picks Varg, Vesper, Ryth). Screen vs Daniel v8 + DE41H v4 (140 games, 35 maps): 80 vs v23m 57 vs v22w 51, margins positive. Guard <40% after 30 -> v23m
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
