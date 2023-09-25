#!/bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

cd ./keymap-drawer/

CONFIG=./config.yaml

keymap -c $CONFIG \
    parse \
    -z ../config/corne.keymap \
    > ./corne.yaml

keymap -c $CONFIG \
    draw \
    ./corne.yaml \
    > ./corne.svg

cd - >/dev/null
