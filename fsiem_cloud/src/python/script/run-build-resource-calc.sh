#!/bin/bash -e

# Require sudo for running docker
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

# Build
docker-compose build --progress=plain fsiem-resource-calc
# Start container and make a build
docker-compose up --remove-orphans fsiem-resource-calc

echo "Copy executable fsiem_resource_calc from inside container back to host's ../terraform/fsiem_deploy/bin/"
DST_BIN=../terraform/fsiem_deploy/bin/fsiem_resource_calc
docker cp fsiem-resource-calc:/app/dist/fsiem_resource_calc $DST_BIN

# Replace root owner back to the user and add read permissions
# SUDO_USER is used to get the identifier of the user who called
chown -R $SUDO_USER:$SUDO_USER $DST_BIN
chmod +rx $DST_BIN
# Stop container
docker-compose down

# output from dists
ls -alh $DST_BIN

echo "*************"
echo "Staging newly built binary file to git"
git add $DST_BIN

# run test
echo "*************"
echo "Running tests"
echo "*************"
$DST_BIN --seats 5 --storage-type clickhouse
$DST_BIN --seats 5 --storage-type eventdb
$DST_BIN -s 5 -t clickhouse -o 1500 -m 500 | jq
