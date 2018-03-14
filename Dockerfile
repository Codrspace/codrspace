FROM python:2.7.14-slim

RUN apt-get update && \
    apt-get install -y git-core && \
    apt-get install -y libmysqlclient-dev && \
    apt-get install -y build-essential

ADD requirements_dev.pip /tmp/requirements_dev.pip
RUN pip install -r /tmp/requirements_dev.pip && rm /tmp/requirements_dev.pip

WORKDIR /code/codrspace_app