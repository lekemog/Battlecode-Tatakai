// kurians-t3-spawnfix (branch team/kurians/t3-contest-rows, not submitted): v24z + a farmer standing ON a spawn tile of its
// non-monolith target group with none of the group's camps in sight steps to the ring beside it (an occupied spawn tile
// blocks the group's respawn: rows deadlock of up to 1438 rounds). Issue #40, T3.
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
