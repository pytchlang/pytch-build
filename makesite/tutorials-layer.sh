#!/bin/bash

if [ -z "$PYTCH_DEPLOYMENT_ID" ]; then
    echo "PYTCH_DEPLOYMENT_ID must be set"
    exit 1
fi

BUILD_DIR="$(realpath "$(dirname "$0")")"
REPO_ROOT="$(realpath "$BUILD_DIR"/..)"

cd "$REPO_ROOT"

LAYER_WORKDIR="$REPO_ROOT"/website-layer
CONTENT_DIR="$LAYER_WORKDIR"/layer-content

if [ -e venv -o -e "$CONTENT_DIR" ]; then
    echo "Must be run in a clean clone"
    echo '(i.e., no "venv" or "website-layer/layer-content")'
    exit 1
fi

TUTORIALS_REPO_ROOT="$(realpath "$REPO_ROOT"/../pytch-tutorials)"
if [ ! -e "$TUTORIALS_REPO_ROOT"/.git ]; then
    echo No '"'pytch-tutorials'"' git repo found parallel to this one
    exit 1
fi

virtualenv -p python3 venv \
    && source venv/bin/activate \
    && pip install -r requirements_dev.txt \
    && python setup.py install

LAYER_ZIPFILE="$LAYER_WORKDIR"/layer.zip

(
    cd "$TUTORIALS_REPO_ROOT"

    # Decide whether to build from a releases commit or the tip of
    # release-recipes based on whether we're currently checked out at
    # "release-recipes".

    if [ "$(git rev-parse --abbrev-ref HEAD)" = release-recipes ]; then
        pytchbuild-gather-tutorials \
            --index-source=RECIPES_TIP \
            -o "$LAYER_ZIPFILE"
    else
        pytchbuild-gather-tutorials \
            --from-release HEAD \
            -o "$LAYER_ZIPFILE"
    fi
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
