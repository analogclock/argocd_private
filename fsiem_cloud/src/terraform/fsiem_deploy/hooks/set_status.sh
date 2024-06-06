#!/bin/bash

# Updating DynamoDB record with a specified deployment status

echo "==> Executing a hook to set $1 status for $DEPLOYMENT_NAME"
echo "DynamoDB table (from env):  $DYNAMODB_ACTIVATION_TABLE"
echo "Deployment name (from env): $DEPLOYMENT_NAME"
echo "AWS region (from env):      $PORTAL_AWS_REGION"
echo "Status (from arg):          $1"

CMD="
UPDATE $DYNAMODB_ACTIVATION_TABLE
  SET status='$1'
WHERE
  serialNumber='$DEPLOYMENT_NAME'
"

echo "Executing AWS DynamoDB statement:"
echo "$CMD"
aws dynamodb execute-statement --region "$PORTAL_AWS_REGION" --statement "$CMD"
echo "Done."
