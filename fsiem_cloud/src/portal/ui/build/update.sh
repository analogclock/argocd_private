#!/bin/bash

# -e => exit on error
set -e

echo "[ui] Performing update of npm dependencies"
echo "[ui] Node: $(node --version), npm: $(npm --version), yarn: $(yarn --version)"

echo "[ui] Removing node_modules and lock file"
rm -rf node_modules
rm -rf package-lock.json

echo "[ui] Installing npm npm-check-updates module to perform the update"
# This has to be installed as a global package, else it doesn't work :/
npm install -g --no-fund npm-check-updates

echo "[ui] Updating npm modules that can be updated"
ncu -u

echo "[ui] Running npm install"
npm install --no-fund --force --legacy-peer-deps

# Check if this environment is local build, set env and deploy path
if [ -z "${CI_ENVIRONMENT_NAME}" ]; then
  echo $"[ui] [WARN] CI_ENVIRONMENT_NAME not set, assuming a dev build"
  CI_ENVIRONMENT_NAME="dev"; export CI_ENVIRONMENT_NAME
fi

echo "[ui] Running npm build for '$CI_ENVIRONMENT_NAME'"
npm run build:$CI_ENVIRONMENT_NAME

echo "[ui] Update is finished. Please review logs above for errors and warnings"
