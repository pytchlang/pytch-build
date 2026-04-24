#!/bin/bash -e

CONTENT_REPO_SYMLINK=pytch-demo-catalogue-content
BUILD_TOOL_REPO_SYMLINK=pytch-demo-catalogue-build-tool

have_all_links=yes

if [ ! -L "$PYTCH_REPO_BASE"/"$CONTENT_REPO_SYMLINK" ]; then
    1>&2 echo Symlink \""$CONTENT_REPO_SYMLINK"\" missing
    1>&2 echo from \""$PYTCH_REPO_BASE"\"
    1>&2 echo
    1>&2 echo Create this symlink, pointing to the root of the repo
    1>&2 echo containing the catalogue of discoverable demo content.
    have_all_links=no
fi

if [ ! -L "$PYTCH_REPO_BASE"/"$BUILD_TOOL_REPO_SYMLINK" ]; then
    1>&2 echo Symlink \""$BUILD_TOOL_REPO_SYMLINK"\" missing
    1>&2 echo from \""$PYTCH_REPO_BASE"\"
    1>&2 echo
    1>&2 echo Create this symlink, pointing to the root of the repo
    1>&2 echo containing the build tool for discoverable demo content.
    have_all_links=no
fi

if [ "$have_all_links" = "no" ]; then
    if [ -n "$TMUX" ]; then
        1>&2 echo
        1>&2 echo Will now sleep so you can read this in tmux.
        sleep 600
    fi
    exit 1
fi

exec env PYTCH_LOCAL_SERVER_DIR="$PYTCH_LOCAL_SERVER_DIR" \
     "$PYTCH_REPO_BASE"/"$BUILD_TOOL_REPO_SYMLINK"/local-server/serve.sh \
     "$PYTCH_REPO_BASE"/"$CONTENT_REPO_SYMLINK"
