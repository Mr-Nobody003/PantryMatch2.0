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
  const [removedLlmValues, setRemovedLlmValues] = useState(new Set());

  // Reset removed ingredients when new detection happens
  useEffect(() => {
    setRemovedCnnValues(new Set());
    setRemovedLlmValues(new Set());
  }, [cnnDetected, llmDetected]);

  const handleDetect = async () => {
    if (multiImageFiles.length > 0) {
      await onDetectIngredients('multi');
    }
  };

  const handleRemoveCnn = (ingredientName) => {
    const newRemoved = new Set(removedCnnValues);
    newRemoved.add(ingredientName);
    setRemovedCnnValues(newRemoved);
  };

  const handleRemoveLlm = (ingredientName) => {
    const newRemoved = new Set(removedLlmValues);
    newRemoved.add(ingredientName);
    setRemovedLlmValues(newRemoved);
    
    // Update the search ingredients when LLM ingredient is removed
    const filteredLlm = llmDetected.filter((ing) => !newRemoved.has(ing));
    if (onIngredientsChange) {
      onIngredientsChange(filteredLlm.join(', '));
    }
  };

  // Filter out removed ingredients for display
  const displayedCnn = cnnDetected.filter((ing) => !removedCnnValues.has(ing));
  const displayedLlm = llmDetected.filter((ing) => !removedLlmValues.has(ing));

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
        llmDetected={displayedLlm}
        onRemoveCnn={handleRemoveCnn}
        onRemoveLlm={handleRemoveLlm}
      />
    </>
  );
}

export default ImageUploadSection;

