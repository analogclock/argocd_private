#!/bin/bash

# -e => exit on error
set -e

ARTIFACTS_DIR=artifacts
DISTRIBUTION_DIR=dist

echo "[ui] You can bash into this container using the following command"
echo "[ui] sudo docker run -it --rm --entrypoint sh portal_ui_build"
echo "[ui] Expecting version set via env variables"
echo "[ui] Main version components: $VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH.$VERSION_REVISION"
echo "[ui] Dev ops build #: $DEVOPS_BUILD_NUMBER, Dev ops build type: $DEVOPS_BUILD_TYPE"

echo "[ui] Generating version.json file"
VER="$VERSION_MAJOR.$VERSION_MINOR ($CI_COMMIT_SHORT_SHA)"
VER_FULL1="$VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH.$VERSION_REVISION,"
VER_FULL2="$CI_ENVIRONMENT_NAME, $DEVOPS_BUILD_TYPE $DEVOPS_BUILD_NUMBER,"
VER_FULL3="($CI_COMMIT_SHORT_SHA)"
VER_FULL="$VER_FULL1 $VER_FULL2 $VER_FULL3"
VER_INFO="Maj.Min.Patch.Rev, env, devops build type #, (git commit sha1)"
jq  --null-input               \
    --arg VERSION "$VER"       \
    --arg VER_FULL "$VER_FULL" \
    --arg VER_INFO "$VER_INFO" \
  '{version: $VERSION, fullVersion: $VER_FULL, fullVersionInfo: $VER_INFO}' > version.json
echo "[ui] Version file has been updated:"
cat version.json

# Check if this environment is local build, set env and deploy path
if [ -z "${CI_ENVIRONMENT_NAME}" ]; then
  echo $"[WARN] CI_ENVIRONMENT_NAME not set, assuming a local dev build"
  CI_ENVIRONMENT_NAME="dev"; export CI_ENVIRONMENT_NAME
fi

echo "[ui] Node: disable npm updater notifications"
npm config set update-notifier false

echo "[ui] Node: $(node --version), npm: $(npm --version), yarn: $(yarn --version)"
echo "[ui] Environment: $CI_ENVIRONMENT_NAME"

echo "[ui] Install node modules"
echo "[ui] NPM Registry: '${NPM_PROXY}'"
npm --registry ${NPM_PROXY} install --no-fund --no-audit

echo "[ui] Lint source code"
npm run lint

echo "[ui] Build '$CI_ENVIRONMENT_NAME' target"
npm run build:$CI_ENVIRONMENT_NAME

echo "[ui] Setup artifacts dir"
if [ -d "$ARTIFACTS_DIR" ]; then rm -Rf $ARTIFACTS_DIR; fi
mkdir -p $ARTIFACTS_DIR
cp -R ./$DISTRIBUTION_DIR ./$ARTIFACTS_DIR
