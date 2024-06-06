#!/bin/bash

#
# This script copies an existing AMI to all supported regions
# Example usage:
# ./copy_image_all_regions.sh "ami-0e6504d3a6cc4becd" "FortiSIEM-VA-6.7.0.1951"

copy_ami() {
  echo "Region: $3"
  aws ec2 copy-image \
    --source-region us-east-1 \
    --region $3 \
    --name $2 \
    --source-image-id $1 \
    --encrypted
}

AMI_REGIONS=(
  "eu-central-1" "eu-west-1" "eu-west-2" "eu-west-3" "eu-north-1" "us-east-2" "us-west-2"
  "ca-central-1" "ap-south-1" "ap-southeast-1" "ap-southeast-2" "me-south-1" "af-south-1" "ap-east-1"
)
for i in "${AMI_REGIONS[@]}"; do copy_ami $1 $2 "$i"; done
