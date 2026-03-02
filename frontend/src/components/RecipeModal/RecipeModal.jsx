import React from 'react';
import ModalHeader from './ModalHeader';
import IngredientsSection from './IngredientsSection';
import InstructionsSection from './InstructionsSection';
import AdaptationSection from './AdaptationSection';
import VideosSection from './VideosSection';

function RecipeModal({ 
  recipe, 
  onClose, 
  missing, 
  setMissing, 
  adaptedStep, 
  adaptLoading, 
  onGetAdaptation,
  videos,
  videosLoading,
  onSaveRecipe,
  savingRecipe,
  isSaved,
}) {
  if (!recipe) return null;

  return (
    <>
      <div className="modal-backdrop" onClick={onClose}></div>
      <div className="recipe-modal">
        <button className="modal-close-btn" onClick={onClose} aria-label="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div className="recipe-modal-content">
          <ModalHeader recipe={recipe} />

          <div className="modal-body">
            <IngredientsSection ingredients={recipe.ingredients} />
            <InstructionsSection instructions={recipe.instructions} />
            <AdaptationSection
              missing={missing}
              setMissing={setMissing}
              adaptedStep={adaptedStep}
              adaptLoading={adaptLoading}
              onGetAdaptation={onGetAdaptation}
            />
            <VideosSection videos={videos} videosLoading={videosLoading} />

            {onSaveRecipe && (
              <div style={{ marginTop: 32, display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="tile-action"
                  style={{ maxWidth: 260 }}
                  onClick={() => onSaveRecipe(recipe)}
                  disabled={savingRecipe || isSaved}
                >
                  {savingRecipe ? (
                    <>
                      <span className="btn-loader-small" />
                      Saving…
                    </>
                  ) : isSaved ? (
                    <>
                      Saved
                      <svg
                        className="action-arrow"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    </>
                  ) : (
                    <>
                      Save to favorites
                      <svg
                        className="action-arrow"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                      >
                        <path d="M12 21.35l-1.45-1.32C6 15.36 3 12.28 3 8.5 3 6 5 4 7.5 4 9.04 4 10.54 4.81 11.25 6.09 11.96 4.81 13.46 4 15 4 17.5 4 19.5 6 19.5 8.5c0 3.78-3 6.86-7.55 11.54L12 21.35z" />
                      </svg>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default RecipeModal;

