#!/bin/bash

VERSION_PACKAGE=0.5.4

docker build -t tfs_notify:"$VERSION_PACKAGE" . && \
docker run --network host -d --restart always -it tfs_notify:"$VERSION_PACKAGE"
