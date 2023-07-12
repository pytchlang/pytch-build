#!/bin/bash

cd_or_fail() { cd "$1" || exit 1; }

cd_or_fail "$PYTCH_REPO_BASE"/pytch-webapp

dotenvfile=./src/.env
if [ ! -r ${dotenvfile} ]; then
    echo No .env file in src
    sleep 60
    exit 1
fi

set -o allexport
# shellcheck disable=SC1090
source ${dotenvfile}
set +o allexport

npx() {
    command npx --no-install "$@"
}

basearg=""
if [ -n "$DEV_VITE_BASE_PATH" ]; then
    basearg="--base=$DEV_VITE_BASE_PATH"
fi

if [ "${DEV_VITE_USE_PREVIEW:-no}" = "yes" ]; then
    echo Running tsc...
    npx tsc && npx vite build "$basearg" && npx vite preview "$basearg"
else
    npx vite "$basearg"
fi

# Keep the shell process running in case of error, so tmux doesn't
# discard the window before we can read the error message.
sleep 60
