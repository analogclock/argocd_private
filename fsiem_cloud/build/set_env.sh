#!/bin/bash -Eeou
# Shared env variables for all environments.
# If a variable is passed in as external env variable, this value take precedence.
# If a value is not defined as env variable, a default value will be set by this file.
# Note: if you add a new variable here, remember to also add it to build/docker-compose.yml.
# As otherwise docker compose will not pass this newly added variable to the build/deploy.

# Import functions
# shellcheck disable=SC1091
source build/utilities.sh

echo "Exporting common env variables:"

# Year, shorten to last two digits for 2022, this will be 22
# shellcheck disable=SC2034
YY=$(date +%y)
# Current quarter, e.g. 1, 2, 3, or 4
# shellcheck disable=SC2034
Q=$(date +"%-m" | awk '{printf ("%1d", (($1-1)/3)+1)}')

SHA1_SHORT=$(git rev-parse --short HEAD)
CI_COMMIT_SHORT_SHA_SANITIZED=$(sanitize "$SHA1_SHORT")

set -x # Print out debug info, including values of vars
VERSION_MAJOR=${VERSION_MAJOR:-$YY}
VERSION_MINOR=${VERSION_MINOR:-$Q}
VERSION_PATCH=${VERSION_PATCH:-0}
VERSION_REVISION=${VERSION_REVISION:-0}
DEVOPS_BUILD_NUMBER=${DEVOPS_BUILD_NUMBER:-1}
DEVOPS_BUILD_TYPE=${DEVOPS_BUILD_TYPE:-dev}
CI_COMMIT_SHORT_SHA=$CI_COMMIT_SHORT_SHA_SANITIZED
CI_ENVIRONMENT_NAME=${CI_ENVIRONMENT_NAME:-dev}
TF_PORTAL_DEPLOY_DIR=${TF_PORTAL_DEPLOY_DIR:-"src/terraform/portal/env/$CI_ENVIRONMENT_NAME"}
TF_ENV_SETUP_DEPLOY_DIR=${TF_ENV_SETUP_DEPLOY_DIR:-"src/terraform/env_setup/env/$CI_ENVIRONMENT_NAME"}
TF_BM_DEPLOY_DIR=${TF_BM_DEPLOY_DIR:-"src/terraform/fsiem_benchmarking/env/$CI_ENVIRONMENT_NAME"}
TF_BM_COLLS_DEPLOY_DIR=${TF_BM_COLLS_DEPLOY_DIR:-"src/terraform/fsiem_collector/env/$CI_ENVIRONMENT_NAME"}
COLLECTOR_INSTANCE_COUNT=${COLLECTOR_INSTANCE_COUNT:-0}
BM_SERIAL_NUMBER=${BM_SERIAL_NUMBER:-"siemtestcoll"}
DOCKER_REGISTRY_NEXUS_URL=${DOCKER_REGISTRY_NEXUS_URL:-""}
NEXUS_NUGET_PROXY=${NEXUS_NUGET_PROXY:-""}
NEXUS_NPM_PROXY=${NEXUS_NPM_PROXY:-""}
NEXUS_TERRAFORM_PROXY=${NEXUS_TERRAFORM_PROXY:-""}
NEXUS_AWS_PROXY=${NEXUS_AWS_PROXY:-""}
NEXUS_HASHICORP_PROXY=${NEXUS_HASHICORP_PROXY:-""}
NEXUS_GITHUB_PROXY=${NEXUS_GITHUB_PROXY:-""}

# Variable initialised here as it is used in several different projects.
# And an empty value doesn't work as a default, we need a valid PyPi URL.
NEXUS_PYPI_URL=${NEXUS_PYPI_URL:-"https://pypi.org/simple"}

# Build proxy to use for all components that don't have package managers
# intentionally set to empty. Don't wrap double quotes
BUILD_HTTP_PROXY=${BUILD_HTTP_PROXY:-}

set +x # Turn off debug printing for sensitive data

AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-$(aws configure get region)}
echo "AWS_DEFAULT_REGION   : $AWS_DEFAULT_REGION"

AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID-$(aws configure get aws_access_key_id)}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-$(aws configure get aws_secret_access_key)}

echo "Print out of sensitive vars (last N chars)"
# IMPORTANT:
# - This is used to ensure the vars have valid and correct values.
# - Be sure not to disclose sensitive info.
# - SPACE after colon is important, without it full value will be printed :/
echo "AWS_ACCESS_KEY_ID    : ***${AWS_ACCESS_KEY_ID: -3}"
echo "AWS_SECRET_ACCESS_KEY: ***${AWS_SECRET_ACCESS_KEY: -1}"

export VERSION_MAJOR
export VERSION_MINOR
export VERSION_PATCH
export VERSION_REVISION
export DEVOPS_BUILD_NUMBER
export DEVOPS_BUILD_TYPE
export CI_COMMIT_SHORT_SHA
export CI_MERGE_REQUEST_ID=0
export CI_ENVIRONMENT_NAME
export TF_PORTAL_DEPLOY_DIR
export TF_ENV_SETUP_DEPLOY_DIR
export TF_BM_DEPLOY_DIR
export TF_BM_COLLS_DEPLOY_DIR
export COLLECTOR_INSTANCE_COUNT
export BM_SERIAL_NUMBER
export DOCKER_REGISTRY_NEXUS_URL
export NEXUS_NUGET_PROXY
export NEXUS_NPM_PROXY
export NEXUS_PYPI_URL
export NEXUS_TERRAFORM_PROXY
export AWS_DEFAULT_REGION
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export BUILD_HTTP_PROXY
export NEXUS_AWS_PROXY
export NEXUS_HASHICORP_PROXY
export NEXUS_GITHUB_PROXY

echo "Finished exporting common env variables"
