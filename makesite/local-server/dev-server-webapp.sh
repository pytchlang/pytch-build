#!/bin/bash

cd_or_fail() { cd "$1" || exit 1; }

cd_or_fail "$PYTCH_REPO_BASE"/pytch-webapp
npm start

# Keep the shell process running in case of error, so tmux doesn't
# discard the window before we can read the error message.
sleep 60
