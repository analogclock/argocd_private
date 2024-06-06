ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/lambda_ssm_automation
COPY ./lambda_ssm_automation .

RUN pip3 install -r requirements.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
    pip3 install -r requirements-unittest.txt --index-url ${NEXUS_PYPI_URL} --quiet

RUN ./build/unittest.sh
