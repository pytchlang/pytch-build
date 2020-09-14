#!/bin/bash

if [ -z "$SOURCE_REPO" ]; then
    echo "need SOURCE_REPO env to be set"
    exit 1
fi

# TODO: Allow building from tip of "release".

WORKDIR=$(mktemp -d -t pytch-tmp-XXXXXXXXXXXX)
REPODIR="$WORKDIR"/repo

ZIPFILE_BASENAME=tutorials-layer.zip

git clone --quiet --mirror "$SOURCE_REPO" "$REPODIR"

(
    cd "$REPODIR"
    pytchbuild-gather-tutorials \
        --index-source=RECIPES_TIP \
        -o "$WORKDIR"/raw-"$ZIPFILE_BASENAME"
)

# Seems a bit annoying to unzip and then re-zip the contents but it
# does the job.

mkdir "$WORKDIR"/tutorials
unzip -d "$WORKDIR"/tutorials "$WORKDIR"/raw-"$ZIPFILE_BASENAME"
(
    cd "$WORKDIR"
    find tutorials -type d -print0 | xargs -0 chmod 755
    find tutorials -type f -print0 | xargs -0 chmod 644
    zip -r "$ZIPFILE_BASENAME" tutorials
)

echo ________LAYER_ZIPFILE________ "$WORKDIR"/"$ZIPFILE_BASENAME"
