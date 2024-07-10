#!/bin/bash -e

THIS_DIR=$(dirname "$0")
PYTCH_REPOS_BASE=$(realpath "$THIS_DIR"/../..)
export PYTCH_REPOS_BASE

(
    cd "$PYTCH_REPOS_BASE"
    for x in pytch-*; do
        [ -d "$x" ] && (
            cd "$x"
            echo
            tput bold
            echo ------------------------------------------------------------------------
            printf "%-16s  %s\n" "$x" "$(git rev-parse HEAD)"
            echo
            tput sgr0
            git status
        )
    done
)

echo
