# Replay analysis tools

These scripts read `.repl26a` replays downloaded from the platform (one zip per match). The replays only exist in the binary engine format, so `extract.mjs` loads each one into the visualiser's own wasm engine, steps through it, and writes one omniscient snapshot per round to JSON. Replays don't store team names: you have to note which team is which yourself.

## One-time setup: get the visualiser assets
`cambc view` serves the visualiser. Its JS and wasm files are what the extractor runs.
```
cambc view some/replay.repl26a --port 7026 &      # leave it running
mkdir -p vis/assets && cd vis/assets
curl -s http://127.0.0.1:7026/ | grep -o 'assets/index-[^"]*\.js'   # find the entry file
curl -sO http://127.0.0.1:7026/assets/<index-file>.js
for f in $(grep -o '\./[A-Za-z0-9_.-]*\.js' <index-file>.js | sort -u | sed 's|\./||'); do curl -sO http://127.0.0.1:7026/assets/$f; done
curl -s http://127.0.0.1:7026/assets/v0_0_3-zaIi77qe.wasm -o v0_0_3.wasm   # names are in the index file
```
`extract.mjs` imports `PanelChrome-DDwagTqG.js` by name. With SDK 2.2.4 the hash is this one; on a newer SDK, update the filename and check the export letters (`P` header, `F` full snapshot, `T` omniscient perspective).

## Pipeline
```
# replays/<match-id>/replay.repl26a (unzip each download into its own folder)
for d in replays/*/; do node tools/replay/extract.mjs vis/assets $d/replay.repl26a json/$(basename $d).json; done
python3 tools/replay/mapmatch.py replays json      # json/maps.json
python3 tools/replay/analyze.py json               # per-team rows -> json/teams.json
python3 tools/replay/captures.py json              # every camp capture: who, how many champions, gems
python3 tools/replay/solo.py json rows corners     # HP lost by a lone champion clearing a group
python3 tools/replay/deaths.py json                # where, and against whom, champions die
```
It takes about 3 s per replay. The per-round JSON is large (15–30 MB per match), so keep it out of git.

## Decoded fields
- Group `state`: 1 is awake, 2 is being captured (`captureTeam` is set), and 3 is captured or asleep.
- Event kinds (`events[i][1]`): 2 capture, 4 move, 5 attack, 6 cast, 11 recall, 12 submit gems, 13 shop, 14 place ward, 18 gems submitted, 20 altar lock, 21 teleport, 25 sell.
- Champion `type`: 0 Ryth, 1 Vesper, 2 Vendetta, 3 Cassi, 4 Issac, 5 Stellar, 6 Prism, 7 Marcella, 8 Willow, 9 Ren, 10 Varg, 11 Tavi, 12 HeartOfRuin.
- Champion `items` is 42 counts in the order Monster, Power, Durability, Treasure, Jungle, Home, Bruiser. Each family has Shard/Emblem × Strength/Focus/Health.
- `header.outcome`: 1 means team 0 won and 2 means team 1 won.
