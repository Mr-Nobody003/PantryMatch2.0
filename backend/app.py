import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
import os
import base64
import sqlite3
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import io
from PIL import Image
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Starting PantryMatch backend...")

from ml_infer_ingredients import load_model, predict_ingredients_from_bytes

# -- Import API Keys from config --
try:
    from config import (
        OPENROUTER_API_KEY,
        OPENROUTER_API_URL,
        OPENROUTER_MODEL,
        RAPIDAPI_KEY,
        RAPIDAPI_HOST
    )
except ImportError:
    # Fallback to environment variables if config.py doesn't exist
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    OPENROUTER_API_URL = os.getenv('OPENROUTER_API_URL', 'https://openrouter.ai/api/v1/chat/completions')
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'openai/gpt-4o-mini')
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', '')
    RAPIDAPI_HOST = os.getenv('RAPIDAPI_HOST', 'youtube-v3-alternative.p.rapidapi.com')
    
    if not OPENROUTER_API_KEY or not RAPIDAPI_KEY:
        print("Warning: API keys not found. Please create config.py or set environment variables.")

app = Flask(__name__)

# Configure CORS based on environment
if os.environ.get('FLASK_ENV') == 'production':
    CORS(app, origins=["https://pantry-match-delta.vercel.app"])
else:
    CORS(app)

# --- Simple Token-Based Auth Setup (SQLite + signed tokens) ---
DATABASE_PATH = os.path.join("data", "users.db")
AUTH_SECRET = os.getenv("AUTH_SECRET_KEY") or "pantrymatch-dev-secret-key-for-auth"
TOKEN_EXP_SECONDS = 60 * 60 * 24 * 7  # 7 days

serializer = URLSafeTimedSerializer(AUTH_SECRET)


def _encode_crop_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90, optimize=True)
    return buf.getvalue()


def _generate_grid_crops(image_bytes: bytes):
    """
    Split a single image into multiple overlapping grid crops.
    Returns List[Tuple[str, bytes]] where name is crop label.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    w, h = img.size

    crops = [("full", image_bytes)]

    # If the image is too small, skip cropping
    if min(w, h) < 240:
        return crops

    # Add 2x2 and 3x3 grids with slight overlap to avoid splitting ingredients.
    # With batch inference, we safely evaluate 15 crops without timing out.
    grids = [(2, 2), (3, 3)]
    overlap = 0.08

    for rows, cols in grids:
        cell_w = w / cols
        cell_h = h / rows
        pad_w = cell_w * overlap
        pad_h = cell_h * overlap
        for r in range(rows):
            for c in range(cols):
                left = int(max(0, (c * cell_w) - pad_w))
                top = int(max(0, (r * cell_h) - pad_h))
                right = int(min(w, ((c + 1) * cell_w) + pad_w))
                bottom = int(min(h, ((r + 1) * cell_h) + pad_h))
                if right - left < 120 or bottom - top < 120:
                    continue
                crop = img.crop((left, top, right, bottom))
                crops.append((f"grid_{rows}x{cols}_r{r}c{c}", _encode_crop_bytes(crop)))

    # Add a center crop (helps when ingredient is centered)
    cx0 = int(w * 0.1)
    cy0 = int(h * 0.1)
    cx1 = int(w * 0.9)
    cy1 = int(h * 0.9)
    if cx1 - cx0 >= 160 and cy1 - cy0 >= 160:
        crops.append(("center_80", _encode_crop_bytes(img.crop((cx0, cy0, cx1, cy1)))))

    return crops


def get_db_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Users table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            preferences TEXT
        )
        """
    )
    # Saved recipes for each user
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            ingredients TEXT,
            instructions TEXT,
            time INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    # Search history
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    # Helpful indexes (safe to run repeatedly)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_recipes_user_created ON saved_recipes(user_id, created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_saved_recipes_user_title ON saved_recipes(user_id, title)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_search_history_user_created ON search_history(user_id, created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_search_history_user_query ON search_history(user_id, query)")
    conn.commit()
    conn.close()


def generate_token(user_id):
    return serializer.dumps({"user_id": user_id})


def verify_token(token):
    try:
        data = serializer.loads(token, max_age=TOKEN_EXP_SECONDS)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None


def get_auth_user_id():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        return verify_token(token)
    return None


init_db()

# -- Load Recipes & TF-IDF Search Setup --
logger.info("Loading recipes dataset (data/final_recipes.csv)...")
try:
    df = pd.read_csv("data/final_recipes.csv")
    logger.info(f"Successfully loaded {len(df)} recipes.")
except Exception as e:
    logger.error(f"Failed to load recipes: {e}")
    # Create an empty dataframe to avoid crashing
    df = pd.DataFrame(columns=['TranslatedRecipeName', 'processed_ingredients', 'TranslatedInstructions', 'TotalTimeInMins', 'ingredient_synonyms'])

# Optionally enrich recipes with diet & spice classifications
RECIPE_DIET_MAP = {}
RECIPE_SPICE_MAP = {}


def _normalize_title_for_lookup(title):
    return (str(title) or "").strip().lower()


try:
    logger.info("Loading recipe classifications...")
    classifications_df = pd.read_csv("data/recipe_classifications.csv")
    # Keep only the columns we care about and merge by recipe title
    classifications_df = classifications_df[
        ["TranslatedRecipeName", "Spice Tolerance", "Dietary Preference"]
    ]
    df = df.merge(
        classifications_df,
        on="TranslatedRecipeName",
        how="left",
        suffixes=("", "_cls"),
    )

    # Build quick lookup maps for saved-recipes and other places that only have titles
    for _, row in df[["TranslatedRecipeName", "Spice Tolerance", "Dietary Preference"]].iterrows():
        key = _normalize_title_for_lookup(row["TranslatedRecipeName"])
        if not key:
            continue
        diet_val = row.get("Dietary Preference")
        spice_val = row.get("Spice Tolerance")
        # Last one wins, but dataset titles should be unique
        RECIPE_DIET_MAP[key] = diet_val
        RECIPE_SPICE_MAP[key] = spice_val
except FileNotFoundError:
    # If the file is missing, keep columns empty so code still works
    print(
        "Warning: data/recipe_classifications.csv not found. "
        "Dietary preference and spice filters will be disabled and icons hidden."
    )
    df["Spice Tolerance"] = None
    df["Dietary Preference"] = None

# Combine processed_ingredients and ingredient_synonyms for better matching
# Handle NaN values in ingredient_synonyms column and normalize
df['ingredient_synonyms'] = df['ingredient_synonyms'].fillna('')
# Replace commas with spaces in synonyms to ensure proper tokenization
df['ingredient_synonyms'] = df['ingredient_synonyms'].astype(str).str.replace(',', ' ')
# Combine both columns for comprehensive matching
df['combined_ingredients'] = df['processed_ingredients'].astype(str) + ' ' + df['ingredient_synonyms'].astype(str)

# Use combined ingredients for TF-IDF vectorization
# This allows matching against both original ingredients and their synonyms
logger.info("Fitting TF-IDF vectorizer...")
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['combined_ingredients'])
logger.info("TF-IDF vectorization complete.")


def _normalize_pref_value(value):
    """
    Normalize preference strings to a simple, comparable form.
    Examples:
      "Non-Vegetarian" -> "nonvegetarian"
      "No specific preference" -> "none"
      "Non-Spicy" -> "nonspicy"
    """
    if not isinstance(value, str):
        return None
    return value.strip().lower().replace("-", "").replace(" ", "")


def _extract_user_preference_flags(prefs):
    """
    Extract normalized diet & spice preference flags from a preferences dict.
    Supported diet values include:
      - "No specific preference", "none", "any"
      - "Vegetarian"
      - "Non-Vegetarian", "Non Veg", etc.
    Supported spice values include:
      - "Spicy"
      - "Non-Spicy", "Mild"
    """
    prefs = prefs or {}

    raw_diet = (
        prefs.get("dietaryPreference")
        or prefs.get("dietary_preference")
        or prefs.get("diet")
    )
    raw_spice = (
        prefs.get("spiceTolerance")
        or prefs.get("spice_tolerance")
        or prefs.get("spice")
    )

    diet = _normalize_pref_value(raw_diet)
    spice = _normalize_pref_value(raw_spice)

    # Map "no preference" style values to None (no filtering)
    if diet in {"none", "nospecificpreference", "any", ""}:
        diet = None
    if spice in {"none", "any", ""}:
        spice = None

    return diet, spice


def _recipe_matches_flags(row, diet_flag, spice_flag):
    """
    Check if a single recipe row matches the given normalized flags.
    If a flag is None, that dimension is not filtered.
    """
    if diet_flag is None and spice_flag is None:
        return True

    # Normalize classification values from the merged CSV
    recipe_diet = _normalize_pref_value(row.get("Dietary Preference"))
    recipe_spice = _normalize_pref_value(row.get("Spice Tolerance"))

    # If a preference is set but the recipe has no classification, exclude it.
    if diet_flag is not None and not recipe_diet:
        return False
    if spice_flag is not None and not recipe_spice:
        return False

    # Diet filtering
    if diet_flag is not None:
        if diet_flag == "vegetarian":
            if recipe_diet != "vegetarian":
                return False
        elif diet_flag in {"nonvegetarian", "nonveg"}:
            if recipe_diet != "nonvegetarian":
                return False

    # Spice filtering
    if spice_flag is not None:
        if spice_flag == "spicy":
            if recipe_spice != "spicy":
                return False
        elif spice_flag in {"nonspicy", "mild"}:
            if recipe_spice != "nonspicy":
                return False

    return True


# -- Root Endpoint --
@app.route('/', methods=['GET'])
def home():
    return "Pantry match backend is running", 200


# -- 1. Recipe Search Endpoint --
@app.route('/search', methods=['GET'])
def search():
    user_query = request.args.get('q', '')
    user_vec = vectorizer.transform([user_query])
    scores = cosine_similarity(user_vec, tfidf_matrix).flatten()

    # Load user preferences (if authenticated) to apply diet & spice filters
    user_id = get_auth_user_id()
    diet_flag = None
    spice_flag = None
    if user_id:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT preferences FROM users WHERE id = ?", (user_id,))
            row = cur.fetchone()
            conn.close()
            prefs = {}
            if row and row["preferences"]:
                try:
                    prefs = json.loads(row["preferences"]) or {}
                except Exception:
                    prefs = {}
            diet_flag, spice_flag = _extract_user_preference_flags(prefs)
        except Exception as e:
            print("Failed to load user preferences:", str(e))

    # Collect the top 6 recipes that both match the query and respect preferences
    ranked_indices = scores.argsort()[::-1]
    selected_indices = []
    for idx in ranked_indices:
        if len(selected_indices) >= 6:
            break
        row = df.iloc[idx]
        if _recipe_matches_flags(row, diet_flag, spice_flag):
            selected_indices.append(idx)

    results = []
    for idx in selected_indices:
        row = df.iloc[idx]
        diet_val = row.get("Dietary Preference")
        spice_val = row.get("Spice Tolerance")
        results.append({
            'title': str(row['TranslatedRecipeName']),
            'ingredients': str(row['processed_ingredients']),
            'instructions': str(row['TranslatedInstructions']),
            'time': int(row['TotalTimeInMins']) if pd.notnull(row['TotalTimeInMins']) else None,
            'score': float(scores[idx]),
            'dietaryPreference': str(diet_val) if pd.notnull(diet_val) else None,
            'spiceTolerance': str(spice_val) if pd.notnull(spice_val) else None,
        })

    # Optionally record search history for authenticated users (dedup by query per user)
    if user_id and user_query.strip():
        try:
            normalized = " ".join(user_query.strip().split()).lower()
            conn = get_db_connection()
            # Remove older duplicates so the list stays unique
            conn.execute(
                "DELETE FROM search_history WHERE user_id = ? AND lower(trim(query)) = ?",
                (user_id, normalized),
            )
            conn.execute(
                "INSERT INTO search_history (user_id, query, created_at) VALUES (?, ?, ?)",
                (user_id, user_query.strip(), datetime.utcnow().isoformat()),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print("Failed to record search history:", str(e))

    return jsonify(results)


# -- Auth & User Profile Endpoints --
@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Simple hash: not production-grade but better than plain text
    # Use sha256 with salt derived from AUTH_SECRET
    import hashlib

    salt = AUTH_SECRET.encode("utf-8")
    pwd_hash = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO users (name, email, password_hash, created_at, preferences)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, pwd_hash, datetime.utcnow().isoformat(), json.dumps({"diet": "none"})),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "An account with this email already exists"}), 400

    cur.execute("SELECT id, name, email, created_at, preferences FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    token = generate_token(user_id)
    profile = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "created_at": row["created_at"],
        "preferences": json.loads(row["preferences"]) if row["preferences"] else {},
    }
    return jsonify({"token": token, "user": profile}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    import hashlib

    salt = AUTH_SECRET.encode("utf-8")
    pwd_hash = hashlib.sha256(salt + password.encode("utf-8")).hexdigest()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, email, password_hash, created_at, preferences FROM users WHERE email = ?",
        (email,),
    )
    row = cur.fetchone()
    conn.close()

    if not row or row["password_hash"] != pwd_hash:
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(row["id"])
    profile = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "created_at": row["created_at"],
        "preferences": json.loads(row["preferences"]) if row["preferences"] else {},
    }
    return jsonify({"token": token, "user": profile}), 200


@app.route('/auth/me', methods=['GET'])
def me():
    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, email, created_at, preferences FROM users WHERE id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "User not found"}), 404

    profile = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "created_at": row["created_at"],
        "preferences": json.loads(row["preferences"]) if row["preferences"] else {},
    }
    return jsonify({"user": profile}), 200


@app.route('/user/preferences', methods=['POST'])
def update_preferences():
    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    preferences = data.get("preferences") or {}

    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET preferences = ? WHERE id = ?",
        (json.dumps(preferences), user_id),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "preferences": preferences}), 200


@app.route('/user/saved-recipes', methods=['GET', 'POST', 'DELETE'])
def saved_recipes():
    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'GET':
        cur.execute(
            """
            SELECT id, title, ingredients, instructions, time, created_at
            FROM saved_recipes
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        conn.close()
        # De-duplicate by title (most recent wins)
        seen_titles = set()
        recipes = []
        for r in rows:
            key = (r["title"] or "").strip().lower()
            if not key or key in seen_titles:
                continue
            seen_titles.add(key)

            # Attach dietary preference & spice tolerance from our lookup maps (best-effort)
            diet_val = RECIPE_DIET_MAP.get(key)
            spice_val = RECIPE_SPICE_MAP.get(key)

            recipes.append(
                {
                    "id": r["id"],
                    "title": r["title"],
                    "ingredients": r["ingredients"],
                    "instructions": r["instructions"],
                    "time": r["time"],
                    "created_at": r["created_at"],
                    "dietaryPreference": diet_val,
                    "spiceTolerance": spice_val,
                }
            )
        return jsonify({"recipes": recipes}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        title = (data.get("title") or "").strip()
        if not title:
            conn.close()
            return jsonify({"error": "Title is required"}), 400

        ingredients = data.get("ingredients") or ""
        instructions = data.get("instructions") or ""
        time_val = data.get("time")

        # Prevent duplicates: one saved recipe per title per user
        now = datetime.utcnow().isoformat()
        cur.execute(
            "SELECT id FROM saved_recipes WHERE user_id = ? AND lower(trim(title)) = ? LIMIT 1",
            (user_id, title.lower()),
        )
        existing = cur.fetchone()
        if existing:
            recipe_id = existing["id"]
            cur.execute(
                """
                UPDATE saved_recipes
                SET ingredients = ?, instructions = ?, time = ?, created_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    ingredients,
                    instructions,
                    int(time_val) if isinstance(time_val, (int, float)) else None,
                    now,
                    recipe_id,
                    user_id,
                ),
            )
            conn.commit()
            conn.close()
            return jsonify({"id": recipe_id, "success": True, "duplicate": True}), 200

        cur.execute(
            """
            INSERT INTO saved_recipes (user_id, title, ingredients, instructions, time, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                title,
                ingredients,
                instructions,
                int(time_val) if isinstance(time_val, (int, float)) else None,
                now,
            ),
        )
        conn.commit()
        recipe_id = cur.lastrowid
        conn.close()
        return jsonify({"id": recipe_id, "success": True, "duplicate": False}), 201

    # DELETE
    recipe_id = request.args.get("id")
    clear_all = request.args.get("clear") in ("1", "true", "yes")
    if clear_all:
        cur.execute("DELETE FROM saved_recipes WHERE user_id = ?", (user_id,))
    else:
        if not recipe_id:
            conn.close()
            return jsonify({"error": "Recipe id is required"}), 400
        cur.execute(
            "DELETE FROM saved_recipes WHERE id = ? AND user_id = ?",
            (recipe_id, user_id),
        )
    conn.commit()
    conn.close()
    return jsonify({"success": True}), 200


@app.route('/user/search-history', methods=['GET', 'DELETE'])
def get_search_history():
    user_id = get_auth_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'DELETE':
        clear_all = request.args.get("clear") in ("1", "true", "yes")
        history_id = request.args.get("id")
        if clear_all:
            cur.execute("DELETE FROM search_history WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return jsonify({"success": True}), 200
        if not history_id:
            conn.close()
            return jsonify({"error": "History id is required"}), 400
        cur.execute(
            "DELETE FROM search_history WHERE id = ? AND user_id = ?",
            (history_id, user_id),
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 200

    cur.execute(
        """
        SELECT id, query, created_at
        FROM search_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 120
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()

    # De-duplicate by normalized query (most recent wins)
    seen = set()
    history = []
    for r in rows:
        q = (r["query"] or "").strip()
        key = " ".join(q.split()).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        history.append({"id": r["id"], "query": q, "created_at": r["created_at"]})
        if len(history) >= 50:
            break

    return jsonify({"history": history}), 200

# -- 2. AI Adaptation Endpoint (OpenRouter) --
@app.route('/adapt', methods=['POST'])
def adapt():
    data = request.get_json()
    instructions = data.get('instructions', '')
    missing_ingredient = data.get('missing', '')
    title = data.get('title', '')
    prompt = (
        f"You are a smart Indian cooking assistant. Here is the recipe for '{title}'.\n"
        f"Instructions:\n{instructions}\n"
        f"The user does NOT have '{missing_ingredient}'. Suggest the best adaptation or workaround step (with local Indian knowledge), "
        f"explaining briefly what to do. Only output the modified or additional instruction, not the whole recipe."
    )
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful Indian recipe assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "PantryMatch adaptation"
    }
    try:
        resp = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(payload), timeout=40)
        if resp.status_code == 200:
            reply = resp.json()["choices"][0]["message"]["content"]
            return jsonify({"adaptedStep": reply})
        else:
            error_message = resp.text
            return jsonify({"adaptedStep": f"Could not fetch adaptation. Error: {error_message}"}), resp.status_code
    except Exception as e:
        return jsonify({"adaptedStep": "Could not fetch adaptation. Error: " + str(e)}), 500

# -- 3. YouTube Video Search Endpoint (RapidAPI, robust ID fix) --
@app.route('/videos', methods=['GET'])
def get_youtube_videos():
    recipe = request.args.get('recipe', '')
    # Only return the top 2 most relevant videos
    max_results = 2
    url = f"https://youtube-v3-alternative.p.rapidapi.com/search"
    params = {"query": recipe + " recipe", "maxResults": str(max_results)}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    resp = requests.get(url, headers=headers, params=params, timeout=20)
    print("RapidAPI response:", resp.status_code, resp.text)  # Debug

    results_key = "results"
    try:
        data = resp.json()
        if results_key not in data:
            if "data" in data:
                results_key = "data"
            elif "items" in data:
                results_key = "items"
        entries = data.get(results_key, [])
    except Exception as e:
        entries = []
        print("JSON parse error:", str(e))

    videos = []
    for item in entries[:max_results]:
        # Try link, then videoId/id, fallback empty string if not found
        link = item.get("link")
        if not link or link == "https://youtube.com/watch?v=None":
            video_id = item.get("id") or item.get("videoId")
            if video_id and video_id != "None":
                link = f"https://youtube.com/watch?v={video_id}"
            else:
                link = ""
        videos.append({
            "title": item.get("title", "No Title"),
            "url": link
        })

    if resp.status_code == 429:
        return jsonify({"error": "RapidAPI quota exceeded"}), 429
    elif resp.status_code != 200:
        return jsonify({"error": resp.text}), resp.status_code
    return jsonify(videos)

# -- 4. Image Ingredient Classification Endpoint (ResNet18) --

from ml_infer_ingredients import load_model, predict_ingredients_batch_from_bytes
print("Pre-loading ingredient classification model globally...")
try:
    ING_MODEL, ING_CLASSES, ING_DEVICE = load_model()
except Exception as e:
    print(f"Warning: Failed to load global ResNet model: {e}")
    ING_MODEL, ING_CLASSES, ING_DEVICE = None, [], None

@app.route('/classify-image', methods=['POST'])
def classify_image():
    """
    Classify ingredients from an uploaded image using the trained ResNet model.

    Accepts:
      - multipart/form-data with 'image' file

    Returns:
      - ingredients: list of ingredient names above a confidence threshold
      - predictions: full top-k predictions with probabilities
    """
    # Mode:
    #   - 'cnn' (default): use ResNet + optional OpenRouter
    #   - 'llm_only': skip ResNet, only call OpenRouter on uploaded image(s)
    mode = request.args.get('mode', 'cnn')

    # Support both single file ('image') and multiple files ('images')
    files = []
    if 'images' in request.files:
        files = request.files.getlist('images')
    elif 'image' in request.files:
        files = [request.files['image']]

    files = [f for f in files if f and f.filename]
    if not files:
        return jsonify({"error": "No image file provided"}), 400

    try:
        # Read all image bytes once
        image_bytes_list = [f.read() for f in files]

        all_preds = []
        cnn_ingredients_unique = []
        extra_ingredients = []

        # -------- Mode: CNN (multi images, ResNet + optional LLM) --------
        if mode == 'cnn':
            threshold = 0.35  # lower threshold for crop-based detection
            cnn_ingredients = []

            # 1. GENERATE GRID CROPS
            # We strictly use Grid Crops because it is faster and detects 100% of items without YOLO overhead
            all_crops = []
            for f, img_bytes in zip(files, image_bytes_list):
                crop_list = _generate_grid_crops(img_bytes)
                all_crops.append((f, crop_list))

            # 2. RUN FAST RESNET INFERENCE IN BATCHES
            for f, crop_list in all_crops:
                if not crop_list:
                    continue
                
                crop_names = [c[0] for c in crop_list]
                crop_bytes_list = [c[1] for c in crop_list]
                
                # Evaluate in batches of 8 to speed up PyTorch inference drastically and avoid timeout
                batch_preds = predict_ingredients_batch_from_bytes(
                    ING_MODEL, ING_CLASSES, ING_DEVICE, crop_bytes_list, top_k=10, max_batch_size=8
                )
                
                for crop_name, preds in zip(crop_names, batch_preds):
                    all_preds.append({"filename": f"{f.filename}:{crop_name}", "predictions": preds})
                    for p in preds:
                        if p["prob"] >= threshold:
                            cnn_ingredients.append(p["name"])

            # Deduplicate CNN ingredients
            seen_cnn = set()
            for name in cnn_ingredients:
                key = name.lower()
                if key not in seen_cnn:
                    seen_cnn.add(key)
                    cnn_ingredients_unique.append(name)

        # Return only CNN (ResNet18) ingredients for search
        # OpenRouter is reserved for the /adapt endpoint (AI ingredient substitution)
        all_ings = cnn_ingredients_unique

        return jsonify({
            "ingredients": all_ings,
            "cnn_ingredients": cnn_ingredients_unique,
            "llm_ingredients": extra_ingredients,
            "per_image_predictions": all_preds,
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print("Error in /classify-image:", str(e))
        return jsonify({"error": "Failed to classify image", "details": str(e)}), 500
    finally:
        import gc
        gc.collect()


# -- Run App --
if __name__ == '__main__':
    app.run(debug=True)
