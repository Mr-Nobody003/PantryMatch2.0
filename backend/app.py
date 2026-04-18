import os

# Render constraints removed - optimizing for Vercel multi-core processing

from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
# Try to import optimized scikit-learn ML libraries, fallback to lightweight local versions for Vercel
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    from simple_tfidf import SimpleTfidfVectorizer as TfidfVectorizer
    from simple_tfidf import simple_cosine_similarity as cosine_similarity
import requests
import json
import base64
import sqlite3
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import io
import pymongo
from bson.objectid import ObjectId
from PIL import Image
import gc

from ml_infer_ingredients import load_model, predict_ingredients_batch_from_bytes, predict_ingredients_from_bytes

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
# Explicit CORS config for the frontend to prevent preflight blocking and credential issues
CORS(
    app,
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:3000",
                "https://pantry-match-delta.vercel.app",
                "https://pantrymatch2-0.onrender.com",
                "https://pantry-match-api.vercel.app"
            ]
        }
    }
)

# --- Simple Token-Based Auth Setup (SQLite + signed tokens) ---
DATABASE_PATH = os.path.join("data", "users.db")
AUTH_SECRET = os.getenv("AUTH_SECRET_KEY") or "dev-secret-key"
TOKEN_EXP_SECONDS = 60 * 60 * 24 * 7  # 7 days

MONGO_URI = os.getenv("MONGO_URI")
if MONGO_URI:
    mongo_client = pymongo.MongoClient(MONGO_URI)
    mongo_db = mongo_client.get_default_database(default="pantrymatch")
else:
    mongo_client = None
    mongo_db = None

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
    
    # [CRITICAL OPTIMIZATION]: Downscale heavily to prevent OOM memory spikes and Render crashes 
    # on multi-image uploads (typical phone images are 12+ Megapixels taking ~36MB RAM per image).
    img.thumbnail((800, 800))
    w, h = img.size

    crops = [("full", _encode_crop_bytes(img))]

    # If the image is too small, skip cropping
    if min(w, h) < 240:
        return crops

    # Add 2x2 and 3x3 crops with slight overlap to avoid splitting ingredients.
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


def _generate_yolo_crops(image_bytes: bytes):
    """
    Use YOLO (via ONNX) to detect food objects and return crops around detected boxes,
    combined with standard grid crops for maximum coverage.
    Returns List[Tuple[str, bytes]] where name is crop label.
    """
    # Start with all grid crops so we don't miss anything YOLO doesn't recognize
    crops = _generate_grid_crops(image_bytes)
    
    try:
        from ml_infer_ingredients import predict_boxes_onnx
        boxes = predict_boxes_onnx(image_bytes)
        
        if boxes:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # Same thumbnailing as in _generate_grid_crops for consistency
            img.thumbnail((800, 800))
            w_orig, h_orig = Image.open(io.BytesIO(image_bytes)).size
            scale_w = img.size[0] / w_orig
            scale_h = img.size[1] / h_orig
            
            for idx, (x1, y1, x2, y2) in enumerate(boxes):
                # Scale boxes to thumbnailed image size
                x1, y1, x2, y2 = int(x1*scale_w), int(y1*scale_h), int(x2*scale_w), int(y2*scale_h)
                
                # Add padding
                pad = 20
                x1 = max(0, x1 - pad)
                y1 = max(0, y1 - pad)
                x2 = min(img.size[0], x2 + pad)
                y2 = min(img.size[1], y2 + pad)
                
                if x2 - x1 >= 80 and y2 - y1 >= 80:
                    crop = img.crop((x1, y1, x2, y2))
                    crops.append((f"yolo_box_{idx}", _encode_crop_bytes(crop)))
    except Exception as e:
        print(f"Warning: YOLO cropping failed: {e}")
        
    return crops


def get_db_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if mongo_db is not None:
        mongo_db.users.create_index("email", unique=True)
        return
        
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


# -- Root Endpoint (Health Check for Render) --
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Pantry match backend is running"}), 200

# -- Load Recipes & TF-IDF Search Setup --
RECIPE_DIET_MAP = {}
RECIPE_SPICE_MAP = {}
RECIPES_DATA = []
combined_ingredients = []
vectorizer = None
tfidf_matrix = None
_search_initialized = False

def _normalize_title_for_lookup(title):
    return (str(title) or "").strip().lower()

def init_search_data():
    global _search_initialized, vectorizer, tfidf_matrix, RECIPES_DATA, RECIPE_DIET_MAP, RECIPE_SPICE_MAP, combined_ingredients
    if _search_initialized:
        return

    # Pure native Python lookup maps to prevent memory overhead of Pandas
    try:
        with open("data/recipe_classifications.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = _normalize_title_for_lookup(row.get("TranslatedRecipeName", ""))
                if key:
                    RECIPE_DIET_MAP[key] = row.get("Dietary Preference")
                    RECIPE_SPICE_MAP[key] = row.get("Spice Tolerance")
    except FileNotFoundError:
        print(
            "Warning: data/recipe_classifications.csv not found. "
            "Dietary preference and spice filters will be disabled and icons hidden."
        )

    with open("data/final_recipes.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Keep only required fields in memory
            key = _normalize_title_for_lookup(row.get("TranslatedRecipeName", ""))
            diet_val = RECIPE_DIET_MAP.get(key)
            spice_val = RECIPE_SPICE_MAP.get(key)

            RECIPES_DATA.append({
                'TranslatedRecipeName': row.get("TranslatedRecipeName", ""),
                'processed_ingredients': row.get("processed_ingredients", ""),
                'TranslatedInstructions': row.get("TranslatedInstructions", ""),
                'TotalTimeInMins': row.get("TotalTimeInMins") if row.get("TotalTimeInMins") else None,
                'Dietary Preference': diet_val,
                'Spice Tolerance': spice_val
            })
            
            synonyms = row.get("ingredient_synonyms", "").replace(",", " ")
            ingredients = row.get("processed_ingredients", "")
            combined = str(ingredients) + " " + str(synonyms)
            combined_ingredients.append(combined)

    # Initialize Vectorizer securely on native string arrays (Saves >100MB of RAM)
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(combined_ingredients)
    
    _search_initialized = True


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


# -- 1. Recipe Search Endpoint --
@app.route('/search', methods=['GET'])
def search():
    init_search_data()
    user_query = request.args.get('q', '')
    user_vec = vectorizer.transform([user_query])
    scores = cosine_similarity(user_vec, tfidf_matrix).flatten()

    # Load user preferences (if authenticated) to apply diet & spice filters
    user_id = get_auth_user_id()
    diet_flag = None
    spice_flag = None
    if user_id:
        try:
            if mongo_db is not None:
                doc = mongo_db.users.find_one({"_id": ObjectId(user_id) if len(str(user_id)) == 24 else user_id})
                prefs = doc.get("preferences", {}) if doc else {}
            else:
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
        row = RECIPES_DATA[idx]
        if _recipe_matches_flags(row, diet_flag, spice_flag):
            selected_indices.append(idx)

    results = []
    for idx in selected_indices:
        row = RECIPES_DATA[idx]
        diet_val = row.get("Dietary Preference")
        spice_val = row.get("Spice Tolerance")
        time_val = row.get('TotalTimeInMins')
        
        try:
            time_int = int(float(time_val)) if time_val else None
        except ValueError:
            time_int = None
            
        results.append({
            'title': str(row.get('TranslatedRecipeName', '')),
            'ingredients': str(row.get('processed_ingredients', '')),
            'instructions': str(row.get('TranslatedInstructions', '')),
            'time': time_int,
            'score': float(scores[idx]),
            'dietaryPreference': str(diet_val) if diet_val else None,
            'spiceTolerance': str(spice_val) if spice_val else None,
        })

    # Optionally record search history for authenticated users (dedup by query per user)
    if user_id and user_query.strip():
        try:
            normalized = " ".join(user_query.strip().split()).lower()
            if mongo_db is not None:
                mongo_db.search_history.delete_many({"user_id": user_id, "normalized_query": normalized})
                mongo_db.search_history.insert_one({
                    "user_id": user_id,
                    "query": user_query.strip(),
                    "normalized_query": normalized,
                    "created_at": datetime.utcnow().isoformat()
                })
            else:
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

    if mongo_db is not None:
        try:
            now = datetime.utcnow().isoformat()
            doc = {
                "name": name,
                "email": email,
                "password_hash": pwd_hash,
                "created_at": now,
                "preferences": {"diet": "none"}
            }
            mongo_db.users.insert_one(doc)
            user_id = str(doc["_id"])
            profile = {
                "id": user_id,
                "name": name,
                "email": email,
                "created_at": now,
                "preferences": {"diet": "none"}
            }
            token = generate_token(user_id)
            return jsonify({"token": token, "user": profile}), 201
        except pymongo.errors.DuplicateKeyError:
            return jsonify({"error": "An account with this email already exists"}), 400
    else:
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

    if mongo_db is not None:
        doc = mongo_db.users.find_one({"email": email})
        if not doc or doc.get("password_hash") != pwd_hash:
            return jsonify({"error": "Invalid email or password"}), 401
            
        user_id = str(doc["_id"])
        token = generate_token(user_id)
        profile = {
            "id": user_id,
            "name": doc.get("name"),
            "email": doc.get("email"),
            "created_at": doc.get("created_at"),
            "preferences": doc.get("preferences", {})
        }
        return jsonify({"token": token, "user": profile}), 200
    else:
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

    if mongo_db is not None:
        doc = mongo_db.users.find_one({"_id": ObjectId(user_id) if len(str(user_id)) == 24 else user_id})
        if not doc:
            return jsonify({"error": "User not found"}), 404
        profile = {
            "id": str(doc["_id"]),
            "name": doc.get("name"),
            "email": doc.get("email"),
            "created_at": doc.get("created_at"),
            "preferences": doc.get("preferences", {})
        }
        return jsonify({"user": profile}), 200
    else:
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

    if mongo_db is not None:
        mongo_db.users.update_one(
            {"_id": ObjectId(user_id) if len(str(user_id)) == 24 else user_id},
            {"$set": {"preferences": preferences}}
        )
    else:
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

    if mongo_db is not None:
        if request.method == 'GET':
            init_search_data()
            cursor = mongo_db.saved_recipes.find({"user_id": user_id}).sort("created_at", pymongo.DESCENDING)
            seen_titles = set()
            recipes = []
            for r in cursor:
                key = (r.get("title") or "").strip().lower()
                if not key or key in seen_titles:
                    continue
                seen_titles.add(key)
                diet_val = RECIPE_DIET_MAP.get(key)
                spice_val = RECIPE_SPICE_MAP.get(key)
                recipes.append({
                    "id": str(r["_id"]),
                    "title": r.get("title"),
                    "ingredients": r.get("ingredients"),
                    "instructions": r.get("instructions"),
                    "time": r.get("time"),
                    "created_at": r.get("created_at"),
                    "dietaryPreference": diet_val,
                    "spiceTolerance": spice_val,
                })
            return jsonify({"recipes": recipes}), 200

        if request.method == 'POST':
            data = request.get_json() or {}
            title = (data.get("title") or "").strip()
            if not title:
                return jsonify({"error": "Title is required"}), 400

            ingredients = data.get("ingredients") or ""
            instructions = data.get("instructions") or ""
            time_val = data.get("time")
            now = datetime.utcnow().isoformat()
            time_int = int(time_val) if isinstance(time_val, (int, float)) else None

            existing = mongo_db.saved_recipes.find_one({"user_id": user_id, "lower_title": title.lower()})
            if existing:
                mongo_db.saved_recipes.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"ingredients": ingredients, "instructions": instructions, "time": time_int, "created_at": now}}
                )
                return jsonify({"id": str(existing["_id"]), "success": True, "duplicate": True}), 200

            doc = {
                "user_id": user_id,
                "title": title,
                "lower_title": title.lower(),
                "ingredients": ingredients,
                "instructions": instructions,
                "time": time_int,
                "created_at": now
            }
            mongo_db.saved_recipes.insert_one(doc)
            return jsonify({"id": str(doc["_id"]), "success": True, "duplicate": False}), 201

        recipe_id = request.args.get("id")
        clear_all = request.args.get("clear") in ("1", "true", "yes")
        if clear_all:
            mongo_db.saved_recipes.delete_many({"user_id": user_id})
        else:
            if not recipe_id:
                return jsonify({"error": "Recipe id is required"}), 400
            mongo_db.saved_recipes.delete_one({"_id": ObjectId(recipe_id) if len(str(recipe_id)) == 24 else recipe_id, "user_id": user_id})
        return jsonify({"success": True}), 200

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'GET':
        init_search_data()
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

    if mongo_db is not None:
        if request.method == 'DELETE':
            clear_all = request.args.get("clear") in ("1", "true", "yes")
            history_id = request.args.get("id")
            if clear_all:
                mongo_db.search_history.delete_many({"user_id": user_id})
                return jsonify({"success": True}), 200
            if not history_id:
                return jsonify({"error": "History id is required"}), 400
            mongo_db.search_history.delete_one({"_id": ObjectId(history_id) if len(str(history_id)) == 24 else history_id, "user_id": user_id})
            return jsonify({"success": True}), 200

        cursor = mongo_db.search_history.find({"user_id": user_id}).sort("created_at", pymongo.DESCENDING).limit(120)
        seen = set()
        history = []
        for r in cursor:
            q = (r.get("query") or "").strip()
            key = " ".join(q.split()).lower()
            if not key or key in seen:
                continue
            seen.add(key)
            history.append({"id": str(r["_id"]), "query": q, "created_at": r.get("created_at")})
            if len(history) >= 50:
                break
        return jsonify({"history": history}), 200

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

# Load globally once to prevent high-memory load cost on every request
ING_MODEL, ING_CLASSES, ING_DEVICE = None, None, None
try:
    print("Loading ingredient classification model globally...")
    ING_MODEL, ING_CLASSES, ING_DEVICE = load_model()
except Exception as e:
    print(f"Warning: Failed to load ingredient model globally. Error: {e}")

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
            if ING_MODEL is None:
                return jsonify({"error": "Ingredient model not loaded"}), 500

            threshold = 0.35  # lower threshold for crop-based detection

            cnn_ingredients = []

            # 1. PROCESS HYBRID CROPS (YOLO + GRIDS)
            all_crops = []
            for f, img_bytes in zip(files, image_bytes_list):
                crop_list = _generate_yolo_crops(img_bytes)
                all_crops.append((f, crop_list))
            
            # 2. RUN INFERENCE IN BATCHES
            for f, crop_list in all_crops:
                if not crop_list:
                    continue
                
                crop_names = [c[0] for c in crop_list]
                crop_bytes = [c[1] for c in crop_list]
                
                # Use batched prediction to process multiple crops significantly faster
                batch_preds = predict_ingredients_batch_from_bytes(
                    ING_MODEL, ING_CLASSES, ING_DEVICE, crop_bytes, top_k=10, max_batch_size=8
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
        # Force garbage collection to free memory on the Render server immediately
        gc.collect()


# -- Run App --
if __name__ == '__main__':
    app.run(debug=True)
