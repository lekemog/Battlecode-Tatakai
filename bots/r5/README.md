# r5: release the opening pack after first contact

Based on v53i (submission 236); the only behavior change is to end escort and opening squad grouping at round 60 instead of 100. Combat, draft, shopping, and learned weights are unchanged. `knowledge.cpp` updates the nearby explanatory comment.

Engine 3.0.0, CLI 5.0.0, full current 128-map pool, both sides: **r5 133–123 v53i, 0 bot faults**. By round 600, r5 averaged 2504 vs 2457 earned gold, 436 vs 433 collected gems, 1.69 vs 1.69 kills, and 1.97 vs 2.01 deaths. This is a small local edge and requires testing against other opponent styles before platform activation.

The same suite gave r3 122–134 and r4 114–142 versus v53i. R3's map-size selector is retained only as an experiment because it was chosen on the tested maps.

Research: current-game public repositories [Ajayendra2705/cambridge-battlecode-2026a](https://github.com/Ajayendra2705/cambridge-battlecode-2026a), [coleseven/cambridge-battlebot](https://github.com/coleseven/cambridge-battlebot), [satvikmittal638/CamBattlecode-2026a](https://github.com/satvikmittal638/CamBattlecode-2026a), and [Ahmed-Abdul-Rahim/definetly-not-battlecode](https://github.com/Ahmed-Abdul-Rahim/definetly-not-battlecode). Their published results mostly predate engine 3.0.0; transfer hypotheses, not raw parameters. V53i already has a 94-weight learned layer. A targeted predictor of camp capture or short-horizon enemy reinforcement, trained and evaluated by whole-game map/opponent splits on current-patch replays, is the next ML experiment.
