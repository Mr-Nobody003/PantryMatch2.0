import React from 'react';
import SingleImageUpload from './ImageUpload/SingleImageUpload';
import MultiImageUpload from './ImageUpload/MultiImageUpload';
import DetectedIngredients from './DetectedIngredients';

function ImageUploadSection({
  // Single image
  singleImageFile,
  singleImagePreview,
  onSingleImageUpload,
  onRemoveSingleImage,
  detectingSingle,
  
  // Multi image
  multiImageFiles,
  multiImagePreviews,
  onMultiImageUpload,
  onRemoveMultiImage,
  detectingMulti,
  
  // Detection
  onDetectIngredients,
  
  // Detected ingredients
  cnnDetected,
  llmDetected,
}) {
  const handleDetect = async () => {
    if (multiImageFiles.length > 0) {
      await onDetectIngredients('multi');
    } else if (singleImageFile) {
      await onDetectIngredients('single');
    }
  };

  return (
    <>
      <SingleImageUpload
        imageFile={singleImageFile}
        imagePreview={singleImagePreview}
        onImageUpload={onSingleImageUpload}
        onRemove={onRemoveSingleImage}
        detecting={detectingSingle}
      />

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
          disabled={
            detectingSingle ||
            detectingMulti ||
            (!singleImageFile && multiImageFiles.length === 0)
          }
        >
          {detectingSingle || detectingMulti ? (
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
        cnnDetected={cnnDetected} 
        llmDetected={llmDetected} 
      />
    </>
  );
}

export default ImageUploadSection;

