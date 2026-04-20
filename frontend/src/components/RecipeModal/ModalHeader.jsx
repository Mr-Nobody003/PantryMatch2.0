import React from 'react';

function getDietInfo(dietaryPreference) {
  const raw = (dietaryPreference || '').toString().toLowerCase();
  if (!raw) return null;
  if (raw.includes('non')) {
    return { type: 'nonveg', label: 'Non-vegetarian recipe' };
  }
  if (raw.includes('veg')) {
    return { type: 'veg', label: 'Vegetarian recipe' };
  }
  return null;
}

function ModalHeader({ recipe }) {
  const dietInfo = getDietInfo(recipe.dietaryPreference || recipe.Dietary_Preference || recipe.diet);

  return (
    <div className="modal-header-section">
      <div style={{ flex: 1 }}>
        <h2 className="modal-recipe-title">{recipe.title}</h2>
        {dietInfo && (
          <div
            className={`diet-icon diet-icon--inline ${
              dietInfo.type === 'veg' ? 'diet-icon--veg' : 'diet-icon--nonveg'
            }`}
            aria-label={dietInfo.label}
            title={dietInfo.label}
          >
            <span className="diet-icon-dot" />
            <span className="diet-icon-text">
              {dietInfo.type === 'veg' ? 'Veg' : 'Non‑veg'}
            </span>
          </div>
        )}
      </div>
      {recipe.time && (
        <div className="modal-time-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
          {recipe.time} minutes
        </div>
      )}
    </div>
  );
}

export default ModalHeader;

