#!/bin/bash

#
# This script creates a user with sudo privileges.
#

set -uo pipefail

USERNAME=cloud-user

echo "Add $USERNAME group"
groupadd USERNAME

echo "Add $USERNAME account"
adduser $USERNAME -g $USERNAME -G wheel,adm
mkdir -p ~$USERNAME/.ssh
chown $USERNAME:$USERNAME ~$USERNAME/.ssh
chmod 700 ~$USERNAME/.ssh
mkdir -p ~root/.ssh
chmod 700 ~root/.ssh

echo "[$(date +"%F:%T")] [warn] User [$USERNAME] has been created and granted sudo privileges"
