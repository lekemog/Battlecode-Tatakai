#!/bin/bash
# run1.sh A B MAP ROUNDS TAG -> decodes replay into an/TAG/dec.json
A=$1; B=$2; M=$3; R=$4; T=$5
cd /root/lab; rm -rf an/$T; mkdir -p an/$T
cambc run bots/$A bots/$B --map $M --release --json -o an/$T --rounds $R --statistics an/$T/s.json > an/$T/run.log 2>&1
f=$(ls an/$T/*.repl26a | head -1); unzip -o -q $f -d an/$T/z
node /home/user/BattlecodeConversation/tools/replay/extract5.mjs $(ls -d ~/.cache/cambc/assets/*/visualiser/assets | head -1) an/$T/z/replay.repl26a an/$T/dec.json >/dev/null 2>&1
