# KrishiSathi AI

KrishiSathi AI is a full-stack machine-learning application for crop suitability recommendations and sustainable farming guidance. It uses soil nutrients and environmental conditions to help farmers explore crops that may be suitable for a given field.

The project is aligned primarily with **UN Sustainable Development Goal 2: Zero Hunger**, with supporting emphasis on resource-aware and sustainable agricultural decisions.

## Problem statement

Crop selection depends on interacting soil and climate conditions. A farmer or agricultural learner should be able to enter nutrient values and environmental measurements, receive an interpretable crop recommendation, and understand the conditions behind that recommendation. KrishiSathi AI is intended as an educational decision-support tool; it is not a substitute for local agronomic expertise, soil testing, or government guidance.

## Product theme

The approved Modern GreenTech visual theme is:

- Forest green: `#174D35`
- Sage green: `#86A98A`
- Lime accent: `#C8E66B`
- Off-white background: `#F7F8F2`

The planned interface uses a dark-green sidebar, white content cards, readable charts, subtle borders, consistent typography, and responsive layouts.

## Dataset status

The supplied dataset is stored at `data/Crop_recommendation.csv` and was inspected during Phase 1. It contains 2,200 rows and 8 columns:

`N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`, and `label`.

The seven expected input features are present exactly as specified, with `label` as the target. There are no missing values and no duplicate records. Each of the 22 crop classes has 100 records. Full audit output is in [docs/dataset-audit.md](docs/dataset-audit.md).

## Selected technology stack

### Frontend

- React with Vite
- JavaScript
- Tailwind CSS
- Recharts
- React Router
- Axios
- Lucide React icons

### Backend

- Python
- FastAPI
- pandas and NumPy
- scikit-learn
- joblib
- SQLite

No dependencies have been installed as part of Phase 1.

## Proposed architecture

```text
React/Vite client
        |
        | Axios / JSON over HTTP
        v
FastAPI service
        |
        +-- validation and recommendation endpoints
        +-- trained scikit-learn pipeline (Phase 2)
        +-- SQLite persistence for local history (later phase)
        |
        +-- data/Crop_recommendation.csv (training source)
```

The frontend will provide the responsive user experience and visual explanations. The backend will validate inputs, load a versioned model artifact, return predictions and supporting metadata, and later persist local recommendation history. The model and database are intentionally not implemented in Phase 1.

## Initial project structure

```text
krishisathi-ai/
├── backend/                 # FastAPI application (Phase 2+)
├── data/
│   └── Crop_recommendation.csv
├── docs/
│   └── dataset-audit.md
├── frontend/                # React/Vite application (Phase 2+)
├── .gitignore
└── README.md
```

## Setup instructions

### Backend setup

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn pandas numpy scikit-learn joblib
```

The commands above are preparation for the implementation phase; Phase 1 does not install them. A future backend entry point will be run with:

```powershell
python -m uvicorn backend.main:app --reload
```

### Frontend setup

From the repository root in PowerShell:

```powershell
Set-Location frontend
npm install
npm run dev
```

The frontend starts at [http://localhost:5173](http://localhost:5173). Set `VITE_API_BASE_URL` in `frontend/.env.local` when the API is hosted somewhere other than the Vite development proxy. The provided `.env.example` uses `/api`, which proxies to `http://127.0.0.1:8000` during development.

The frontend production build can be verified with:

```powershell
npm run build
```

## Phased implementation plan

### Phase 1 — foundation and data audit (current)

- Inspect the workspace and supplied CSV.
- Confirm the schema, quality, class balance, and numerical ranges.
- Create the repository structure, README, and ignore rules.
- Verify the local development tools without installing unnecessary dependencies.

### Phase 2 — machine learning model

- Build a reproducible training/evaluation script using the verified seven features and `label` target.
- Use a stratified train/test split and suitable baseline classifiers.
- Compare metrics such as accuracy, macro F1, confusion matrix, and per-class performance.
- Persist the selected pipeline with joblib only after evaluation and review.
- Document assumptions, limitations, and reproducibility details.

### Phase 3 — backend API

- Create FastAPI health and recommendation endpoints.
- Validate feature ranges and return clear errors.
- Load the versioned model artifact safely.
- Add SQLite-backed local recommendation history where useful.
- Add API tests.

## FastAPI backend

The Phase 3 backend is implemented under `backend/app`. It uses the persisted Phase 2 model and metadata, the real CSV for cached dashboard analytics, and a local SQLite database for successful prediction history.

### Backend dependencies

The current environment has FastAPI, Uvicorn, Pydantic, pandas, NumPy, scikit-learn, joblib, and httpx available. If setting up a fresh environment, install only the backend dependencies with:

```powershell
python -m pip install fastapi uvicorn pydantic pandas numpy scikit-learn joblib httpx
```

### Start the backend

From the project root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Interactive API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). The local React origin is configurable with `KRISHISATHI_ALLOWED_ORIGINS`, for example `http://localhost:5173,http://127.0.0.1:5173`.

### API endpoints

- `GET /api/health` — service and model availability.
- `GET /api/metadata` — feature names, target classes, and model version.
- `GET /api/dashboard/summary` — dataset and model summary.
- `GET /api/dashboard/crop-distribution` — real CSV class counts.
- `GET /api/dashboard/feature-statistics` — numerical feature statistics.
- `GET /api/dashboard/model-metrics` — saved cross-validation and held-out metrics.
- `GET /api/dashboard/confusion-matrix` — saved matrix with explicit class ordering.
- `GET /api/dashboard/feature-importance` — selected estimator importances when supported.
- `POST /api/predict` — validated crop recommendation and persistence to history.
- `GET /api/history?limit=50&offset=0` — bounded prediction history.
- `GET /api/history/{prediction_id}` — one history record.
- `DELETE /api/history/{prediction_id}` — delete one history record.
- `GET /api/history/export` — CSV export of local history.

### Required artifacts and database

The API requires `data/Crop_recommendation.csv`, `backend/models/crop_model.joblib`, and `backend/models/model_metadata.json`. The database is created automatically at `backend/data/krishisathi.db`; it stores only local prediction inputs, outputs, model identifiers, and UTC timestamps. SQLite files are excluded by `.gitignore`.

### Backend tests

Run all existing ML and backend tests without pytest:

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s backend/tests -t . -v
```

Backend tests use an isolated temporary SQLite database and do not contaminate the real local history.

### Known limitations

- Model scores are `predict_proba` outputs, not calibrated agronomic risk estimates.
- Dashboard metrics are the saved evaluation results for the supplied benchmark dataset.
- Out-of-observed-range values receive warnings when they remain within the API's supported physical/input bounds.
- Authentication, production deployment, and frontend integration are outside this phase.

### Phase 4 — frontend experience

- Scaffold the React/Vite app and apply the Modern GreenTech theme.
- Build the input form, recommendation result card, explanation views, and responsive sidebar.
- Add Recharts visualizations and connect the API with Axios.
- Add loading, empty, validation, and error states.

### Phase 5 — integration and quality

- Integrate frontend and backend locally.
- Add end-to-end checks, accessibility review, and responsive QA.
- Review model limitations and sustainability messaging.
- Prepare deployment documentation using free/local tooling only.

## Verified local workflow

The current Phase 5 verification uses Python 3.14.2, scikit-learn 1.9.1, joblib 1.6.0, and the installed frontend toolchain. The persisted model metadata records that the artifact was trained with scikit-learn 1.7.2, so loading it emits an `InconsistentVersionWarning`. Predictions and tests currently succeed, but the model should be retrained and its artifact replaced only as a deliberate compatibility change in a controlled environment; do not silence the warning or upgrade/retrain automatically.

Run the backend and ML test suites from the repository root:

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s backend/tests -t . -v
```

Start the local API in one terminal:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Start the React development server in a second terminal:

```powershell
Set-Location frontend
npm run dev -- --host 127.0.0.1
```

Open `http://localhost:5173/`. The verified UI workflow is: open the dashboard, use `/predictor` with seven finite numeric values, confirm the real model result and top-three candidates, review `/history`, export `krishisathi-history.csv`, and remove a test record when cleanup is intended. The other verified routes are `/model-performance`, `/insights`, and the catch-all redirect.

Build the production frontend with:

```powershell
Set-Location frontend
npm run build
```

The build currently succeeds. Vite reports a non-fatal bundle-size warning because the main JavaScript chunk is larger than 500 kB; code splitting can be considered separately from functional verification.

## Phase 1 boundaries

This phase does not train a model, create a dashboard, fabricate records, replace the supplied CSV, install the full dependency set, or require paid services or API keys.
