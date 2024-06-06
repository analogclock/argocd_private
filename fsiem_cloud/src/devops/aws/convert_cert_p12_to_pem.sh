#!/bin/bash

#
# Convert .p12 certificate into .pem format. This is used for AWS certificate management.
# The outcome will be 3 files, and you could import them into AWS region:
#   - clientcert.key    (AWS: Certificate body)
#   - clientcert.cer    (AWS: Certificate private key)
#   - cacerts.cer       (AWS: Certificate chain)

set -uo pipefail

echo "This script converts .p12 certificate into .pem files"
echo "If passphrase is used, you must input it for openssl to convert the file"
echo "Expect to provide a p12 file passphrase for the export (3 times: for a key, a cert, and a CA exports)"

FILE="$1"
if [ ! -f "$FILE" ]; then echo "File not found: $FILE"; exit 1; fi

# Thanks to https://unix.stackexchange.com/a/393484/510780
echo "Step 1. Create key file"
openssl pkcs12 -in "$FILE" -nocerts -nodes | sed -ne '/-BEGIN PRIVATE KEY-/,/-END PRIVATE KEY-/p' > 2_clientcert.key
echo "Step 2. Create certificate file"
openssl pkcs12 -in "$FILE" -clcerts -nokeys | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > 1_clientcert.cer
echo "Step 3. Create CA file"
openssl pkcs12 -in "$FILE" -cacerts -nokeys | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > 3_cacerts.cer

echo "Done"
