#!/bin/bash
set -euo pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"


docker volume create --driver local -o o=bind -o type=none -o \
    device="$DIR" zmk-config

cd - >/dev/null
