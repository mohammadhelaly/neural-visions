# NeuralVisions

A web app for answering open-ended questions about images, developed using Python, Flask and React.js.

## Project Status

NeuralVisions is almost complete and the core visual question answering functionality works in development environments when the backend model files are available.

The project is currently paused. At the moment, only the frontend is deployed, so live model inference requires running the Flask backend locally or deploying a compatible backend service. The frontend article/About section content and contact section are still not complete.

## Tech Stack

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
|   |   `-- prepare_artifacts.py       # Downloads and normalizes Kaggle model artifacts
|   |-- src/
|   |   |-- artifacts/
|   |   |   `-- vqna/                   # Runtime VQnA model bundle, ignored by git
|   |   |-- images/                 # Temporary uploaded/downloaded images during prediction
|   |   |-- models/                 # PyTorch model class and CLIP-based inference logic
|   |   |-- routes/                 # Flask route blueprints for web and prediction routes
|   |   |-- utils/                  # Loader, validation, and API response helpers
|   |   |-- app.py                  # Flask app factory, CORS, routes, and static folder config
|   |   |-- config.py               # Paths for client build, runtime images, and artifacts
|   |   `-- main.py                 # Flask app entry point
|   |-- requirements.txt
|   |-- requirements-dev.txt
|   |-- pyproject.toml              # Ruff formatting and linting configuration
|   `-- .gitignore
|-- Dockerfile
|-- docker-compose.yml
|-- docs/                           # Project paper/report PDF
|-- notebooks/                      # Visual question answering notebook and model experimentation
|-- README.md
`-- LICENSE
```

## Prerequisites

- Docker and Docker Compose for the recommended setup.
- A free Kaggle API token for the first artifact download. Generate one from [Kaggle API settings](https://www.kaggle.com/settings/api).
- Internet access on first startup so the app can download the Kaggle VQnA artifact bundle and CLIP can download its own weights.

Node.js and Python are only required when running the frontend or backend outside Docker.

## Environment Variables

Create a root `.env` file before running Docker. This file is intentionally ignored by git because it contains your Kaggle token.

```env
KAGGLE_API_TOKEN=your_token_here

# Keep this unchanged unless you are intentionally changing model/runtime assets.
KAGGLE_MODEL_HANDLE=mohammadhelaly/visualqna/pytorch/default/2
PORT=5000

# Optional runtime tuning.
WEB_CONCURRENCY=1
GUNICORN_TIMEOUT=180
VQNA_FORCE_ARTIFACT_DOWNLOAD=0
```

`KAGGLE_API_TOKEN` is required for the first download. For a public Kaggle model, any valid Kaggle API token can fetch the artifacts; it does not need to belong to the model owner.

Keep `KAGGLE_MODEL_HANDLE` pinned to a versioned Kaggle model handle so deployments do not accidentally upgrade. To use a new published Kaggle version, change this handle and restart the container. The new version must contain `VisualQnA.pth`, `model_encoder_answer.pkl`, and `model_encoder_answer_type.pkl`.

The app stores VQnA artifacts, CLIP weights, and temporary uploaded images in fixed internal paths under `server/src/`. Those paths are code constants because they are tied to the Docker volume layout and the trained model architecture.

Use `VQNA_FORCE_ARTIFACT_DOWNLOAD=1` only for a one-off refresh when you want to redownload artifacts without changing `KAGGLE_MODEL_HANDLE`; set it back to `0` afterward. `PORT`, `WEB_CONCURRENCY`, and `GUNICORN_TIMEOUT` can be tuned without changing project behavior.

All root `.env` values are runtime Docker Compose settings, so changing them does not require rebuilding the image. Restart or recreate the container with `docker compose up -d` after changing `.env`; use `docker compose up --build` only after code, dependency, Dockerfile, or frontend build changes. Changing `PORT` also recreates the port mapping, so open the app at the new port afterward.

No-rebuild `.env` changes are `KAGGLE_API_TOKEN`, `KAGGLE_MODEL_HANDLE`, `PORT`, `WEB_CONCURRENCY`, `GUNICORN_TIMEOUT`, and `VQNA_FORCE_ARTIFACT_DOWNLOAD`.

For local frontend development outside Docker, create `client/.env`:

```env
VITE_BACKEND_BASE_URL=http://localhost:5000
```

## Runbook

Start the full app with Docker:

```bash
docker compose up --build
```

Open the app at:

```text
http://localhost:5000
```

On first startup, the container downloads the VQnA artifact bundle from Kaggle into a Docker volume mounted at `/app/server/src/artifacts`. The bundle must include:

```text
VisualQnA.pth
model_encoder_answer.pkl
model_encoder_answer_type.pkl
```

The startup script downloads each required file explicitly from the pinned Kaggle version. The `.pth` and matching `.pkl` files must exist together in that Kaggle version.

Later restarts reuse the downloaded artifacts unless `KAGGLE_MODEL_HANDLE` changes or `VQNA_FORCE_ARTIFACT_DOWNLOAD=1` is set. Docker also prepares the CLIP `ViT-L/14@336px` cache under `/app/server/src/artifacts/clip`, so that download is persistent and verified before Gunicorn imports the app and loads the model.

The prediction endpoint is available at `POST /predict` and expects multipart form data with a `question` field plus exactly one of an uploaded `image` file or an `image_url` value.

Uploaded files and remote image URLs are size-limited and validated before inference runs.

Run the backend outside Docker only when you need local Python development. Use a virtual environment on the host, then run the same artifact preparation script before Flask imports the model. On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and set the token with `$env:KAGGLE_API_TOKEN="your_token_here"`.

```bash
cd server
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel "setuptools<80"
python -m pip install --no-build-isolation -r requirements-dev.txt
KAGGLE_API_TOKEN=your_token_here python scripts/prepare_artifacts.py
flask --app src.main run --host 0.0.0.0 --port 5000
```

For frontend-only local development:

```bash
cd client
npm install
npm run dev
```

The Vite dev server is configured to run at `http://localhost:3000`.

Build the frontend production bundle outside Docker:

```bash
cd client
npm run build
```

After `client/dist` exists, Flask serves the built frontend from `/` and the API from `/predict`.

Run frontend linting:

```bash
cd client
npm run lint
```

Format frontend code:

```bash
cd client
npm run format
```

Format backend Python code:

```bash
cd server
python -m ruff format src scripts
```

Lint backend Python code:

```bash
cd server
python -m ruff check src scripts
```

Apply safe backend lint fixes:

```bash
cd server
python -m ruff check src scripts --fix
```

There is no backend test script currently configured.

## Deployment

The recommended deployment unit is the Docker image built from this repository. The image contains the app code and Python/Node build output, while large VQnA artifacts are downloaded on startup into a persistent volume.

For production, keep `KAGGLE_MODEL_HANDLE` pinned to an explicit version and provide `KAGGLE_API_TOKEN` as a deployment secret. Use a persistent volume for `/app/server/src/artifacts` so scaled or restarted containers do not redownload the VQnA bundle every time.

## Development Notes

- The VQnA `.pth` file and `.pkl` encoders are treated as one runtime artifact bundle and must be versioned together on Kaggle.
- Uploaded image files and images fetched from URLs are temporarily stored under `server/src/images/` and removed after each prediction request.
- The model runs on CPU in the current backend configuration.
- The notebook work took place on [Kaggle](https://www.kaggle.com/code/mohammadhelaly/visual-question-answering); the local notebook under `notebooks/` and the PDF under `docs/` provide historical project and model-development context.
- Some frontend sections still contain placeholder or unfinished content and should be completed before treating the project as a polished public product.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
