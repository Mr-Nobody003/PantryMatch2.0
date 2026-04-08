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
        style={{ marginTop: 24, display: 'flex', justifyContent: 'center' }}
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

