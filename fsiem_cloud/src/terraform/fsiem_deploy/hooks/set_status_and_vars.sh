#!/bin/bash

# Updating DynamoDB record with deployment status and vars from deployment:
# SUPER_URL and WORKERS_URL

echo "==> Executing a hook to set $2 status and vars for $DEPLOYMENT_NAME"
echo "Total number of args:       $#"
echo "First argument (dir):       $1"
echo "Second argument (status):   $2"
echo "DynamoDB table (from env):  $DYNAMODB_ACTIVATION_TABLE"
echo "Deployment name (from env): $DEPLOYMENT_NAME"
echo "AWS region (from env):      $PORTAL_AWS_REGION"

# Getting URLs from terragrunt output. We have to do some jank with the directories.
dir=$(echo $PWD)
cd $1
SUPER_URL=$(terragrunt output super_url     | tr -d '"')
WORKERS_URL=$(terragrunt output workers_url | tr -d '"')
EXTERNAL_STORAGE_ARN=$(terragrunt output external_storage | tr -d '"')
cd $dir

CMD="
UPDATE $DYNAMODB_ACTIVATION_TABLE
  SET status='$2'
  SET url='$SUPER_URL'
  SET workersUrl='$WORKERS_URL'
  SET externalStorage = '$EXTERNAL_STORAGE_ARN'
WHERE
  serialNumber='$DEPLOYMENT_NAME'
"

echo "Executing AWS DynamoDB statement:"
echo "$CMD"
aws dynamodb execute-statement --region "$PORTAL_AWS_REGION" --statement "$CMD"
echo "Done."
