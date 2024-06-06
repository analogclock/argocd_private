#!/bin/bash

#
# Convert .p12 certificate into base64 encoded format. This is used for AWS
# secrets manager and the API to provide a Client Certificate
# for FortiCloud communications
# The outcome will be 1 file, and you could import them into AWS region:
#   - clientcert.json   (AWS: Secret Value)

set -uo pipefail

echo "This script converts .p12 certificate into required JSON format for certs"

FILE="$1"
if [ ! -f "$FILE" ]; then echo "File not found: $FILE"; exit 1; fi

# Thanks to https://unix.stackexchange.com/a/393484/510780
certBase=$(base64 -w 0 $FILE)
cat <<EOF >clientcert.json
{
  "certificate": "${certBase}"
}
EOF
echo "Done"
