// kurians-t3-rowsfarm (branch team/kurians/t3-contest-rows, not submitted): kurians-t3-spawnfix + on rows only (fingerprint
// 50x50, 2 altars, 9 groups, 54 camps) one champion farms the harmless gold-only flank group in parallel. Issue #40, T3.
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
