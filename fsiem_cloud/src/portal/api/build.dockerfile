# Set another registry via the build args
# Notice that it should end with "/"
ARG DOCKER_REGISTRY
ARG DOCKER_DOTNET_VERSION
FROM ${DOCKER_REGISTRY}dotnet/sdk:${DOCKER_DOTNET_VERSION}

ARG NEXUS_NUGET_PROXY
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

ENV DOTNET_CLI_TELEMETRY_OPTOUT=true
ENV PATH="${PATH}:/root/.dotnet/tools"
ENV NEXUS_NUGET_PROXY="${NEXUS_NUGET_PROXY}"
# See
# - https://learn.microsoft.com/en-us/dotnet/core/tools/nuget-signed-package-verification
# - https://learn.microsoft.com/en-us/nuget/reference/errors-and-warnings/nu3028
# - https://stackoverflow.com/q/59965577/706456
# .NET 8 turned on package verification which requires Internet access to a
# certificate verification server. On build machine, there is no access to it.
# Which results in a hanging build on `dotnet nuget restore`.
# Setting this var, fixes hanging build problem on the build machine.
ENV NUGET_CERT_REVOCATION_MODE="offline"


# replace nuget public source with JFrog
RUN dotnet nuget remove source nuget.org; \
  dotnet nuget add source ${NEXUS_NUGET_PROXY}; \
  # replace public apk repo with JFrog
  rm /etc/apk/repositories; \
  echo -e "${NEXUS_APK_PROXY}\n${NEXUS_APK_COMMUNITY_PROXY}\n" > /etc/apk/repositories; \
  apk update --no-cache; \
  apk add --update --no-cache zip ca-certificates

WORKDIR /root/portal_api
COPY . .

# restore our tools from the tools manifest
RUN dotnet tool restore --disable-parallel

RUN sh build/build.sh && sh build/unittest.sh
