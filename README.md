# 🍳 PantryMatch

> **Recipe Retrieval Using Image of Ingredients** - Find delicious recipes from your pantry ingredients using our custom-trained ML model and computer vision

PantryMatch is an intelligent recipe discovery platform that helps you find the perfect recipes based on ingredients you already have. It uses machine learning **(TF-IDF and cosine similarity)** to match your pantry items with recipes, **computer vision (ResNet18 CNN)** to detect ingredients from photos, **AI vision models** for enhanced detection, **synonym matching** for better recipe discovery, **user authentication** with preferences and saved recipes, and **AI to suggest ingredient substitutions** when you're missing something.

![PantryMatch](https://img.shields.io/badge/PantryMatch-Recipe%20Finder-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-19.2-blue?style=for-the-badge&logo=react)
![Flask](https://img.shields.io/badge/Flask-3.1-green?style=for-the-badge&logo=flask)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange?style=for-the-badge&logo=pytorch)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=for-the-badge&logo=sqlite)

## ✨ Features

### 🔍 Core Features
- **Smart Recipe Search** - Enter your ingredients and get matched recipes using TF-IDF vectorization and cosine similarity
- **Synonym Matching** - Advanced matching system that recognizes ingredient synonyms (e.g., "chili powder" matches "red chilli powder", "chilli powder")
- **Match Score** - See how well each recipe matches your ingredients (0-100%)
- **Missing Ingredients Tracker** - Each recipe card highlights exactly which ingredients you're missing, or lets you know if you have everything you need.
- **Interactive Filtering & Sorting** - Dynamically filter results by max prep time, missing ingredients limit, or dietary preference. Sort recipes by Best Match, Prep Time, or Missing Items.
- **Pagination** - Navigate through matched recipes effortlessly using a seamless "Show More" functionality
- **Fast & Responsive** - Optimized search with pre-processed recipe data

### 👤 User Account Features
- **User Authentication** - Sign up and login with email/password authentication
- **User Preferences** - Filter recipes by dietary preferences (vegetarian/non-vegetarian) and spice tolerance (spicy/mild)
- **Saved Recipes** - Save your favorite recipes with one click
- **Search History** - Track your previous searches
- **Persistent Profiles** - All your preferences and saved recipes are preserved across sessions

### 📸 Image-Based Ingredient Detection
Two powerful options for detecting ingredients from images:
1. **Separate Images Mode** (CNN + YOLO Cropping):
   - Upload multiple images, one per ingredient
   - **YOLO v8n object detection** automatically segments food items
   - ResNet18 model analyzes each detected crop
   - Detailed processing to extract accurate ingredient predictions
   - See CNN predictions with confidence scores
   - **Comprehensive cropping strategy**: Base Grid crops (2x2, 3x3) + Center crop + YOLO detection for extra precision

2. **Combined Image Mode** (CNN + YOLO Cropping):
   - Upload a single image with all your ingredients
   - **Smart cropping mechanism** uses YOLO to detect food objects
   - Multiple crops analyzed per image (YOLO detections + overlapping grid crops)
   - Uses the ResNet18 model across all crops to cleanly separate and extract ingredients
   - Clean ingredient list ready for recipe search

### 🧠 ML-Powered Detection Features
- **Combined Smart Cropping** - Generates standard grid crops (2x2, 3x3 grids with 8% overlap) as a baseline, and layers on YOLOv8n object detection to add highly-precise crops for specific food objects (confidence threshold 0.6). This ensures no obscure ingredients are missed while cleanly bounding known ones.
- **Multi-Crop Analysis** - Processes multiple crops per image: full image, YOLO-detected regions, overlapping grid segments, and center crops
- **Confidence-Based Search & Prediction Rules** - Filters predictions with a strict confidence threshold (0.35). Explicitly filters out specific problematic predictions (e.g. "Sweetpotato") to reduce false-positive rates.
- **Robust Detection System** - Combines custom-trained ResNet18 model with YOLO object detection for best accuracy

### 📊 Additional Features
- **Dietary Classification** - Recipes categorized by dietary preference and spice tolerance
- **🎥 Video Tutorials** - Access YouTube video tutorials for each recipe
- **🎨 Beautiful UI** - Modern, food-themed design with warm colors, smooth animations, and a recently refined visually-appealing Authentication workflow
- **🏗️ Component-Based Architecture** - Modern React structure with reusable components and custom hooks

## 🛠️ Tech Stack

### Backend
- **Python 3.11+**
- **Flask** - Web framework
- **PyTorch** - Deep learning framework for ResNet18 model
- **scikit-learn** - TF-IDF vectorization and cosine similarity
- **pandas** - Data processing
- **Pillow (PIL)** - Image processing
- **RapidAPI** - YouTube video search

### Frontend
- **React 19.2** - UI framework with component-based architecture
- **Vite** - Build tool
- **CSS3** - Custom styling with modern design
- **Custom Hooks** - Reusable state management hooks
- **Component Architecture** - Modular, maintainable code structure

### Machine Learning
- **ResNet18** - Pre-trained CNN architecture fine-tuned on 95 ingredient classes
- **YOLOv8n (Nano)** - Lightweight YOLO model for real-time food object detection
- **Transfer Learning** - Fine-tuning pre-trained ResNet18 for ingredient classification
- **Custom Dataset** - 95 classes of fruits and vegetables

## � Dependencies

### Backend Dependencies

**Web Framework:**
- `flask>=3.1` - Python web framework
- `flask-cors` - Cross-Origin Resource Sharing support

**Data Processing:**
- `pandas` - Data manipulation and CSV handling
- `scikit-learn` - Machine learning (TF-IDF, cosine similarity)

**Machine Learning:**
- `torch>=2.0` - PyTorch deep learning framework
- `torchvision` - Computer vision utilities and pre-trained models
- `ultralytics` - YOLOv8 object detection models

**Image Processing:**
- `pillow` - Image processing library

**API & External Services:**
- `requests` - HTTP client for external API calls
- RapidAPI YouTube API - Video search

**Security & Data:**
- `itsdangerous` - Security utilities for token generation
- `sqlite3` - Built-in database (no extra package needed)

**Full backend requirements:**
```bash
pip install flask flask-cors pandas scikit-learn torch torchvision pillow requests itsdangerous ultralytics
```

### Frontend Dependencies

**Core:**
- `react@^19.2.0` - UI framework
- `react-dom@^19.2.0` - React DOM rendering

**Development:**
- `vite@^7.2.4` - Build tool
- `@vitejs/plugin-react@^5.1.1` - React plugin for Vite
- `eslint@^9.39.1` - Code linting
- `eslint-plugin-react-hooks` - React hooks linting
- `eslint-plugin-react-refresh` - React Refresh support

**Install all:**
```bash
npm install
```

## �📋 Prerequisites

- Python 3.11 or higher
- Node.js 18+ and npm
- API Keys:
  - RapidAPI key (for YouTube videos)
- GPU (optional but recommended for training the CNN model)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/PantryMatch.git
cd PantryMatch
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install flask flask-cors pandas scikit-learn requests torch torchvision pillow itsdangerous ultralytics

# Set up API keys
# Copy the example config file and add your API keys
cp config.example.py config.py  # On Windows: copy config.example.py config.py
# Then edit config.py with your actual API keys
```

**API Keys Required:**
- `RAPIDAPI_KEY` - Get from https://rapidapi.com (YouTube API)

### 3. Train the Ingredient Classification Model (Optional)

If you want to train your own ResNet18 model or retrain with new data:

```bash
cd backend

# Make sure you have the dataset structure:
# backend/data/Train/ (with subdirectories for each ingredient class)

# Train the model using 5-fold cross validation
python ml_train_ingredients_model_5fold_cv_enhanced.py --epochs 15 --batch-size 32

# The trained model will be saved to:
# backend/models/best_enhanced_5fold_model.pt
```

**Note**: Training requires a dataset organized as:
```
backend/data/
└── Train/
    ├── Apple/
    │   ├── Apple_1.jpg
    │   ├── Apple_2.jpg
    │   └── ...
    ├── Banana/
    └── ... (other ingredient classes)
```

The model will automatically detect the number of classes from the directory structure.

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## 🎯 Quick Start

### Start Backend Server

```bash
cd backend

# Activate virtual environment (if not already activated)
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Run the Flask server
python app.py
```

The Flask server will run on `http://127.0.0.1:5000`

**First Run Notes:**
- The database (`users.db`) will be created automatically in `backend/data/`
- The ResNet18 model will be loaded from `backend/models/best_enhanced_5fold_model.pt`
- If the model doesn't exist, you must train it in order to use image classification

### Start Frontend Development Server

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

The React app will run on `http://localhost:5173` (or another port if 5173 is busy)

### Build for Production

**Frontend:**
```bash
cd frontend
npm run build
```

The production build will be in `frontend/dist/`

## 🔐 Authentication & User Data

### How Authentication Works

1. **Sign Up**: Create an account with email and password
   - Password is hashed using SHA256 with salt
   - User profile is created in database
   
2. **Login**: Authenticate with email and password
   - Returns authentication token (Bearer token)
   - Token is valid for 7 days
   
3. **Token Usage**: Include token in Authorization header
   ```
   Authorization: Bearer <token>
   ```
   
4. **Protected Endpoints**: Automatically use token if available
   - User preferences are applied to recipe search
   - Saved recipes and search history are personalized

### Default Behavior (No Authentication)

- All search and image detection features work without authentication
- Recipes are filtered by general popularity/relevance
- No persistent data storage
- No user preferences or saved recipes

### With Authentication

- User preferences (diet, spice) automatically filter results
- All searched recipes are saved with search history
- Save favorite recipes for quick access later
- Personalized recommendations based on preferences
- All data persists across sessions

### User Data Storage

All user data is stored locally in SQLite:
- User accounts and passwords (hashed)
- User preferences (diet, spice tolerance)
- Saved recipes (title, ingredients, instructions)
- Search history (queries with timestamps)

### Using the Application

#### Without Authentication
1. **Search Recipes**: Enter your ingredients (comma-separated) in the search box. The system automatically matches against ingredient synonyms for better results.
2. **Image Detection** (Two Options):
   - **Option 1 - Separate Images**: Upload multiple images, one per ingredient. The ResNet18 model analyzes each image (with multi-crop processing). See "Detected by model" chips for CNN predictions.
   - **Option 2 - Combined Image**: Upload a single image containing all ingredients. Uses CNN with YOLO multi-crop processing to comprehensively capture and classify ingredients.
3. **View Results**: Browse matched recipes sorted by match score
4. **Refine Search**: Use the interactive sliders to filter by maximum Preparation Time or Missing Items, and toggle Veg/Non-Veg dietary preferences. You can also re-sort results based on Preparation Time or Missing Items.
5. **View Recipe Details**: Click "View Recipe" to see full instructions
6. **Get Substitutions**: Enter a missing ingredient to get AI-powered suggestions
6. **Watch Tutorials**: Access YouTube video tutorials for visual guidance

#### With User Account
After signing up or logging in, you get:
1. **Save Recipes** - Click the save icon on recipes to add them to your personal collection
2. **Set Preferences** - Configure dietary preferences (vegetarian/non-vegetarian) and spice tolerance (spicy/mild) to personalize recipe recommendations
3. **Track History** - Your recent searches are automatically saved
4. **Access Saved Recipes** - View all your saved recipes anytime from your profile
5. **All searches and preferences are persisted** across sessions

## 📡 API Endpoints

### Authentication Endpoints

#### `POST /auth/signup`
Create a new user account.

**Request Body:**
```json
{
  "name": "User Name",
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (201 Created):**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com",
    "created_at": "2024-01-15T10:30:00.000000",
    "preferences": {"diet": "none", "spice": "none"}
  }
}
```

**Error Responses:**
- `400`: Missing required fields or password < 6 characters
- `400`: Email already registered

#### `POST /auth/login`
Authenticate an existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com",
    "created_at": "2024-01-15T10:30:00.000000",
    "preferences": {"diet": "vegetarian", "spice": "mild"}
  }
}
```

**Error Responses:**
- `400`: Missing email or password
- `401`: Invalid email or password

#### `GET /auth/me`
Get current authenticated user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com",
    "created_at": "2024-01-15T10:30:00.000000",
    "preferences": {"diet": "vegetarian", "spice": "mild"}
  }
}
```

**Error Responses:**
- `401`: Unauthorized (invalid/missing token)
- `404`: User not found

### Recipe Search Endpoints

#### `GET /search`
Search for recipes based on ingredients. Matches against both original ingredients and synonyms. Applies user preferences if authenticated.

**Query Parameters:**
- `q` (string, required): Comma-separated list of ingredients

**Headers (optional):**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
[
  {
    "title": "Chicken Curry",
    "ingredients": "chicken, tomato, onion, garlic, ginger, spices",
    "instructions": "Step-by-step instructions...",
    "time": 45,
    "score": 0.92,
    "dietaryPreference": "nonvegetarian",
    "spiceTolerance": "spicy"
  },
  {
    "title": "Vegetable Stir Fry",
    "ingredients": "cabbage, carrot, onion, soya sauce",
    "instructions": "Heat oil and add vegetables...",
    "time": 20,
    "score": 0.78,
    "dietaryPreference": "vegetarian",
    "spiceTolerance": "mild"
  }
]
```

**How Synonym Matching Works:**
- Recipes have both `processed_ingredients` (main ingredients) and `ingredient_synonyms` columns
- User queries are matched against both original names and all synonym variations
- Example: Searching for "chili powder" matches recipes with "red chilli powder", "chilli powder", "red chili powder" in their synonyms
- Results return top 6 recipes ranked by match score

#### `POST /classify-image`
Detect ingredients from uploaded image(s). Supports two modes with **YOLO-based smart cropping**.

**Cropping Strategy:**
- **YOLO Detection**: Uses YOLOv8n to automatically detect food objects in the image with a stable threshold (0.6)
- **Smart Crop Generation (Combined Strategy)**:
  1. Full image crop (always included)
  2. Overlapping grid crops (2x2 and 3x3 grids with 8% overlap) - protects against obscure ingredients that YOLO doesn't recognize
  3. Center crop (80% of image centered) - helps capture centrally positioned ingredients
  4. YOLO-detected regions (with 20px adaptive padding) - layers high-precision crops of specific detected objects on top of the grid crops constraints
- **Multi-Crop Analysis**: Each crop is analyzed by ResNet18 model separately
- **Confidence Filtering**: Only predictions with confidence >= 0.35 are included to avoid false positives
- **Deduplication**: Results are deduplicated by ingredient name

**Request Body:**
- Content-Type: `multipart/form-data`
- `images` (multiple files) or single `image`

**Response (200 OK):**
```json
{
  "ingredients": ["chicken", "apple", "corn", "cabbage"],
  "cnn_ingredients": ["Cabbage", "Corn", "Apple"],
  "per_image_predictions": [
    {
      "filename": "image1.jpg:full",
      "predictions": [
        {"name": "Cabbage", "prob": 0.996},
        {"name": "Corn", "prob": 0.992}
      ]
    },
    {
      "filename": "image1.jpg:yolo_obj_0_conf_0.85",
      "predictions": [
        {"name": "Cabbage", "prob": 0.98}
      ]
    }
  ]
}
```

**Crop Types in Per-Image Predictions:**
- `full` - Full image (always included)
- `yolo_obj_<idx>_conf_<confidence>` - YOLO-detected object with confidence score
- `grid_2x2_r<row>c<col>` - 2x2 grid crop
- `grid_3x3_r<row>c<col>` - 3x3 grid crop
- `center_80` - Center 80% crop

**Response Fields:**
- `ingredients`: Deduplicated list of detected ingredients from ResNet18
- `cnn_ingredients`: Ingredients detected by ResNet18 model (confidence > 0.35)
- `per_image_predictions`: Detailed CNN predictions per image with confidence scores

#### `GET /videos`
Get YouTube video tutorials for a recipe.

**Query Parameters:**
- `recipe` (string, required): Recipe name

**Response (200 OK):**
```json
[
  {
    "title": "How to Make Chicken Curry - Easy Recipe",
    "url": "https://www.youtube.com/watch?v=..."
  },
  {
    "title": "Quick Chicken Curry Tutorial",
    "url": "https://www.youtube.com/watch?v=..."
  }
]
```

### User Preference Endpoints

#### `POST /user/preferences`
Update user preferences (diet and spice tolerance).

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "preferences": {
    "diet": "vegetarian",
    "spice": "spicy"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "preferences": {
    "diet": "vegetarian",
    "spice": "spicy"
  }
}
```

**Preference Values:**
- `diet`: `"none"`, `"vegetarian"`, `"nonvegetarian"` (or `"nonveg"`)
- `spice`: `"none"`, `"spicy"`, `"nonspicy"` (or `"mild"`)

**Error Responses:**
- `401`: Unauthorized

### Saved Recipes Endpoints

#### `GET /user/saved-recipes`
Get all saved recipes for the authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "recipes": [
    {
      "id": 1,
      "title": "Chicken Curry",
      "ingredients": "chicken, tomato, onion...",
      "instructions": "Heat oil and cook...",
      "time": 45,
      "created_at": "2024-01-15T10:30:00.000000",
      "dietaryPreference": "nonvegetarian",
      "spiceTolerance": "spicy"
    }
  ]
}
```

**Error Responses:**
- `401`: Unauthorized

#### `POST /user/saved-recipes`
Save a recipe or update an existing saved recipe.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Chicken Curry",
  "ingredients": "chicken, tomato, onion, garlic",
  "instructions": "Heat oil and cook chicken...",
  "time": 45
}
```

**Response (201 Created or 200 OK):**
```json
{
  "id": 1,
  "success": true,
  "duplicate": false
}
```

**Response Fields:**
- `duplicate`: `false` = new recipe created, `true` = existing recipe updated
- Prevents duplicate recipes per user by title

**Error Responses:**
- `400`: Title is required
- `401`: Unauthorized

#### `DELETE /user/saved-recipes`
Delete a saved recipe or clear all saved recipes.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters (one required):**
- `id` (number): Delete specific recipe by ID
- `clear=true`: Delete all saved recipes

**Response (200 OK):**
```json
{
  "success": true
}
```

**Error Responses:**
- `400`: Missing `id` parameter or valid `clear` value
- `401`: Unauthorized

### Search History Endpoints

#### `GET /user/search-history`
Get recent search history for authenticated user (up to 120 most recent).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "history": [
    {
      "id": 1,
      "query": "chicken, tomato, onion",
      "created_at": "2024-01-15T10:30:00.000000"
    }
  ]
}
```

**Error Responses:**
- `401`: Unauthorized

#### `DELETE /user/search-history`
Delete specific search history entry or clear all history.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters (one required):**
- `id` (number): Delete specific history entry by ID
- `clear=true`: Delete all search history

**Response (200 OK):**
```json
{
  "success": true
}
```

**Error Responses:**
- `400`: Missing `id` parameter or valid `clear` value
- `401`: Unauthorized

## 🗄️ Database Schema

PantryMatch uses SQLite for persistent data storage with the following tables:

### `users` Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    preferences TEXT
);
```

### `saved_recipes` Table
```sql
CREATE TABLE saved_recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    ingredients TEXT,
    instructions TEXT,
    time INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### `search_history` Table
```sql
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    query TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Indexes:**
- `idx_saved_recipes_user_created` - For fast sorting of recipes
- `idx_saved_recipes_user_title` - For preventing duplicate titles per user
- `idx_search_history_user_created` - For chronological search history
- `idx_search_history_user_query` - For deduplication and quick lookup

**Location:** `backend/data/users.db` (auto-created on first run)

## 📁 Project Structure

```
PantryMatch/
├── README.md                           # Project documentation
├── backend/                            # Flask backend server
│   ├── app.py                          # Main Flask application with all API endpoints
│   ├── ml_train_ingredients_model_5fold_cv_enhanced.py   # ResNet18 model training script with 5-fold CV
│   ├── ml_infer_ingredients.py         # Model loading and inference utilities
│   ├── prepare_data.py                 # Data preprocessing utilities
│   ├── generate_final_report.py        # Utility to generate classification reports
│   ├── yolov8n.pt                      # YOLOv8 object detection model weights
│   ├── config.py                       # API keys configuration (git-ignored)
│   ├── config.example.py               # API keys template
│   ├── __pycache__/                    # Python cache directory
│   ├── data/
│   │   ├── Cleaned_Indian_Food_Dataset.csv    # Original raw recipe dataset
│   │   ├── final_recipes.csv                  # Processed recipe data with TF-IDF
│   │   ├── recipe_classifications.csv         # Dietary/spice classifications
│   │   ├── users.db                           # SQLite user database (auto-created)
│   │   └── Train/                             # Training images for ResNet18 (95 classes)
│   │       ├── Apple/          # 95 ingredient class directories
│   │       ├── Banana/         # Each contains training images
│   │       ├── Cabbage/
│   │       ├── Carrot/
│   │       ├── Chicken/
│   │       ├── Corn/
│   │       ├── ... (other classes)
│   │       └── Tomato/
│   └── models/
│       ├── best_enhanced_5fold_model.pt # Best trained ResNet18 model weights
│       ├── enhanced_5fold_metrics.json  # Cross-validation performance metrics
│       ├── enhanced_5fold_report.txt    # Summary training report
│       ├── fold_*_ingredients_resnet18.pt # Individual fold model weights
│       └── ingredients_classes.txt      # 95 ingredient class names (one per line)
│
├── frontend/                            # React frontend application
│   ├── eslint.config.js                 # ESLint configuration
│   ├── package.json                     # NPM dependencies and scripts
│   ├── vite.config.js                   # Vite build configuration
│   ├── index.html                       # HTML entry point
│   ├── README.md                        # Frontend-specific documentation
│   ├── public/                          # Static assets (public files)
│   ├── src/
│   │   ├── main.jsx                     # React entry point
│   │   ├── App.jsx                      # Main application component
│   │   ├── App.css                      # Main application styles
│   │   ├── index.css                    # Global styles
│   │   ├── assets/                      # Images and static assets
│   │   ├── components/                  # React components
│   │   │   ├── Alert.jsx                # Alert/notification component
│   │   │   ├── Header.jsx               # App header with navigation
│   │   │   ├── SearchBox.jsx            # Ingredient search input
│   │   │   ├── LoginPage.jsx            # Login page component
│   │   │   ├── SignupPage.jsx           # Sign up page component
│   │   │   ├── ProfilePage.jsx          # User profile page
│   │   │   ├── DetectedIngredients.jsx  # Display detected ingredients
│   │   │   ├── EmptyState.jsx           # Empty state placeholder
│   │   │   ├── RecipeList.jsx           # Recipe results container
│   │   │   ├── RecipeCard.jsx           # Individual recipe card
│   │   │   ├── Toast.jsx                # Toast notification component
│   │   │   ├── ImageUploadSection.jsx   # Image upload container
│   │   │   ├── ImageUpload/             # Image upload mode components
│   │   │   │   ├── SingleImageUpload.jsx # Single combined image upload
│   │   │   │   └── MultiImageUpload.jsx  # Multiple individual ingredient images
│   │   │   ├── styles/                  # Component-specific styles
│   │   │   └── RecipeModal/
│   │   │       ├── RecipeModal.jsx      # Recipe detail modal
│   │   │       ├── ModalHeader.jsx      # Modal header with title
│   │   │       ├── IngredientsSection.jsx    # Modal ingredients section
│   │   │       ├── InstructionsSection.jsx   # Modal instructions section
│   │   │       ├── AdaptationSection.jsx     # Modal adaptation/substitution section
│   │   │       └── VideosSection.jsx        # Modal videos section
│   │   ├── hooks/                       # Custom React hooks
│   │   │   ├── useImageUpload.js        # Image upload state management
│   │   │   └── useIngredientDetection.js # Ingredient detection logic
│   │   ├── services/                    # API service layer
│   │   │   └── api.js                   # Centralized API communication
│   │   ├── data/                        # Data files (if any)
│   │   └── utils/                       # Utility functions
│   │       └── helpers.js               # Helper functions
│   └── dist/                            # Production build (created by: npm run build)
│
└── test/                                # Test directory (if any)
```

### Key Directories Explained

#### Backend Data Directory (`backend/data/`)
- **CSV Files**: Recipe datasets with processed ingredients and synonyms
- **Train folder**: 95 ingredient classes for model training
  - Each class folder contains JPEG images of that ingredient
  - Automatically organized for PyTorch's ImageFolder dataset loader
- **users.db**: SQLite database created automatically on first run
  - Stores users, saved recipes, and search history
  - Location: `backend/data/users.db`

#### Backend Models Directory (`backend/models/`)
- **best_enhanced_5fold_model.pt**: PyTorch checkpoint file containing:
  - Best model state dictionary from 5-fold cross-validation
  - Class names list (95 ingredients)
  - All necessary info for inference
- Size: ~43 MB (ResNet18 weights)
- **Other Files**:
  - `enhanced_5fold_metrics.json`: Detailed accuracy metrics per fold
  - `enhanced_5fold_report.txt`: Summary report of training performance
  - `fold_X_ingredients...`: Individual weights per fold

#### Frontend Components
- **Page Components**: Full-page views (LoginPage, ProfilePage, etc.)
- **Feature Components**: Reusable feature components (SearchBox, RecipeCard, etc.)
- **Modal Components**: Sub-components for recipe modal functionality
- **Image Upload**: Separate folder for image upload related components

## 🔬 How It Works

### Recipe Matching Algorithm

1. **Data Preprocessing**: Recipe ingredients are cleaned and normalized
2. **Synonym Integration**: The system combines `processed_ingredients` and `ingredient_synonyms` columns for comprehensive matching
3. **TF-IDF Vectorization**: Both user query and combined recipe text are converted to TF-IDF vectors
4. **Cosine Similarity**: Computes similarity between query and each recipe
5. **Ranking**: Recipes are sorted by match score (0-100%)

**Formula:**
```
Match Score = cosine_similarity(user_ingredients, combined_recipe_text) × 100
```

**Synonym Matching Example:**
- Recipe has: `processed_ingredients = "red chilli powder"` and `ingredient_synonyms = "chili powder, chilli powder, red chili powder"`
- User searches: `"chili powder"`
- System matches because "chili powder" appears in the synonyms column

### Image-Based Ingredient Detection

PantryMatch uses a **multi-crop CNN approach** with smart image segmentation:

#### Image Detection Process
1. **YOLO Detection**: Detects individual food objects in the image
2. **Smart Cropping**: Generates multiple crops (YOLO objects + grid + center)
3. **ResNet18 Analysis**: Each crop is analyzed by the fine-tuned ResNet18 model
4. **Confidence Filtering**: Only predictions above 0.35 confidence are kept
5. **Deduplication**: Results are merged and deduplicated by ingredient name

**Model Architecture:**
- **Base**: ResNet18 (pre-trained on ImageNet)
- **Fine-tuning**: Last fully-connected layer replaced for 51-class classification
- **Training**: Transfer learning with Adam optimizer, learning rate scheduling
- **Classes**: 51 ingredient types (fruits and vegetables)

### YOLO Object Detection & Smart Cropping Architecture

**NEW**: PantryMatch now includes advanced **YOLO-based object detection** for more accurate ingredient identification from combined images.

#### Why YOLO + Smart Cropping?
- **Problem**: A single image with multiple ingredients can be challenging for classification
- **Solution**: 
  1. Detect individual food objects using YOLO
  2. Extract crops around detected objects
  3. Analyze each crop separately with ResNet18
  4. Combine results for higher accuracy

#### Cropping Strategy Flow

```
User uploads image
    ↓
YOLO v8n detection (using yolov8n.pt - lightweight nano model)
    ↓
Detection successful? → Generate YOLO crops (+ padding)
 ├─ YES: Continue with YOLO crops
 └─ NO: Fallback to grid cropping
    ↓
Multi-crop analysis:
 ├─ Full Image Crop (always included, no modification)
 ├─ YOLO-Detected Object Crops (with 20px adaptive padding)
 ├─ Grid Crops (2x2 and 3x3 overlapping grids with 8% overlap) 
 ├─ Center Crop (80% of image centered - helps capture centered ingredients)
 └─ Minimum size filtering (crops < 80-120px rejected)
    ↓
ResNet18 analyzes each crop separately
    ↓
Results deduplicated and merged
```

#### Crop Types Generated

| Crop Type | Purpose | When Used |
|-----------|---------|-----------|
| `full` | Full unmodified image | Always included as baseline |
| `yolo_obj_<idx>_conf_<score>` | Individual YOLO-detected objects | When YOLO detection succeeds |
| `grid_2x2_r<r>c<c>` | 2x2 grid cropping (4 segments) | Fallback if YOLO fails, grid size > 240px |
| `grid_3x3_r<r>c<c>` | 3x3 grid cropping (9 segments) | Fallback if YOLO fails, grid size > 240px |
| `center_80` | Center 80% crop | Helps detect centered ingredients |

#### Technical Implementation Details

**YOLO Configuration:**
- **Model**: YOLOv8 Nano (`yolov8n.pt`) - lightweight, optimized for speed
- **Confidence Threshold**: 0.6 (filters out low-confidence detections)
- **Input Resolution**: Image scaled to YOLO's input size
- **Output**: Bounding boxes (x1, y1, x2, y2) with confidence scores

**Adaptive Padding Strategy:**
```python
pad = 20  # pixels
x1 = max(0, x1 - pad)        # Expand left
y1 = max(0, y1 - pad)        # Expand up
x2 = min(width, x2 + pad)    # Expand right
y2 = min(height, y2 + pad)   # Expand down
```
- **Goal**: Capture full ingredient without cutting edges
- **Boundary Handling**: Clamps to image boundaries

**Grid Cropping Parameters:**
```python
Minimum image size: 240 pixels
2x2 Grid: 50% × 50% cells each
3x3 Grid: 33.3% × 33.3% cells each
Overlap: 8% (prevents splitting ingredients at boundaries)
Minimum crop size: 120 pixels
```

**ResNet18 Analysis per Crop:**
- Confidence threshold: **0.35** (lower than separate image mode for crop-specific predictions)
- Top-K predictions: 10 per crop
- Deduplication: Merges duplicate ingredient detections across crops

#### Fallback Mechanism

```python
if YOLO_detects_objects:
    use_yolo_crops()
else:
    print("YOLO: No objects detected, using grid crops as backup")
    use_grid_crops()
```

**Fallback advantages:**
- ✅ Ensures graceful degradation if YOLO fails
- ✅ Guarantees coverage of entire image even without object detection
- ✅ Provides multiple analysis angles for robust detection
- ✅ Handles edge cases (plain background, unclear objects, etc.)

#### Performance Characteristics

| Metric | Value |
|--------|-------|
| YOLO Model Size | ~21 MB (YOLOv8n) |
| YOLO Inference Time | ~50-100ms per image |
| Total Crops Per Image | 5-15 (depending on YOLO detections) |
| ResNet18 Inference | ~50ms per crop |
| Total Processing | ~1-2 seconds for combined image |

#### Result Merging Strategy

```
Per-Image Analysis:
├─ Full image → [Apple: 0.95, Tomato: 0.88]
├─ YOLO crop 1 → [Tomato: 0.92, Onion: 0.85]
├─ YOLO crop 2 → [Apple: 0.91]
├─ Grid 2x2 → [Apple: 0.87, Tomato: 0.89]
└─ Grid 3x3 → [Tomato: 0.90, Salt: 0.75]

Deduplication:
├─ Apple: [0.95, 0.91, 0.87] → Keep best
├─ Tomato: [0.88, 0.92, 0.89, 0.90] → Keep best
├─ Onion: [0.85]
└─ Salt: [0.75] → Confidence > 0.35 ✓

Final ingredients: [Apple, Tomato, Onion]
```

#### Multi-Crop Detection (CNN + YOLO)

**Full Pipeline**:
1. YOLO detects objects in image
2. ResNet18 analyzes each YOLO crop + grid crops + center crop
3. Results merged with deduplication
4. Final list returned sorted by confidence

**Example Response:**
```json
{
  "ingredients": ["Chicken", "Tomato", "Onion", "Garlic"],
  "cnn_ingredients": ["Tomato", "Onion"],
  "per_image_predictions": [
    {
      "filename": "pantry.jpg:full",
      "predictions": [{"name": "Tomato", "prob": 0.92}]
    },
    {
      "filename": "pantry.jpg:yolo_obj_0_conf_0.87",
      "predictions": [{"name": "Chicken", "prob": 0.95}]
    }
  ]
}
```

## 🏗️ Frontend Architecture

The frontend is built with React and Vite, using a modern component-based architecture with custom hooks for state management.

### Core Components

**Page Components:**
- **App** (`App.jsx`) - Main application component that manages navigation and routing
- **LoginPage** (`LoginPage.jsx`) - User authentication and login interface
- **SignupPage** (`SignupPage.jsx`) - New user registration interface
- **ProfilePage** (`ProfilePage.jsx`) - User profile with saved recipes and preferences

**Feature Components:**
- **Header** (`Header.jsx`) - App header with navigation and user menu
- **SearchBox** (`SearchBox.jsx`) - Ingredient search input with error handling
- **ImageUploadSection** (`ImageUploadSection.jsx`) - Container for image upload modes
- **SingleImageUpload** (`ImageUpload/ImageUploadSection.jsx`) - Single combined image upload
- **MultiImageUpload** (`ImageUpload/` folder) - Multiple individual ingredient images
- **DetectedIngredients** (`DetectedIngredients.jsx`) - Display detected ingredients with tags
- **RecipeList** (`RecipeList.jsx`) - Container for displaying recipe results
- **RecipeCard** (`RecipeCard.jsx`) - Individual recipe card with quick view
- **RecipeModal** (`RecipeModal/RecipeModal.jsx`) - Detailed recipe view with sub-components:
  - **ModalHeader** - Recipe title and save button
  - **IngredientsSection** - Full ingredient list with quantities
  - **InstructionsSection** - Step-by-step cooking instructions
  - **AdaptationSection** - AI substitution suggestions
  - **VideosSection** - Related YouTube video tutorials
- **EmptyState** (`EmptyState.jsx`) - Placeholder displayed when no recipes found
- **Alert** (`Alert.jsx`) - Error/success notification component
- **Toast** (`Toast.jsx`) - Transient notification messages

### Custom Hooks

**State Management Hooks:**
- **`useImageUpload.js`** - Manages image file selection and upload state
  - Handles single and multiple file uploads
  - File validation and formatting
  - Upload state tracking

- **`useIngredientDetection.js`** - Manages ingredient detection logic
  - Calls `/classify-image` API endpoint
  - Handles CNN and LLM detection modes
  - Manages loading and error states
  - Deduplicates detected ingredients

### Services

**API Service (`services/api.js`):**
- Central API communication layer
- Handles all backend API calls
- Manages authentication tokens (Bearer token in Authorization header)
- Built-in error handling and response formatting
- Methods for:
  - User authentication (signup, login, profile)
  - Recipe search
  - Image classification
  - Recipe adaptation
  - Video search
  - Saved recipes management
  - Search history
  - User preferences

### Utilities

**Helper Functions (`utils/helpers.js`):**
- Text formatting utilities
- Ingredient name normalization
- Score display formatting
- Time formatting for recipe durations

### Styling

- **App.css** - Main application styles with food-themed design
- **CSS3 Features**: Modern design with CSS Grid, Flexbox, and animations
- **Color Palette**: Warm orange and earth tones for food theme
- **Component Styles**: Scoped styling per component for maintainability
- **Responsive Design**: Mobile-first approach with media queries

## 🧪 Model Training Details

### Training Configuration
- **Architecture**: ResNet18
- **Input Size**: 224x224 pixels
- **Batch Size**: 32
- **Epochs**: 15 (default, configurable)
- **Optimizer**: Adam (lr=0.001)
- **Scheduler**: ReduceLROnPlateau (reduces LR when validation loss plateaus)
- **Loss Function**: CrossEntropyLoss
- **Data Augmentation**: 
  - Random resized crop (224x224)
  - Random horizontal flip
  - Color jitter (brightness, contrast, saturation, hue)
  - ImageNet normalization

### Training Process
1. **Transfer Learning**: Uses pre-trained ResNet18 weights from ImageNet
2. **Fine-tuning**: Replaces final fully-connected layer for 95-class classification
3. **5-Fold Cross-Validation**: 
   - Divides dataset into 5 separate folds
   - Trains and validates the model 5 times (using a different fold for validation each time)
   - Ensures robust performance evaluation across the entire dataset
4. **Training Loop**: 
   - Forward pass through ResNet18
   - CrossEntropyLoss calculation
   - Adam optimizer step with learning rate scheduling
5. **Model Evaluation & Saving**: Maintains accuracy metrics per fold and saves the best overall performing model.

### Model Performance
- The model is trained on a dataset of 95 ingredient classes using 5-fold CV
- Extensive metrics are tracked and logged per fold (`enhanced_5fold_metrics.json`)
- Best model checkpoint is saved based on validation performance across all folds
- Model file: `backend/models/best_enhanced_5fold_model.pt`

## 🔧 Development

### Backend Development
- All API endpoints are in `backend/app.py`
- Model training: `backend/ml_train_ingredients_model_5fold_cv_enhanced.py`
- Model inference: `backend/ml_infer_ingredients.py`
- Metrics report generation: `backend/generate_final_report.py`

### Frontend Development
- Main app: `frontend/src/App.jsx`
- Components: `frontend/src/components/`
- Hooks: `frontend/src/hooks/`
- Services: `frontend/src/services/`
- Styles: `frontend/src/App.css`

### Adding New Features
1. **New Component**: Create in `frontend/src/components/`
2. **New Hook**: Create in `frontend/src/hooks/`
3. **New API Endpoint**: Add to `backend/app.py`
4. **New Service**: Add to `frontend/src/services/api.js`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Recipe dataset: Indian Food Dataset
- Object Detection: YOLOv8 (Ultralytics)
- Video API: RapidAPI YouTube Alternative
- Deep Learning Framework: PyTorch
- Pre-trained Model: ResNet18 (ImageNet)
- Frontend Framework: React

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for food lovers who want to discover recipes from their pantry**
