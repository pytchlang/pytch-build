#!/bin/bash

tmux set-option -g mouse on

PYTCH_REPO_BASE="$(realpath "$(dirname "$0")"/../../..)"
PYTCH_LOCAL_SERVER_DIR="$(realpath "$(dirname "$0")")"

tmux split-window -d -b -v \
     env \
     PYTCH_REPO_BASE="$PYTCH_REPO_BASE" \
     VITE_DEPLOY_BASE_URL="" \
     VITE_SKULPT_BASE=http://localhost:8124 \
     VITE_TUTORIALS_BASE=http://localhost:8125 \
     VITE_DEMOS_BASE=http://localhost:8126 \
     VITE_MEDIALIB_BASE=http://localhost:8127 \
     VITE_LESSON_SPECIMENS_BASE=http://localhost:8128 \
     VITE_LIVE_RELOAD_WEBSOCKET=yes \
     VITE_VERSION_TAG=local-development-build \
     "$PYTCH_LOCAL_SERVER_DIR"/dev-server-webapp.sh

tmux split-window -h \
     env \
     PYTCH_REPO_BASE="$PYTCH_REPO_BASE" \
     PYTCH_LOCAL_SERVER_DIR="$PYTCH_LOCAL_SERVER_DIR" \
     "$PYTCH_LOCAL_SERVER_DIR"/dev-server-tutorials.sh

tmux split-window -t 0 -h \
     env \
     PYTCH_REPO_BASE="$PYTCH_REPO_BASE" \
     PYTCH_IN_PROGRESS_TUTORIAL="$PYTCH_IN_PROGRESS_TUTORIAL" \
     "$PYTCH_LOCAL_SERVER_DIR"/dev-server-live-reload-watch.sh

tmux split-window -t 2 \
     env \
     PYTCH_REPO_BASE="$PYTCH_REPO_BASE" \
     PYTCH_LOCAL_SERVER_DIR="$PYTCH_LOCAL_SERVER_DIR" \
     "$PYTCH_LOCAL_SERVER_DIR"/dev-server-medialib.sh

tmux split-window -t 4 \
     env \
     PYTCH_REPO_BASE="$PYTCH_REPO_BASE" \
     PYTCH_LOCAL_SERVER_DIR="$PYTCH_LOCAL_SERVER_DIR" \
     "$PYTCH_LOCAL_SERVER_DIR"/dev-server-static-blobs.sh

exec \
     env \
     PYTCH_REPO_BASE="$PYTCH_REPO_BASE" \
     PYTCH_LOCAL_SERVER_DIR="$PYTCH_LOCAL_SERVER_DIR" \
     "$PYTCH_LOCAL_SERVER_DIR"/dev-server-skulpt.sh

# TODO: How to integrate the live-reload/push of tutorial content with
# the React App?
