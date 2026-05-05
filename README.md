# NeuralVisions

A web app for answering open-ended questions about images, developed using Python, Flask and React.js.

## Project Status

The repository is currently optimized for local Docker development and Docker image builds and is not yet deployed. The core visual question answering flow works, but some public-facing site content is still incomplete.

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
- Flask-CORS for cross-origin requests between the local Vite dev server and Flask API.
- PyTorch and TorchVision for model loading and inference.
- OpenAI CLIP for image and text encoding.
- scikit-learn, NumPy, Pillow, and supporting scientific Python packages for model utilities, preprocessing, encoders, and image handling.
- KaggleHub for downloading the project's VQnA artifact bundle at container startup

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
|   |-- pyproject.toml
|   `-- requirements.txt
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

- `KAGGLE_API_TOKEN` is required when the `artifacts` volume does not already contain the VQnA bundle, or when a forced refresh is requested. Any valid Kaggle API token can fetch the artifacts; it does not need to belong to the model owner.
- `KAGGLE_MODEL_HANDLE` is the exact Kaggle model handle for this project's trained VQnA bundle. It is not a general configuration value and must remain exactly `mohammadhelaly/visualqna/pytorch/default/2`, because the backend expects the files published in that specific bundle.
- `PORT`, `WEB_CONCURRENCY`, and `GUNICORN_TIMEOUT` are runtime settings for the single-container `web` service.
- `VQNA_FORCE_ARTIFACT_DOWNLOAD=true` forces a one-off artifact refresh on the next container start; set it back to `false` afterward.

The root `.env` file includes one fixed project identifier, `KAGGLE_MODEL_HANDLE`, and the remaining runtime settings. Changing `.env` values affects container startup behavior, not the image build, so you only need to restart the relevant compose stack. `KAGGLE_MODEL_HANDLE` should still remain exactly as shown above.

For the Docker dev stack, `VITE_BACKEND_BASE_URL=http://localhost:5000` is already injected by `docker-compose.dev.yml`, so no `client/.env` file is needed.

## Runbook

### Development

Start the live-reload Docker development stack:

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
- The `artifacts` volume is shared with the production-style stack, so once the model files are downloaded they are reused by both workflows.
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

- `client/package.json` or `client/package-lock.json`
- `server/requirements.txt`
- `Dockerfile`
- either compose file

Simple source edits under `client/` and `server/` do not need an image rebuild.

### Build And Deployment-Style Run

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
- The final `web` container serves the built frontend from Flask and starts the backend with Gunicorn.
- The entrypoint always runs `server/scripts/prepare_artifacts.py` before Gunicorn starts.

Useful runtime commands:

```bash
# Stop the production-style stack
docker compose down

# Follow startup/runtime logs
docker compose logs -f web
```

Build-related notes:

- Building the runtime image does not require Kaggle credentials by itself; the Kaggle token is needed when the container starts and the artifacts volume is empty or being refreshed.
- Rebuild the runtime image after code changes, dependency changes, or Dockerfile changes.
- If you only change root `.env` values, restart the container; no rebuild is needed.

### Artifacts And Cache Behavior

On first container startup, the entrypoint prepares:

- VQnA artifacts under `/app/server/src/artifacts/vqna`
- The CLIP `ViT-L/14@336px` cache under `/app/server/src/artifacts/clip`

The VQnA bundle contains:

```text
VisualQnA.pth
model_encoder_answer.pkl
model_encoder_answer_type.pkl
```

Those files are fetched from the exact `KAGGLE_MODEL_HANDLE` shown above.

To clear the cached artifacts and force a clean re-download, stop the relevant stack and remove its volumes with the matching command:

```bash
# Deployment-style stack
docker compose down -v

# Dev stack
docker compose -f docker-compose.dev.yml down -v
```

Use that only when you intentionally want to discard the shared artifact cache.

## Deployment

The recommended deployment unit is the runtime Docker image produced by this repository. For deployments:

- Use the exact `KAGGLE_MODEL_HANDLE` shown above; it identifies the trained Kaggle bundle this project depends on
- Provide `KAGGLE_API_TOKEN` as a secret
- Mount persistent storage at `/app/server/src/artifacts`
- Expose `PORT` from the `web` container

## Development Notes

- The VQnA `.pth` file and `.pkl` encoders are treated as one runtime artifact bundle and are versioned together on Kaggle.
- The deployment-style image serves the frontend and API from the same origin, so the frontend build does not need a backend URL baked in.
- The current backend configuration runs the model on CPU.
- `docs/` and `notebooks/` are historical references and are excluded from the Docker build context.
- The notebook work took place on [Kaggle](https://www.kaggle.com/code/mohammadhelaly/visual-question-answering); the local notebook under `notebooks/` and the PDF under `docs/` provide historical project and model-development context.
- Some frontend sections still contain placeholder or unfinished content and should be completed before treating the project as a polished public product.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
