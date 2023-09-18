#!/bin/bash
set -eo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"


if [ "$1" == "left" ]; then
    echo "Flashing Left side"
    TOFLASH='left'
elif [ "$1" == "right" ]; then
    echo "Flashing Right side"
    TOFLASH='right'
else
    echo "Invalid argument. Please provide either 'left' or 'right'"
    exit 1
fi
TMPDIR=tmpfirmware

rm -rf $TMPDIR
mkdir $TMPDIR
gh run download -n firmware -D $TMPDIR

cp $TMPDIR/*${TOFLASH}*.uf2 /Volumes/NICENANO/

rm -rf $TMPDIR

cd - >/dev/null
