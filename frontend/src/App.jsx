import { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import LoginPage from './components/LoginPage';
import SearchBox from './components/SearchBox';
import ImageUploadSection from './components/ImageUploadSection';
import RecipeList from './components/RecipeList';
import RecipeModal from './components/RecipeModal/RecipeModal';
import { useImageUpload } from './hooks/useImageUpload';
import { useIngredientDetection } from './hooks/useIngredientDetection';
import { api } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

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
  const searchRecipes = async () => {
    if (!ingredients.trim()) return;
    
    setLoading(true);
    setError('');
    try {
      const data = await api.searchRecipes(ingredients);
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

  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="app">
      <div className="app-container">
        <Header />

        <div className="content-wrapper">
          <SearchBox
            ingredients={ingredients}
            setIngredients={setIngredients}
            onSearch={searchRecipes}
            loading={loading}
            error={error}
          />

          <ImageUploadSection
            singleImageFile={singleImageFile}
            singleImagePreview={singleImagePreview}
            onSingleImageUpload={handleSingleImageUploadWrapper}
            onRemoveSingleImage={removeSingleImage}
            detectingSingle={detectingSingle}
            multiImageFiles={multiImageFiles}
            multiImagePreviews={multiImagePreviews}
            onMultiImageUpload={handleMultiImageUploadWrapper}
            onRemoveMultiImage={removeMultiImage}
            detectingMulti={detectingMulti}
            onDetectIngredients={handleDetectIngredients}
            cnnDetected={cnnDetected}
            llmDetected={llmDetected}
          />

          <RecipeList
            results={results}
            loading={loading}
            onViewRecipe={openRecipe}
          />
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
      />
    </div>
  );
}

export default App;
