## For ALPINE version
FROM python:3-alpine3.14
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apk update && apk upgrade && \
	apk add --no-cache alpine-sdk libffi-dev zlib-dev jpeg-dev
WORKDIR /backend
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir cython && \
	pip install --no-cache-dir -r requirements.txt
