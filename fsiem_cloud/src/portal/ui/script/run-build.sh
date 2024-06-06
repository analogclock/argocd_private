#!/bin/bash

# -e => exit on error
set -e

# Require sudo for running docker
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "[ui] [src/portal/ui/script/run-build.sh] Expecting version set via env variables"
echo "[ui] Main version components: $VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH.$VERSION_REVISION"
echo "[ui] Dev ops build #: $DEVOPS_BUILD_NUMBER, Dev ops build type: $DEVOPS_BUILD_TYPE"

ARTIFACTS_DIR=artifacts

if [ -d "$ARTIFACTS_DIR" ]; then rm -Rf $ARTIFACTS_DIR; fi
mkdir -p $ARTIFACTS_DIR

echo "[ui] Build the container for build environment"
# --progress=plain    prints out every line to standard out
# --progress=tty      prints out current subset of commands (~10 lines),
#                     then collapses the output into one line.
#                     This option seem to be default, but it isn't useful in CI.
docker-compose build --force-rm --progress=plain portal_ui_build

echo "[ui] Run docker-compose up with --no-start (this is the create flag)"
docker-compose up --no-start portal_ui_build

echo "[ui] Copy the contents of artifacts from the container back to host machine"
# Assume we are running from within the root
docker cp --quiet portal_ui_build:/root/portal_ui_build/artifacts/. "./${ARTIFACTS_DIR}"
docker cp --quiet portal_ui_build:/root/portal_ui_build/package-lock.json "./"

echo "[ui] Remove the container and everything else associated with it"
docker-compose down > /dev/null
echo "[ui] Finished destroying build container, exit code: $?"
