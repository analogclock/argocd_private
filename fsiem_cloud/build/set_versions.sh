#!/bin/bash -Eeou
# Set versions of dependencies and tools from build/versions.yaml file.

# Import functions
# shellcheck disable=SC1091
source build/utilities.sh

# Parse versions of the docker containers
echo "Parsing build/versions.yaml file"
eval "$(parse_yaml "build/versions.yaml")"

set -x # Print out debug info, including values of vars

# Parsed versions from "build/versions.yaml"
# shellcheck disable=SC2154
DOCKER_UBUNTU_VERSION=${versions_docker_ubuntu_version}
# shellcheck disable=SC2154
DOCKER_DOTNET_VERSION=${versions_docker_dotnet_version}
# shellcheck disable=SC2154
DOCKER_NODE_VERSION=${versions_docker_node_version}
# shellcheck disable=SC2154
DOCKER_PYTHON_VERSION=${versions_docker_python_version}

# Build tools
# shellcheck disable=SC2154
TF_VERSION=${versions_terraform}
# shellcheck disable=SC2154
TERRAGRUNT_VERSION=${versions_terragrunt}
# shellcheck disable=SC2154
DOCKER_COMPOSE_VERSION=${versions_docker_compose}
# shellcheck disable=SC2154
TFSEC_VERSION=${versions_tfsec}
# shellcheck disable=SC2154
AWS_CLI_VERSION=${versions_aws_cli}

set +x # Turn off debug printing

export DOCKER_UBUNTU_VERSION
export DOCKER_DOTNET_VERSION
export DOCKER_NODE_VERSION
export DOCKER_PYTHON_VERSION

export TF_VERSION
export TERRAGRUNT_VERSION
export DOCKER_COMPOSE_VERSION
export TFSEC_VERSION
export AWS_CLI_VERSION

echo "Finished exporting versions of dependencies and tools"
