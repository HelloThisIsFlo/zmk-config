#!/bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

TMPDIR=tmpfirmware
mkdir $TMPDIR
gh run download -n firmware -D $TMPDIR

cp $TMPDIR/*left*.uf2 /Volumes/NICENANO/

rm -rf $TMPDIR

cd - >/dev/null
