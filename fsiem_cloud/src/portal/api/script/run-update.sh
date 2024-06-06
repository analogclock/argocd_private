#!/bin/bash

# -e => exit on error
set -e

# Require sudo for running docker
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "[portal-api] Updating dependencies of this project"

echo "[portal-api] NOTE: build and update environments are the same"
echo "[portal-api] NOTE: we require additional docker compose file to mount source code"
# --progress=plain    prints out every line to standard out
# --progress=tty      prints out current subset of commands (~10 lines),
#                     then collapses the output into one line.
#                     This option seem to be default, but it isn't useful in CI.
docker-compose -f docker-compose.yml -f script/docker-compose.update.yml \
  build --force-rm --progress=plain portal_api_build
echo "[portal-api] Finished building update environment, exit code: $?"

echo "[portal-api] Update dotnet tools"
docker-compose -f docker-compose.yml -f script/docker-compose.update.yml \
  run --entrypoint "/bin/sh -c \"(dotnet tool list --local | awk 'NR>2' | cut -d ' ' -f 1 | xargs -n 1 dotnet tool update)\"" --rm portal_api_build

echo "[portal-api] Execute dotnet outdated command in the docker-compose run"
docker-compose -f docker-compose.yml -f script/docker-compose.update.yml \
  run --entrypoint "dotnet tool run dotnet-outdated --upgrade" --rm portal_api_build
echo "[portal-api] Finished running update environment, exit code: $?"
