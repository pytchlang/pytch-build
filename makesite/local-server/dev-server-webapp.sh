#!/bin/bash

cd_or_fail() { cd "$1" || exit 1; }

cd "$PYTCH_REPO_BASE"/pytch-webapp
exec npm start
