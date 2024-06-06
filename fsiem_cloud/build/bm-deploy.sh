#!/bin/bash -e

# Run benchmark deploy

echo "Executing bm-deploy.sh script"
echo "==> Deploy $CI_ENVIRONMENT_NAME environment"
echo "CI_ENVIRONMENT_NAME               : $CI_ENVIRONMENT_NAME"
echo "Benchmarking deployment source dir: $TF_BM_DEPLOY_DIR"

#
# Terragrunt
#
# For tf debug pass these flags: --terragrunt-log-level debug --terragrunt-debug
echo "Deploying benchmarking env"
(cd "$TF_BM_DEPLOY_DIR" && terragrunt apply --auto-approve -no-color)

echo "Deploying collector env"
(cd "$TF_BM_COLLS_DEPLOY_DIR" && terragrunt apply --auto-approve -no-color)
