#!/bin/bash

VERSION_PACKAGE=0.6.2.dev5

docker build -t tfs_notify:"$VERSION_PACKAGE" . && \
docker run --network host -d --restart always -it tfs_notify:"$VERSION_PACKAGE"
