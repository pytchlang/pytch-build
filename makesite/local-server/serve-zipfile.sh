#!/bin/bash

if [ -z "$1" ]; then
    echo "usage: $0 ZIP_FILENAME [ DEMOS_ZIP_FILENAME ]"
    exit 1
fi

# This is sometimes unnecessary, but it's very quick, so worthwhile to
# make sure we have the latest image configuration:
docker build --tag pytch-local-server .

CONTENTDIR=$(mktemp -d -t pytch-local-server-content-XXXXXXXXXXXX)
CONTAINERNAME=$(basename "$CONTENTDIR")

echo Serving contents of "$1" from http://localhost:5888/

unzip -q -d "$CONTENTDIR" "$1"

if [ -n "$2" ]; then
    mkdir "$CONTENTDIR"/demos
    unzip -q -d "$CONTENTDIR"/demos "$2"
fi

chmod 755 "$CONTENTDIR"

(
    cd "$CONTENTDIR"
    if [ -e releases ]; then
        echo Release zipfile: setting up redirection
        cp releases/*/toplevel-dot-htaccess .htaccess
    else
        app_path=$(python -c "import zipfile; print(zipfile.ZipFile('$1').infolist()[0].filename)")
        if [ -z "$app_path" ]; then
            echo
            echo Problem finding path within zipfile "$1"
            echo
        fi

        echo
        echo Cypress command within pytch-webapp directory:
        echo CYPRESS_BASE_URL=http://localhost:5888/${app_path}app/ ./node_modules/.bin/cypress open
        echo
    fi
)

docker run -it --rm \
       --name "$CONTAINERNAME" \
       -p 5888:80 \
       -v "$CONTENTDIR"/:/usr/local/apache2/htdocs/ \
       pytch-local-server
