#!/bin/bash

tmux set-option -g mouse on

PYTCH_REPO_BASE="$(realpath "$(dirname "$0")"/../../..)"
PYTCH_LOCAL_SERVER_DIR="$(realpath "$(dirname "$0")")"

tmux split-window -d -b -v \
     env \
     PYTCH_REPO_BASE="$PYTCH_REPO_BASE" \
     PUBLIC_URL="" \
     REACT_APP_DEPLOY_BASE_URL="" \
     REACT_APP_SKULPT_BASE=http://localhost:8124 \
     REACT_APP_TUTORIALS_BASE=http://localhost:8125 \
     REACT_APP_DEMOS_BASE=http://localhost:8126 \
     REACT_APP_ENABLE_LIVE_RELOAD_WEBSOCKET=yes \
     REACT_APP_VERSION_TAG=local-development-build \
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

exec \
     env \
     PYTCH_REPO_BASE="$PYTCH_REPO_BASE" \
     PYTCH_LOCAL_SERVER_DIR="$PYTCH_LOCAL_SERVER_DIR" \
     "$PYTCH_LOCAL_SERVER_DIR"/dev-server-skulpt.sh

# TODO: How to integrate the live-reload/push of tutorial content with
# the React App?
