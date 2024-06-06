#!/bin/bash

# Get available regions from AWS and print them out
# This can be used in terraform, for example.
REGIONS=$(aws ec2 describe-regions --output json | \
          jq '.Regions[].RegionName' | sort | tr "\\n" " " | tr -d "\"")

echo "Print draft region to timezone map (time zone is empty)"
echo "Check https://aws.amazon.com/about-aws/global-infrastructure/regions_az/"
printf "\n"

for r in $REGIONS ; do
    printf "\"${r}\" = \"\"\\n"
done
