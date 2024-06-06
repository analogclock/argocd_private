ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_APK_PROXY
ARG NEXUS_APK_COMMUNITY_PROXY
ARG NEXUS_PYPI_URL

WORKDIR /app
COPY ./lambda_ses_reject .

RUN pip3 install -r requirements.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
    pip3 install -r requirements-unittest.txt --index-url ${NEXUS_PYPI_URL} --quiet

RUN ./unittest.sh

RUN pip3 uninstall -y --quiet -r requirements-unittest.txt && \
    pip3 uninstall -y setuptools coverage pip > /dev/null && \
    rm -rf /root/.cache/pip && \
    find / | grep -E "(/__pycache__$|\.pyc$|\.pyo|\.exe$)" | xargs rm -rf && \
    BOTO_DATA=/usr/local/lib/python3.11/site-packages/botocore/data && \
    find $BOTO_DATA | grep examples-1.json | xargs rm -rf && \
    find $BOTO_DATA/ec2        -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
    find $BOTO_DATA/cloudfront -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
    rm -rf $BOTO_DATA/sagemaker $BOTO_DATA/rds $BOTO_DATA/mediaconvert

ENTRYPOINT python3 -u main.py
