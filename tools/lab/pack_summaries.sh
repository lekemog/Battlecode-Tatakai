#!/bin/bash
# pack_summaries.sh : gzip the raw match summaries a panel run downloads (results/panel/summaries/*.json -> .json.gz, about 6% of the size).
# Run it before committing panel results. Readers (tools/lab/census.py) accept both forms.
cd "$(dirname "${BASH_SOURCE[0]}")/../../results/panel/summaries" && gzip -9 -f ./*.json 2>/dev/null; ls | wc -l
