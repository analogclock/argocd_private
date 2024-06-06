ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/fsiem_scheduled_upgrade
COPY ./fsiem_scheduled_upgrade .
COPY ./fsiem_api_client /app/fsiem_api_client

ENV DYNAMODB_ACTIVATION_TABLE=""
ENV DYNAMODB_SCHEDULED_UPGRADES_TABLE=""
ENV DYNAMODB_UPGRADE_TABLE=""
ENV TABLES_REGION=""
ENV AUTOMATION_ROLE=""
ENV EVENT_BUS_NAME=""

ENV PYTHONUNBUFFERED=TRUE

RUN set -eux && \
  pip3 install -r requirements.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
  pip3 install -r requirements-unittest.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
  ./build/unittest.sh && \
  pip3 uninstall -y --quiet -r requirements-unittest.txt && \
  pip3 uninstall -y setuptools coverage pip > /dev/null && \
  rm -rf /root/.cache/pip && \
  find / | grep -E "(/__pycache__$|\.pyc$|\.pyo|\.exe$)" | xargs rm -rf && \
  BOTO_DATA=/usr/local/lib/python3.11/site-packages/botocore/data && \
  find $BOTO_DATA | grep examples-1.json | xargs rm -rf && \
  find $BOTO_DATA/ec2        -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
  find $BOTO_DATA/cloudfront -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
  rm -rf $BOTO_DATA/sagemaker $BOTO_DATA/rds $BOTO_DATA/mediaconvert

ENTRYPOINT python3 -u main.py --activation_table ${DYNAMODB_ACTIVATION_TABLE} \
  --scheduled_upgrades_table ${DYNAMODB_SCHEDULED_UPGRADES_TABLE} \
  --upgrade_table ${DYNAMODB_UPGRADE_TABLE} --tables_region ${TABLES_REGION} \
  --automation_role_name ${AUTOMATION_ROLE} --event_bus_name ${EVENT_BUS_NAME}
