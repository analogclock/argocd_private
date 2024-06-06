#!/bin/bash -e

# This is required to be run once on every new build machine.
# Script to configure company proxy for offline builds and reboot docker.

mkdir -p /etc/systemd/system/docker.service.d
echo $'[Service]\nEnvironment="HTTPS_PROXY=http://172.30.41.250:3128"\nEnvironment="NO_PROXY=dops-nexus.fortinet-us.com"' \
| sudo tee -a /etc/systemd/system/docker.service.d/http-proxy.conf

echo "reload docker daemon"
systemctl daemon-reload

echo "restart docker"
systemctl restart docker

echo "show property"
systemctl show --property=Environment docker
