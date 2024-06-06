#!/bin/bash -e

# This script is used to keep JWK keys fresh and
# the logic is based on https://stackoverflow.com/a/67943659/706456.
#
# This is how it works:
# - Check if /opt/phoenix/config/cloud/jwks.json exists
#   - If it doesn't exist, create the file and adjust permissions and ownership
# - Download a fresh copy of keys from AWS Cognito
# - Compare new keys with the contents of /opt/phoenix/config/cloud/jwks.json
#   - If they are different, overwrite the file with new keys
#   - Adjust permissions and ownership of the file
#   - Restart app server

# To debug this script, add -x to parameters
set -Eeou pipefail

# this uses terraform template file to replace cognito_url
# with the one passed in via params
URL="${cognito_url}"
PUBLIC_KEY_FILE="/opt/phoenix/config/cloud/jwks.json"
PUBLIC_KEY_TEMP_FILE="/tmp/jwks.json"

if [ ! -f "$PUBLIC_KEY_FILE" ]; then
    echo "==> File $PUBLIC_KEY_FILE does not exist, creating it"
    install -D /dev/null $PUBLIC_KEY_FILE
    # Set user and group to admin
    chown admin:admin $PUBLIC_KEY_FILE
    # Set permissions to rwxr-xr-x, like other config files
    chmod 751 $PUBLIC_KEY_FILE
    echo "OK"
fi

echo "==> HTTP GET JWT"
echo "Source URL: $URL"
JWKS_URI=$(curl -s $URL | jq -r '.jwks_uri')
echo "OK"

echo "==> Save new JWT keys"
echo "Destination file: $PUBLIC_KEY_TEMP_FILE"
JWKS_URI=$(curl -s $JWKS_URI | jq > $PUBLIC_KEY_TEMP_FILE )
echo "OK"

echo "==> Compare old and new keys"
if cmp -s "$PUBLIC_KEY_TEMP_FILE" "$PUBLIC_KEY_FILE"; then
    echo "Keys are the same, no work required"
    exit 0
fi
echo "Keys are different, updating"
echo "Replacing $PUBLIC_KEY_FILE and adjusting permissions"
mv $PUBLIC_KEY_TEMP_FILE $PUBLIC_KEY_FILE
# Set user and group to admin
chown admin:admin $PUBLIC_KEY_FILE
# Set permissions to rwxr-xr-x, like other config files
chmod 751 $PUBLIC_KEY_FILE

echo "==> Restarting app server"
/opt/glassfish/bin/asadmin stop-domain domain1
echo "OK"

