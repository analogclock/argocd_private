ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_APK_PROXY
ARG NEXUS_APK_COMMUNITY_PROXY
ARG NEXUS_PYPI_URL

WORKDIR /app
COPY ./lambda_monitor_cleanup .

RUN pip3 install -r requirements.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
    pip3 install -r requirements-unittest.txt --index-url ${NEXUS_PYPI_URL} --quiet

RUN ./unittest.sh
