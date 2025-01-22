#!/bin/bash
if docker inspect pixeldrain-uploader > /dev/null 
then
echo "Skipping Build..."
else
docker build --pull -t pixeldrain-uploader $(dirname $(realpath "$0"))
fi
docker run  --log-driver=none --rm -i pixeldrain-uploader "$@"