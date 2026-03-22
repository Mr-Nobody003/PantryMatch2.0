import React from 'react';

function DetectedIngredients({ cnnDetected, llmDetected, onRemoveCnn, onRemoveLlm }) {
  if (cnnDetected.length === 0 && llmDetected.length === 0) {
    return null;
  }

  return (
    <div className="detected-summary">
      <div className="detected-group">
        <p className="detected-label">Ingredients detected by ResNet model</p>
        {cnnDetected.length > 0 && (
          <p className="detected-count">{cnnDetected.length} ingredients detected</p>
        )}
        {cnnDetected.length > 0 ? (
          <div className="image-model-chips">
            {cnnDetected.map((ing) => (
              <div key={`cnn-${ing}`} className="image-model-chip-wrapper">
                {onRemoveCnn && (
                  <button
                    className="ingredient-remove-btn"
                    onClick={() => onRemoveCnn(ing)}
                    title="Remove ingredient"
                    aria-label={`Remove ${ing}`}
                  >
                    ×
                  </button>
                )}
                <span className="image-model-chip">
                  {ing}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="detected-empty">No ResNet ingredients detected yet.</p>
        )}
      </div>

      <div className="detected-group">
        <p className="detected-label">All ingredients available (OpenRouter)</p>
        {llmDetected.length > 0 && (
          <p className="detected-count">{llmDetected.length} ingredients detected</p>
        )}
        {llmDetected.length > 0 ? (
          <div className="image-model-chips">
            {llmDetected.map((ing) => (
              <div key={`llm-${ing}`} className="image-model-chip-wrapper">
                {onRemoveLlm && (
                  <button
                    className="ingredient-remove-btn"
                    onClick={() => onRemoveLlm(ing)}
                    title="Remove ingredient"
                    aria-label={`Remove ${ing}`}
                  >
                    ×
                  </button>
                )}
                <span className="image-model-chip">
                  {ing}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="detected-empty">No OpenRouter ingredients detected yet.</p>
        )}
      </div>
    </div>
  );
}

export default DetectedIngredients;

