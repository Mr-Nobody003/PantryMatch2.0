import React from 'react';
import picImage from '../assets/pic.png';

function EmptyState() {
  return (
    <div className="lower-image-container">
      <img src={picImage} alt="PantryMatch" className="lower-background-image" />
    </div>
  );
}

export default EmptyState;

