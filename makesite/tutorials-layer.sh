#!/bin/bash

cd_or_fail() { cd "$1" || exit 1; }

: "${PYTCH_DEPLOYMENT_ID:?}"

BUILD_DIR="$(realpath "$(dirname "$0")")"
REPO_ROOT="$(realpath "$BUILD_DIR"/..)"

cd_or_fail "$REPO_ROOT"

if [ "$(git status --porcelain | wc -l)" -ne 0 ]; then
    (
        echo "Working directory not clean; abandoning build"
        echo
        git status
    ) >&2
    exit 1
fi

LAYER_WORKDIR="$REPO_ROOT"/website-layer
CONTENT_DIR="$LAYER_WORKDIR"/layer-content

# Leave the "venv" check even though we now use poetry.
if [ -e venv ] || [ -e .venv ] || [ -e "$CONTENT_DIR" ]; then
    (
        echo "Must be run in a clean clone"
        echo '(no "venv" or ".venv" or "website-layer/layer-content")'
    ) >&2
    exit 1
fi

# Poetry seems to want a keyring even if doing an operation which
# doesn't need one.  Tell it to use a null one.
PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
export PYTHON_KEYRING_BACKEND

n_poetry_envs=$(poetry env list | wc -l)

if [ "$n_poetry_envs" -ne 0 ]; then
    (
        echo "Must be run in a clean clone"
        echo "(no existing poetry environment)"
    ) >& 2
    exit 1
fi

TUTORIALS_REPO_ROOT="$(realpath "$REPO_ROOT"/../pytch-tutorials)"
if [ ! -e "$TUTORIALS_REPO_ROOT"/.git ]; then
    (
        echo No '"'pytch-tutorials'"' git repo found parallel to this one
    ) >&2
    exit 1
fi

MEDIALIB_REPO_ROOT="$(realpath "$REPO_ROOT"/../pytch-medialib)"
if [ ! -e "$MEDIALIB_REPO_ROOT"/.git ]; then
    (
        echo No '"'pytch-medialib'"' git repo found parallel to this one
    ) >&2
    exit 1
fi

poetry env use -q python3
poetry install
source "$(poetry env info --path)"/bin/activate

mkdir -p "$LAYER_WORKDIR"
LAYER_ZIPFILE="$LAYER_WORKDIR"/layer.zip

(
    cd_or_fail "$TUTORIALS_REPO_ROOT"

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


########################################################################
#
# TMP: Include tutorial-sourced media library in the "tutorials" layer.
#
# TODO: This will need re-writing once we have media content which
# does not come from tutorials.  There will need to be some process
# which merges media libraries: one from tutorials, and one
# directly-sourced.

medialib_outputdir="$CONTENT_DIR"/medialib/"$PYTCH_DEPLOYMENT_ID"
mkdir -p "$medialib_outputdir"

(
    cd_or_fail "$TUTORIALS_REPO_ROOT"

    pytchbuild-gather-asset-media \
        --index-source=WORKING_DIRECTORY \
        --output-directory="$medialib_outputdir"
)

# /TMP
#
########################################################################


rm "$LAYER_ZIPFILE"
(
    cd_or_fail "$CONTENT_DIR"
    find tutorials -type d -print0 | xargs -0 chmod 755
    find tutorials -type f -print0 | xargs -0 chmod 644
    zip -q -r "$LAYER_ZIPFILE" tutorials medialib
)
