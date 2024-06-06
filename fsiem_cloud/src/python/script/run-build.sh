#!/bin/bash -e

# Require sudo for running docker
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "[python] Expecting version set via env variables"
echo "[python] Version: $VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH.$VERSION_REVISION"
echo "[python] DevOps build #: $DEVOPS_BUILD_NUMBER, build type: $DEVOPS_BUILD_TYPE"

echo "[python] Build the container for build environment"
# --progress=plain    prints out every line to standard out
# --progress=tty      prints out current subset of commands (~10 lines),
#                     then collapses the output into one line.
#                     This option seem to be default, but it isn't useful in CI.
docker-compose build --force-rm --progress=plain
echo "[python] Finished building build environment, exit code: $?"
