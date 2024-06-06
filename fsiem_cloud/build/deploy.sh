#!/bin/bash -e

# Run deploy

# Error handling
set -Eeou pipefail

# import functions
# shellcheck disable=SC1091
source build/utilities.sh

PYTHON_DIR="src/python"
DEPLOY_DIR="src/terraform/fsiem_deploy"

echo "Executing deploy.sh script"
echo "==> Deploy $CI_ENVIRONMENT_NAME environment"
echo "CI_ENVIRONMENT_NAME             : $CI_ENVIRONMENT_NAME"
echo "CI_COMMIT_SHORT_SHA             : $CI_COMMIT_SHORT_SHA"
echo "CI_MERGE_REQUEST_ID             : $CI_MERGE_REQUEST_ID"
echo "Portal deployment source dir    : $TF_PORTAL_DEPLOY_DIR"
echo "Env setup deployment source dir : $TF_ENV_SETUP_DEPLOY_DIR"
echo "AWS identity                    :"
aws sts get-caller-identity --output table

if [[ -z "${NEXUS_TERRAFORM_PROXY}" ]]; then
  echo "NEXUS_TERRAFORM_PROXY is not set... Accessing terraform registry directly"
else
  echo "NEXUS_TERRAFORM_PROXY is set to ${NEXUS_TERRAFORM_PROXY}"
  # output the file we need, and use it
  cat <<EOF >"$HOME"/config.tfrc
provider_installation {
  direct {
      exclude = ["registry.terraform.io/*/*"]
  }
  network_mirror {
      url = "${NEXUS_TERRAFORM_PROXY}"
  }
}
EOF

  echo "Content of $HOME/config.tfrc"
  cat "$HOME/config.tfrc"
  export TF_CLI_CONFIG_FILE=$HOME/config.tfrc
  echo "using TF_CLI_CONFIG_FILE=${TF_CLI_CONFIG_FILE}"
fi

echo $'==> Deploying env_setup and portal\n'

tg_deploy() {
  # $1 == directory to run from
  CURRENT_DIR=$(pwd)

  echo "Running deployment for: $1"

  cd "$1"

  # check if the nexus terraform proxy has been set
  # if it has then we move our override file into place
  if [[ -z "${NEXUS_TERRAFORM_PROXY}" ]]; then
    echo "NEXUS_TERRAFORM_PROXY is not set... Accessing terraform registry directly"
  else
    if [[ -f "../../override.tf" ]]; then
      echo "override already exists, a build has happened before and is using the proxy"
    else
      # we need to check if we want to use the proxy
      if [[ -f "../../override.tf.proxy" ]]; then
        # may not exist when running in env_setup
        # as no modules are required.
        echo "override.tf.proxy exists"
        cp ../../override.tf.proxy ../../override.tf
        echo "NEXUS_TERRAFORM_PROXY is set, will use override.tf"
      else
        echo "Override proxy does not exists -- will not copy or use proxy"
      fi
    fi
  fi
  echo $'Deploying terraform in '"$1 "$''
  terragrunt apply --auto-approve -no-color
  # get back to root
  cd "$CURRENT_DIR"
}

#
# Terragrunt
#
# For tf debug pass these flags: --terragrunt-log-level debug --terragrunt-debug
echo "Deploying setup env (configure VM, add storage, insert licence, etc)..."
tg_deploy "$TF_ENV_SETUP_DEPLOY_DIR"

echo "Deploying portal (API, UI)"
# If you ever accidentally lock the state and you are SURE its because no one else is using it
# then uncomment the line below. Change the ID to the one in the error message. Or the ID
# from the dynamoDB info field
# (cd "$TF_PORTAL_DEPLOY_DIR" && terragrunt force-unlock 2470d357-5542-df02-42ff-e67901da13e8)
tg_deploy "$TF_PORTAL_DEPLOY_DIR"

# Print out size of TF file, expect sizes of ~ 1 MB or less
# We are using two buckets, one for dev/playground and another one for prod
TF_STATE_BUCKET="fsiem-terraform-ftn"
if [ "$CI_ENVIRONMENT_NAME" = "prod" ]; then TF_STATE_BUCKET="fsiem-terraform-prod"; fi
TF_STATE_URL="s3://$TF_STATE_BUCKET/portal/env/$CI_ENVIRONMENT_NAME/terraform.tfstate"
echo "Expected tf state file location: $TF_STATE_URL"
TF_STATE_SIZE=$(remote_file_size "$TF_STATE_URL")
echo "Terraform state file size for '$CI_ENVIRONMENT_NAME' env is: $TF_STATE_SIZE"

#
# Docker images
#
echo "Pushing docker images"
AWS_ACCOUNT=$(aws sts get-caller-identity --query "Account" --output text)
AWS_DNS="$AWS_ACCOUNT.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
aws ecr get-login-password --region "$AWS_DEFAULT_REGION" |
  docker login --username AWS --password-stdin "$AWS_DNS"

# Push docker image to AWS ECR
push_docker_image() {
  local IMG_NAME=$1 # name of the image
  local SRC_DIR=$2  # docker-compose file directory
  echo "Pushing '$IMG_NAME' docker image"
  CONTAINER_IMAGE_NAME="$AWS_DNS/$IMG_NAME-$CI_ENVIRONMENT_NAME:latest"
  (cd "$SRC_DIR" &&
    export CONTAINER_IMAGE_NAME="$CONTAINER_IMAGE_NAME" &&
    docker-compose build --progress=plain "$IMG_NAME" &&
    docker-compose push "$IMG_NAME")
}

# Deployment image
push_docker_image "fsiem-deploy" "$DEPLOY_DIR"

# Python automation images
push_docker_image "fsiem-setup" "$PYTHON_DIR"
push_docker_image "fsiem-backup" "$PYTHON_DIR"
push_docker_image "fsiem-daily-job" "$PYTHON_DIR"
push_docker_image "fsiem-storage-enforcer" "$PYTHON_DIR"
push_docker_image "fsiem-terraform-updater" "$PYTHON_DIR"
push_docker_image "fsiem-scheduled-upgrade" "$PYTHON_DIR"
push_docker_image "fsiem-license" "$PYTHON_DIR"
push_docker_image "fsiem-metrics" "$PYTHON_DIR"
push_docker_image "fsiem-expiry-notification" "$PYTHON_DIR"
push_docker_image "fsiem-monitor" "$PYTHON_DIR"
push_docker_image "fsiem-worker-lifecycle" "$PYTHON_DIR"
