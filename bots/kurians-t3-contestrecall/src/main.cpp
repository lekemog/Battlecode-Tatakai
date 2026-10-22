// kurians-t3-contestrecall (branch team/kurians/t3-contest-rows, not submitted): kurians-t3-spawnfix + on contest only (forced_pack
// fingerprint) low-HP and shop recalls need no visible enemy within 9 tiles; otherwise walk out. Issue #40, T3.
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
