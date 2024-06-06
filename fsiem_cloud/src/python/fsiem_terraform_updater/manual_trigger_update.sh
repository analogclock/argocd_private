#!/bin/bash -e
# Manualy schedule an upgrade for an env (dev/playground)
# Example usage:
#     ./manual_trigger_update.sh
#         OR
#     ./manual_trigger_update.sh "fsiem_activation_table_playground" \
#         "us-east-1" "portal-bus-playground"
echo "This script is for dev testing. It schedules an update process for env."


# Argument to the script, if none is provided we default to playground values
DYNAMO_TABLE=$1
AWS_REGION=$2
EVENT_BUS_NAME=$3

# This means variable not given as an argument to this script.
# Assign default values, assuming default is playground env
if [ -z "${DYNAMO_TABLE}" ]; then
  echo "Assuming DYNAMO_TABLE:   fsiem_activation_table_playground"
  DYNAMO_TABLE=fsiem_activation_table_playground
fi

if [ -z "${AWS_REGION}" ]; then
  echo "Assuming AWS_REGION:  us-east-1"
  AWS_REGION=us-east-1
fi

if [ -z "${EVENT_BUS_NAME}" ]; then
  echo "Assuming EVENT_BUS_NAME: portal-bus-playground"
  EVENT_BUS_NAME=portal-bus-playground
fi

echo "Executing python script:"

set -x
python3 main.py                       \
  --dynamodb_table  "$DYNAMO_TABLE"   \
  --dynamodb_region "$AWS_REGION"  \
  --event_bus_name  "$EVENT_BUS_NAME"
