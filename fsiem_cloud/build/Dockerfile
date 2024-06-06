# Create a docker build environment for FSIEM SaaS project.
# The script simply invokes a bootstrap scrip file that installs all the build dependencies.
# Please note, you should call this file from the _root_ folder, e.g.:
#
#   cd ~/git/fsiem_cloud
#   sudo docker build -f ./build/Dockerfile .
#
# This is done to keep the root of the project clean.
ARG DOCKER_REGISTRY=""
ARG DOCKER_UBUNTU_VERSION=""
FROM --platform=linux/amd64 ${DOCKER_REGISTRY}ubuntu:${DOCKER_UBUNTU_VERSION}

ARG NEXUS_APT_PROXY
ARG NEXUS_APT_SECURITY_PROXY
ARG NEXUS_DOCKER_APT_PROXY
ARG NEXUS_AWS_PROXY
ARG NEXUS_HASHICORP_PROXY
ARG NEXUS_GITHUB_PROXY
ARG BUILD_HTTP_PROXY

# Removes interactive question for TZ (timezone)
# without this line it will ask you for a default time zone, and hault creating of the image
ARG DEBIAN_FRONTEND=noninteractive

# Python PYPI url
ARG NEXUS_PYPI_URL

# Ignore the message about adding repo keys, e.g. Hashi Corp keys
ARG APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

# Python PYPI url saved to environment variable required during build
ENV NEXUS_PYPI_URL=${NEXUS_PYPI_URL}

ENV BUILD_HTTP_PROXY=${BUILD_HTTP_PROXY}
ENV NEXUS_AWS_PROXY=${NEXUS_AWS_PROXY}
ENV NEXUS_HASHICORP_PROXY=${NEXUS_HASHICORP_PROXY}
ENV NEXUS_GITHUB_PROXY=${NEXUS_GITHUB_PROXY}

RUN set -eux && \
    # Remove Ubuntu repos, we are using Nexus
    rm -rf /var/lib/apt/lists/ && \
    rm /etc/apt/sources.list && \
    # Insert Nexus repo source
    # trusted=yes -- this means we do not need a GPG key for this repository
    # NOTE: when updating the base image version, you need to update code name - jammy
    echo "deb [trusted=yes] ${NEXUS_APT_PROXY} jammy main restricted universe multiverse\n\
deb [trusted=yes] ${NEXUS_APT_PROXY} jammy-updates main restricted universe multiverse\n\
deb [trusted=yes] ${NEXUS_APT_PROXY} jammy-backports main restricted universe multiverse\n\
deb [trusted=yes] ${NEXUS_APT_SECURITY_PROXY} jammy-security main restricted universe multiverse\n\
deb [arch=amd64 trusted=yes] ${NEXUS_DOCKER_APT_PROXY} jammy stable\n" > /etc/apt/sources.list && \
    # Install ca-certificates package, we need to switch verify peer off for the
    # first time because the proxy will use a certificate that isn't bundled
    # with Ubuntu, but we get it the next time we run update-ca-certificates
    apt-get -o Acquire::https::Verify-Peer=0 update && \
    apt-get -o Acquire::https::Verify-Peer=0 install -y --no-install-recommends ca-certificates && \
    update-ca-certificates

WORKDIR /saas_repo

COPY ./build ./build

RUN ./build/bootstrap.sh
