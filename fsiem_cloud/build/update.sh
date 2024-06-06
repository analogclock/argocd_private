#!/bin/bash -e
#
# Update libraries and dependencies for this project
#

# Error handling
set -Eeou pipefail

# Check for sudo user, this is required for using docker in dotnet code
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

# Variables definition
API_DIR="src/portal/api"
UI_DIR="src/portal/ui"
PYTHON_DIR="src/python"

echo "Executing update.sh script"

# UI
echo $'\n==> Updating UI in '"$UI_DIR"$'\n'
(cd $UI_DIR && ./script/run-update.sh)

# Update Python requirement files
echo $'\n==> Updating Portal API in '"$API_DIR"$'\n'
(cd $PYTHON_DIR && ./script/run-update.sh)

# API dotnet code
echo $'\n==> Updating Portal API in '"$API_DIR"$'\n'
echo "[IMPORTANT] To update API, we need to enable NUGET source, which is disabled by default, comment out"
echo "[IMPORTANT] RUN dotnet nuget remove source nuget.org"
echo "[IMPORTANT] in src/portal/api/build.dockerfile file"
(cd $API_DIR && ./script/run-update.sh)
