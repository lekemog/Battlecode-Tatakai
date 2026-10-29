# Frozen map-robustness experiments

Work in progress: five fixed policies (unchanged v50c, timestamped hazard history, carrier-origin ring replanning every 16 rounds, danger banking at 10 gems, and all three combined). No thresholds changed after inspecting results.

Source baseline: `2d93a142df388db48596f82842cf7cca47809cec`, `bots/v50c`. The main branch still does not contain that baseline folder; obtain it from that commit. Verify every source hash in baseline-sha256.json, then run `python materialize_candidates.py /path/to/v50c /path/to/cambc-project`. All four reproduced candidates were verified byte-for-byte against tested sources. No copied build caches.

Current maps.zip contains all 70 active maps downloaded from the official platform on 29 October. The historical bench has 40 unique map layouts; 14 old names differ by hyphen/underscore, and the current pool has 30 genuinely new byte-distinct maps. Common layouts were unchanged byte-for-byte. Source-manifest.json records hashes.

The current 2,800-game design contains: five policies × 40 old maps × three frozen opponents × both sides (1,200); five policies × 30 new maps × the same three opponents × both sides (900); five policies × all 70 maps × unchanged v50c × both sides, including v50c self-play (700). Treat repeated deterministic games as paired cases, not independent evidence. Opponents x_de41h4/x_daniel8/h_mohnish are frozen repo bench sources; the latter is withheld from tuning. All builds use CLI 4.0.0, engine 2.0.0/build 85aa7167b44db7cea97509f55e997750520e33d644e9f4f90d6128c50eba1d21.

The initial baseline rapidly saturates the three old opponents; this is a regression screen, not a prediction of top-ten ladder performance. Do not select a winner from partial counts, compare different completed subsets, or deploy a candidate from these tests alone. Final completed evidence and map audit will be added when all runs finish.
