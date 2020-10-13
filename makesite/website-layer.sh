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

ZIPFILE_BASENAME=website-layer.zip

git clone --quiet --depth 1 "$SOURCE_REPO" "$REPODIR" -b "$SOURCE_BRANCH"

(
    cd "$REPODIR"

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements_dev.txt

    bin/make-cleanly.sh

    mkdir "$WORKDIR"/zip-content
    mv build/html "$WORKDIR"/zip-content/doc
    (
        cd "$WORKDIR"/zip-content
        find doc -type d -print0 | xargs -0 chmod 755
        find doc -type f -print0 | xargs -0 chmod 644
        zip -r ../"$ZIPFILE_BASENAME" doc
    )
)

echo ________LAYER_ZIPFILE________ "$WORKDIR"/"$ZIPFILE_BASENAME"
