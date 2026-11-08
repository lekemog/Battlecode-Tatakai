# Archive

`bots-v1-v41.tar.xz` holds 96 bot folders from the first six weeks (the `v7n`, `v9c`, `v25`-`v41` lines and the old `bots/_archive/` with the `v1x`-`v24x` versions): 1,747 files, 25 MB uncompressed, 0.1 MB packed (the versions are near-copies). Verified against git byte for byte before the loose folders were removed (8 Nov 2026).

Restore one folder:
```bash
tar -xJf archive/bots-v1-v41.tar.xz bots/v27i          # or any other folder name
```
Everything removed in the tidy is also still in git history: the last commit before it is `03b34544c02d0e9b501183f5d1f4a60759ceec9f` (`git show 03b34544:bots/v27i/src/bot.cpp`).
