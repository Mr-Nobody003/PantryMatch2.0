import { useState, useEffect, useRef } from 'react';
import './App.css';
import Header from './components/Header';
import LoginPage from './components/LoginPage';
import SignupPage from './components/SignupPage';
import ProfilePage from './components/ProfilePage';
import Toast from './components/Toast';
import SearchBox from './components/SearchBox';
import ImageUploadSection from './components/ImageUploadSection';
import RecipeList from './components/RecipeList';
import RecipeModal from './components/RecipeModal/RecipeModal';
import { useImageUpload } from './hooks/useImageUpload';
import { useIngredientDetection } from './hooks/useIngredientDetection';
import { api } from './services/api';

function App() {
  const [authUser, setAuthUser] = useState(null);
  const [authToken, setAuthToken] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('pm_token') || null;
    }
    return null;
  });
  const [currentView, setCurrentView] = useState('login'); // 'login' | 'signup' | 'main' | 'profile'

  // Recipe search state
  const [ingredients, setIngredients] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Recipe modal state
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [missing, setMissing] = useState('');
  const [adaptedStep, setAdaptedStep] = useState('');
  const [adaptLoading, setAdaptLoading] = useState(false);
  const [videos, setVideos] = useState([]);
  const [videosLoading, setVideosLoading] = useState(false);
  const [savingRecipe, setSavingRecipe] = useState(false);
  const [toast, setToast] = useState(null);
  const [savedCount, setSavedCount] = useState(0);
  const [savedTitleSet, setSavedTitleSet] = useState(() => new Set());
  const [isClearing, setIsClearing] = useState(false);
  const recipeListRef = useRef(null);

  const normalizeTitle = (t) => (t || '').trim().toLowerCase();

  const refreshSavedMeta = async () => {
    if (!authToken || !authUser) return;
    try {
      const recipes = await api.getSavedRecipes(authToken);
      const titles = recipes.map((r) => normalizeTitle(r?.title)).filter(Boolean);
      const set = new Set(titles);
      setSavedTitleSet(set);
      setSavedCount(set.size);
    } catch {
      // ignore
    }
  };

  // Image upload hooks
  const {
    singleImageFile,
    singleImagePreview,
    multiImageFiles,
    multiImagePreviews,
    handleSingleImageUpload,
    handleMultiImageUpload,
    removeSingleImage,
    removeMultiImage,
    clearAllImages,
  } = useImageUpload();

  // Ingredient detection hook
  const {
    detectingSingle,
    detectingMulti,
    cnnDetected,
    llmDetected,
    detectFromSingleImage,
    detectFromMultiImages,
    clearDetections,
  } = useIngredientDetection();

  // Search recipes
  const searchRecipes = async (queryOverride) => {
    const q = (queryOverride ?? ingredients).trim();
    if (!q) return;
    
    setLoading(true);
    setError('');
    try {
      const data = await api.searchRecipes(q, authToken);
      setResults(data);
      
      // Check if no results or all results have very low similarity scores
      if (data.length === 0) {
        setError('No matches found in the dataset. Please try different ingredients.');
      } else {
        // Check if all results have very low scores (indicating irrelevant query)
        const maxScore = Math.max(...data.map(r => r.score || 0));
        if (maxScore < 0.01) {
          setError('The query appears to be irrelevant or not found in the dataset. Please try different ingredients.');
          setResults([]);
        } else {
          // Valid results found, smoothly scroll down
          setTimeout(() => {
            recipeListRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }, 100);
        }
      }
    } catch (err) {
      setError('Error fetching recipes. Make sure the server is running!');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Handle image uploads with error handling
  const handleSingleImageUploadWrapper = (file, errorMsg) => {
    if (errorMsg) {
      setError(errorMsg);
      return;
    }
    if (file) {
      clearDetections();
      setError('');
      handleSingleImageUpload(file);
    }
  };

  const handleMultiImageUploadWrapper = (files, errorMsg) => {
    if (errorMsg) {
      setError(errorMsg);
      return;
    }
    if (files && files.length > 0) {
      clearDetections();
      setError('');
      handleMultiImageUpload(files);
    }
  };

  // Detect ingredients from images
  const handleDetectIngredients = async (mode) => {
    if (mode === 'single') {
      await detectFromSingleImage(
        singleImageFile,
        (ingredientsList) => {
          setIngredients(ingredientsList);
          setError('');
        },
        (errMsg) => setError(errMsg)
      );
    } else if (mode === 'multi') {
      await detectFromMultiImages(
        multiImageFiles,
        (ingredientsList) => {
          setIngredients(ingredientsList);
          setError('');
        },
        (errMsg) => setError(errMsg)
      );
    }
  };

  const handleClearAllState = () => {
    setIsClearing(true);
    setTimeout(() => {
      clearAllImages();
      clearDetections();
      setIngredients('');
      setResults([]);
      setError('');
      setIsClearing(false);
    }, 350); // Matches the CSS transition duration
  };

  // Handle recipe modal
  const openRecipe = (recipe) => {
    setSelectedRecipe(recipe);
    setMissing('');
    setAdaptedStep('');
    setVideos([]);
    setVideosLoading(true);
  };

  const closeModal = () => {
    setSelectedRecipe(null);
    setMissing('');
    setAdaptedStep('');
    setVideos([]);
  };

  const handleSaveRecipe = async (recipe) => {
    if (!authToken) return;
    try {
      setSavingRecipe(true);
      const resp = await api.saveRecipe(authToken, {
        title: recipe.title,
        ingredients: recipe.ingredients,
        instructions: recipe.instructions,
        time: recipe.time,
      });
      if (resp?.duplicate) {
        setToast({ type: 'success', title: 'Already saved', message: 'Updated in your favorites.' });
      } else {
        setToast({ type: 'success', title: 'Saved', message: 'Added to your favorites.' });
      }
      refreshSavedMeta();
    } catch (err) {
      console.error('Failed to save recipe', err);
      setToast({
        type: 'error',
        title: 'Couldn’t save',
        message: err?.message || 'Please try again.',
      });
    } finally {
      setSavingRecipe(false);
    }
  };

  // Get adaptation advice
  const getAdaptationAdvice = async () => {
    if (!missing.trim() || !selectedRecipe) return;
    
    setAdaptLoading(true);
    setAdaptedStep('');
    try {
      const adaptedStepText = await api.getAdaptation(
        selectedRecipe.instructions,
        missing,
        selectedRecipe.title
      );
      setAdaptedStep(adaptedStepText);
    } catch (err) {
      setAdaptedStep(
        'AI adaptation could not be fetched. Please check your backend and API configuration.'
      );
    } finally {
      setAdaptLoading(false);
    }
  };

  // Fetch YouTube videos when recipe modal opens
  useEffect(() => {
    if (selectedRecipe) {
      setVideosLoading(true);
      api.getVideos(selectedRecipe.title)
        .then(setVideos)
        .catch(() => setVideos([]))
        .finally(() => setVideosLoading(false));
    }
  }, [selectedRecipe]);

  // Try to hydrate user from token on first load
  useEffect(() => {
    const init = async () => {
      if (authToken && !authUser) {
        try {
          const user = await api.getCurrentUser(authToken);
          setAuthUser(user);
          setCurrentView('main');
        } catch (err) {
          console.error('Failed to hydrate session', err);
          setAuthToken(null);
          if (typeof window !== 'undefined') {
            localStorage.removeItem('pm_token');
          }
        }
      }
    };
    init();
  }, [authToken, authUser]);

  // Keep saved count fresh for header badge
  useEffect(() => {
    let active = true;
    const run = async () => {
      if (!active) return;
      await refreshSavedMeta();
    };
    run();
    return () => {
      active = false;
    };
  }, [authToken, authUser]);

  const handleAuthSuccess = ({ token, user }) => {
    // Reset app-visible state so new session starts clean
    setIngredients('');
    setResults([]);
    setError('');
    setSelectedRecipe(null);
    setMissing('');
    setAdaptedStep('');
    setVideos([]);
    clearDetections();
    clearAllImages();

    setAuthToken(token);
    setAuthUser(user);
    if (typeof window !== 'undefined') {
      localStorage.setItem('pm_token', token);
    }
    setCurrentView('main');
  };

  const handleLogout = () => {
    // Clear UI state when logging out to avoid leaving residue
    setIngredients('');
    setResults([]);
    setError('');
    setSelectedRecipe(null);
    setMissing('');
    setAdaptedStep('');
    setVideos([]);
    clearDetections();
    clearAllImages();

    setAuthToken(null);
    setAuthUser(null);
    setSavedCount(0);
    setSavedTitleSet(new Set());
    if (typeof window !== 'undefined') {
      localStorage.removeItem('pm_token');
    }
    setCurrentView('login');
  };

  // --- Auth Screens ---
  if (!authUser) {
    if (currentView === 'signup') {
      return (
        <SignupPage
          onSignup={async ({ name, email, password }) => {
            const data = await api.signup({ name, email, password });
            handleAuthSuccess(data);
          }}
          onSwitchToLogin={() => setCurrentView('login')}
        />
      );
    }

    return (
      <LoginPage
        onLogin={async ({ email, password }) => {
          const data = await api.login({ email, password });
          handleAuthSuccess(data);
        }}
        onSwitchToSignup={() => setCurrentView('signup')}
      />
    );
  }

  if (currentView === 'profile') {
    return (
      <>
        <ProfilePage
          user={authUser}
          token={authToken}
          onNavigate={setCurrentView}
          onLogout={handleLogout}
          onToast={setToast}
          onRunSearch={(q) => {
            setCurrentView('main');
            setIngredients(q);
            // run immediately with provided string
            searchRecipes(q);
          }}
          onOpenSavedRecipe={(r) => {
            // Stay on profile; open the modal on top.
            openRecipe({
              title: r.title,
              ingredients: r.ingredients || '',
              instructions: r.instructions || '',
              time: r.time,
            });
          }}
          onSavedChanged={refreshSavedMeta}
          onPreferencesSaved={(prefs) => {
            setAuthUser((prev) =>
              prev ? { ...prev, preferences: { ...(prev.preferences || {}), ...prefs } } : prev
            );
          }}
        />

        <RecipeModal
          recipe={selectedRecipe}
          onClose={closeModal}
          missing={missing}
          setMissing={setMissing}
          adaptedStep={adaptedStep}
          adaptLoading={adaptLoading}
          onGetAdaptation={getAdaptationAdvice}
          videos={videos}
          videosLoading={videosLoading}
          onSaveRecipe={authToken ? handleSaveRecipe : undefined}
          savingRecipe={savingRecipe}
          isSaved={!!selectedRecipe && savedTitleSet.has(normalizeTitle(selectedRecipe.title))}
        />

        <Toast toast={toast} onClose={() => setToast(null)} />
      </>
    );
  }

  return (
    <div className="app">
      <div className="app-container">
        <Header user={authUser} onNavigate={setCurrentView} onLogout={handleLogout} />

        <div className={`content-wrapper ${isClearing ? 'content-fade-out' : ''}`}>
          <SearchBox
            ingredients={ingredients}
            setIngredients={setIngredients}
            onSearch={() => searchRecipes()}
            loading={loading}
            error={error}
          />

          <ImageUploadSection
            multiImageFiles={multiImageFiles}
            multiImagePreviews={multiImagePreviews}
            onMultiImageUpload={handleMultiImageUploadWrapper}
            onRemoveMultiImage={removeMultiImage}
            detectingMulti={detectingMulti}
            onDetectIngredients={handleDetectIngredients}
            onIngredientsChange={setIngredients}
            cnnDetected={cnnDetected}
            llmDetected={llmDetected}
            onClearAll={handleClearAllState}
          />

          <div ref={recipeListRef} style={{ scrollMarginTop: '20px' }}>
            <RecipeList
              results={results}
              loading={loading}
              onViewRecipe={openRecipe}
              userIngredients={ingredients}
            />
          </div>
        </div>
      </div>

      <RecipeModal
        recipe={selectedRecipe}
        onClose={closeModal}
        missing={missing}
        setMissing={setMissing}
        adaptedStep={adaptedStep}
        adaptLoading={adaptLoading}
        onGetAdaptation={getAdaptationAdvice}
        videos={videos}
        videosLoading={videosLoading}
        onSaveRecipe={authToken ? handleSaveRecipe : undefined}
        savingRecipe={savingRecipe}
        isSaved={!!selectedRecipe && savedTitleSet.has(normalizeTitle(selectedRecipe.title))}
      />

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}

export default App;
