#!/bin/bash

cd_or_fail() { cd "$1" || exit 1; }

# Use 'true' from PATH instead of shell builtin
enable -n true

# shellcheck disable=SC1091
. "$PYTCH_REPO_BASE"/pytch-build/.venv/bin/activate || {
    echo Could not activate pytch-build venv
    sleep 60
    exit 1
}

cd_or_fail "$PYTCH_REPO_BASE"/pytch-tutorials

if [ -z "$PYTCH_IN_PROGRESS_TUTORIAL" ]; then
    echo "PYTCH_IN_PROGRESS_TUTORIAL not set; not watching any tutorial/code"

    # Keep this script running, to stop the tmux pane from vanishing:
    while true; do
        sleep 60
    done
fi

echo "Watching tutorial $PYTCH_IN_PROGRESS_TUTORIAL"

pytchbuild-watch "$PYTCH_IN_PROGRESS_TUTORIAL"

# Keep the shell process running in case of error, so tmux doesn't
# discard the window before we can read the error message.
sleep 60
