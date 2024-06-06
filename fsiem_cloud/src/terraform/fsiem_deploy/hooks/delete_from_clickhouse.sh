#!/bin/bash

# Updating DynamoDB record with a specified deployment status

echo "==> Executing a hook to remove data during destroy"
echo "Deployment name (from env): $DEPLOYMENT_NAME"
echo "AWS region (from env):      $AWS_REGION"
echo "Environment (from env):     $ENVIRONMENT"

echo "Executing AWS s3 delete statement, delete data dir:"
aws s3 rm --recursive s3://fsiem-clickhouse-data-$AWS_REGION-$ENVIRONMENT/$DEPLOYMENT_NAME/

echo "Executing AWS s3 delete statement, delete archive dir:"
aws s3 rm --recursive s3://fsiem-clickhouse-backups-$AWS_REGION-$ENVIRONMENT/$DEPLOYMENT_NAME/

echo "Done."
