ARG DOCKER_REGISTRY=""
ARG DOCKER_NODE_VERSION=""
FROM ${DOCKER_REGISTRY}node:${DOCKER_NODE_VERSION}

ARG NEXUS_NPM_PROXY
ARG NEXUS_APK_PROXY
ARG NEXUS_APK_COMMUNITY_PROXY

# These must be args, because they are accessed during build time
# See https://docs.docker.com/compose/compose-file/compose-file-v3/#build
# These args will be set via env variables by the calling script
ARG VERSION_MAJOR
ARG VERSION_MINOR
ARG VERSION_PATCH
ARG VERSION_REVISION
ARG DEVOPS_BUILD_NUMBER
ARG DEVOPS_BUILD_TYPE
ARG CI_ENVIRONMENT_NAME
ARG CI_COMMIT_SHORT_SHA

ENV NPM_PROXY=${NEXUS_NPM_PROXY}

# replace public apk repo with JFrog
RUN rm /etc/apk/repositories; \
    echo -e "${NEXUS_APK_PROXY}\n${NEXUS_APK_COMMUNITY_PROXY}\n" > /etc/apk/repositories; \
    apk update --no-cache; \
    # jq is used for creating version.json file
    apk add --no-cache jq

WORKDIR /root/portal_ui_build
COPY . .

# Delete any log files in the NPM dir (intermittend build issue)
RUN rm -rf /root/.npm/_logs/* \
    # Run main build
    && sh build/build.sh \
    # Sometimes build fails on a build machine with:
    #
    #13 7.178 npm ERR! code EPIPE
    #13 7.178 npm ERR! syscall write
    #13 7.179 npm ERR! errno -32
    #13 7.180 npm ERR! write EPIPE
    #13 7.207
    #13 7.207 npm ERR! A complete log of this run can be found in:
    #13 7.207 npm ERR!     /root/.npm/_logs/2023-01-07T00_24_55_366Z-debug-0.log
    #
    # We want to print out that log file(s), when error happens.
    # || means cmd is only executed when previous cmd failed with non-0 exit code.
    # List files in the log folder, sort to get most oldest log files first
    # and print out log contents. Most recent log will be last, handy for viewing.
    || (cd /root/.npm/_logs/ && ls | sort | xargs cat)

# Commented out by DH
# this currently will not function in the build container we
# use. Tests require Chrome, which cannot be installed on
# alpine images
# RUN sh build/unittest.sh
