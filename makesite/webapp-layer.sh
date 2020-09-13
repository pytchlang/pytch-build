#!/bin/bash

if [ -z "$SOURCE_REPO" ]; then
    echo "need SOURCE_REPO env to be set"
    exit 1
fi

if [ -z "$SOURCE_BRANCH" ]; then
    echo "need SOURCE_BRANCH env to be set"
    exit 1
fi

if [ -z "$DEPLOY_BASE_URL" ]; then
   echo "need DEPLOY_BASE_URL env to be set"
   exit 1
fi


WORKDIR=$(mktemp -d -t pytch-tmp-XXXXXXXXXXXX)
REPODIR="$WORKDIR"/repo

ZIPFILE_BASENAME=app-layer.zip

git clone --quiet --depth 1 "$SOURCE_REPO" "$REPODIR" -b "$SOURCE_BRANCH"

htaccess_content() {
    cat <<EOF
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME} !-l
RewriteRule . index.html [L]
EOF
}

(
    cd "$REPODIR"
    npm install

    env PUBLIC_URL="$DEPLOY_BASE_URL"/app \
        REACT_APP_SKULPT_BASE="$DEPLOY_BASE_URL"/skulpt \
        npm run build

    mkdir "$WORKDIR"/zip-content
    mv build "$WORKDIR"/zip-content/app
    (
        cd "$WORKDIR"/zip-content
        htaccess_content > app/.htaccess
        find app -type d -print0 | xargs -0 chmod 755
        find app -type f -print0 | xargs -0 chmod 644
        zip -r ../"$ZIPFILE_BASENAME" app
    )
)

echo ________LAYER_ZIPFILE________ "$WORKDIR"/"$ZIPFILE_BASENAME"
