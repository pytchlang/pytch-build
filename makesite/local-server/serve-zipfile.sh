#!/bin/bash

if [ -z "$1" ]; then
    echo "usage: $0 ZIP_FILENAME"
    exit 1
fi

# This is sometimes unnecessary, but it's very quick, so worthwhile to
# make sure we have the latest image configuration:
docker build --tag pytch-local-server .

CONTENTDIR=$(mktemp -d -t pytch-local-server-content-XXXXXXXXXXXX)
CONTAINERNAME=$(basename "$CONTENTDIR")

echo Serving contents of "$1" from http://localhost:5888/

unzip -q -d "$CONTENTDIR" "$1"
chmod 755 "$CONTENTDIR"

docker run -it --rm \
       --name "$CONTAINERNAME" \
       -p 5888:80 \
       -v "$CONTENTDIR"/:/usr/local/apache2/htdocs/ \
       pytch-local-server
