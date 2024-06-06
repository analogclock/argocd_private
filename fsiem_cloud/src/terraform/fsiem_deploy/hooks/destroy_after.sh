#!/bin/bash

# Removing items from DynamoDB tables
# Triggered by Terragrunt after_hook on destroy's.
echo "==> Executing a hook after destroying a deployment"
echo "DynamoDB backup options table     : $DYNAMODB_BACKUP_OPTIONS_TABLE"
echo "DynamoDB compute override table   : $DYNAMODB_COMPUTE_OVERRIDE_TABLE"
echo "DynamoDB activation table         : $DYNAMODB_ACTIVATION_TABLE"
echo "DynamoDB backup table             : $DYNAMODB_BACKUP_TABLE"
echo "DynamoDB restore table            : $DYNAMODB_RESTORE_TABLE"
echo "DynamoDB scheduled upgrades table : $DYNAMODB_SCHEDULE_UPGRADES_TABLE"
echo "DynamoDB POC approval table       : $DYNAMODB_POC_APPROVAL_TABLE"
echo "DynamoDB storage approval table   : $DYNAMODB_STORAGE_APPROVAL_TABLE"
echo "DynamoDB ext storage table        : $DYNAMODB_EXT_STORAGE_TABLE"
echo "DynamoDB ext storage status table : $DYNAMODB_EXT_STORAGE_STATUS_TABLE"
echo "Deployment name                   : $DEPLOYMENT_NAME"
echo "AWS region                        : $PORTAL_AWS_REGION"

# A map of DynamoDB table name to it's range key. Some tables do not have range
# key, so the value is empty string. For example:
#
# fsiem_backup_options_playground           => ""
# fsiem_compute_override_playground         => ""
# fsiem_clickhouse_backup_playground        => "name"
# fsiem_scheduled_upgrades_table_playground => "upgradePath"
#
declare -Ar TABLE_RANGE_KEY_MAP=(
  ["$DYNAMODB_BACKUP_OPTIONS_TABLE"]=""
  ["$DYNAMODB_COMPUTE_OVERRIDE_TABLE"]=""
  ["$DYNAMODB_ACTIVATION_TABLE"]=""
  ["$DYNAMODB_POC_APPROVAL_TABLE"]=""
  ["$DYNAMODB_STORAGE_APPROVAL_TABLE"]=""

  ["$DYNAMODB_BACKUP_TABLE"]="name"
  ["$DYNAMODB_RESTORE_TABLE"]="name"
  ["$DYNAMODB_SCHEDULE_UPGRADES_TABLE"]="upgradePath"
  ["$DYNAMODB_EXT_STORAGE_TABLE"]="organizationId"
  ["$DYNAMODB_EXT_STORAGE_STATUS_TABLE"]="startDateTime"
)

# Loop over each DynamoDb table
for TABLE in "${!TABLE_RANGE_KEY_MAP[@]}"; do

  RANGE_KEY=${TABLE_RANGE_KEY_MAP[${TABLE}]}

  # If range key is empty, we have a DynamoDb table with a single partition key.
  # We can run a single DELETE command to delete a single row.
  if [ "$RANGE_KEY" == "" ]; then
    CMD="DELETE FROM $TABLE WHERE serialNumber='$DEPLOYMENT_NAME'"
    echo "$CMD"
    aws dynamodb execute-statement --region "$PORTAL_AWS_REGION" --statement "$CMD"

  # We have a range key. We need to first select all the range keys given one
  # partition key (we assume partition key is always "serialNumber").
  # Then we can delete all rows using partition key and range key.
  else
    CMD="SELECT $RANGE_KEY FROM $TABLE WHERE serialNumber='$DEPLOYMENT_NAME'"
    echo "$CMD"
    RANGE_KEY_VALUES=$(
      aws dynamodb execute-statement --region "$PORTAL_AWS_REGION" --statement "$CMD" --output json |
        jq --raw-output ".Items[].$RANGE_KEY.S // .Items[].$RANGE_KEY.N"
    )
    CMD="aws dynamodb describe-table --table-name $TABLE --query "Table.AttributeDefinitions[?AttributeName==\`\"$RANGE_KEY\"\`].AttributeType" | jq --raw-output '.[0]'"
    echo "$CMD"
    RANGE_KEY_TYPE=$(aws dynamodb describe-table --table-name $TABLE --region "$PORTAL_AWS_REGION" --query "Table.AttributeDefinitions[?AttributeName==\`\"$RANGE_KEY\"\`].AttributeType" | jq --raw-output '.[0]')
    for RANGE_KEY_VALUE in $RANGE_KEY_VALUES; do
      echo "Deleting item $DEPLOYMENT_NAME:$RANGE_KEY_VALUE from table $TABLE"
      CMD="DELETE FROM $TABLE WHERE serialNumber='$DEPLOYMENT_NAME' AND $RANGE_KEY=$(if [[ \"$RANGE_KEY_TYPE\" == \"S\" ]]; then echo "'$RANGE_KEY_VALUE'"; else echo "$RANGE_KEY_VALUE"; fi)"
      echo "$CMD"
      aws dynamodb execute-statement --region "$PORTAL_AWS_REGION" --statement "$CMD"
    done
  fi
  echo "> $TABLE - cleaned"
done

echo "DynamoDB tables were cleaned"
echo "Done"
