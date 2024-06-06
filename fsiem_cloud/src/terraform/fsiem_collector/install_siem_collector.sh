#! /bin/bash -xe

exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
echo "Downloading scripts"
aws s3 cp --recursive "s3://${s3_scripts_bucket}" --region "${s3_scripts_bucket_region}" "/home/${user}/scripts/"
chown -R "${user}:${user}" "/home/${user}/scripts/"
chmod -R 755 "/home/${user}/scripts/"
echo "* * * * * root /bin/cp -f /opt/phoenix/cache/EventPerSecInfo /tmp/EventPerSecInfo && chown panopta-agent:panopta-agent /tmp/EventPerSecInfo" > /etc/cron.d/EventPerSecInfo
echo "Downloading ec2test2.tar"
cd /root
wget https://scalability.s3.amazonaws.com/ec2test2.tar
echo "Un-tar ec2test2.tar"
tar -xvf ec2test2.tar
echo "Running FortiSiem setup"
local_ip=`curl http://169.254.169.254/latest/meta-data/local-ipv4`
local_hostname=`curl http://169.254.169.254/latest/meta-data/local-hostname`
gateway_ip=`ip route show 0.0.0.0/0 dev eth0 | cut -d\  -f3`
/usr/local/bin/configureFSM.py -r collector -z Etc/UTC -i $local_ip -m 255.255.255.0 -g $gateway_ip --host $local_hostname -t 4 --dns1 10.0.0.2 -o install_without_fips --testpinghost google.com
