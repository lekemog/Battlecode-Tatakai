#!/bin/bash
# fullbench.sh POOLFILE LABEL BOT [BOT...] -> 7-opponent bench of each bot on the pool, appended to data/p5_bench.txt
P=$1;L=$2;shift 2
cd /home/claude
for b in "$@"; do
  echo "== $b $L" >> data/p5_bench.txt
  MAPS=$(cat $P) JOBS=2 python3 -I tools/gauntlet.py $b x_daniel8,x_de41h4,h_mohnish,h_deysag,h_vatsal,h_photon,h_apex 2>&1 | grep -E "TOTAL|GAUNTLET" >> data/p5_bench.txt
done
