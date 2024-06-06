ARG DOCKER_REGISTRY=""
ARG DOCKER_UBUNTU_VERSION
FROM ${DOCKER_REGISTRY}ubuntu:${DOCKER_UBUNTU_VERSION}

ARG NEXUS_PYPI_URL
ARG NEXUS_APT_PROXY
ARG NEXUS_APT_SECURITY_PROXY

# Remove meta information
RUN set -eux && \
    rm -rf /var/lib/apt/lists/ && \
    rm /etc/apt/sources.list

# append new sources to the sources lists
# trusted=yes -- these means we do not need a GPG key for this repository
# NOTE:: updating the base image version, will mean you need to update
# the code name in use
RUN set -eux && \
    echo "deb [trusted=yes] ${NEXUS_APT_PROXY} jammy main restricted universe multiverse\n\
deb [trusted=yes] ${NEXUS_APT_PROXY} jammy-updates main restricted universe multiverse\n\
deb [trusted=yes] ${NEXUS_APT_PROXY} jammy-backports main restricted universe multiverse\n\
deb [trusted=yes] ${NEXUS_APT_SECURITY_PROXY} jammy-security main restricted universe multiverse\n" > /etc/apt/sources.list

WORKDIR /app
COPY ./fsiem_resource_calc .

# note we need to switch verify peer off for the first time
# because the proxy will use a certificate that isn't bundled
# with ubuntu, but we get it the next time we run update-ca-certificates
RUN apt-get -o Acquire::https::Verify-Peer=0 update -qq > /dev/null && \
    apt-get -o Acquire::https::Verify-Peer=0 install -y --no-install-recommends \
    ca-certificates python3 python3-dev pip binutils > /dev/null && \
    update-ca-certificates

RUN pip3 install -r requirements.txt --quiet --no-cache-dir --no-build-isolation \
                 --index-url ${NEXUS_PYPI_URL}

RUN ./build/unittest.sh

ENTRYPOINT pyinstaller main.spec
