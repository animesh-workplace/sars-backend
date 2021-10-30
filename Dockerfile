## For ALPINE version
FROM python:3.9
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt -y update && apt -y upgrade && apt install -y git minimap2
WORKDIR /backend
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir cython && \
	pip install --no-cache-dir -r requirements.txt && \
	curl -fsSL 'https://github.com/nextstrain/nextclade/releases/latest/download/nextalign-Linux-x86_64' -o /bin/nextalign && chmod +x /bin/nextalign && \
	curl -fsSL 'https://github.com/nextstrain/nextclade/releases/latest/download/nextclade-Linux-x86_64' -o /bin/nextclade && chmod +x /bin/nextclade && \
	curl -fsSL 'https://github.com/cov-ert/gofasta/releases/latest/download/gofasta-linux-amd64' -o /bin/gofasta && chmod +x /bin/gofasta
