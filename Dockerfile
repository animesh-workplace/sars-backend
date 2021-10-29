## For ALPINE version
FROM python:3-alpine3.14
ENV PYTHONUNBUFFERED=1
RUN apk update && apk upgrade && \
	apk add alpine-sdk libev-dev libev libffi-dev rust cargo openssl-dev ncurses-dev
WORKDIR /backend
COPY requirements.txt requirements.txt
RUN pip install cython && pip install -r requirements.txt
