# PantryMatch 2.0 Backend

## Overview
This is the backend repository for PantryMatch 2.0, an intelligent recipe discovery and kitchen management application. It serves as an API built with Flask, powering text-based recipe search using TF-IDF cosine similarity, AI-assisted recipe adaptation via OpenRouter, YouTube video fetching via RapidAPI, and advanced image-based ingredient classification using a hybrid PyTorch (ResNet18) and YOLOv8 ONNX-based model.

The architecture has been highly optimized for memory-constrained deployment environments, specifically designed to remain stable on the Render free tier (max 512MB RAM and 1 CPU).

## Tech Stack
- **Framework**: Flask, Python 3
- **Database**: SQLite (built-in)
- **Machine Learning**: PyTorch, ONNXRuntime, Scikit-Learn (TF-IDF)
- **Deployment Server**: Gunicorn
- **Authentication**: Custom Token mechanism (`itsdangerous` URLSafeTimedSerializer)
- **Other Utilities**: Flask-CORS, Pillow (Image Processing), Requests

## Architecture & Machine Learning Optimizations
The backend implements several crucial optimizations to stay under the 512MB RAM constraint of the Render deployment environment:
1. **Thread Constraining**: Single-threading enforced on `OMP`, `MKL`, and `OPENBLAS` to avoid memory spikes in single-core containers.
2. **Model ONNX Conversion**: PyTorch Object Detection tools (like YOLO) have been exported into `.onnx` models to drastically trim initialization size and optimize memory footprints.
3. **Chunked Grid Cropping**: Uploaded high-res images are automatically compressed (thumbnailed) and sliced into overlapping grid crops before prediction, to keep memory peak usage under 300MB per concurrent request.
4. **Native Caching over Pandas**: Memory-heavy libraries like Pandas were bypassed for native Python `csv` dictionary mapping to load search corpus strings into TF-IDF transformers securely.
5. **Garbage Collection Hooks**: Forced HTTP endpoint-level `gc.collect()` usage intercepts memory balloons quickly for ML routes.

## Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Virtual Environment (recommended)

### 2. Install Dependencies
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables & API Keys
You can set standard environment variables via `.env` or create a `config.py` file in the backend directory.

**Required Keys:**
- `AUTH_SECRET_KEY` (Used to hash user passwords and sign Bearer tokens)
- `OPENROUTER_API_KEY` (Required for the `/adapt` AI Chef features)
- `OPENROUTER_API_URL` (Defaults to `https://openrouter.ai/api/v1/chat/completions`)
- `OPENROUTER_MODEL` (Defaults to `openai/gpt-4o-mini`)
- `RAPIDAPI_KEY` (Required for `/videos` YouTube searches)
- `RAPIDAPI_HOST` (Defaults to `youtube-v3-alternative.p.rapidapi.com`)

### 4. Base Data Structures
The backend expects static CSV datasets populated within the `/data` directory:
- `data/final_recipes.csv`: Main TF-IDF matrix target with translated names.
- `data/recipe_classifications.csv`: Additional dietary and spice preference mappings.
*(Note: User data is structured inside an auto-generated SQLite database file `data/users.db` upon initial spin up).*

### 5. Start the Server
Local Development mode:
```bash
python app.py
```
Production mode (Gunicorn):
```bash
gunicorn -w 1 -b 0.0.0.0:5000 --timeout 120 app:app
```

## Core API Endpoints

### 1. Recipes & Search
- `GET /search?q={query}`: Runs a cosine-similarity analysis against the `final_recipes.csv` matrix using a TF-IDF vectorizer. Respects authenticated user preference flags (Dietary/Spice filtering).

### 2. User Authentication
All secure endpoints expect an `Authorization: Bearer <token>` header.
- `POST /auth/signup`: Create a new user (expects email, name, password)
- `POST /auth/login`: Authenticate an existing user returning a JWT token
- `GET /auth/me`: Validate token strings and get the current user profile.

### 3. User Preferences & Local Storage
- `POST /user/preferences`: Apply modifications to user diet/spice filtering rules.
- `GET /user/saved-recipes`: Fetch all custom user-saved recipes.
- `POST /user/saved-recipes`: Log a new recipe into storage.
- `DELETE /user/saved-recipes`: Delete a single recipe (`?id=`) or clear the list entirely (`?clear=1`).
- `GET /user/search-history`: Pull recent text-search histories up to a 120 block limit.
- `DELETE /user/search-history`: Delete single or complete logged search history.

### 4. ML Integrations
- `POST /classify-image`: Multi-part form-data endpoint handling `image` frames. Reduces scale padding and slices via bounding grids, then runs CNN (ResNet) batches mapping detections > `0.35` thresholds. Returns raw detected physical food ingredients globally.
- `POST /adapt`: Proxies OpenRouter completions mapping instructions lacking certain ingredients to valid local Indian kitchen workarounds.
- `GET /videos?recipe={query}`: Fetches top 2 relevant YouTube tutorials matching search criteria.

## Repository Layout
```text
/backend/
├── app.py                      # Main Flask Application
├── config.py                   # API Key declarations
├── ml_infer_ingredients.py     # Inference bridge script
├── convert_to_onnx.py          # Weight exporter scripts
├── data/                       # CSV database & DB files
├── models/                     # Static ONNX and PyTorch checkpoints (.pt)
├── venv/                       # Environment package libraries
├── yolov8n.pt                  # Raw PyTorch model files
├── requirements.txt            # Dep configuration list
├── runtime.txt                 # Python configuration (used by Render)
├── procfile                    # Gunicorn Render launch wrapper
└── .python-version             # Strict Python targeting
```
