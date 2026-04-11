const API_BASE_URL = import.meta.env.MODE === 'production' 
  ? 'https://pantrymatch2-0.onrender.com' 
  : 'http://127.0.0.1:5000';

export const api = {
  // --- Auth & User ---
  signup: async ({ name, email, password }) => {
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to sign up');
    }
    return data; // { token, user }
  },

  login: async ({ email, password }) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to log in');
    }
    return data; // { token, user }
  },

  getCurrentUser: async (token) => {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to fetch profile');
    }
    return data.user;
  },

  updatePreferences: async (token, preferences) => {
    const response = await fetch(`${API_BASE_URL}/user/preferences`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ preferences }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to update preferences');
    }
    return data.preferences;
  },

  getSavedRecipes: async (token) => {
    const response = await fetch(`${API_BASE_URL}/user/saved-recipes`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to load saved recipes');
    }
    return data.recipes || [];
  },

  saveRecipe: async (token, recipe) => {
    const response = await fetch(`${API_BASE_URL}/user/saved-recipes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(recipe),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to save recipe');
    }
    return data;
  },

  deleteSavedRecipe: async (token, id) => {
    const response = await fetch(
      `${API_BASE_URL}/user/saved-recipes?id=${encodeURIComponent(id)}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to delete recipe');
    }
    return data;
  },

  clearSavedRecipes: async (token) => {
    const response = await fetch(`${API_BASE_URL}/user/saved-recipes?clear=1`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to clear saved recipes');
    }
    return data;
  },

  getSearchHistory: async (token) => {
    const response = await fetch(`${API_BASE_URL}/user/search-history`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to load history');
    }
    return data.history || [];
  },

  deleteSearchHistoryItem: async (token, id) => {
    const response = await fetch(
      `${API_BASE_URL}/user/search-history?id=${encodeURIComponent(id)}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to delete history item');
    }
    return data;
  },

  clearSearchHistory: async (token) => {
    const response = await fetch(`${API_BASE_URL}/user/search-history?clear=1`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to clear history');
    }
    return data;
  },

  // Search recipes by ingredients
  searchRecipes: async (query, token) => {
    const response = await fetch(
      `${API_BASE_URL}/search?q=${encodeURIComponent(query)}`,
      {
        headers: token
          ? {
              Authorization: `Bearer ${token}`,
            }
          : undefined,
      }
    );
    if (!response.ok) throw new Error('Failed to fetch recipes');
    return response.json();
  },

  // Classify ingredients from a single combined image (CNN grid-crops + optional LLM)
  classifySingleImage: async (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch(
      `${API_BASE_URL}/classify-image?mode=cnn`,
      {
        method: 'POST',
        body: formData,
      }
    );
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to classify image');
    }
    
    return response.json();
  },

  // Classify ingredients from multiple images (CNN + LLM)
  classifyMultiImages: async (imageFiles) => {
    const formData = new FormData();
    imageFiles.forEach((file) => {
      formData.append('images', file);
    });
    
    const response = await fetch(
      `${API_BASE_URL}/classify-image?mode=cnn`,
      {
        method: 'POST',
        body: formData,
      }
    );
    
    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || 'Failed to classify images');
    }
    
    return response.json();
  },

  // Get adaptation advice for missing ingredient
  getAdaptation: async (instructions, missing, title) => {
    const response = await fetch(`${API_BASE_URL}/adapt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        instructions,
        missing,
        title,
      }),
    });
    
    if (!response.ok) throw new Error('Failed to get adaptation');
    const data = await response.json();
    return data.adaptedStep;
  },

  // Get YouTube videos for recipe
  getVideos: async (recipeTitle) => {
    const response = await fetch(
      `${API_BASE_URL}/videos?recipe=${encodeURIComponent(recipeTitle)}`
    );
    
    if (!response.ok) return [];
    
    const data = await response.json();
    return Array.isArray(data) ? data : [];
  },
};

