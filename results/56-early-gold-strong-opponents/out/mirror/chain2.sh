#!/bin/bash
cd "$(dirname "$0")"
for c in "$@"; do echo "$(date) start $c" >> chain2.log; ./mir.sh $c v50e1 >> chain2.log 2>&1; echo "$(date) done $c" >> chain2.log; done
