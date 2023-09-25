#!/bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

cd ./keymap-drawer/

CONFIG=./config.yaml

keymap -c $CONFIG \
    parse \
    -z ../config/corne.keymap \
    > ./chocofi_keymap.yaml

keymap -c $CONFIG \
    draw \
    ./chocofi_keymap.yaml \
    > ./chocofi_keymap.svg

cd - >/dev/null
