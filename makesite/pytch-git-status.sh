#!/bin/bash

cd_or_fail() { cd "$1" || exit 1; }

THIS_DIR=$(dirname "$0")
PYTCH_REPOS_BASE=$(realpath "$THIS_DIR"/../..)
export PYTCH_REPOS_BASE

(
    cd_or_fail "$PYTCH_REPOS_BASE"
    for x in pytch-*; do
        [ -d "$x" ] && (
            cd_or_fail "$x"
            echo
            tput bold
            echo ------------------------------------------------------------------------
            echo
            printf "%-16s  %s\n" "$x" "$(git rev-parse HEAD)"
            echo
            tput sgr0
            git status
        )
    done
)

echo
