#!/bin/bash -e

# Run benchmark build

ROOT=$PWD
TF_DIR="src/terraform"
TF_ARTIFACTS_DIR="$ROOT/$TF_DIR/fsiem_benchmarking/artifacts"
TF_COLLS_ARTIFACTS_DIR="$ROOT/$TF_DIR/fsiem_collector/artifacts"

# Terraform code
echo $'==> Validating terraform\n'
tf_checks() {
  cd "$1"
  echo $'Checking terraform in '"$1 "$''
  terraform init -upgrade -backend=false -no-color -migrate-state > /dev/null
  terraform validate -no-color
  terraform fmt -check -recursive -diff
  cd "$ROOT"
}

# Terraform
TF_DIRS="$TF_DIR/fsiem_benchmarking"
./"$TF_DIRS"/python/bm-lambda.sh
for i in "${TF_DIRS[@]}"; do tf_checks "$i"; done

TF_COLLS_DIRS=("$TF_DIR/fsiem_collector")
for i in "${TF_COLLS_DIRS[@]}"; do tf_checks "$i"; done

echo $'\n==> Validating terraform code with tfsec\n'
mkdir -p "$TF_ARTIFACTS_DIR"
for i in "${TF_DIRS[@]}"; do
  filename="tfsec_result__${i//\//__}"
  echo "Writing output to: '$TF_ARTIFACTS_DIR/$filename'"
  tfsec --soft-fail --out "$TF_ARTIFACTS_DIR/$filename" --format default,csv "$i" > /dev/null 2>&1
done

mkdir -p "$TF_COLLS_ARTIFACTS_DIR"
for i in "${TF_COLLS_DIRS[@]}"; do
  filename="tfsec_result__${i//\//__}"
  echo "Writing output to: '$TF_COLLS_ARTIFACTS_DIR/$filename'"
  tfsec --soft-fail --out "$TF_COLLS_ARTIFACTS_DIR/$filename" --format default,csv "$i" > /dev/null 2>&1
done

# Plan deployment
echo $'\n==> Terragrunt deployment planning\n'
echo "Benchmarking deployment source dir: $TF_BM_DEPLOY_DIR"

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
  terragrunt init -no-color -upgrade -reconfigure
  terragrunt plan -no-color -json -out=tfplan > "$DEST_PLAN_FILE"
  terragrunt show -no-color tfplan
  set +x
  cd "$CURRENT_DIR"
}

echo $'\n==> Terragrunt plan benchmarking deployment\n'
terragrunt_plan "$TF_BM_DEPLOY_DIR" "$TF_ARTIFACTS_DIR/terragrunt_plan_bm.txt"

echo $'\n==> Terragrunt plan collector deployment\n'
terragrunt_plan "$TF_BM_COLLS_DEPLOY_DIR" "$TF_COLLS_ARTIFACTS_DIR/terragrunt_plan_colls.txt"
