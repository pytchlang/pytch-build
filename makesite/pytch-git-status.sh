#!/bin/bash

THIS_DIR=$(dirname "$0")
export PYTCH_REPOS_BASE=$(realpath "$THIS_DIR"/../..)

(
    cd "$PYTCH_REPOS_BASE"
    for x in pytch-*; do
        [ -d "$x" ] && (
            cd "$x"
            echo
            tput bold
            echo ------------------------------------------------------------------------
            echo
            printf "%-16s  %s\n" "$x" $(git rev-parse HEAD)
            echo
            tput sgr0
            git status
        )
    done
)

echo
