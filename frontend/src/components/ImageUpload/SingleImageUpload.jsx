import React, { useRef, useState } from 'react';

function SingleImageUpload({ 
  imageFile, 
  imagePreview, 
  onImageUpload, 
  onRemove, 
  detecting 
}) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      onImageUpload(null, 'Please upload a valid image file');
      return;
    }

    onImageUpload(file, null);
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

    const files = e.dataTransfer.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    if (!file.type.startsWith('image/')) {
      onImageUpload(null, 'Please upload a valid image file');
      return;
    }

    onImageUpload(file, null);
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    onRemove();
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div className="image-upload-section">
      <p className="image-upload-title">Option 1: Upload a single image with all ingredients</p>
      {imagePreview ? (
        <div 
          className={`image-upload-box ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          style={{ background: 'transparent', border: 'none', padding: 0, cursor: 'default' }}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            className="image-upload-input"
            onChange={handleFileChange}
            disabled={detecting}
          />
          <div className="image-upload-preview-wrapper">
            <div className="image-preview-container">
              <img
                src={imagePreview}
                alt="Combined ingredients preview"
                className="image-upload-preview"
              />
              <button
                className="image-remove-btn"
                onClick={handleRemove}
                aria-label="Remove image"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
          </div>
        </div>
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
            accept="image/*"
            className="image-upload-input"
            onChange={handleFileChange}
            disabled={detecting}
          />
          <div className="image-upload-placeholder">
            <span className="image-upload-icon">📸</span>
            <span className="image-upload-main">Drop a single image or click to browse</span>
            <span className="image-upload-hint">
              Best when all ingredients are visible in one clear photo
            </span>
          </div>
        </label>
      )}
    </div>
  );
}

export default SingleImageUpload;

