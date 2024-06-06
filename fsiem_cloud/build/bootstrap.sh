#!/bin/bash -e

# Install dependencies that the application requires for building and running.
# Tested on Ubuntu machine
set -o pipefail

# Require sudo for installation of tools
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi
cd "$(dirname "$0")/.." || exit

cat << EOF
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  Creating project build env
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

==> Updating system repositories...

EOF
apt-get update -qq

echo $'\n==> Installing required packages, std output is noisy and thus muted...'
apt-get install -yqq \
  curl containerd.io docker-ce docker-ce-cli docker-compose-plugin \
  docker-scan-plugin git gnupg2 lsb-release python3.11 python3-pip \
  shellcheck software-properties-common unzip zip > /dev/null

# Import helper functions
# shellcheck disable=SC1091
source build/utilities.sh

# Read versions for the build tools and build dependencies
# shellcheck disable=SC1091
source "build/set_versions.sh"

echo "Update python3 alternative to 3.11 (higher number takes priority)"
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 90
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 100
echo "Python3 version: $(python3 --version)"

echo $'\n==> Installing pip dependencies\n'
pip3 install -r build/requirements.txt --index-url "$NEXUS_PYPI_URL" > /dev/null

echo $'\n==> Installing AWS CLI'
curl -fsSL "$NEXUS_AWS_PROXY/awscli-exe-linux-x86_64-$AWS_CLI_VERSION.zip" -o "awscliv2.zip"
unzip -oqq awscliv2.zip
./aws/install > /dev/null
rm -rf aws
rm awscliv2.zip
echo "Please ensure you configure your AWS access with [sudo aws configure]"
echo "aws version: $(aws --version)"

echo $'\n==> Installing terraform and terragrunt'
URL="$NEXUS_HASHICORP_PROXY/terraform/$TF_VERSION/terraform_${TF_VERSION}_linux_amd64.zip"
install_zipped_binary_from_url "$URL" "terraform"
echo "terraform version: $(terraform --version)"

URL="$NEXUS_GITHUB_PROXY/gruntwork-io/terragrunt/releases/download/$TERRAGRUNT_VERSION/terragrunt_linux_amd64"
install_binary_from_url "$URL" "terragrunt"
echo "terragrunt version: $(terragrunt --version)"

# docker-compose
echo "docker version: $(docker version)"
URL="$NEXUS_GITHUB_PROXY/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-linux-x86_64"
install_binary_from_url "$URL" "docker-compose"
echo "docker-compose version: $(docker-compose version)"

# tfsec
URL="$NEXUS_GITHUB_PROXY/aquasecurity/tfsec/releases/download/$TFSEC_VERSION/tfsec-checkgen-linux-amd64"
install_binary_from_url "$URL" "tfsec-checkgen"
URL="$NEXUS_GITHUB_PROXY/aquasecurity/tfsec/releases/download/$TFSEC_VERSION/tfsec-linux-amd64"
install_binary_from_url "$URL" "tfsec"
echo "tfsec version: $(tfsec --version)"

echo $'\n==> Reloading profile file'
# shellcheck disable=SC1090
source ~/.profile
echo $'\nSuccessfully created build environment'
