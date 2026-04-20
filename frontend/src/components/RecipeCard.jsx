import React from 'react';

export function getDietInfo(dietaryPreference) {
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

export function getSpiceInfo(spiceTolerance) {
  const raw = (spiceTolerance || '').toString().toLowerCase();
  if (!raw) return null;
  if (raw.includes('non') || raw.includes('mild')) return { type: 'nonspicy', label: 'Non-spicy' };
  if (raw.includes('spicy')) return { type: 'spicy', label: 'Spicy' };
  return null;
}

// Tokenise an ingredient string into a Set of lowercase words
function tokenise(str) {
  return new Set(
    (str || '')
      .toLowerCase()
      .replace(/[^a-z\s]/g, ' ')
      .split(/\s+/)
      .filter((w) => w.length > 2)   // ignore tiny words like "of", "in"
  );
}

// Split a comma/dot/newline separated ingredient string into individual items
function splitIngredients(str) {
  return (str || '')
    .split(/,|\n|\./)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function getMissingIngredients(recipeIngredients, userIngredients) {
  const userTokens = tokenise(userIngredients);
  if (userTokens.size === 0) return [];

  const recipeItems = splitIngredients(recipeIngredients);

  return recipeItems.filter((item) => {
    const itemTokens = tokenise(item);
    // An item is "missing" if none of its meaningful words appear in the user's pantry
    return ![...itemTokens].some((t) => userTokens.has(t));
  });
}

function formatIngredients(str) {
  if (!str) return '';
  return str
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join(', ');
}

function RecipeCard({ recipe, index, onViewRecipe, userIngredients }) {
  const dietInfo = getDietInfo(recipe.dietaryPreference);
  const missingIngredients = getMissingIngredients(recipe.ingredients, userIngredients);

  return (
    <article
      className="recipe-tile"
      style={{ '--delay': `${index * 50}ms` }}
    >
      <div className="tile-header">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, flex: 1, minWidth: 0 }}>
          <h3 className="tile-title" title={recipe.title}>{recipe.title}</h3>
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
      
      <div className="tile-section ingredient-section">
        <span className="section-label">Ingredients</span>
        <p className="section-text">{formatIngredients(recipe.ingredients)}</p>
      </div>

      {missingIngredients.length > 0 ? (
        <div className="tile-section missing-section">
          <span className="section-label missing-label">
            ⚠ Missing ({missingIngredients.length})
          </span>
          <div className="missing-chips">
            {missingIngredients.map((item) => (
              <span key={item} className="missing-chip">
                {item.charAt(0).toUpperCase() + item.slice(1)}
              </span>
            ))}
          </div>
        </div>
      ) : userIngredients ? (
        <div className="tile-section missing-section" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <span className="missing-all-good">✓ You have all ingredients!</span>
        </div>
      ) : (
        <div className="tile-section missing-section empty-placeholder" style={{ visibility: 'hidden', padding: 0, border: 'none', margin: 0, height: 0 }}></div>
      )}

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

