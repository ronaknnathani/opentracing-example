##########################################
# Dockerfile for Flask+Open tracing container
# Based on ronaknnathani/python2
###########################################
FROM ronaknnathani/python2

MAINTAINER Ronak Nathani

RUN apt-get update \
    && apt-get install -y libpq-dev

RUN pip install flask Flask-Opentracing sqlalchemy psycopg2 flask-compress
