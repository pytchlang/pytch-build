#!/bin/bash

cd_or_fail() { cd "$1" || exit 1; }

: "${PYTCH_DEPLOYMENT_ID:?}"

BUILD_DIR="$(realpath "$(dirname "$0")")"
REPO_ROOT="$(realpath "$BUILD_DIR"/..)"

cd_or_fail "$REPO_ROOT"

# Previous script has already checked build requirements.

TUTORIALS_REPO_ROOT="$(realpath "$REPO_ROOT"/../pytch-tutorials)"
MEDIALIB_REPO_ROOT="$(realpath "$REPO_ROOT"/../pytch-medialib)"

# shellcheck disable=SC1091
source .venv/bin/activate

(
    cd_or_fail "$TUTORIALS_REPO_ROOT"

    pytchbuild-gather-asset-credits \
        --index-source=WORKING_DIRECTORY \
        --output-file="$MEDIALIB_REPO_ROOT/doc/source/user/tutorials.rst"
)
