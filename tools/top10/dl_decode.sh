#!/bin/bash
S=$1;ID=$2;A=$(ls -d /root/.cache/cambc/assets/*/visualiser/assets)
[ -f $S/rep/$ID.json ] && exit 0
mkdir -p $S/rep/$ID; cambc matches download $ID -o $S/rep/$ID/b.zip >/dev/null 2>&1
cd $S/rep/$ID && python3 -c "import zipfile;z=zipfile.ZipFile('b.zip');z.extractall('.')" && cd /tmp && node /home/user/BattlecodeConversation/tools/replay/extract3.mjs $A $S/rep/$ID/replay.repl26a $S/rep/$ID.json >/dev/null 2>&1; echo $ID done
