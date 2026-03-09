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

function RecipeCard({ recipe, index, onViewRecipe }) {
  const dietInfo = getDietInfo(recipe.dietaryPreference);

  return (
    <article
      className="recipe-tile"
      style={{ '--delay': `${index * 50}ms` }}
    >
      <div className="tile-header">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1 }}>
          <h3 className="tile-title">{recipe.title}</h3>
          {dietInfo && (
            <div
              className={`diet-icon ${dietInfo.type === 'veg' ? 'diet-icon--veg' : 'diet-icon--nonveg'}`}
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
          <div className="tile-badge">
            <svg className="badge-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            {recipe.time}m
          </div>
        )}
      </div>
      
      <div className="tile-body">
        <div className="tile-section">
          <span className="section-label">Ingredients</span>
          <p className="section-text">{recipe.ingredients}</p>
        </div>
        
        <div className="tile-section">
          <span className="section-label">Instructions</span>
          <p className="section-text">
            {recipe.instructions.slice(0, 120)}
            {recipe.instructions.length > 120 ? '...' : ''}
          </p>
        </div>
      </div>

      <div className="tile-footer">
        {recipe.score && (
          <div className="match-indicator">
            <div className="match-bar">
              <div 
                className="match-fill" 
                style={{ width: `${recipe.score * 100}%` }}
              ></div>
            </div>
            <span className="match-text">{Math.round(recipe.score * 100)}% match</span>
          </div>
        )}
        <button
          className="tile-action"
          onClick={() => onViewRecipe(recipe)}
        >
          View Recipe
          <svg className="action-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </button>
      </div>
    </article>
  );
}

export default RecipeCard;

