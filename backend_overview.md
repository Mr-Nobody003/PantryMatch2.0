# PantryMatch 2.0 Backend Architecture & Optimizations

This document explains the architecture, setup, and key optimizations of the PantryMatch 2.0 backend, specifically tailored for resource-constrained environments like the Render Free Tier.

## 1. Tech Stack
- **Framework**: Flask (Python) exposing RESTful JSON APIs.
- **Authentication**: Simple Token-Based Authentication via `itsdangerous` (URLSafeTimedSerializer).
- **Database**: SQLite3 (`data/users.db`) for user profiles, saved recipes, and search history. Native Python arrays/hashes for in-memory recipe operations.
- **Machine Learning**: `scikit-learn` for TF-IDF Text Search and `onnxruntime` for Deep Learning (Ingredient Classification).
- **Web Server**: Gunicorn.

## 2. Core Modules & Endpoints

### Data Loading & Search (`app.py`)
- The recipe backend loads a static dataset (`data/final_recipes.csv` & `data/recipe_classifications.csv`). 
- Recipes are searched via an in-memory TF-IDF Vectorizer matching parsed ingredient combinations and synonyms with user queries using **Cosine Similarity**.
- The search dynamically filters out recipes according to a user's `Dietary Preference` and `Spice Tolerance` parsed directly from user configurations in the SQLite database.

### External APIs
- **OpenRouter AI Adaptation (`/adapt`)**: Employs an LLM (`openai/gpt-4o-mini` by default) setup via OpenRouter to smartly adapt recipe instructions if a user is missing a specific ingredient.
- **YouTube Tutorials (`/videos`)**: Queries the YouTube v3 Alternative via RapidAPI to search and deliver relevant cooking tutorial URLs corresponding to recipes.

### Machine Learning Ingredient Inference (`ml_infer_ingredients.py`)
- Provides functionality to scan a user's image, crop it, and determine the ingredients present.
- Uses a ResNet18-based model that runs without PyTorch in production.

---

## 3. Key Optimizations

A substantial amount of the backend is thoroughly engineered to remain well under the strict **512 MB memory limit** and **single-core limits** of deploying on the Render free tier.

### PyTorch Removal & ONNX Conversion
- **Problem**: PyTorch and Torchvision modules regularly consume upwards of 300-500MB of RAM just holding their module definitions, directly causing Out-Of-Memory (OOM) crashes on Render.
- **Solution**: The original ResNet18 model is converted to the lightweight ONNX format (`convert_to_onnx.py`). Inference is done purely using `onnxruntime` (`CPUExecutionProvider`).
- **Torchvision Replacement**: Image scaling, center cropping, normalizations, and `ToTensor` transitions are exactly mathematically replicated using standard `numpy` and `PIL.Image`, completely bypassing `torchvision` (`ml_infer_ingredients.py`).

### Native Python Memory Avoidance
- **Problem**: The `pandas` library incurs significant memory overhead when parsing DataFrames.
- **Solution**: Recipe CSVs are parsed locally using Python's native `csv.DictReader`. Lookups (dietary classifications and spices) are cached in native dictionaries (`RECIPE_DIET_MAP`, `RECIPE_SPICE_MAP`), shaving off >100MB of RAM.

### Image Tiling & Grid Cropping (`_generate_grid_crops` in `app.py`)
- Processing original 12+ Megapixel camera photos can trigger 36MB+ RAM spikes in raw matrix transformations alone.
- Uploaded images are heavily downscaled to `800x800` memory-safe dimensions.
- They are cleverly spliced into multiple overlapping `2x2` and `3x3` grid crops and a center crop to allow accurate Object Recognition without heavy un-scaled object detection models (e.g. YOLOv8 object detection).

### Processing & Thread Containment
- **Restricted Threading**: Common Python numerical libraries heavily multiplex threads mapping to full CPU states which forces enormous crashes. Variables such as `OMP_NUM_THREADS="1"` and `OPENBLAS_NUM_THREADS="1"` force single-threading execution to remain exceptionally frugal.
- **Gunicorn Workers**: Configured securely inside `procfile` (`--timeout 120 --workers 1 --threads 2`). A strict 2-thread, 1-worker environment gives deep learning requests generous time to finish without parallel traffic overloading the server.
- **Batch Inference Processing**: Instead of looping through matrixes individually sequentially, overlapping grid crops are processed in chunks via `max_batch_size=8` directly through the ONNX model to bypass worker timeouts smoothly on large images. 

### Tight CORS Governance
- Defined carefully explicitly for trusted Vercel and Localhost frontends (`flask_cors`), neutralizing persistent missing credential header and preflight failure gateway loops. 

### Vercel Serverless Optimization & Cold-Starts
- **Problem**: Vercel forces a 250MB size limit for internal caching. PyTorch, Pandas, and Scikit-learn easily exceed 450MB, causing Vercel to default to "Runtime Dependency Installation" which triggers a 15-20 second cold start delay.
- **Solution**: Heavy frameworks like `scikit-learn` and `pandas` were dynamically abstracted out of `requirements.txt`. A pure `numpy` standard `SimpleTfidfVectorizer` automatically functions as a fallback if `sklearn` drops or is uninstalled. This brings the bundle down to ~145MB safely. Local setups with heavy tools pip installed will natively utilize the underlying high-level C++ math capabilities gracefully.
