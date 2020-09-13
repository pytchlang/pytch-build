#!/bin/bash

cd $PYTCH_REPO_BASE/pytch-vm/dist

echo Serving Skulpt layer from $(pwd)

python3 $PYTCH_LOCAL_SERVER_DIR/cors_server.py 8124
