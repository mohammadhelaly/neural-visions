# syntax=docker/dockerfile:1

FROM node:20-bookworm-slim AS client-base

WORKDIR /app/client

COPY client/package*.json ./
RUN npm ci


FROM client-base AS client-build

COPY client/ ./

ARG VITE_BACKEND_BASE_URL=""
ENV VITE_BACKEND_BASE_URL=${VITE_BACKEND_BASE_URL}

RUN npm run build


FROM client-base AS client-dev

EXPOSE 3000


FROM python:3.11-slim AS server-base

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

COPY docker/entrypoint.sh ./docker/entrypoint.sh

RUN chmod +x ./docker/entrypoint.sh \
    && mkdir -p /app/server/src/artifacts/vqna \
        /app/server/src/artifacts/clip \
        /app/server/src/images

EXPOSE 5000


FROM server-base AS server-dev

WORKDIR /app/server

ENTRYPOINT ["/app/docker/entrypoint.sh"]


FROM server-base AS runtime

COPY server ./server
COPY --from=client-build /app/client/dist ./client/dist

# ============================
# This block is specific for deployment with Hugging Face.

RUN useradd -m -u 1000 user \
    && chown -R user:user /app/server/src/artifacts /app/server/src/images
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
# ============================

# The uid, gid and mode settings are specific for deployment with Hugging Face.
RUN --mount=type=secret,id=KAGGLE_API_TOKEN,uid=1000,gid=1000,mode=0400,required=true \
    export KAGGLE_API_TOKEN="$(cat /run/secrets/KAGGLE_API_TOKEN)" \
    && python /app/server/scripts/prepare_artifacts.py

WORKDIR /app/server

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers ${WEB_CONCURRENCY:-1} --timeout ${GUNICORN_TIMEOUT:-180} src.main:app"]
