# T3 (#40) re-check on the current engine: rows deadlock mechanism (v24z vs kurians-t3-spawnfix, 4 opponents x both
# sides) plus corners and boss_battle controls. Runs games, decodes them with the newest visualiser assets that contain
# the engine, and prints spawnblock.py mechanism numbers and results.
# usage (from the repo root): powershell -File tools/t3engine103.ps1 MAPDIR OUTDIR
param([string]$MapDir, [string]$Out)
# 'Continue': in Windows PowerShell 5.1 a native tool's stderr warning (cambc's SDK notice) becomes an error record,
# which 'Stop' would turn into a crash. Results are checked from the replays instead.
$ErrorActionPreference = 'Continue'
$py = 'C:\Users\Kurians Biju\AppData\Local\Python\pythoncore-3.14-64\python.exe'
$root = (Get-Location).Path
if (Test-Path $Out) { Remove-Item -Recurse -Force $Out }
New-Item -ItemType Directory $Out | Out-Null
$q = [char]34
$rows = Join-Path $MapDir '00rows.map26a'; $corners = Join-Path $MapDir '00corners.map26a'; $boss = Join-Path $MapDir '01boss-battle.map26a'
$lines = @()
foreach ($bot in 'v24z', 'kurians-t3-spawnfix') {
    foreach ($opp in 'v24c', 'fz_solo', 'cc_contest', 'starter-cpp') {
        $lines += "$q$root/bots/$bot$q $q$root/bots/$opp$q $q$rows$q $q$Out/rows__${bot}__${opp}__0.repl26a$q"
        $lines += "$q$root/bots/$opp$q $q$root/bots/$bot$q $q$rows$q $q$Out/rows__${bot}__${opp}__1.repl26a$q"
    }
}
foreach ($m in @(@('corners', $corners), @('boss', $boss))) {
    $lines += "$q$root/bots/kurians-t3-spawnfix$q $q$root/bots/v24z$q $q$($m[1])$q $q$Out/$($m[0])__kurians-t3-spawnfix__v24z__0.repl26a$q"
    $lines += "$q$root/bots/v24z$q $q$root/bots/kurians-t3-spawnfix$q $q$($m[1])$q $q$Out/$($m[0])__kurians-t3-spawnfix__v24z__1.repl26a$q"
    $lines += "$q$root/bots/v24z$q $q$root/bots/v24z$q $q$($m[1])$q $q$Out/$($m[0])__v24z__v24z__0.repl26a$q"
}
($lines -join "`n").Replace('\', '/') | Set-Content -Encoding ascii (Join-Path $Out 'm.txt')
cambc run-batch (Join-Path $Out 'm.txt') --jobs 4 2>&1 | Out-Null
$assets = Get-ChildItem "$env:LOCALAPPDATA\cambc\assets" -Directory | Where-Object { Get-ChildItem (Join-Path $_.FullName 'visualiser\assets') -Filter 'v1_0_3-*.wasm' -ErrorAction SilentlyContinue } |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
$a = Join-Path $assets.FullName 'visualiser\assets'
$versions = @{}
foreach ($f in Get-ChildItem $Out -Filter *.repl26a) {
    $x = Join-Path $Out $f.BaseName; New-Item -ItemType Directory -Force $x | Out-Null
    tar -xf $f.FullName -C $x
    $o = node tools/replay/extract3.mjs $a (Join-Path $x 'replay.repl26a') (Join-Path $Out "$($f.BaseName).json") 2>&1 | Out-String
    if ($o -match '(v\d+_\d+_\d+)') { $versions[$matches[1]] = 1 + [int]$versions[$matches[1]] }
}
"engine versions decoded: " + (($versions.GetEnumerator() | ForEach-Object { "$($_.Key) x$($_.Value)" }) -join ', ')
& $py -c @"
import json,glob,os,sys
sys.path.insert(0,'tools')
from spawnblock import analyse
out=r'$Out'
for p in sorted(glob.glob(os.path.join(out,'*.json'))):
    n=os.path.basename(p)[:-5]; mp,bot,opp,side=n.split('__'); side=int(side)
    d=json.load(open(p,encoding='utf-8')); R=[x for x in d['rounds'] if x['phase']!=12]; L=R[-1]
    g=L['submittedGems']; gold=[sum(c['earnedGold'] for c in L['champions'] if c['team']==t) for t in (0,1)]
    win=g[side]>g[1-side] or (g[side]==g[1-side] and gold[side]>gold[1-side])
    m=analyse(p,side)
    print(f"{mp:7} {bot:20} vs {opp:12} side {side} {'WIN ' if win else 'loss'} {g[side]:>4}-{g[1-side]:<4} | due_blocked {m['due_blocked']:>4} worst {m['worst_block'][0]:>4}r g{m['worst_block'][1]} | respawns {m['respawns']:>3} max delay {m['max_delay']:>4} total {m['total_delay']:>5} | stuck>=10r {len(m['stuck_10'])}"+(f" {m['stuck_10'][:2]}" if m['stuck_10'] else ''))
"@
