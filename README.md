# 🍳 PantryMatch

> **Recipe Retrieval Using Image of Ingredients** - Find delicious recipes from your pantry ingredients using AI-powered matching and computer vision

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
- **Fast & Responsive** - Optimized search with pre-processed recipe data

### 👤 User Account Features
- **User Authentication** - Sign up and login with email/password authentication
- **User Preferences** - Filter recipes by dietary preferences (vegetarian/non-vegetarian) and spice tolerance (spicy/mild)
- **Saved Recipes** - Save your favorite recipes with one click
- **Search History** - Track your previous searches
- **Persistent Profiles** - All your preferences and saved recipes are preserved across sessions

### 📸 Image-Based Ingredient Detection
Two powerful options for detecting ingredients from images:
1. **Separate Images Mode** (CNN + AI Vision):
   - Upload multiple images, one per ingredient
   - ResNet18 model analyzes each image
   - AI vision API refines the results
   - See CNN-only predictions with confidence scores

2. **Combined Image Mode** (AI Vision Only):
   - Upload a single image with all your ingredients
   - Direct AI analysis for ingredient extraction
   - Clean ingredient list ready for recipe search

### 🤖 AI-Powered Features
- **AI Ingredient Substitution** - Get intelligent, context-aware suggestions when you're missing an ingredient
- **AI Vision Detection** - Powered by GPT-4o-mini for high-accuracy ingredient identification
- **Hybrid Detection System** - Combines custom-trained ResNet18 model with OpenRouter vision API for best accuracy

### 📊 Additional Features
- **Dietary Classification** - Recipes categorized by dietary preference and spice tolerance
- **🎥 Video Tutorials** - Access YouTube video tutorials for each recipe
- **🎨 Beautiful UI** - Modern, food-themed design with warm colors and smooth animations
- **🏗️ Component-Based Architecture** - Modern React structure with reusable components and custom hooks

## 🛠️ Tech Stack

### Backend
- **Python 3.11+**
- **Flask** - Web framework
- **PyTorch** - Deep learning framework for ResNet18 model
- **scikit-learn** - TF-IDF vectorization and cosine similarity
- **pandas** - Data processing
- **Pillow (PIL)** - Image processing
- **OpenRouter API** - AI-powered ingredient substitution and vision (GPT-4o-mini)
- **RapidAPI** - YouTube video search

### Frontend
- **React 19.2** - UI framework with component-based architecture
- **Vite** - Build tool
- **CSS3** - Custom styling with modern design
- **Custom Hooks** - Reusable state management hooks
- **Component Architecture** - Modular, maintainable code structure

### Machine Learning
- **ResNet18** - Pre-trained CNN architecture fine-tuned on 51 ingredient classes
- **Transfer Learning** - Fine-tuning pre-trained ResNet18 for ingredient classification
- **Custom Dataset** - 51 classes of fruits and vegetables (Train/val split)

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

**Image Processing:**
- `pillow` - Image processing library

**API & External Services:**
- `requests` - HTTP client for external API calls
- OpenRouter API (via requests) - AI vision and substitution
- RapidAPI YouTube API - Video search

**Security & Data:**
- `itsdangerous` - Security utilities for token generation
- `sqlite3` - Built-in database (no extra package needed)

**Full backend requirements:**
```bash
pip install flask flask-cors pandas scikit-learn torch torchvision pillow requests itsdangerous
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
  - OpenRouter API key (for AI substitutions and vision)
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
pip install flask flask-cors pandas scikit-learn requests torch torchvision pillow itsdangerous

# Set up API keys
# Copy the example config file and add your API keys
cp config.example.py config.py  # On Windows: copy config.example.py config.py
# Then edit config.py with your actual API keys
```

**API Keys Required:**
- `OPENROUTER_API_KEY` - Get from https://openrouter.ai
- `RAPIDAPI_KEY` - Get from https://rapidapi.com (YouTube API)

### 3. Train the Ingredient Classification Model (Optional)

If you want to train your own ResNet18 model or retrain with new data:

```bash
cd backend

# Make sure you have the dataset structure:
# backend/data/Train/ (with subdirectories for each ingredient class)
# backend/data/val/ (with subdirectories for each ingredient class)

# Train the model
python ml_train_ingredients_model.py --epochs 15 --batch-size 32

# The trained model will be saved to:
# backend/models/ingredients_resnet18.pt
```

**Note**: Training requires a dataset organized as:
```
backend/data/
├── Train/
│   ├── Apple/
│   │   ├── Apple_1.jpg
│   │   ├── Apple_2.jpg
│   │   └── ...
│   ├── Banana/
│   └── ... (other ingredient classes)
└── val/
    ├── Apple/
    ├── Banana/
    └── ... (validation images)
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
- The ResNet18 model will be loaded from `backend/models/ingredients_resnet18.pt`
- If the model doesn't exist, image classification will only use AI vision

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
   - **Option 1 - Separate Images**: Upload multiple images, one per ingredient. The ResNet18 model analyzes each image, and AI vision refines the results. See "Detected by model" chips for CNN predictions.
   - **Option 2 - Combined Image**: Upload a single image containing all ingredients. Uses AI vision directly for detection.
3. **View Results**: Browse matched recipes with match scores
4. **View Recipe Details**: Click "View Recipe" to see full instructions
5. **Get Substitutions**: Enter a missing ingredient to get AI-powered suggestions
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
Detect ingredients from uploaded image(s). Supports two modes.

**Query Parameters:**
- `mode` (string, optional): 
  - `cnn` (default): Uses ResNet18 + optional OpenRouter vision
  - `llm_only`: Skips ResNet18, uses only OpenRouter vision

**Request Body:**
- Content-Type: `multipart/form-data`
- For `mode=cnn`: `images` (multiple files) or single `image`
- For `mode=llm_only`: `image` (single file)

**Response (200 OK):**
```json
{
  "ingredients": ["chicken", "apple", "corn", "cabbage"],
  "cnn_ingredients": ["Cabbage", "Corn", "Apple"],
  "llm_ingredients": ["chicken", "apple", "corn", "cabbage", "salt"],
  "per_image_predictions": [
    {
      "filename": "image1.jpg",
      "predictions": [
        {"name": "Cabbage", "prob": 0.996},
        {"name": "Corn", "prob": 0.992}
      ]
    }
  ]
}
```

**Response Fields:**
- `ingredients`: Final merged list (prefers LLM if available, otherwise CNN)
- `cnn_ingredients`: Ingredients detected by ResNet18 model only (confidence > 0.5)
- `llm_ingredients`: Ingredients detected by OpenRouter vision API
- `per_image_predictions`: Detailed CNN predictions per image with confidence scores

#### `POST /adapt`
Get AI-powered ingredient substitution suggestions.

**Request Body:**
```json
{
  "title": "Chicken Curry",
  "instructions": "Cook chicken with tomato sauce and spices...",
  "missing": "chicken"
}
```

**Response (200 OK):**
```json
{
  "adaptedStep": "You can substitute chicken with paneer (cottage cheese) for a vegetarian version, or use tofu for a vegan option. Keep the same cooking time and add the substitute at the same step."
}
```

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
│   ├── ml_train_ingredients_model.py   # ResNet18 model training script
│   ├── ml_infer_ingredients.py         # Model loading and inference utilities
│   ├── prepare_data.py                 # Data preprocessing utilities
│   ├── config.py                       # API keys configuration (git-ignored)
│   ├── config.example.py               # API keys template
│   ├── __pycache__/                    # Python cache directory
│   ├── data/
│   │   ├── Cleaned_Indian_Food_Dataset.csv    # Original raw recipe dataset
│   │   ├── final_recipes.csv                  # Processed recipe data with TF-IDF
│   │   ├── recipe_classifications.csv         # Dietary/spice classifications
│   │   ├── users.db                           # SQLite user database (auto-created)
│   │   ├── Train/                             # Training images for ResNet18 (51 classes)
│   │   │   ├── Apple/          # 51 ingredient class directories
│   │   │   ├── Banana/         # Each contains training images
│   │   │   ├── Cabbage/
│   │   │   ├── Carrot/
│   │   │   ├── Chicken/
│   │   │   ├── Corn/
│   │   │   ├── ... (other classes)
│   │   │   └── Tomato/
│   │   └── val/                          # Validation images for ResNet18
│   │       ├── Apple/          # Same 51 ingredient classes
│   │       ├── Banana/         # For validation during training
│   │       └── ... (other classes)
│   └── models/
│       ├── ingredients_resnet18.pt      # Trained ResNet18 model weights
│       └── ingredients_classes.txt      # 51 ingredient class names (one per line)
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
│   │   │   ├── ImageUpload/
│   │   │   │   └── ImageUploadSection.jsx # Image upload container
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
- **Train/val folders**: 51 ingredient classes for model training
  - Each class folder contains JPEG images of that ingredient
  - Automatically organized for PyTorch's ImageFolder dataset loader
- **users.db**: SQLite database created automatically on first run
  - Stores users, saved recipes, and search history
  - Location: `backend/data/users.db`

#### Backend Models Directory (`backend/models/`)
- **ingredients_resnet18.pt**: PyTorch checkpoint file containing:
  - Model state dictionary (trained weights)
  - Class names list (51 ingredients)
  - All necessary info for inference
- Size: ~50 MB (ResNet18 is relatively small)

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

PantryMatch uses a **hybrid approach** combining custom ML and AI vision:

#### Option 1: Separate Images (CNN + AI Vision)
1. **ResNet18 Analysis**: Each uploaded image is analyzed by a custom-trained ResNet18 model
2. **Confidence Filtering**: Only predictions above 0.5 confidence are kept
3. **AI Vision Enhancement**: All images are sent to OpenRouter's GPT-4o-mini vision model
4. **Result Merging**: CNN and AI vision results are combined and deduplicated
5. **Display**: CNN-only detections shown separately; final list uses AI vision when available

#### Option 2: Combined Image (AI Vision Only)
1. **Direct AI Analysis**: Single image sent directly to OpenRouter vision API
2. **Ingredient Extraction**: AI model identifies all visible ingredients
3. **Result**: Clean ingredient list ready for recipe search

**Model Architecture:**
- **Base**: ResNet18 (pre-trained on ImageNet)
- **Fine-tuning**: Last fully-connected layer replaced for 51-class classification
- **Training**: Transfer learning with Adam optimizer, learning rate scheduling
- **Classes**: 51 ingredient types (fruits and vegetables)

### AI Substitution

When a user is missing an ingredient, the app:
1. Sends the recipe and missing ingredient to OpenRouter API (GPT-4o-mini model)
2. Gets context-aware substitution suggestions
3. Provides Indian cooking-specific alternatives when applicable

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
2. **Fine-tuning**: Replaces final fully-connected layer for 51-class classification
3. **Training Loop**: 
   - Forward pass through ResNet18
   - CrossEntropyLoss calculation
   - Backward propagation
   - Adam optimizer step
4. **Validation**: Monitors validation accuracy after each epoch
5. **Model Saving**: Saves best model based on validation accuracy

### Model Performance
- The model is trained on a dataset of 51 ingredient classes
- Validation accuracy is monitored during training
- Best model checkpoint is saved based on validation performance
- Model file: `backend/models/ingredients_resnet18.pt`

## 🔧 Development

### Backend Development
- All API endpoints are in `backend/app.py`
- Model training: `backend/ml_train_ingredients_model.py`
- Model inference: `backend/ml_infer_ingredients.py`

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
- AI Model: GPT-4o-mini via OpenRouter
- Video API: RapidAPI YouTube Alternative
- Deep Learning Framework: PyTorch
- Pre-trained Model: ResNet18 (ImageNet)
- Frontend Framework: React

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for food lovers who want to discover recipes from their pantry**
