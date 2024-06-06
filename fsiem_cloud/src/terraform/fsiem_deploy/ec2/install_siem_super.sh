#! /bin/bash -xe

exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Downloading scripts"
aws s3 cp --recursive "s3://${s3_scripts_bucket}" --region "${s3_scripts_bucket_region}" "/home/${user}/scripts/"
chown -R "${user}:${user}" "/home/${user}/scripts/"
chmod -R 755 "/home/${user}/scripts/"
echo "Schedule JWT script to pull the auth key from AWS Cognito"
echo "*/5 * * * * root /home/${user}/scripts/cognito_update_keys.sh > /tmp/cognito_update_keys.log 2>&1" > /etc/cron.d/jwt-key-download
echo "Installing fortimonitor agent"
cat > /etc/fm-agent-manifest <<EOF
[agent]
customer_key = ${id}
tags = ${serial_no},super,fsiem
disable_server_match = true
server_key = ${fmon_server_key}
fqdn = ${fmon_server_key}
[attributes]
Environment = ${env}
SerialNumber = ${serial_no}
EOF

# We have to install, uninstall, then reinstall fortimonitor due to a bug in fortimonitor
curl --retry 5 --retry-delay 3 -fsSL "https://repo.fortimonitor.com/install/linux_fm_agent_install.py" -o "/tmp/linux_agent_install.py"
python3 /tmp/linux_agent_install.py
yum remove -y fm-agent
python3 /tmp/linux_agent_install.py
mv "/home/${user}/scripts/fsiem.py" /usr/share/fm-agent/fsiem.py
rm /tmp/linux_agent_install.py
echo "* * * * * root /bin/cp -f /opt/phoenix/cache/EventPerSecInfo /tmp/EventPerSecInfo && chown fm-agent:fm-agent /tmp/EventPerSecInfo" > /etc/cron.d/EventPerSecInfo

echo "Checking if all required disks are present"
echo "Will wait disks attachments for 10 minutes max"
# num_exp_disks=7 # for worker (1 root, 5 clickhouse, 1 opt)
# num_exp_disks=3 # for keeper (1 root, 1 clickhouse, 1 opt)
for ((i = 0; i < 60 ; i++ )); do
    NUM_ACTUAL_DISKS=$(ls -l /sys/block/*/device | wc -l)
    if [ ${num_exp_disks} -gt $NUM_ACTUAL_DISKS ]; then
        echo "WARN: Waiting for disks. Expected: ${num_exp_disks}, actual: $NUM_ACTUAL_DISKS..."
        sleep 10
    else
	      echo "All expected disks have been attached and are available"
        break
    fi
done
if [ ${num_exp_disks} -gt $NUM_ACTUAL_DISKS ]; then echo "ERROR: Expected disks not found"; fi

echo "Running FortiSiem setup"
local_ip=`curl http://169.254.169.254/latest/meta-data/local-ipv4`
gateway_ip=`ip route show 0.0.0.0/0 dev eth0 | cut -d\  -f3`
host_fqdn="${host_input}"
/usr/local/bin/configureFSM.py -r super -z Etc/UTC -i $local_ip -m 255.255.255.0 -g $gateway_ip --host $host_fqdn -t 4 --dns1 10.0.0.2 -o install_without_fips --testpinghost google.com
