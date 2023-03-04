#!/bin/bash

cd_or_fail() { cd "$1" || exit 1; }

media_distdir="$PYTCH_REPO_BASE"/pytch-medialib/dist
mkdir -p "$media_distdir"
cd_or_fail "$media_distdir"

# shellcheck disable=SC1091
. "$PYTCH_REPO_BASE"/pytch-build/.venv/bin/activate || {
    echo Could not activate pytch-build venv
    sleep 60
    exit 1
}

echo Generating media library contribution from tutorials
pytchbuild-gather-asset-media \
    --repository-path="$PYTCH_REPO_BASE"/pytch-tutorials \
    --output-directory=.

echo Serving media library from "$(pwd)"

python3 "$PYTCH_LOCAL_SERVER_DIR"/cors_server.py 8127

# Keep the shell process running in case of error, so tmux doesn't
# discard the window before we can read the error message.
sleep 60
