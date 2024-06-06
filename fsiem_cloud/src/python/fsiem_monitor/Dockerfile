ARG DOCKER_REGISTRY=""
ARG DOCKER_UBUNTU_VERSION
FROM ${DOCKER_REGISTRY}ubuntu:${DOCKER_UBUNTU_VERSION}

ARG NEXUS_APT_PROXY
ARG NEXUS_APT_SECURITY_PROXY
ARG NEXUS_DOCKER_APT_PROXY
ARG NEXUS_AWS_PROXY
ARG NEXUS_HASHICORP_PROXY
ARG NEXUS_GITHUB_PROXY

# Removes interactive question for TZ (timezone)
# without this line it will ask you for a default time zone, and hault creating of the image
ARG DEBIAN_FRONTEND=noninteractive

# Python PYPI url
ARG NEXUS_PYPI_URL

# Ignore the message about adding repo keys, e.g. Hashi Corp keys
ARG APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

# Python PYPI url saved to environment variable required during build
ENV NEXUS_PYPI_URL=${NEXUS_PYPI_URL}

WORKDIR /app/fsiem_monitor
COPY ./fsiem_monitor/install.sh .
COPY ./fsiem_monitor/requirements.txt .
COPY ./fsiem_monitor/scrape_metrics.py .
COPY ./fsiem_api_client /app/fsiem_api_client

COPY ./fsiem_monitor/fsiem_api.py .

ENV CUSTOMER_KEY=""
ENV TAGS=""
ENV PLUGIN_URL=""
ENV ENVIRONMENT=""
ENV SERIAL_NUMBER=""
ENV SUPER_URL=""
ENV DYNAMODB_ACTIVATION_TABLE=""
ENV DYNAMODB_REGION=""
ENV SECRET_VM_AUTH=""
ENV COGNITO_URL=""
ENV REGION=""

RUN set -eux && \
    # Make backup of default sources.list
    cp /etc/apt/sources.list /tmp/sources.list && \
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
    apt-get -o Acquire::https::Verify-Peer=0 install -y --no-install-recommends python3-pip python-is-python3 curl cron jq && \
    pip3 install -r requirements.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
    chmod +x install.sh && \
    # Revert sources.list back to its default state without the proxy settings
    rm /etc/apt/sources.list && \
    cp /tmp/sources.list /etc/apt/sources.list

ENTRYPOINT ./install.sh
