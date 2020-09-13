#!/bin/bash

if [ -z "$SOURCE_REPO" ]; then
    echo "need SOURCE_REPO env to be set"
    exit 1
fi

if [ -z "$SOURCE_BRANCH" ]; then
    echo "need SOURCE_BRANCH env to be set"
    exit 1
fi

WORKDIR=$(mktemp -d -t pytch-tmp-XXXXXXXXXXXX)
REPODIR="$WORKDIR"/repo

ZIPFILE_BASENAME=vm-layer.zip

git clone --quiet --depth 1 "$SOURCE_REPO" "$REPODIR" -b "$SOURCE_BRANCH"

(
    cd "$REPODIR"
    npm install
    npm run build

    SKULPT_ABS_DIR="$WORKDIR"/skulpt
    mkdir "$SKULPT_ABS_DIR"

    (
        cd dist
        cp --target-directory="$SKULPT_ABS_DIR" \
           skulpt.min.js \
           skulpt.min.js.map \
           skulpt-stdlib.js
    )
)

(
    cd "$WORKDIR"
    zip -r "$ZIPFILE_BASENAME" skulpt
)

echo ________LAYER_ZIPFILE________ "$WORKDIR"/"$ZIPFILE_BASENAME"
