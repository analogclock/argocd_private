#!/bin/bash

#
# Call lambda function from local dev machine
#
# Example usage: ./invoke.sh

NAME='fsiem_s3_tag_playground'
PAYLOAD=$(cat <<EOF
{
  "region": "us-east-1",
  "sn": "FSMCLD0000000177",
  "account_id": "023941436530",
  "role_arn": "arn:aws:iam::023941436530:role/lambda-fsiem-s3-tag-playground",
  "manifest_bucket": "fsiem-s3-job-playground",
  "manifest_tags": "SerialNumber=FSMCLD0000000177",
  "bucket": "fsiem-clickhouse-data-us-east-1-dev",
  "prefix": "FSMCLD0000000177"
}
EOF
)

echo "Invoking lambda: $NAME"
echo "Payload:"
echo $PAYLOAD | jq

echo "API response"
aws lambda invoke --function-name $NAME --payload "$PAYLOAD" \
    --cli-binary-format raw-in-base64-out out.json

echo "Result:"
cat out.json | jq
