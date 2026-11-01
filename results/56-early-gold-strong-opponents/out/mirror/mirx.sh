#!/bin/bash
# mir.sh CAND [BASE]: resumable paired mirror, CAND vs BASE on 70 maps, both sides. Waits for any other batch to finish first.
C=$1; B=${2:-v50d}; P=/tmp/claude-0/-home-user-BattlecodeConversation/efdc7f3e-edfb-5016-b385-eb414f18c8fe/scratchpad/m56
cd $P
for x in $C $B; do rm -rf bots/$x; cp -r /home/user/BattlecodeConversation/bots/$x bots/; rm -rf bots/$x/.cambc; done
O=$P/mirx_${C}_$B; mkdir -p $O
: > $O/manifest.txt
while read m; do
  for pr in "$C $B" "$B $C"; do set -- $pr
    [ -s $O/${m}_$1_$2.json ] || echo "$P/bots/$1 $P/bots/$2 $P/maps/$m.map26a $O/${m}_$1_$2.repl26a --statistics $O/${m}_$1_$2.json --json" >> $O/manifest.txt
  done
done < xall.txt
if [ -s $O/manifest.txt ]; then
  while [ "$(pgrep -f "^cambc run-batch" | wc -l)" -ge 2 ]; do sleep 15; done
  cambc run-batch $O/manifest.txt --jobs 3 --release --json --timeout 900 --log-limit 600000 > $O/batch.log 2>&1
fi
rm -f $O/*.repl26a
python3 -I $P/an.py $C $B $O > $P/resx_${C}_$B.txt 2>&1
head -3 $P/resx_${C}_$B.txt | cut -c1-400
