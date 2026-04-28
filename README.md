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
|   |-- src/
|   |   |-- images/                 # Temporary uploaded/downloaded images during prediction
|   |   |-- models/                 # PyTorch model class and CLIP-based inference logic
|   |   |-- routes/                 # Flask route blueprints for web and prediction routes
|   |   |-- saved/
|   |   |   |-- encoders/            # Pickled label encoders committed with the repo
|   |   |   `-- models/              # Place VisualQnA.pth here before running the backend
|   |   |-- utils/                  # Loader, validation, and API response helpers
|   |   |-- app.py                  # Flask app factory, CORS, routes, and static folder config
|   |   |-- config.py               # Local paths for client build, images, encoders, and model file
|   |   `-- main.py                 # Flask app entry point
|   |-- requirements.txt
|   `-- .gitignore
|-- docs/                           # Project paper/report PDF
|-- notebooks/                      # Visual question answering notebook and model experimentation
|-- README.md
`-- LICENSE
```

## Prerequisites

- Node.js 18 or newer.
- npm. The frontend includes `package-lock.json`, so npm is the expected package manager.
- Python 3.10 or newer is recommended for the pinned scientific Python dependencies.
- A Python virtual environment for the Flask backend.
- Internet access during first backend setup so pip can install dependencies and CLIP can download its model weights if they are not already cached.
- The trained `VisualQnA.pth` model file downloaded from [Kaggle](https://www.kaggle.com/models/mohammadhelaly/visualqna).

Before running the backend, download `VisualQnA.pth` and place it at:

```text
server/src/saved/models/VisualQnA.pth
```

The backend loads the model during route initialization, so it will fail to start if this file is missing. The `.pth` file is intentionally ignored by git because it is a large model artifact.

## Environment Variables

The frontend reads the backend base URL from a Vite environment variable.

Create `client/.env` for local development:

```env
VITE_BACKEND_BASE_URL=http://localhost:5000
```

There are currently no required backend environment variables for local development. Backend paths for the model, encoders, temporary images, and client build output are configured in `server/src/config.py`.

## Runbook

Download the trained model from Kaggle first:

```text
https://www.kaggle.com/models/mohammadhelaly/visualqna
```

Place the downloaded file here:

```text
server/src/saved/models/VisualQnA.pth
```

Install backend dependencies in a virtual environment. Depending on your local Python setup, use either `python3` or `python` for these commands:

```bash
cd server
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start the Flask backend API:

```bash
cd server
source .venv/bin/activate
flask --app src.main run --host 0.0.0.0 --port 5000
```

By default, the backend runs at `http://localhost:5000`. The prediction endpoint is available at `POST /predict` and expects multipart form data with a `question` field plus either an `image` file or an `image_url` field.

Install frontend dependencies:

```bash
cd client
npm install
```

Create the local frontend environment file:

```bash
cd client
printf "VITE_BACKEND_BASE_URL=http://localhost:5000\n" > .env
```

Start the frontend development server:

```bash
cd client
npm run dev
```

The Vite dev server is configured to run at `http://localhost:3000`.

Build the frontend production bundle:

```bash
cd client
npm run build
```

Preview the production frontend bundle with Vite:

```bash
cd client
npm run preview
```

Serve the built frontend through Flask:

```bash
cd client
npm run build

cd ../server
source .venv/bin/activate
flask --app src.main run --host 0.0.0.0 --port 5000
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

There is no backend test script currently configured.

## Deployment

The current deployed surface is frontend-only. Because the hosted backend/model inference service is not currently active, deployed prediction requests require a configured `VITE_BACKEND_BASE_URL` that points to a running Flask backend with `VisualQnA.pth` installed under `server/src/saved/models/`.

For a full deployment, the backend environment must include the Python dependencies, the CLIP model cache or internet access for first load, the committed encoder files, and the downloaded Kaggle model artifact.

## Development Notes

- Download `VisualQnA.pth` from the [Kaggle model page](https://www.kaggle.com/models/mohammadhelaly/visualqna) before running backend inference locally.
- Uploaded image files and images fetched from URLs are temporarily stored under `server/src/images/` and removed after each prediction request.
- The model runs on CPU in the current backend configuration.
- The notebook work took place on [Kaggle](https://www.kaggle.com/code/mohammadhelaly/visual-question-answering); the local notebook under `notebooks/` and the PDF under `docs/` provide historical project and model-development context.
- Some frontend sections still contain placeholder or unfinished content and should be completed before treating the project as a polished public product.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
