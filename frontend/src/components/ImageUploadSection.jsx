import React, { useState, useEffect } from 'react';
import MultiImageUpload from './ImageUpload/MultiImageUpload';
import DetectedIngredients from './DetectedIngredients';

function ImageUploadSection({
  // Multi image
  multiImageFiles,
  multiImagePreviews,
  onMultiImageUpload,
  onRemoveMultiImage,
  detectingMulti,
  
  // Detection
  onDetectIngredients,
  onIngredientsChange,
  
  // Detected ingredients
  cnnDetected,
  llmDetected,
  onClearAll,
}) {
  const [removedCnnValues, setRemovedCnnValues] = useState(new Set());

  // Reset removed ingredients when new detection happens
  useEffect(() => {
    setRemovedCnnValues(new Set());
  }, [cnnDetected]);

  const handleDetect = async () => {
    if (multiImageFiles.length > 0) {
      await onDetectIngredients('multi');
    }
  };

  const handleClearAll = () => {
    setRemovedCnnValues(new Set());
    if (onClearAll) {
      onClearAll();
    } else if (onIngredientsChange) {
      onIngredientsChange('');
    }
  };

  const handleRemoveCnn = (ingredientName) => {
    const newRemoved = new Set(removedCnnValues);
    newRemoved.add(ingredientName);
    setRemovedCnnValues(newRemoved);
    
    // Update the search ingredients when CNN ingredient is removed
    const filteredCnn = cnnDetected.filter((ing) => !newRemoved.has(ing));
    if (onIngredientsChange) {
      onIngredientsChange(filteredCnn.join(', '));
    }
  };

  // Filter out removed ingredients for display
  const displayedCnn = cnnDetected.filter((ing) => !removedCnnValues.has(ing));
  const hasDetected = cnnDetected.length > 0;

  return (
    <>
      <MultiImageUpload
        imageFiles={multiImageFiles}
        imagePreviews={multiImagePreviews}
        onImageUpload={onMultiImageUpload}
        onRemove={onRemoveMultiImage}
        detecting={detectingMulti}
      />

      <div
        className="image-upload-section"
        style={{ marginTop: 12, display: 'flex', justifyContent: 'center', gap: 12 }}
      >
        <button
          className="image-upload-button"
          onClick={handleDetect}
          disabled={detectingMulti || multiImageFiles.length === 0}
        >
          {detectingMulti ? (
            <>
              <span className="detect-spinner" aria-hidden="true" />
              <span>Detecting all ingredients…</span>
            </>
          ) : (
            'Detect all ingredients'
          )}
        </button>

        {hasDetected && (
          <button
            className="clear-detected-btn"
            onClick={handleClearAll}
            title="Clear all detected ingredients"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
            Clear All
          </button>
        )}
      </div>

      <DetectedIngredients 
        cnnDetected={displayedCnn} 
        llmDetected={[]}
        onRemoveCnn={handleRemoveCnn}
        onRemoveLlm={undefined}
      />
    </>
  );
}

export default ImageUploadSection;

