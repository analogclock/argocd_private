#!/usr/bin/env bash
set -e

# Run CI/CD action
#
# Example usage:
# cd ~/git/fsiem_cloud
# export CI_ENVIRONMENT_NAME=playground
# sudo -E bash build/ci-wrapper.sh <build> / <deploy> / <update> / <format>

echo $'\n*********************'
echo "*     Starting      *"
echo $'*********************\n'

# First argument to the script, if none is provided we default to <build>
ACTION=$1

# Trap will be auto invoked when this or child process fails with an error code.
# Note, the error code may or may not be captured correctly, not sure why.
trap 'echo -e "\n😖  \e[41mAction <$ACTION> failed, exit code: $?.\e[m\n"' ERR

START_TIME=$(date +%s)
BUILD_DIR="build"

echo "Executing ci-wrapper.sh -- entry point for CI"
echo "Total number of arguments: $#"
echo "First argument:            $1"

# Import helper functions
# shellcheck disable=SC1091
source build/utilities.sh

#
# Parse action
#
SUPPORTED_ACTIONS="build, deploy, update, format, bm-build, bm-deploy"
echo "The following actions are supported: $SUPPORTED_ACTIONS"
if [ -z "${ACTION}" ]; then
  echo "Action was not provided as a first argument to the script, assuming it is: build"
  ACTION=build
fi
# Check if action is supported, e.g. it is <build> or <deploy>
contains "$SUPPORTED_ACTIONS" "$ACTION"
# shellcheck disable=SC2181
if [ $? -ne 0 ]; then
  echo "Failed to parse action '$ACTION'. You can only use $SUPPORTED_ACTIONS."
  exit 1
fi

#
# Configure env vars
#
# Check if environment is set, if not default to <playground>
if [ -z "${CI_ENVIRONMENT_NAME}" ]; then
  echo "[WARN] CI_ENVIRONMENT_NAME not set, assuming environment is playground"
  CI_ENVIRONMENT_NAME="playground"; export CI_ENVIRONMENT_NAME
fi
ENV_FILE="build/set_env.sh"
echo $"Reading env variables from '$ENV_FILE' using current shell"
if [ ! -f "$ENV_FILE" ]; then echo "$ENV_FILE does not exist."; exit 1; fi
# shellcheck disable=SC1090
source $ENV_FILE

VERSIONS_FILE="build/set_versions.sh"
echo $"Reading versions from '$VERSIONS_FILE' using current shell"
if [ ! -f "$VERSIONS_FILE" ]; then echo "$VERSIONS_FILE does not exist."; exit 1; fi
# shellcheck disable=SC1090
source $VERSIONS_FILE

#
# Check hardware (enough free disk space)
#
# Cleanup docker if the disk space used > 80%
echo "Checking disk space (80% used triggers a cleanup)"
print_root_vol_disk_usage
USED_DISK=$(root_vol_disk_usage_percent)
if ((USED_DISK > 80)); then
  echo "[WARN] Disk space cleanup threshold reached"
  ./src/devops/docker/docker-clean.sh
  ./src/devops/docker/docker-info.sh
  ./src/devops/docker/inspect_disk_usage.sh
fi

#
# Make docker build environment: build_env
#
# Expecting this is triggered from the root of the project: cd ~/git/fsiem_cloud
# To keep the root dir clean, all build files are in the "build" folder
# -f build/docker-compose.yml    pass needed config file
# --project-directory .          tells docker to use current folder as a root
# build                          command to execute, build docker compose service
# build_env                      name of the docker compose service
# --progress=plain               output progress to log file
echo "Running docker-compose build step, creating build environment"
docker-compose -f build/docker-compose.yml --project-directory . \
  build --progress=plain build_env

echo "[dev] You can bash into the container using the following command:"
echo "sudo docker-compose -f build/docker-compose.yml --project-directory . run --rm --entrypoint bash build_env"

echo "*********************"
echo "*    Env created    *"
echo "*********************"

#
# Run action
#
echo "Executing action: $ACTION"

# BUILD
if [ "$ACTION" = "build" ]; then

  docker-compose -f build/docker-compose.yml --project-directory . \
    run --rm build_env ./build/build.sh

# DEPLOY
elif [ "$ACTION" = "deploy" ]; then

  echo "Inspecting artifacts directory:"
  du -h --max-depth=1 src/portal/api/artifacts/ | sort -h
  du -h --max-depth=1 src/portal/ui/artifacts/  | sort -h
  du -h --max-depth=1 src/terraform/artifacts/  | sort -h

  docker-compose -f build/docker-compose.yml --project-directory . \
    run --rm build_env ./build/deploy.sh

# UPDATE
elif [ "$ACTION" = "update" ]; then

  ./$BUILD_DIR/update.sh

# FORMAT
elif [ "$ACTION" = "format" ]; then

  ./$BUILD_DIR/format.sh

# BM-BUILD
elif [ "$ACTION" = "bm-build" ]; then

  echo "Collector instance count is: '$COLLECTOR_INSTANCE_COUNT' "
  docker-compose -f build/docker-compose.yml --project-directory . \
    run --rm build_env ./build/bm-build.sh

# BM-DEPLOY
elif [ "$ACTION" = "bm-deploy" ]; then

  echo "Inspecting artifacts directory:"
  du -h --max-depth=1 src/terraform/fsiem_benchmarking/artifacts/  | sort -h

  docker-compose -f build/docker-compose.yml --project-directory . \
    run --rm build_env ./build/bm-deploy.sh

# Erm... This is some action that we don't currently support
else
  echo "Unsupported action: $ACTION"
  exit 1
fi

END_TIME=$(date +%s)
DELTA_SEC=$((END_TIME - START_TIME))
HH=$((DELTA_SEC / 3600)); MM=$(((DELTA_SEC % 3600) / 60)); SS=$(((DELTA_SEC % 3600) % 60))
echo -e "\n==> $ACTION for $CI_ENVIRONMENT_NAME ($CI_COMMIT_SHORT_SHA) took $HH:$MM:$SS (hh:mm:ss)\n"
echo "******************"
echo "*    Finished    *"
echo "******************"
