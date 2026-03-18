import React, { useRef, useState } from 'react';

function MultiImageUpload({ 
  imageFiles, 
  imagePreviews, 
  onImageUpload, 
  onRemove, 
  onAddMore,
  detecting 
}) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    const validImages = files.filter((file) => file.type.startsWith('image/'));
    if (validImages.length === 0) {
      onImageUpload([], 'Please upload valid image files');
      return;
    }

    onImageUpload(validImages);
    
    // Reset the file input so the same files can be selected again if needed
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files || []);
    if (files.length === 0) return;

    const validImages = files.filter((file) => file.type.startsWith('image/'));
    if (validImages.length === 0) {
      onImageUpload([], 'Please upload valid image files');
      return;
    }

    onImageUpload(validImages);
  };

  const handleAddMore = () => {
    if (inputRef.current) {
      inputRef.current.click();
    }
  };

  const handleRemove = (index, e) => {
    e.stopPropagation();
    onRemove(index);
    if (imageFiles.length === 1 && inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div className="image-upload-section" style={{ marginTop: 24 }}>
      <p className="image-upload-title">Upload Images of Your Ingredients</p>
      {imagePreviews && imagePreviews.length > 0 ? (
        <>
          <input
            ref={inputRef}
            type="file"
            multiple
            accept="image/*"
            className="image-upload-input"
            onChange={handleFileChange}
            disabled={detecting}
            style={{ display: 'none' }}
          />
          <div 
            className="image-upload-box"
            style={{ padding: 0, backgroundColor: 'transparent', border: 'none', cursor: 'default' }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="image-upload-preview-wrapper">
              {imagePreviews.map((src, idx) => (
                <div key={idx} className="image-preview-container">
                  <img
                    src={src}
                    alt={`Ingredient ${idx + 1}`}
                    className="image-upload-preview"
                  />
                  <button
                    className="image-remove-btn"
                    onClick={(e) => handleRemove(idx, e)}
                    aria-label="Remove image"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </div>
              ))}
              <button
                className="image-add-more-btn"
                onClick={handleAddMore}
                aria-label="Add more images"
                type="button"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
            </div>
          </div>
        </>
      ) : (
        <label 
          className={`image-upload-box ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            accept="image/*"
            className="image-upload-input"
            onChange={handleFileChange}
            disabled={detecting}
          />
          <div className="image-upload-placeholder">
            <span className="image-upload-icon">📸</span>
            <span className="image-upload-main">Drop multiple images or click to browse</span>
            <span className="image-upload-hint">
              Best when each ingredient is in its own clear photo
            </span>
          </div>
        </label>
      )}
    </div>
  );
}

export default MultiImageUpload;

