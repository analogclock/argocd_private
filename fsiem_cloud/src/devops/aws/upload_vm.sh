#!/bin/bash

#
# Upload FortiSiem qcow2 VM file to fsiem-terraform/qcow2/
# Sometimes you can upload it manually in S3, but because the file is
# larger than 5 GB, I (OM) had uploads failed several times around 90% mark.
# It was something to do with multi-part upload and `asw s3 cp`
# uses it by default, unlike browser upload.
#

set -uo pipefail

# Path on the local system to the qcow2 file
SRC=FortiSIEM-VA-6.4.0.1518.qcow2

# This is where we want it to go
# AWS_REGION=eu-west-1
# AWS_ACCOUNT_ID=023941436530
# AWS_BUCKET=fsiem-terraform
DST=s3://fsiem-terraform/qcow2/

echo "Copying $SRC ==> $DST. Please wait..."
aws s3 cp $SRC $DST
echo "File was copied successfully"
