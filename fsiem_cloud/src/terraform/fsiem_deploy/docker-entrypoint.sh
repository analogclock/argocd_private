#!/bin/bash
# This script is a wrapper for main logic: if deployment fails, exit code is set to
# non-zero value, and we update record in DynamoDb, to set status to UpdateFailed or
# CreateFailed.

# Execute main logic
./run-terraform.sh

# If exit code is not 0 (success), update DynamoDb record
exit_code=$?
echo "run-terraform.sh exit code: $exit_code"

if [ $exit_code -ne 0 ]; then

  updating_deployment=${UPDATING_DEPLOYMENT:-false}
  echo "Deployment did not succeded, update deployment status to failure"

  if [ "$updating_deployment" = "true" ]; then
    ./hooks/set_status.sh "UpdateFailed"
  else
    ./hooks/set_status.sh "CreateFailed"
  fi

fi
