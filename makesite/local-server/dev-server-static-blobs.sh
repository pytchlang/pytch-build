#!/bin/bash -e

cd "$PYTCH_REPO_BASE"/pytch-static-blobs/data

echo Serving static blobs from $(pwd)
python3 "$PYTCH_LOCAL_SERVER_DIR"/cors_server.py 8129
