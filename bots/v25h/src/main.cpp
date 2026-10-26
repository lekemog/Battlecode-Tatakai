// SUBMISSION NOTE (kurians-t3-spawnfix, 2026-10-22 11:22 UTC)
// Kurians' T3 fix (#40): v24z + step off a respawning group's spawn tile when none of its camps is visible (rows respawn deadlock: farmer froze 1055 rounds; 3 ranked rows losses). Monolith groups excluded. 7-opp 40-map bench 458/560 (= v24z level: 449 on the 39 shared maps vs v24w 448). Revert to v24z if ranked worse.
// END NOTE
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
