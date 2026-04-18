const FALLBACK_URLS = import.meta.env.MODE === 'production' 
  ? ['https://pantry-match-api.vercel.app'] 
  : ['http://127.0.0.1:5000'];

const getBaseUrl = async () => {
    let cached = sessionStorage.getItem('activeApiUrl');
    if (cached) return cached;
    for (const url of FALLBACK_URLS) {
        try {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), 3000);
            const res = await fetch(url + '/', { signal: controller.signal });
            clearTimeout(id);
            if (res.ok) {
                sessionStorage.setItem('activeApiUrl', url);
                return url;
            }
        } catch (e) {
            console.warn('Backend ' + url + ' unreachable');
        }
    }
    sessionStorage.setItem('activeApiUrl', FALLBACK_URLS[0]);
    return FALLBACK_URLS[0];
};

const apiFetch = async (endpoint, options) => {
    const base = await getBaseUrl();
    const cleanBase = base.replace(/\/$/, '');
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
    return fetch(cleanBase + cleanEndpoint, options);
};


const compressImage = async (file) => {
  if (!file || !file.type.startsWith('image/')) return file;
  if (file.size < 1024 * 1024 * 1.5) return file; // Skip compression if under 1.5MB
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target.result;
      img.onload = () => {
        const MAX_WIDTH = 1200;
        const MAX_HEIGHT = 1200;
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > MAX_WIDTH) {
            height = Math.round((height *= MAX_WIDTH / width));
            width = MAX_WIDTH;
          }
        } else {
          if (height > MAX_HEIGHT) {
            width = Math.round((width *= MAX_HEIGHT / height));
            height = MAX_HEIGHT;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            if (blob) {
              const compressedFile = new File([blob], file.name, {
                type: 'image/jpeg',
                lastModified: Date.now(),
              });
              resolve(compressedFile);
            } else {
              resolve(file); // fallback
            }
          },
          'image/jpeg',
          0.7 // reduce quality to drop size remarkably
        );
      };
      img.onerror = () => resolve(file); // fallback
    };
    reader.onerror = () => resolve(file); // fallback
  });
};

export const api = {
  // --- Auth & User ---
  signup: async ({ name, email, password }) => {
    const response = await apiFetch(`/auth/signup`, {
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
    const response = await apiFetch(`/auth/login`, {
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
    const response = await apiFetch(`/auth/me`, {
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
    const response = await apiFetch(`/user/preferences`, {
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
    const response = await apiFetch(`/user/saved-recipes`, {
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
    const response = await apiFetch(`/user/saved-recipes`, {
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
    const response = await apiFetch(`/user/saved-recipes?clear=1`, {
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
    const response = await apiFetch(`/user/search-history`, {
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
    const response = await apiFetch(`/user/search-history?clear=1`, {
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
    const response = await apiFetch(
      `/search?q=${encodeURIComponent(query)}`,
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
    const compressedImage = await compressImage(imageFile);
    const formData = new FormData();
    formData.append('image', compressedImage);
    
    const response = await apiFetch(
      `/classify-image?mode=cnn`,
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
    for (const file of imageFiles) {
      const compressedImage = await compressImage(file);
      formData.append('images', compressedImage);
    }
    
    const response = await apiFetch(
      `/classify-image?mode=cnn`,
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
    const response = await apiFetch(`/adapt`, {
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
    const response = await apiFetch(
      `/videos?recipe=${encodeURIComponent(recipeTitle)}`
    );
    
    if (!response.ok) return [];
    
    const data = await response.json();
    return Array.isArray(data) ? data : [];
  },
};

