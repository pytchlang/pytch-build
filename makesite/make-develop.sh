#!/bin/bash

MAKESITE_DIR=$(dirname "$0")
export PYTCH_REPOS_BASE=file://$(realpath "$MAKESITE_DIR"/../..)
exec "$MAKESITE_DIR"/make.sh "$@"
