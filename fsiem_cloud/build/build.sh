#!/usr/bin/env bash
set -e

# Run build on CI server

# Error handling
set -Eeou pipefail
ROOT=$PWD
BUILD_DIR="build"
TF_DIR="src/terraform"
TF_ARTIFACTS_DIR="$ROOT/$TF_DIR/artifacts"
TF_PLAN_TESTS_DIR="$ROOT/$TF_DIR/fsiem_deploy/plan_tests"
TF_PLAN_REGIONS_TESTS_DIR="$ROOT/$TF_DIR/fsiem_deploy/region_tests"
PYTHON_DIR="src/python"
LAMBDA_LAYER_DIR="$ROOT/$PYTHON_DIR/lambda_layer"
LAMBDA_ARTIFACTS_DIR="$ROOT/$PYTHON_DIR/artifacts"
API_DIR="src/portal/api"
UI_DIR="src/portal/ui"

# Terrform module downloads can fail due to a git security measure, this prevents that
git config --global --add safe.directory '*'

# Check for sudo user, this is required for using docker in dotnet code
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "Executing build.sh script"
echo "Total number of arguments  : $#"

echo "[build] Version details: $VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH.$VERSION_REVISION"
echo "[build] DevOps build number: $DEVOPS_BUILD_NUMBER, build type: $DEVOPS_BUILD_TYPE"

#
# Linters and validators
#

# Python code
echo $'\n==> Checking Python code complies with Flake8 linter\n'
(cd $PYTHON_DIR && flake8 --exclude fsiem_api_client/build/lib --exclude venv --exclude artifacts)

# Terraform code
if [[ -z "${NEXUS_TERRAFORM_PROXY}" ]]; then
  echo "NEXUS_TERRAFORM_PROXY is not set... Accessing terraform registry directly"
else
  echo "NEXUS_TERRAFORM_PROXY is set to ${NEXUS_TERRAFORM_PROXY}"
  # output the file we need, and use it
  cat << EOF >"$HOME"/config.tfrc
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

echo $'==> Validating terraform\n'
tf_checks() {
  cd "$1"
  if [[ -z "${NEXUS_TERRAFORM_PROXY}" ]]; then
    echo "NEXUS_TERRAFORM_PROXY is not set... Accessing terraform registry directly"
  else
    echo "NEXUS_TERRAFORM_PROXY is set, will use override.tf"
    cp override.tf.proxy override.tf
  fi
  echo $'Checking terraform in '"$1 "$''
  terraform init -upgrade -backend=false -no-color -migrate-state > /dev/null
  terraform validate -no-color
  terraform fmt -check -recursive -diff
  cd "$ROOT"
}

# Terraform
TF_DIRS=("$TF_DIR/portal" "$TF_DIR/fsiem_deploy/ec2")
for i in "${TF_DIRS[@]}"; do tf_checks "$i"; done

echo $'\n==> Validating terraform code with tfsec\n'
mkdir -p "$TF_ARTIFACTS_DIR"
for i in "${TF_DIRS[@]}"; do
  filename="tfsec_result__${i//\//__}"
  echo "Writing output to: '$TF_ARTIFACTS_DIR/$filename'"
  tfsec --soft-fail --out "$TF_ARTIFACTS_DIR/$filename" --format default,csv "$i" > /dev/null 2>&1
done

# Bash code
echo $'\n==> Validating bash/shell code\n'
shell_checks() {
  echo $'  Checking bash/shell code in '"$1 "$''
  shellcheck "$1"
}

SH_DIRS=("$BUILD_DIR"/*.sh)
for i in "${SH_DIRS[@]}"; do shell_checks "$i"; done

#
# Compilation of source code
#

# Dotnet code
echo $'\n==> Building Portal API in '"$API_DIR"$'\n'
echo "Copying .editorconfig file into the $API_DIR for docker build, otherwise formatting isn't picked up"
cp .editorconfig $API_DIR
(cd $API_DIR && ./script/run-build.sh)
echo "Inspecting artifacts directory:"
du -h --max-depth=1 $API_DIR/artifacts/ | sort -h

echo $'\n==> Building Portal UI in '"$UI_DIR"$'\n'
echo "Copying .editorconfig file into the $UI_DIR for docker build, otherwise formatting isn't picked up"
cp .editorconfig $UI_DIR

# UI Angular code
(cd $UI_DIR && ./script/run-build.sh)
echo "Inspecting artifacts directory:"
du -h --max-depth=1 $UI_DIR/artifacts/ | sort -h

#
# Building Lambda packages
#
echo $'\n==> Building python lambda zips\n'
pushd $PYTHON_DIR
mkdir -p "$LAMBDA_ARTIFACTS_DIR"

py_lambda() {
  FUNC_DIR="$1"
  DEST_DIR="$LAMBDA_ARTIFACTS_DIR/$FUNC_DIR"
  zip -rjq "$DEST_DIR" "$FUNC_DIR"
  echo "Created lambda: $DEST_DIR"
}

py_lambda lambda_monitor_cleanup
py_lambda lambda_notification_email
py_lambda lambda_ses_reject
py_lambda lambda_s3_tag

popd

echo $'\n==> Building lambda layers\n'
pushd "$LAMBDA_LAYER_DIR"
./build_lambda_layers.sh
popd

#
# Building docker images
#
echo $'\n==> Building all in one docker image in '"$TF_DIR/fsiem_deploy "$'\n'
(cd $TF_DIR/fsiem_deploy && docker-compose build --progress=plain fsiem-deploy)

echo $'\n==> Building python docker images in '"$PYTHON_DIR "$'\n'
(cd $PYTHON_DIR && docker-compose build --progress=plain)

# Plan deployment
echo $'\n==> Terragrunt deployment planning\n'
echo "CI_ENVIRONMENT_NAME             : $CI_ENVIRONMENT_NAME"
echo "CI_COMMIT_SHORT_SHA             : $CI_COMMIT_SHORT_SHA"
echo "CI_MERGE_REQUEST_ID             : $CI_MERGE_REQUEST_ID"
echo "Portal deployment source dir    : $TF_PORTAL_DEPLOY_DIR"
echo "Env setup deployment source dir : $TF_ENV_SETUP_DEPLOY_DIR"
echo "AWS identity                    :"
# Note1: for some reason using --output table started to hang in the terminal
# switching to --output json seems to have sorted it
# Note 2: build started to fail here,
# setting AWS_PAGER, see https://stackoverflow.com/a/68361849/706456
export AWS_PAGER=""
aws sts get-caller-identity --output json

# Runs terragrun init/plan/show. Example usage:
# terragrunt_plan <hcl_file_directory> <artifact_plan_name>
# terragrunt_plan "src/terraform/env_setup/env/dev" "artifacts/terragrunt_plan_env_setup.txt"
terragrunt_plan() {
  CURRENT_DIR=$(pwd)
  DEST_DIR="$1"
  DEST_PLAN_FILE="$2"
  echo "Standard output for terragrunt commands is muted, but saved into $DEST_PLAN_FILE"
  cd "$DEST_DIR"

  set -x
  terragrunt init -no-color -upgrade -migrate-state > /dev/null
  terragrunt plan -no-color -json -out=tfplan > "$DEST_PLAN_FILE"
  terragrunt show -no-color tfplan
  set +x
  cd "$CURRENT_DIR"
}

echo $'\n==> Terragrunt plan AWS environment setup (ECR/KMS/SSM)\n'
terragrunt_plan "$TF_ENV_SETUP_DEPLOY_DIR" "$TF_ARTIFACTS_DIR/terragrunt_plan_env_setup.txt"

echo $'\n==> Terragrunt plan portal deployment\n'
terragrunt_plan "$TF_PORTAL_DEPLOY_DIR" "$TF_ARTIFACTS_DIR/terragrunt_plan_portal.txt"

echo $'\n==> Terragrunt run test plans for EC2 deployments\n'
if [ "$DEVOPS_BUILD_TYPE" = "dev" ]
then
  cd "$TF_PLAN_TESTS_DIR"
  for dir in "$TF_PLAN_TESTS_DIR"/*/
  do
    echo "Running plan for ${dir}"
    cd "$dir"
    terragrunt init -upgrade
    terragrunt plan > /dev/null
  done
else
  echo "Planning for ec2 deployments will only run when build type is dev"
fi


echo $'\n==> Terragrunt plan FSIEM deployments in supported regions\n'
cd "$TF_PLAN_REGIONS_TESTS_DIR"

REGIONS=(
  "eu-central-1"
  "eu-west-1"
  "eu-west-2"
  "eu-west-3"
  "eu-north-1"
  "us-east-1"
  "us-east-2"
  "us-west-2"
  "ca-central-1"
  "ap-south-1"
  "ap-southeast-1"
  "ap-southeast-2"
  "me-south-1"
  # "af-south-1"
  # "ap-east-1"
)

if [ "$DEVOPS_BUILD_TYPE" = "dev" ]
then
  for i in "${REGIONS[@]}"
  do
    echo "Region: ${i}"
    sed "s/<replace_test_region>/${i}/g" terragrunt_hcl_template > terragrunt.hcl
    terragrunt init -upgrade
    terragrunt plan > /dev/null
    rm -f terragrunt.hcl
  done
else
  echo "Planning for ec2 deployments will only run when build type is dev"
fi

# done
cd "$ROOT"
