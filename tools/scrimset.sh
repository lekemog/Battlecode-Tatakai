#!/bin/bash
# scrimset.sh LABEL -> queue 6 unranked groups vs ranks ~160-235 on a fixed 5-map set, wait, print results; group ids saved to data/scrimset_LABEL.txt
L=$1;O="62270180-b974-4f66-9bca-3ff6a25940c3 afdecb06-d440-4133-b536-4a712300f74d bd917cb0-38c7-4dd5-b431-014f8aa6b51a 561c0480-6779-4e88-8084-b3f3cf4f6daa fe852ad6-1ff3-4415-8c6b-0fbb65c4a9b8"
G=""
for t in $O; do g=$(cambc match-groups create $t --maps 00lanes,00quadrants,00eight,01starfish,00great_wall --sides a,b,a,b,a --json 2>&1 | python3 -c "import json,sys;d=json.loads(sys.stdin.read());print(d.get('groupId') or d.get('id'))"); G="$G $g"; done
echo $G > /home/claude/data/scrimset_$L.txt; echo GROUPS $G
/home/claude/tools/waitgroups.sh $G
