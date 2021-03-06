#!/bin/bash

if [ -z "$PYTCH_DEPLOYMENT_ID" ]; then
    (
        echo "PYTCH_DEPLOYMENT_ID must be set"
    ) >&2
    exit 1
fi

BUILD_DIR="$(realpath "$(dirname "$0")")"
REPO_ROOT="$(realpath "$BUILD_DIR"/..)"

cd "$REPO_ROOT"

if [ $(git status --porcelain | wc -l) -ne 0 ]; then
    (
        echo "Working directory not clean; abandoning build"
        echo
        git status
    ) >&2
    exit 1
fi

LAYER_WORKDIR="$REPO_ROOT"/website-layer
CONTENT_DIR="$LAYER_WORKDIR"/layer-content

if [ -e venv -o -e "$CONTENT_DIR" ]; then
    (
        echo "Must be run in a clean clone"
        echo '(i.e., no "venv" or "website-layer/layer-content")'
    ) >&2
    exit 1
fi

TUTORIALS_REPO_ROOT="$(realpath "$REPO_ROOT"/../pytch-tutorials)"
if [ ! -e "$TUTORIALS_REPO_ROOT"/.git ]; then
    (
        echo No '"'pytch-tutorials'"' git repo found parallel to this one
    ) >&2
    exit 1
fi

virtualenv -p python3 venv \
    && source venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements_dev.txt \
    && python setup.py install

mkdir -p "$LAYER_WORKDIR"
LAYER_ZIPFILE="$LAYER_WORKDIR"/layer.zip

(
    cd "$TUTORIALS_REPO_ROOT"

    # Always use the working copy (which we've checked is clean) of the
    # tutorials index.  This is correct both for releases and for the
    # case where we're on a (branch taken off) "release-recipes".
    pytchbuild-gather-tutorials \
        --index-source=WORKING_DIRECTORY \
        -o "$LAYER_ZIPFILE"
)

# We need the content in a "tutorials" directory.  Seems a bit
# annoying to unzip and then re-zip the contents but it does the job.

mkdir -p "$CONTENT_DIR"/tutorials/"$PYTCH_DEPLOYMENT_ID"
unzip -q -d "$CONTENT_DIR"/tutorials/"$PYTCH_DEPLOYMENT_ID" "$LAYER_ZIPFILE"
rm "$LAYER_ZIPFILE"
(
    cd "$CONTENT_DIR"
    find tutorials -type d -print0 | xargs -0 chmod 755
    find tutorials -type f -print0 | xargs -0 chmod 644
    zip -q -r "$LAYER_ZIPFILE" tutorials
)
