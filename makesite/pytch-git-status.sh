#!/bin/bash

THIS_DIR=$(dirname "$0")
export PYTCH_REPOS_BASE=$(realpath "$THIS_DIR"/../..)

(
    cd "$PYTCH_REPOS_BASE"
    for x in pytch-*; do
        (
            cd "$x"
            echo
            tput bold
            echo ------------------------------------------------------------------------
            echo
            echo $x
            echo
            tput sgr0
            git status
        )
    done
)
