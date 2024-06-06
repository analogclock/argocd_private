#!/bin/bash -e

# Require sudo for running docker
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "[portal-api] Formatting source code in this project"
echo "[portal-api] Copying .editorconfig from the root of the project"
cp ../../../.editorconfig .

echo "[portal-api] NOTE: build and format environments are the same"
echo "[portal-api] NOTE: we require additional docker compose file to mount source code"
# --progress=plain    prints out every line to standard out
# --progress=tty      prints out current subset of commands (~10 lines),
#                     then collapses the output into one line.
#                     This option seem to be default, but it isn't useful in CI.
docker-compose -f docker-compose.yml -f script/docker-compose.update.yml \
  build --force-rm --progress=plain portal_api_build
echo "[portal-api] Finished building format environment, exit code: $?"

echo "[portal-api] Execute dotnet format command in the docker-compose run"
docker-compose -f docker-compose.yml -f script/docker-compose.update.yml \
  run --entrypoint "dotnet format" --rm portal_api_build
echo "[portal-api] Finished running format environment, exit code: $?"
