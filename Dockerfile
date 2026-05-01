# syntax=docker/dockerfile:1

FROM node:20-bookworm-slim AS client-build

WORKDIR /app/client

COPY client/package*.json ./
RUN npm ci

COPY client/ ./

ARG VITE_BACKEND_BASE_URL=""
ENV VITE_BACKEND_BASE_URL=${VITE_BACKEND_BASE_URL}

RUN npm run build


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt ./server/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install wheel "setuptools<80" \
    && python -m pip install --no-build-isolation -r server/requirements.txt

COPY server ./server
COPY --from=client-build /app/client/dist ./client/dist
COPY docker/entrypoint.sh ./docker/entrypoint.sh

RUN chmod +x ./docker/entrypoint.sh \
    && mkdir -p /app/server/src/artifacts/vqna \
        /app/server/src/artifacts/clip \
        /app/server/src/images

WORKDIR /app/server

EXPOSE 5000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers ${WEB_CONCURRENCY:-1} --timeout ${GUNICORN_TIMEOUT:-180} src.main:app"]
