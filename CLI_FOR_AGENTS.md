# Linking the `cambc` CLI to your AI (Claude Code, ChatGPT, Codex, anything with a shell)

**Everyone on Tatakai may tweak the bot, test new versions and submit them**, once they've done the due diligence in section 5.
This page shows how to give your own AI agent the same tools main Claude uses: build, local games, panels and submissions.
Verified on 3 Nov 2026 in a Claude Code cloud session: `cambc` 4.0.0, engine 2.0.0, Linux x86_64.

## 1. Pick an environment your agent can run commands in
| Agent | Where it runs | What to check |
|---|---|---|
| Claude Code on the web / app (cloud session) | a Linux container | **Network access** must allow `2026a.battlecode.co.uk` and `github.com`: cloud environment menu in the session title bar → Edit → Network access (a broader level, or add both hosts under *Allowed domains* with *Allow package managers* ticked). Docs: https://code.claude.com/docs/en/cloud-environments#network-access |
| Claude Code CLI / desktop on your own machine | your machine | nothing special; Windows works (see the notes in issue #40: short `PROJ` path without spaces, `PYTHONUTF8=1`) |
| ChatGPT / Codex with a code sandbox | its sandbox | it needs outbound internet to the two hosts above; without it the agent can only read and edit code, and you run the commands yourself |

Test the network: `curl -sS -o /dev/null -w "%{http_code}\n" https://2026a.battlecode.co.uk/` should print `200`.

## 2. Install the CLI and the C++ toolchain
```bash
pip install cambc==4.0.0 && cambc --version     # must say cambc 4.0.0
```
The first `cambc run` downloads wasi-sdk, CMake and ninja. Behind a TLS-intercepting proxy (most cloud agents) it fails with `invalid peer certificate: UnknownIssuer`. Fetch them with curl instead (curl trusts the proxy's CA):
```bash
mkdir -p ~/.cache/cambc && cd ~/.cache/cambc
curl -sSL -o w.tgz https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-33/wasi-sdk-33.0-x86_64-linux.tar.gz
mkdir -p wasi-sdk-33 && tar xzf w.tgz -C wasi-sdk-33 --strip-components=1 && rm w.tgz
curl -sSL -o c.tgz https://github.com/Kitware/CMake/releases/download/v3.31.8/cmake-3.31.8-linux-x86_64.tar.gz
mkdir -p cmake-3.31.8-linux-x86_64 && tar xzf c.tgz -C cmake-3.31.8-linux-x86_64 --strip-components=1 && rm c.tgz
curl -sSL -o n.zip https://github.com/ninja-build/ninja/releases/download/v1.12.1/ninja-linux.zip
mkdir -p ninja-1.12.1-linux-x86_64 && python3 -c "import zipfile;zipfile.ZipFile('n.zip').extractall('ninja-1.12.1-linux-x86_64')" && chmod +x ninja-1.12.1-linux-x86_64/ninja && rm n.zip
```
If a future `cambc` asks for other versions, the error message names the exact URL and folder: download that one the same way.

## 3. Sign the agent in (needs a human, once a week)
```bash
nohup cambc login > login.out 2>&1 &   # background: it waits for approval
sleep 5; cat login.out                  # prints https://2026a.battlecode.co.uk/game/cli-login?code=...
```
The agent gives you the link. **You** open it while signed in to the team account and approve. The session lasts 7 days.
Check it: `cambc submissions list` (or `tools/lab/live_status.sh`). When it expires, every account command says `Sign in first with cambc login`; just repeat this step.
Never paste tokens into the repo or into issues.

## 4. Local lab (no account needed, about 5–30 s per game)
```bash
git clone https://github.com/lekemog/BattlecodeConversation && cd BattlecodeConversation
git checkout claude/vibrant-turing-rtpcwn          # the live v50 line
tools/lab/setup_lab.sh ~/lab v50h5e v50p1 <your-bot>   # project, 86 maps, bench bots, your bots
export PROJ=~/lab
cd $PROJ && cambc run bots/<your-bot> bots/v50h5e --map maps/00contest.map26a --release --json   # one game
cd - && JOBS=4 tools/lab/mirror.sh <your-bot> v50h5e      # 172 games vs the live bot, both sides
python3 -I tools/lab/bankstats.py <your-bot> $PROJ/mirror_<your-bot>_v50h5e   # banked, zero-bank, deaths
```
`TESTING.md` sections 3–4 say which local test fits which kind of change.

## 5. Due diligence before you submit (the only rules)
1. **Own folder** `bots/<you>-<idea>/`, copied from the live bot (`v50h5e` = #226), `rm -rf .cambc`; every change behind a `config.h` flag; your own branch (`team/<you>/<idea>`).
2. **Evidence + mechanism:** match IDs or local games that show the problem, and the code lines that cause it.
3. **Local tiers pass** for your change type (`TESTING.md` §3): smoke clean, bench no-regression, mirror (economy/banking) or `v50p1` early pack (fights/caution).
4. **Book the live slot:** add a row to `LIVE_SLOT.md` and post on the issue you work from. Scrims and panels play whatever is live, so overlapping tests corrupt each other.
5. **Submit or activate** (`tools/lab/submit_wait.sh`, `tools/lab/activate_wait.sh`), run the panel (`TESTING.md` §5), and log it in `SUBMISSIONS.md` with the evidence and the revert target.
6. **Restore** the previous version when you're done (`cambc submissions activate N`) unless your bot passed the panel gate (+4 wins over the two strong panels, deaths not worse). Close your `LIVE_SLOT.md` row.

## 6. A prompt you can paste into your AI
> You are working on team Tatakai's Cambridge Battlecode 2026a bot in https://github.com/lekemog/BattlecodeConversation (branch `claude/vibrant-turing-rtpcwn`). Read `CLI_FOR_AGENTS.md`, `TESTING.md` and `LIVE_SLOT.md` first. Set up `cambc` 4.0.0 as described (curl the toolchain if the download fails on certificates), run `cambc login` in the background and give me the approval link. Work only in a new `bots/<me>-<idea>/` folder copied from `bots/v50h5e`, on branch `team/<me>/<idea>`. My idea: <describe it>. Show evidence and the mechanism, run the local tests that `TESTING.md` §3 names for this kind of change, and report the numbers. Before any `cambc submit`, `submissions activate` or `match-groups create`, check and book `LIVE_SLOT.md`, and ask me. Restore the previous live version afterwards and log everything in `SUBMISSIONS.md`.
