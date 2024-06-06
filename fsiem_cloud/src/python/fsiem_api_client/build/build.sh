#!/bin/sh -eu

echo "[python] [dev] You can bash into this container using the following command"
echo "[python] sudo docker run -it --rm --entrypoint sh fsiem_api_client"
echo "[python] Building package"
# [DH]
# I have tried, and tried, to get setuptools to work with
# a repository manager
# but alas, I cannot.
# so we will localize the HTTPS_PROXY here
# which will allow us to download setuptools via the proxy
# even though we install the setuptools via pip
export HTTPS_PROXY=${BUILD_HTTP_PROXY:-}
echo "[python] Using HTTPS_PROXY=${HTTPS_PROXY}"
python3 -m build --wheel > /dev/null
unset HTTPS_PROXY
echo "[python] Build is done"
