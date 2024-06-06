#! /bin/bash

# -e => exit on error
set -e

ARTIFACTS_DIR=artifacts
DOTNET_FRAMEWORK=net8.0

if [ -d "$ARTIFACTS_DIR" ]; then rm -Rf $ARTIFACTS_DIR; fi
mkdir -p $ARTIFACTS_DIR
echo "[portal-api] [dev] You can bash into this container using the following command"
echo "[portal-api] sudo docker run -it --rm --entrypoint sh portal_api_build"
echo "[portal-api] Expecting version set via env variables"
echo "[portal-api] Main version components: $VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH.$VERSION_REVISION"
echo "[portal-api] Dev ops build #: $DEVOPS_BUILD_NUMBER, Dev ops build type: $DEVOPS_BUILD_TYPE"

echo "[portal-api] Nuget source set to '${NEXUS_NUGET_PROXY}'"
dotnet restore -s "${NEXUS_NUGET_PROXY}" -r linux-x64 --disable-parallel --verbosity minimal

echo "[portal-api] Verifying code formatting"

dotnet format --severity warn --verify-no-changes --verbosity diagnostic

echo "[portal-api] Publishing FortinetOne.Client"
dotnet publish                        \
  src/apps/FortinetOne.Client         \
  --configuration release             \
  --framework $DOTNET_FRAMEWORK       \
  --output "${ARTIFACTS_DIR}/client/"

echo "[portal-api] Publishing FortiMonitor.Client"
dotnet publish                        \
  src/apps/FortiMonitor.Client        \
  --configuration release             \
  --framework $DOTNET_FRAMEWORK       \
  --output "${ARTIFACTS_DIR}/client/"

# Ignore some output, based on https://stackoverflow.com/a/69825282/706456
echo "[portal-api] Publish API as a lambda package"
dotnet tool run dotnet-lambda package         \
 --project-location src/apps/FinsProvisioning \
 --configuration release                      \
 --framework $DOTNET_FRAMEWORK                \
 --output-package "${ARTIFACTS_DIR}/lambda/fins-provisioning.zip" | \
 grep -v -e 'Changed permissions on published file' -e 'zipping'
