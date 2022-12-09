!/bin/bash

docker run --network host -d --restart always -it tfs_notify:$(VERSION_PACKAGE)
