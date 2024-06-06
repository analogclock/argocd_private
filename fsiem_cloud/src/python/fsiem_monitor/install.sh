#!/bin/bash -e

echo "Customer Key:        $CUSTOMER_KEY"
echo "Tags:                $TAGS"
echo "Plugin Url:          $PLUGIN_URL"
echo "Environment:         $ENVIRONMENT"
echo "SerialNumber:        $SERIAL_NUMBER"
echo "Super URL:           $SUPER_URL"
echo "DynamoDB Table:      $DYNAMODB_ACTIVATION_TABLE"
echo "DynamoDB Region:     $DYNAMODB_REGION"
# echo "Secret Auth:         $SECRET_VM_AUTH"
echo "Cognito URL:         $COGNITO_URL"
echo "Region:              $REGION"

# Adds variables to /tmp/vars.json which the python script will read
client_id=$(echo "$SECRET_VM_AUTH" | jq '.client_id')
client_secret=$(echo "$SECRET_VM_AUTH" | jq '.client_secret')
cat > /tmp/vars.json <<EOF
{
  "super_url": "$SUPER_URL",
  "serial_number": "$SERIAL_NUMBER",
  "client_id": ${client_id},
  "client_secret": ${client_secret},
  "cognito_url": "$COGNITO_URL",
  "region": "$REGION",
  "aws_creds_url": "${AWS_CONTAINER_CREDENTIALS_RELATIVE_URI}"
}
EOF

# Create the manifest file and insert values
# server_key is defined and unique across all deployments
# server_key is always the same for this particular deployment
cat > /etc/fm-agent-manifest <<EOF
[agent]
customer_key = $CUSTOMER_KEY
tags = $TAGS
disable_server_match = true
server_key = ${SERIAL_NUMBER}_${ENVIRONMENT}_fsiemcontainer
fqdn = ${SERIAL_NUMBER}_fsiemcontainer
[attributes]
Environment = $ENVIRONMENT
SerialNumber = $SERIAL_NUMBER
EOF

# Install doesn't start cron, we need to start it manually
service cron start

curl -fsSL "https://repo.fortimonitor.com/install/linux_fm_agent_install.py" -o "/linux_agent_install.py"
python /linux_agent_install.py

printf '%s\n' "$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI" >/tmp/aws_cred_uri

cp fsiem_api.py /usr/share/fm-agent/fsiem_api.py
chmod +x /usr/share/fm-agent/fsiem_api.py

# Run scrape_metrics.py and add cron job
python /app/fsiem_monitor/scrape_metrics.py > /var/log/scrape_metrics.log
echo "*/2 * * * *    root    /usr/bin/python /app/fsiem_monitor/scrape_metrics.py"  > /etc/cron.d/scrape_metrics

# Debug version of cronjob
# echo "*/2 * * * *    root    /usr/bin/python /app/fsiem_monitor/scrape_metrics.py >> /var/log/scrape_metrics.log 2>&1"  > /etc/cron.d/scrape_metrics

# Tail the logs to prevent the container exiting and to get the fm logs.
# timeout 1h ensures the tail command will end after an hour which will kill the container
timeout 1h tail -f /var/log/fm-agent/fm-agent.log

# Use this to debug scrape_metrics.log
# tail -f /var/log/scrape_metrics.log
