#!/bin/bash

#
# Scan system for users names, print out their public keys that the system is trusting.
#
set -uo pipefail

for USER_HOME in $(cut -f6 -d ':' /etc/passwd | sort | uniq); do
    if [ -s "$USER_HOME/.ssh/authorized_keys" ]; then
        echo "[$(date +"%F:%T")] [warn] SSH key [${USER_HOME}/.ssh/authorized_keys] -- [$(cat "${USER_HOME}/.ssh/authorized_keys")]"
    fi
done
