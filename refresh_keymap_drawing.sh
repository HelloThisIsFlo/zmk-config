#!/bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

cd ./keymap-drawer/

mv ./chocofi_keymap.yaml ./chocofi_keymap.prev.yaml

keymap -c ./config.yaml \
    parse \
    -b ./chocofi_keymap.prev.yaml \
    -z ../config/corne.keymap \
    > ./chocofi_keymap.yaml

rm ./chocofi_keymap.prev.yaml

keymap draw \
    ./chocofi_keymap.yaml \
    > ./chocofi_keymap.svg


cd - >/dev/null
