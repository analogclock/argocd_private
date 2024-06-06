#!/bin/bash

# -e => exit on error
set -e

# Require sudo for running docker
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "[ui] Updating dependencies of this project"

echo "[ui] NOTE: build and update environments are the same"
echo "[ui] NOTE: we require additional docker compose file to mount source code"
# --progress=plain    prints out every line to standard out
# --progress=tty      prints out current subset of commands (~10 lines),
#                     then collapses the output into one line.
#                     This option seem to be default, but it isn't useful in CI.
docker-compose -f docker-compose.yml -f script/docker-compose.update.yml \
  build --force-rm --progress=plain portal_ui_build
echo "[ui] Finished building update environment, exit code: $?"

echo "[ui] Updating packages..."
docker-compose -f docker-compose.yml -f script/docker-compose.update.yml \
  run  --entrypoint "sh build/update.sh" --rm portal_ui_build

echo "[ui] Finished running update environment, exit code: $?"
