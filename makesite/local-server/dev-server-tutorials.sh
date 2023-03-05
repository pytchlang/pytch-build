#!/bin/bash

cd_or_fail() { cd "$1" || exit 1; }

# shellcheck disable=SC1091
. "$PYTCH_REPO_BASE"/pytch-build/.venv/bin/activate || {
    echo Could not activate pytch-build venv
    sleep 60
    exit 1
}

cd_or_fail "$PYTCH_REPO_BASE"/pytch-tutorials

echo Generating tutorials layer
pytchbuild-gather-tutorials --index-source=RECIPES_TIP -o /tmp/pytch-tutorials.zip
mkdir -p site-layer
cd_or_fail site-layer
unzip -qo /tmp/pytch-tutorials.zip

echo Serving tutorial layer from "$(pwd)"

python "$PYTCH_LOCAL_SERVER_DIR"/cors_server.py 8125

# Keep the shell process running in case of error, so tmux doesn't
# discard the window before we can read the error message.
sleep 60
