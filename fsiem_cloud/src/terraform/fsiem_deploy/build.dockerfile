ARG DOCKER_REGISTRY=""
ARG DOCKER_UBUNTU_VERSION
FROM ${DOCKER_REGISTRY}ubuntu:${DOCKER_UBUNTU_VERSION}

ARG NEXUS_APT_PROXY
ARG NEXUS_APT_SECURITY_PROXY
ARG NEXUS_AWS_PROXY
ARG NEXUS_HASHICORP_PROXY
ARG NEXUS_GITHUB_PROXY
ARG NEXUS_TERRAFORM_PROXY
ARG TF_VERSION="1.5.7"
ARG TERRAGRUNT_VERSION="v0.48.6"
ARG AWS_CLI_VERSION="2.13.7"

ENV NEXUS_APT_PROXY=${NEXUS_APT_PROXY}
ENV NEXUS_APT_SECURITY_PROXY=${NEXUS_APT_SECURITY_PROXY}
ENV NEXUS_AWS_PROXY=${NEXUS_AWS_PROXY}
ENV NEXUS_HASHICORP_PROXY=${NEXUS_HASHICORP_PROXY}
ENV NEXUS_GITHUB_PROXY=${NEXUS_GITHUB_PROXY}
ENV NEXUS_TERRAFORM_PROXY=${NEXUS_TERRAFORM_PROXY}

# AWS region where you want to deploy the resources
ENV AWS_REGION="us-east-1"
# AWS region where the portal and ecs task are running from
ENV PORTAL_AWS_REGION="us-east-1"
ENV DYNAMODB_ACTIVATION_TABLE="fsiem_activation_table_dev"
ENV DYNAMODB_BACKUP_TABLE="fsiem_clickhouse_backup_dev"
ENV DYNAMODB_BACKUP_OPTIONS_TABLE="fsiem_backup_options_dev"
ENV DYNAMODB_RESTORE_TABLE="fsiem_clickhouse_restore_dev"
ENV DYNAMODB_COMPUTE_OVERRIDE_TABLE="fsiem_compute_override_dev"
ENV DYNAMODB_SCHEDULE_UPGRADES_TABLE="fsiem_scheduled_upgrades_table_dev"
ENV DYNAMODB_POC_APPROVAL_TABLE="fsiem_poc_approval_table_dev"
ENV DYNAMODB_STORAGE_APPROVAL_TABLE="fsiem_storage_approval_table_dev"
ENV DYNAMODB_EXT_STORAGE_TABLE="fsiem_external_storage_table_dev"
ENV DYNAMODB_EXT_STORAGE_STATUS_TABLE="fsiem_external_storage_status_table_dev"
ENV DEPLOYMENT_BUCKET="fsiem-terraform"
ENV DEPLOYMENT_BUCKET_REGION="us-east-1"
ENV DEPLOYMENT_NAME="new_deployment"
ENV DEPLOYMENT_ACTION="apply"
ENV DEPLOYMENT_TYPE="va"
ENV DEPLOYMENT_EMAIL="test@test.com"
ENV UPDATING_DEPLOYMENT="false"
ENV IS_POC="false"
ENV IPV4_CIDRS="0.0.0.0/0"
ENV IPV6_CIDRS="::/0"
ENV COMPUTE_SIZE="5"
ENV LIVE_STORAGE="1"
ENV ARCHIVE_STORAGE="1"
ENV ALTERNATE_DOMAIN_CERTIFICATE_ARN=""
ENV PRIMARY_AZ=""
ENV EXTERNAL_STORAGE_DEST=""
# Install packages and apps needed for deployment
RUN set -eux; \
    # Remove meta information
    rm -rf /var/lib/apt/lists/ && \
    rm /etc/apt/sources.list && \
    # append new sources to the sources lists
    # trusted=yes -- these means we do not need a GPG key for this repository
    # NOTE:: updating the base image version, will mean you need to update
    # the code name in use
    echo "deb [trusted=yes] ${NEXUS_APT_PROXY} jammy main restricted universe multiverse\n\
deb [trusted=yes] ${NEXUS_APT_PROXY} jammy-updates main restricted universe multiverse\n\
deb [trusted=yes] ${NEXUS_APT_PROXY} jammy-backports main restricted universe multiverse\n\
deb [trusted=yes] ${NEXUS_APT_SECURITY_PROXY} jammy-security main restricted universe multiverse\n" > /etc/apt/sources.list && \
    # install ca-certificates package
    # note we need to switch verify peer off for the first time
    # because the proxy will use a certificate that isn't bundled
    # with ubuntu, but we get it the next time we run update-ca-certificates
    # Note git is used by terraform and it's required in runtime
    apt-get -o Acquire::https::Verify-Peer=0 update -qq > /dev/null; \
    apt-get -o Acquire::https::Verify-Peer=0 upgrade -y > /dev/null; \
    apt-get -o Acquire::https::Verify-Peer=0 install -y --no-install-recommends \
            ca-certificates git jq unzip curl upx > /dev/null && \
    update-ca-certificates && \
    # Install AWS CLI
    curl -LsS "${NEXUS_AWS_PROXY}/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip" -o "awscliv2.zip" && \
    unzip -qq awscliv2.zip && \
    ./aws/install > /dev/null && \
    find /usr/local/aws-cli -type f -name "*.so" | grep -v "lib-dynload" | xargs upx && \
    rm awscliv2.zip && \
    rm -rf aws/ && \
    rm -rf /usr/local/aws-cli/v2/*/dist/awscli/examples  && \
    # Install terraform
    curl -LsS "${NEXUS_HASHICORP_PROXY}/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip" -o terraform.zip && \
    unzip -qq terraform.zip && \
    mv terraform /usr/local/bin/terraform && \
    chmod +x /usr/local/bin/terraform && \
    upx /usr/local/bin/terraform && \
    rm -f terraform.zip && \
    rm -rf terraform/ && \
    # Install terragrunt
    curl -LsS "${NEXUS_GITHUB_PROXY}/gruntwork-io/terragrunt/releases/download/${TERRAGRUNT_VERSION}/terragrunt_linux_amd64" -o /usr/local/bin/terragrunt && \
    chmod +x /usr/local/bin/terragrunt && \
    upx /usr/local/bin/terragrunt && \
    # Cleanup
    apt-get remove -y curl unzip upx > /dev/null && \
    apt-get autoremove -y > /dev/null && \
    apt-get clean > /dev/null && \
    rm -rf /var/lib/apt/lists/* /var/cache/* /var/log/* /var/lib/dpkg/info/* > /dev/null  && \
    rm -rf /usr/share/doc/* && /usr/bin/upx* > /dev/null

# Keep COPY/ADD at the end of the docker file. This speeds up a build when only
# local files changed. From docker docs: once the cache is invalidated, all
# subsequent Dockerfile commands generate new images and the cache isn’t used.
COPY . /apps/deploy

WORKDIR /apps/deploy

# Install packages and apps needed for deployment
RUN chmod +x bootstrap.sh && \
    ./bootstrap.sh

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh" ]
