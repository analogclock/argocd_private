#!/bin/bash

# Shamelessly stolen from https://winder.ai/how-to-list-all-amis-for-each-region-in-aws/
# Except the author didn't know how escape characters work so I fixed that

if [ -z "$1" ] ; then
    echo "Please pass the name of the AMI"
    exit 1
fi

IMAGE_FILTER="${1}"

REGIONS=$(aws ec2 describe-regions --output json | jq '.Regions[].RegionName' | tr "\\n" " " | tr -d "\"")

for r in $REGIONS ; do
    ami=$(aws ec2 describe-images --query 'Images[*].[ImageId]' --filters "Name=name,Values=${IMAGE_FILTER}" "Name=product-code.type,Values=marketplace" --region ${r} --output json | jq '.[0][0]')
    printf "\"${r}\" = ${ami}\\n"
done
