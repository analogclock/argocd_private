#!/bin/bash -e

# Run deploy for automated dev tools

# Error handling
set -Eeou pipefail

LAMBDA_DIR="lambda"
TF_DIR="terraform"

#
# Create a zip package for lambda or lambda layer.
#
make_zip_lambda() {
  # Source directory, for example "remind_stack_deployed"
  SRC="$1"
  # Destination directory inside, e.g. "artifacts/remind_stack_deployed"
  DEST="artifacts/$SRC"
  echo "> Creating $SRC"
  cp -rf "$SRC" "$DEST"

  pushd "$DEST"
  echo "Minimise lambda size: deleting compiled python files"
  find . | grep -E "(/__pycache__$|\.pyc$|\.pyo|\.exe$)" | xargs rm -rf || true
  # Remove directories with the name tests
  find . -type d -name "tests" -exec rm -rf {} \; || true

  zip -rq9 "../$SRC.zip" .

  popd

  pwd
  echo "Remove $DEST"
  rm -rf "$DEST"
  echo "Done"
}

echo "==> Building python lambda zips"
pushd $LAMBDA_DIR
rm -rf "artifacts"
mkdir -p "artifacts/python"
make_zip_lambda "remind_stack_deployed"
popd

echo "==> Deploying"

pushd $TF_DIR
# terragrunt init
# terragrunt plan
terragrunt apply --auto-approve
popd
