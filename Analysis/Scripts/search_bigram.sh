#!/bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

bigram="$1"

cat Corpus.txt | grep "\w*$bigram\w*" -o | sort | uniq | grep --color=always "$bigram"

cd - >/dev/null
