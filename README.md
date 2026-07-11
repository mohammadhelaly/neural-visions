# NeuralVisions

A web app for answering open-ended questions about images, developed using Python, Flask and React.js.

## Tech Stack

- Docker Compose and a multi-stage Dockerfile for development and runtime packaging
- React 18 and TypeScript for the frontend application UI.
- Vite for local frontend development, production builds, and previewing built assets.
- Tailwind CSS, custom CSS, and Poppins font assets for styling.
- Framer Motion for page and section animations.
- Radix UI Dialog primitives for the mobile navigation drawer.
- React Hook Form and Zod for the visual question answering form and validation.
- TanStack React Query and Axios for API mutation handling and backend requests.
- Python and Flask for the backend API and static frontend serving.
- uv for backend package management.
- Flask-CORS for cross-origin requests between the local Vite dev server and Flask API.
- PyTorch and TorchVision for model loading and inference.
- OpenAI CLIP for image and text encoding.
- scikit-learn, NumPy, Pillow, and supporting scientific Python packages for model utilities, preprocessing, encoders, and image handling.
- KaggleHub for downloading the project's VQnA artifact bundle during dev startup and runtime image builds

## Project Structure

```text
|-- client/
|   |-- public/                     # Static assets, icons, fonts, video, PDF, favicon, and SEO files
|   |-- src/
|   |   |-- api/                    # Axios client, React Query client, and predict API hook
|   |   |-- assets/                 # SVG icon assets and icon exports
|   |   |-- components/             # Reusable sections, navigation, form controls, VQnA UI, and footer
|   |   |-- data/                   # Contact/profile data
|   |   |-- lib/                    # Shared helpers, hooks, and utilities
|   |   |-- styles/                 # Global CSS, font imports, and Tailwind entrypoint
|   |   |-- app.tsx                 # Frontend page composition
|   |   `-- main.tsx                # React entry point and providers
|   |-- index.html
|   |-- package.json
|   |-- tailwind.config.js
|   |-- tsconfig.json
|   `-- vite.config.ts
|-- server/
|   |-- scripts/
|   |   `-- prepare_artifacts.py    # Downloads VQnA artifacts and CLIP weights
|   |-- src/
|   |   |-- artifacts/
|   |   |   `-- clip/               # Persistent runtime VQnA bundle
|   |   |   `-- vqna/               # Persistent runtime VQnA bundle
|   |   |-- images/                 # Temporary uploaded/downloaded images during prediction
|   |   |-- models/                 # PyTorch model class and CLIP-based inference logic
|   |   |-- routes/                 # Flask route blueprints for web and prediction routes
|   |   |-- utils/                  # Loader, validation, and API response helpers
|   |   |-- app.py                  # Flask app factory, CORS, routes, and static folder config
|   |   |-- config.py               # Paths for client build, runtime images, and artifacts
|   |   `-- main.py                 # Flask app entry point
|   |-- pyproject.toml              # Backend project metadata, dependencies, and Ruff config
|   `-- uv.lock                     # Locked backend dependency graph
|-- .github/
|   `-- workflows/
|       `-- deploy-hf-space.yml     # Syncs the repository to a Hugging Face Docker Space
|-- .huggingface/
|   `-- README.md                   # Hugging Face Space README with Docker metadata
|-- docs/                           # Historical project paper/report
|-- notebooks/                      # Historical experimentation notebook
|-- docker-compose.dev.yml          # Live-reload Docker development stack
|-- docker-compose.yml              # Production-style local runtime stack
|-- Dockerfile                      # Multi-stage image for dev and runtime targets
|-- README.md
`-- LICENSE
```

## Prerequisites

- Docker Desktop or Docker Engine with Compose support
- A free Kaggle API token for the first artifact download. Generate one from [Kaggle API settings](https://www.kaggle.com/settings/api).

## Environment Variables

Create a root `.env` file before running Docker. This file is intentionally ignored by git because it contains your Kaggle token.

```env
KAGGLE_API_TOKEN=your_token_here

# These must stay exactly as shown for the project to work.
KAGGLE_MODEL_HANDLE=mohammadhelaly/visualqna/pytorch/default/2
PORT=5000

# Optional runtime tuning.
WEB_CONCURRENCY=1
GUNICORN_TIMEOUT=180
VQNA_FORCE_ARTIFACT_DOWNLOAD=false
```

- `KAGGLE_API_TOKEN` is required for two cases: dev-mode artifact downloads and runtime image builds. Any valid Kaggle API token can fetch the artifacts; it does not need to belong to the model owner.
- `KAGGLE_MODEL_HANDLE` is the exact Kaggle model handle for this project's trained VQnA bundle. It is not a general configuration value and must remain exactly `mohammadhelaly/visualqna/pytorch/default/2`, because the backend expects the files published in that specific bundle.
- `PORT`, `WEB_CONCURRENCY`, and `GUNICORN_TIMEOUT` are runtime settings for the single-container `web` service.
- `VQNA_FORCE_ARTIFACT_DOWNLOAD=true` forces a one-off artifact refresh for startup-based artifact preparation, which currently applies to the dev stack.

The root `.env` file includes one fixed project identifier, `KAGGLE_MODEL_HANDLE`, plus the values used by the current Docker workflows. `KAGGLE_API_TOKEN` is consumed in two places: as a normal environment variable in the dev stack and as a Docker build secret in the runtime image build.

For the Docker dev stack, `VITE_BACKEND_BASE_URL=http://localhost:5000` is already injected by `docker-compose.dev.yml`, so no `client/.env` file is needed.

## Docker Setup

This repository uses two different Docker setups for two different goals.

`docker-compose.dev.yml` is the development setup:

- It runs two services: `client` and `server`.
- It builds the `client-dev` and `server-dev` targets from the multi-stage `Dockerfile`.
- It bind-mounts `./client` and `./server` into the containers so code edits are reflected immediately.
- The frontend runs through the Vite dev server with HMR on `http://localhost:3000`.
- The backend runs Flask in debug mode on `http://localhost:5000`.
- Model artifacts are downloaded at backend container startup and then cached in the dev `artifacts` volume.

`docker-compose.yml` is the deployment-style runtime setup:

- It runs a single `web` service.
- It builds the `runtime` target from the multi-stage `Dockerfile`.
- It does not bind-mount the source tree, so the container runs the image exactly as built.
- The frontend production build is copied into the image and served by Flask from the same container as the API.
- Model artifacts and the CLIP cache are baked into the image during `docker compose build`.
- This is the setup to use when you want to validate production-like behavior or prepare a deployment image.

## Runbook

### Development

Use this setup for local development and iteration.

Compose file: `docker-compose.dev.yml`  
Docker targets: `client-dev` and `server-dev`

Start the live-reload development stack:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Open:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:5000
```

What to expect in dev mode:

- Changes under `client/` are picked up by the Vite dev server with HMR.
- Changes under `server/` are picked up by Flask's debug reloader.
- The `server` service still runs the artifact-preparation entrypoint before Flask starts, so the first startup may take a while while Kaggle artifacts and CLIP weights download.
- The dev stack keeps its own `artifacts` volume, so once the model files are downloaded they are reused across dev restarts and rebuilds.
- The dev stack always binds `client` to port `3000` and `server` to port `5000`; changing root `PORT` only affects the single-container `web` service.

Useful dev commands:

```bash
# Stop the dev stack
docker compose -f docker-compose.dev.yml down

# Rebuild only the dev images after dependency or Docker changes
docker compose -f docker-compose.dev.yml build

# Follow frontend logs
docker compose -f docker-compose.dev.yml logs -f client

# Follow backend logs
docker compose -f docker-compose.dev.yml logs -f server

# Run frontend linting inside the dev client image
docker compose -f docker-compose.dev.yml run --rm client npm run lint

# Run frontend formatting inside the dev client image
docker compose -f docker-compose.dev.yml run --rm client npm run format
```

Rebuild the dev images when any of these change:

- The files `client/package.json` or `client/package-lock.json`
- The files `server/pyproject.toml` or `server/uv.lock`
- `Dockerfile`
- Either compose file

Simple source edits under `client/` and `server/` do not need an image rebuild.

### Build And Deployment-Style Run

Use this setup when you want the app to run the way it would in deployment: one container, built frontend, Gunicorn, and artifacts already baked into the image.

Compose file: `docker-compose.yml`  
Docker target: `runtime`

Build only the runtime image:

```bash
docker compose build web
```

Start the previously built runtime container:

```bash
docker compose up
```

Or build and start in one step:

```bash
docker compose up --build
```

Open the app at the port configured by root `PORT` (`5000` by default):

```text
http://localhost:5000
```

What the runtime build does:

- The `client-build` stage runs `npm ci` and `npm run build`, then copies `client/dist` into the final runtime image.
- The runtime build uses `KAGGLE_API_TOKEN` as a Docker build secret and runs `server/scripts/prepare_artifacts.py` during image build, so the VQnA bundle and CLIP cache are baked into the final image.
- The final `web` container serves the built frontend from Flask and starts the backend with Gunicorn without downloading artifacts at startup.

Useful runtime commands:

```bash
# Stop the production-style stack
docker compose down

# Follow startup/runtime logs
docker compose logs -f web
```

Build-related notes:

- Building the runtime image requires `KAGGLE_API_TOKEN` to be available to Docker Compose so it can be passed as a build secret.
- Rebuild the runtime image after code changes, dependency changes, or Dockerfile changes.
- If you change `KAGGLE_API_TOKEN`, no rebuild is needed unless you are building a fresh runtime image. If you change runtime settings like `PORT`, `WEB_CONCURRENCY`, or `GUNICORN_TIMEOUT`, restart the container; no rebuild is needed.

### Artifacts And Cache Behavior

The runtime image now bakes in:

- VQnA artifacts under `/app/server/src/artifacts/vqna`
- The CLIP `ViT-L/14@336px` cache under `/app/server/src/artifacts/clip`

The VQnA bundle contains:

```text
VisualQnA.pth
model_encoder_answer.pkl
model_encoder_answer_type.pkl
```

Those files are fetched from the exact `KAGGLE_MODEL_HANDLE` shown above.

In the dev stack, artifacts are still prepared at container startup and cached in the `artifacts` Docker volume used by `docker-compose.dev.yml`.

To clear the cached artifacts and force a clean re-download, stop the relevant stack and remove its volumes with the matching command:

```bash
# Dev stack
docker compose -f docker-compose.dev.yml down -v
```

Use that only when you intentionally want to discard the dev artifact cache. The production-style `web` image no longer depends on a runtime artifacts volume.

## Deployment

This project is deployed on Hugging Face. The deployment story is centered around the `runtime` image in the multi-stage `Dockerfile`.

- The frontend is built into static assets with Vite.
- The backend serves both the API and the built frontend from the same Flask/Gunicorn container.
- The trained VQnA artifact bundle and the CLIP cache are baked into the runtime image during the Docker build.
- The deployed container does not depend on a runtime artifact volume.

This makes deployments heavier to build, but more self-contained once built. That tradeoff fits this repository because the model bundle is fixed and the deploy target is expected to boot with everything already present.

### Hugging Face Pipeline

The Hugging Face deployment path is driven by three pieces in this repository:

- The [Dockerfile](./Dockerfile)
  The `runtime` stage defines the image Hugging Face builds and runs.
- The [`.huggingface/README.md`](./.huggingface/README.md)
  This file provides the Hugging Face Space metadata such as `sdk: docker` and `app_port: 5000`.
- The [`.github/workflows/deploy-hf-space.yml`](./.github/workflows/deploy-hf-space.yml)
  This workflow syncs the repository to the target Space and triggers the Hugging Face-side rebuild.

The pipeline works like this:

1. A push lands on the branch watched by the workflow, which is currently `main`.
2. GitHub Actions checks out the repository and prepares a temporary sync payload.
3. The workflow replaces the root README in that payload with `.huggingface/README.md`, because Hugging Face expects Space metadata in the root README.
4. The `huggingface/hub-sync` action syncs that payload to the Space repository on the Hugging Face Hub.
5. Hugging Face detects the new commit in the Space repo and rebuilds the Docker Space from the synced files.
6. During the Hugging Face Docker build, `KAGGLE_API_TOKEN` is provided as a build secret so the runtime image can download and bake in the VQnA artifacts and CLIP cache.

### Tokens, Secrets, And Variables

The deployment path uses two different systems for sensitive values:

- GitHub Actions secrets and variables
- Hugging Face Space secrets

The values have different responsibilities:

- `KAGGLE_API_TOKEN`
  This is a Hugging Face Space secret. It is used inside the Docker build running on Hugging Face so the runtime image can download the fixed Kaggle artifacts.
- `HUGGINGFACE_ACCESS_TOKEN`
  This is a GitHub Actions secret. It lets the GitHub workflow write to the target Hugging Face Space repository.
- `HUGGINGFACE_SPACE_REPOSITORY_ID`
  This is a GitHub Actions variable. It tells the workflow which Hugging Face Space repository to sync to, for example `mohammadhelaly/neural-visions`.
- `KAGGLE_MODEL_HANDLE`
  This is not a deployment secret. It is a fixed runtime identifier that must stay pinned to the exact Kaggle bundle this project expects.

In other words:

- GitHub needs a Hugging Face token so it can push code to the Space repository.
- Hugging Face needs a Kaggle token so it can build the runtime image with the baked model artifacts.

### Hugging Face Space Behavior

The deployed Space exposes the app in two forms:

- The Hugging Face repository page at [huggingface.co/spaces/mohammadhelaly/neural-visions](https://huggingface.co/spaces/mohammadhelaly/neural-visions)
- The direct app page at [mohammadhelaly-neural-visions.hf.space](https://mohammadhelaly-neural-visions.hf.space/)

The repository page includes Hugging Face chrome and embeds the live app. The `.hf.space` URL is the direct live web page for the application itself.

This repository currently targets a Docker Space with the built frontend and backend served from one container on port `5000`. The runtime image also includes a Hugging Face-specific user setup so the container matches the user model expected by Hugging Face Docker Spaces.

For this repository, Hugging Face is responsible for:

- Storing the Space repository
- Rebuilding the Docker image when new commits are synced to the Space
- Providing the live `.hf.space` app URL
- Supplying the Kaggle token at build time through the Space secret store

GitHub is responsible for:

- Storing the main source repository
- Running the sync workflow on pushes to `main`
- Providing the Hugging Face access token and Space repository id to the workflow

## Development Notes

- The VQnA `.pth` file and `.pkl` encoders are treated as one runtime artifact bundle and are versioned together on Kaggle.
- The deployment-style image serves the frontend and API from the same origin, so the frontend build does not need a backend URL baked in.
- The current backend configuration runs the model on CPU.
- The `docs/` and `notebooks/` directories are historical references and are excluded from the Docker build context.
- The notebook work took place on [Kaggle](https://www.kaggle.com/code/mohammadhelaly/visual-question-answering); the local notebook under `notebooks/` and the PDF under `docs/` provide historical project and model-development context.
- Some frontend sections still contain placeholder or unfinished content and should be completed before treating the project as a polished public product.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
