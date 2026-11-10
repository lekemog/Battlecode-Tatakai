# Bots

| Group | Folders | Use |
|---|---|---|
| **Live / baseline** | `v50h5e` (submission 226) | The bot on the ladder. Revert target. Always check `cambc submissions list` for what is actually live. |
| **Candidates (current line)** | `v51a` to `v51e2`, `v51p` (profiler) | New ideas on top of the live bot: `v51d` is the candidate being qualified; `v51e1` (Marcella Focus) and `v51e2` (health mix) are single-flag variants. |
| **Earlier live versions** | `v50a`, `v50b`, `v50c` (221), `v50d` (222), `v50e1` (223) | Fallbacks and history of the v50 line. |
| **Single-change experiments** | `v50e*`, `v50g*`, `v50h*`, `v50i*`, `v50j1`, `v50k*`, `v50q*`, `v50r*` | One idea each, mostly rejected; see the matching study in `results/`. |
| Top-10 gap candidates (10 Nov) | `v62care1`, `v62care2` (diagnostic), `v62tp1`, `v62tp2`, `v62tp3` | v53x plus adaptive careful mode or teleport-crystal shortcuts; results in `results/top10-gap-2026-11-10`. None passed the local gates; `v62tp3` is +4 (noise) and the panel candidate. |
| **Test opponents (never submit)** | `v50p1` to `v50p4` (early-pack bots), `v25u`, `v29e`, `v40a` | Stress and sparring partners. `v25u` / `v29e` are older-line references used by `tools/top10/`, `v40a` by `TESTING.md`. |
| **Tools** | `maprobe`, `starter-cpp` | Map probe and the official starter. |
| Archive | [`../archive/bots-v1-v41.tar.xz`](../archive/README.md) | 96 older folders (`v7n`, `v9c`, `v25*` to `v41*`, `_archive/`), verified byte for byte. |

Rules: one idea per folder, copied from the live bot with `rm -rf .cambc`, every change behind a `config.h` flag. Profiling builds are generated with `tools/lab/add_profiler.py`, not stored.
