#!/bin/bash

mydir="$(dirname "$0")"

tmux new-session -s pytchdev "$mydir"/dev-server-pieces.sh
