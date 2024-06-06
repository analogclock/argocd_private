# Set another registry via the build args
# Notice that it should end with "/"
ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_APK_PROXY
ARG NEXUS_APK_COMMUNITY_PROXY

# These must be args, because they are accessed during build time
ARG VERSION_MAJOR
ARG VERSION_MINOR
ARG VERSION_PATCH
ARG VERSION_REVISION
ARG DEVOPS_BUILD_NUMBER
ARG DEVOPS_BUILD_TYPE
ARG NEXUS_PYPI_URL
ARG BUILD_HTTP_PROXY

# User and group
ENV USER=builder
ENV GROUP=builder
ENV PATH="/home/$USER/.local/bin:${PATH}"
RUN set -eux && addgroup --system $GROUP && adduser --system -D -G $GROUP -s /bin/sh $USER

# remove existing apk repositories file
# update with our new information
RUN rm /etc/apk/repositories && \
    echo -e "${NEXUS_APK_PROXY}\n ${NEXUS_APK_COMMUNITY_PROXY}\n" > /etc/apk/repositories && \
    cat /etc/apk/repositories

# Dependencies from APK
RUN apk update --no-cache && \
    apk add --no-cache gcc musl-dev libffi-dev

# Switching into non-root user for doing actual work with python and pip
USER $GROUP:$USER
WORKDIR /usr/src/app/

COPY --chown=$GROUP:$USER ./fsiem_api_client .

# Install pip packages
RUN python -m pip install --upgrade pip --index-url ${NEXUS_PYPI_URL} && \
    pip install --quiet --user -r requirements.txt --index-url ${NEXUS_PYPI_URL}

# set on the ENV for the build script to access the HTTPS_PROXY
ENV BUILD_HTTP_PROXY=${BUILD_HTTP_PROXY}

RUN ./build/build.sh && ./build/unittest.sh
