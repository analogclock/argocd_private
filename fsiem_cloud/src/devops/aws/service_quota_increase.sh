#!/bin/bash

#
# This script requests a service qouta increase
# Example usage:
# ./service_quota_increase.sh "us-east-1" "aws-service-quota-admin"

set -uo pipefail

REG=$1
PROF=$2
echo "AWS: requesting more resources in '$REG' using '$PROF'"
  
#EC2
echo "Increase 'EC2-VPC Elastic IPs' to 50"
aws service-quotas request-service-quota-increase --region "$REG" --profile "$PROF" \
  --service-code ec2 --quota-code L-0263D0A3 --desired-value 50

# VPC
echo "Increase 'VPCs per REG' to 50"
aws service-quotas request-service-quota-increase --region "$REG" --profile "$PROF" \
  --service-code vpc --quota-code L-F678F1CE --desired-value 50

echo "Increase 'Security groups per network interface' to 10"
aws service-quotas request-service-quota-increase --region "$REG" --profile "$PROF" \
  --service-code vpc --quota-code L-2AFB9258 --desired-value 10

echo "Increase 'NAT gateways per Availability Zone' to 10"
aws service-quotas request-service-quota-increase --region "$REG" --profile "$PROF" \
  --service-code vpc --quota-code L-FE5A380F --desired-value 10

echo "Increase 'IPv4 CIDR blocks per VPC' to 10"
aws service-quotas request-service-quota-increase --region "$REG" --profile "$PROF" \
  --service-code vpc --quota-code L-83CA0A9D --desired-value 10

echo -e "\nDone"
