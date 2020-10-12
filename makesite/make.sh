#!/bin/bash

if [ $# -lt 2 ]; then
    echo "usage: make.sh SOURCE-BRANCHNAME DEPLOY-BASE-URL"
    exit 1
fi

if [ "$2" = "${2#/}" ]; then
    echo "DEPLOY-BASE-URL should be absolute, i.e., start with a '/' character"
    exit 1
fi

if [ -z "$PYTCH_REPOS_BASE" ]; then
    echo "need PYTCH_REPOS_BASE env to be set"
    exit 1
fi

MAKESITE_DIR=$(dirname "$0")

WORKDIR=$(mktemp -d -t pytch-tmp-XXXXXXXXXXXX)

env SOURCE_REPO="$PYTCH_REPOS_BASE"/pytch-tutorials \
    "$MAKESITE_DIR"/tutorials-layer.sh \
    > "$WORKDIR"/tutorials-layer.out \
    2> "$WORKDIR"/tutorials-layer.err &

env SOURCE_REPO="$PYTCH_REPOS_BASE"/pytch-vm \
    SOURCE_BRANCH="$1" \
    "$MAKESITE_DIR"/vm-layer.sh \
    > "$WORKDIR"/vm-layer.out \
    2> "$WORKDIR"/vm-layer.err &

env SOURCE_REPO="$PYTCH_REPOS_BASE"/pytch-webapp \
    SOURCE_BRANCH="$1" \
    DEPLOY_BASE_URL="$2" \
    "$MAKESITE_DIR"/webapp-layer.sh \
    > "$WORKDIR"/webapp-layer.out \
    2> "$WORKDIR"/webapp-layer.err &

wait

ZIPFILE_STEM=$(basename "$2")
ZIPFILE_PATH="$WORKDIR"/"$ZIPFILE_STEM".zip

grep ________LAYER_ZIPFILE________ "$WORKDIR"/*.out \
    | python "$MAKESITE_DIR"/merge_zipfiles.py \
             --out-path-prefix="${2#/}" \
             "$ZIPFILE_PATH"

echo "$ZIPFILE_PATH"
