#!/bin/bash -e
#
# Format source code in this project
#

# Check for sudo user, this is required for using docker in dotnet code
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

# Variables definition
API_DIR="src/portal/api"
TERRAFORM_DIR="src/terraform"

# TODO: implement UI source code formatting
# UI_DIR="src/portal/ui"

echo "Executing format.sh script"

# API dotnet code
echo $'\n==> Formatting code for Portal API in '"$API_DIR"$'\n'
(cd $API_DIR && ./script/run-format.sh)

# UI
# echo $'\n==> Formatting code for UI in '"$UI_DIR"$'\n'
# (cd $UI_DIR && ./script/run-format.sh)

# Terraform dotnet code
echo $'\n==> Formatting code for terraform in '"$TERRAFORM_DIR"$'\n'
(cd $TERRAFORM_DIR && terraform fmt -recursive)
