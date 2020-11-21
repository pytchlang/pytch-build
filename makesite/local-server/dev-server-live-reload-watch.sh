#!/bin/bash

. "$PYTCH_REPO_BASE"/pytch-build/venv/bin/activate
cd "$PYTCH_REPO_BASE"/pytch-tutorials

if [ -z "$PYTCH_IN_PROGRESS_TUTORIAL" ]; then
    echo "PYTCH_IN_PROGRESS_TUTORIAL not set; not watching any tutorial/code"

    # Keep this script running, to stop the tmux pane from vanishing:
    while /bin/true; do
        sleep 60
    done
fi

echo "Watching tutorial $PYTCH_IN_PROGRESS_TUTORIAL"

pytchbuild-watch "$PYTCH_IN_PROGRESS_TUTORIAL" || sleep 10
