// SUBMISSION NOTE (v19n, 2026-10-19 16:32 UTC)
// Stop experimenting on the live bot: ranked 13:00-16:30 UTC 28/65 (43%), rank 267. Back to plain v19n (~51% over 230 games); all further tests local-only until a change is clearly better.
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
