#!/bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

CONFIG=./config.yaml
KEYMAP=../config/corne.keymap

# Using local version until the main project is fixed
PATH=$PATH:$HOME/Library/Caches/pypoetry/virtualenvs/keymap-drawer-GuFs4spq-py3.10/bin

refresh_drawing() {
    echo "Refreshing drawing"
    keymap -c $CONFIG \
        parse \
        -z $KEYMAP \
        > ./corne.yaml

    keymap -c $CONFIG \
        draw \
        ./corne.yaml \
        > ./corne.svg
    echo "Refresh done!"
}

refresh_drawing
printf "\nWatching for changes on $CONFIG and $KEYMAP\n"
fswatch -0 $CONFIG $KEYMAP | while read -d "" modified_file
do
    echo "$(basename $modified_file) was modified"
    refresh_drawing
    printf "\nWatching for changes on $CONFIG and $KEYMAP\n"
done





cd - >/dev/null
