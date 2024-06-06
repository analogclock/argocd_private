#!/bin/bash

# -e => exit on error
set -e

# Require sudo for running docker
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "[portal-api] Expecting version set via env variables"
echo "[portal-api] Main version components: $VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH.$VERSION_REVISION"
echo "[portal-api] Dev ops build #: $DEVOPS_BUILD_NUMBER, Dev ops build type: $DEVOPS_BUILD_TYPE"

ARTIFACTS_DIR=artifacts

if [ -d "$ARTIFACTS_DIR" ]; then rm -Rf $ARTIFACTS_DIR; fi
mkdir -p $ARTIFACTS_DIR

echo "[portal-api] Build the container for build environment"
# --progress=plain    prints out every line to standard out
# --progress=tty      prints out current subset of commands (~10 lines),
#                     then collapses the output into one line.
#                     This option seem to be default, but it isn't useful in CI.
docker-compose build --force-rm --progress=plain portal_api_build
echo "[portal-api] Finished building build environment, exit code: $?"

echo "[portal-api] Run docker-compose up"
docker-compose up --no-start portal_api_build
echo "[portal-api] Finished running build environment, exit code: $?"

echo "[portal-api] Copy the contents of artifacts from the container back to host machine"
# Assume we are running from within the root
docker cp --quiet portal_api_build:/root/portal_api/artifacts/. "./${ARTIFACTS_DIR}"
echo "[portal-api] Finished copying artifacts, exit code: $?"

echo "[portal-api] Remove the container and everything else associated with it"
docker-compose down > /dev/null
echo "[portal-api] Finished destroying build container, exit code: $?"
