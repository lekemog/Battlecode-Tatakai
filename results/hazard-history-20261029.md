# v50c hazard-history candidate

Parent source: 2d93a142df388db48596f82842cf7cca47809cec, bots/v50c. New folder: bots/v50c-hazard-history. Unchanged files reuse exact parent blobs.

Confirmed logic defect: modulo-4 HP samples have no timestamp. A sample written at r4 is incorrectly interpreted as r8 when read at r11 after an observation gap. Sample health 1000 and current health 600 produces a spurious +0.4 loss feature (max HP 1000). The hazard weight on that feature is +1.15225, so stale data can alter retreat decisions. No claim this caused a particular observed match loss.

Fix: exact round stamps; missing r-3 sample contributes zero. Clear history and disengage commitment while dead. Preserve signed healing and every feature value during uninterrupted observations. No weight/threshold retuning or banking/economy changes.

Validation: g++ C++20 with -Wall -Wextra -Werror and AddressSanitizer/UndefinedBehaviorSanitizer; ASAN_OPTIONS=detect_leaks=0 required because LeakSanitizer cannot inspect /proc in this environment. Passed stale-slot reproducer, reset, signed healing, 10,000 continuous rounds and 10,000 sparse rounds. Run from repository root: g++ -I. -std=c++20 -Wall -Wextra -Werror -fsanitize=address,undefined tests/test_hazard_history.cpp -o /tmp/hazard-test && ASAN_OPTIONS=detect_leaks=0 /tmp/hazard-test

Match-test blocker: cambc 4.0.0 installed and project/SDK sources initialized, but required wasi-sdk 33.0 download from official GitHub release fails with Connection refused. No WASI build or local engine matches completed. A native syntax check requires -fpermissive for SDK naming accepted by Clang; this is not a platform build.

Next test gate: compile with official WASI SDK, compare unchanged v50c and this candidate against all seven bench opponents, both sides, on the same 40 maps, then held-out current-engine scrims. The old bench README names engine 1.0.3; use engine 2.0.0 for comparability with the observed games. Do not deploy without match evidence.

Other proposed solutions remain unvalidated: carrier-relative gate planning with progress timeout (#45); bag-sensitive escape routing (#46); opening camp value/clear time allocation (#47). Do not bundle them with this correction. Compiler access blocks evaluating their gameplay effect as well.
