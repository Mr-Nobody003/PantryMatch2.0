import React, { useState, useEffect, useMemo } from 'react';
import RecipeCard, { getDietInfo, getSpiceInfo, getMissingIngredients } from './RecipeCard';
import EmptyState from './EmptyState';

const INITIAL_SIZE = 6;
const PAGE_SIZE = 3;

function RecipeList({ results, loading, onViewRecipe, userIngredients }) {
  const [visibleCount, setVisibleCount] = useState(INITIAL_SIZE);

  const processedResults = useMemo(() => {
    return results.map(r => ({
      ...r,
      parsedTime: parseInt(r.time, 10) || 0,
      missingCount: getMissingIngredients(r.ingredients, userIngredients).length
    }));
  }, [results, userIngredients]);

  const maxGlobalTime = processedResults.length > 0 ? Math.max(...processedResults.map(r => r.parsedTime)) : 120;
  const maxGlobalMissing = processedResults.length > 0 ? Math.max(...processedResults.map(r => r.missingCount)) : 20;

  // Filter states
  const [maxTimeLimit, setMaxTimeLimit] = useState(maxGlobalTime);
  const [maxMissingLimit, setMaxMissingLimit] = useState(maxGlobalMissing);
  const [dietFilter, setDietFilter] = useState('All');
  const [sortOrder, setSortOrder] = useState('Best Match');
  const [isSortOpen, setIsSortOpen] = useState(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!e.target.closest('.sort-group')) {
        setIsSortOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Reset pagination whenever the results or filters change
  useEffect(() => {
    setVisibleCount(INITIAL_SIZE);
  }, [results, maxTimeLimit, maxMissingLimit, dietFilter, sortOrder]);

  // Sync sliders dynamically when data updates
  useEffect(() => {
    setMaxTimeLimit(maxGlobalTime);
    setMaxMissingLimit(maxGlobalMissing);
  }, [maxGlobalTime, maxGlobalMissing]);

  if (results.length === 0 && !loading) {
    return <EmptyState />;
  }

  if (results.length === 0) {
    return null;
  }

  // Apply filters
  const filteredResults = processedResults.filter((recipe) => {
    if (recipe.score !== undefined && recipe.score < 0.20) return false;
    if (recipe.parsedTime > maxTimeLimit) return false;
    if (recipe.missingCount > maxMissingLimit) return false;

    if (dietFilter !== 'All') {
      const diet = getDietInfo(recipe.dietaryPreference) || { type: 'unknown' };
      if (dietFilter === 'Veg' && diet.type !== 'veg') return false;
      if (dietFilter === 'Non-Veg' && diet.type !== 'nonveg') return false;
    }

    return true;
  });

  // Apply sorting
  const sortedResults = [...filteredResults].sort((a, b) => {
    switch (sortOrder) {
      case 'Prep Time (↑)':
        return b.parsedTime - a.parsedTime;
      case 'Prep Time (↓)':
        return a.parsedTime - b.parsedTime;
      case 'Missing Items (↑)':
        return b.missingCount - a.missingCount;
      case 'Missing Items (↓)':
        return a.missingCount - b.missingCount;
      default:
        return (b.score || 0) - (a.score || 0);
    }
  });

  const visibleRecipes = sortedResults.slice(0, visibleCount);
  const hasMore = visibleCount < sortedResults.length;

  const handleShowMore = () => {
    setVisibleCount((prev) => Math.min(prev + PAGE_SIZE, sortedResults.length));
  };

  const renderSortLabel = (val) => {
    if (val === 'Best Match') {
      return (
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          Best Match
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff6b35" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
        </span>
      );
    }
    const isAsc = val.includes('(↑)');
    const text = val.replace(' (↑)', '').replace(' (↓)', '');
    return (
      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        {text}
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff6b35" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
          {isAsc ? (
            <path d="M12 19V5M5 12l7-7 7 7" />
          ) : (
            <path d="M12 5v14M19 12l-7 7-7-7" />
          )}
        </svg>
      </span>
    );
  };

  return (
    <>
      <hr className="results-section-divider" style={{ border: 'none', borderTop: '2px solid #e2e8f0', margin: '12px 0 20px 0', opacity: 0.8 }} />

      <div className="results-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '24px', marginTop: 0, paddingTop: 0 }}>

        {/* Left Section: Counter & Sort */}
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '72px', flexWrap: 'wrap' }}>
          <h2 className="results-title">
            <span className="results-count">{filteredResults.length}</span>
            <span className="results-label">Recipe{filteredResults.length !== 1 ? 's' : ''} Found</span>
          </h2>
        </div>

        {/* Right Section: Interactive Filters */}
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center', flexWrap: 'wrap', transform: 'translateY(-12px)' }}>
          <div className="filter-dropdown-container">
            <div className="filter-dropdown-wrapper">
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end', height: '24px', gap: '6px' }}>
                <span className="filter-dropdown-label">Preparation Time</span>
                <span className="filter-dynamic-value">&le; {maxTimeLimit}m</span>
              </div>
              <div className="filter-dropdown-group">
                <span className="filter-dropdown-icon" title="Cooking Time" style={{ display: 'flex', alignItems: 'center', marginRight: '6px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff6b35" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                </span>
                <input type="range" min="0" max={Math.max(1, maxGlobalTime)} value={maxTimeLimit} onChange={(e) => setMaxTimeLimit(Number(e.target.value))} className="filter-range-slider" title={`${maxTimeLimit} minutes`} />
              </div>
            </div>

            <div className="filter-dropdown-wrapper">
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end', height: '24px', gap: '6px' }}>
                <span className="filter-dropdown-label">Missing Items</span>
                <span className="filter-dynamic-value">&le; {maxMissingLimit} items</span>
              </div>
              <div className="filter-dropdown-group">
                <span className="filter-dropdown-icon" title="Missing Ingredients" style={{ display: 'flex', alignItems: 'center', marginRight: '6px' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff6b35" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="9" cy="21" r="1"></circle>
                    <circle cx="20" cy="21" r="1"></circle>
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                  </svg>
                </span>
                <input type="range" min="0" max={Math.max(1, maxGlobalMissing)} value={maxMissingLimit} onChange={(e) => setMaxMissingLimit(Number(e.target.value))} className="filter-range-slider" title={`${maxMissingLimit} items`} />
              </div>
            </div>

            <div className="filter-dropdown-wrapper">
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end', height: '24px' }}>
                <span className="filter-dropdown-label">Dietary Preference</span>
              </div>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>

                {/* Veg Toggle */}
                <div
                  className={`diet-toggle-btn ${dietFilter === 'Veg' ? 'active-veg' : ''}`}
                  onClick={() => setDietFilter(dietFilter === 'Veg' ? 'All' : 'Veg')}
                  title="Vegetarian Only"
                >
                  <div className="veg-icon">
                    <div className="veg-dot"></div>
                  </div>
                  <div className="diet-toggle-switch"></div>
                </div>

                {/* Non-Veg Toggle */}
                <div
                  className={`diet-toggle-btn ${dietFilter === 'Non-Veg' ? 'active-nonveg' : ''}`}
                  onClick={() => setDietFilter(dietFilter === 'Non-Veg' ? 'All' : 'Non-Veg')}
                  title="Non-Vegetarian Only"
                >
                  <div className="nonveg-icon">
                    <div className="nonveg-triangle"></div>
                  </div>
                  <div className="diet-toggle-switch"></div>
                </div>
              </div>
            </div>

            {/* Moved Sort Controls to right boundary */}
            <div className="sort-wrapper">
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end', height: '24px' }}>
                <span className="sort-label">Sort By</span>
              </div>
              <div className={`sort-group ${isSortOpen ? 'dropdown-active' : ''}`} onClick={() => setIsSortOpen(!isSortOpen)}>
                <div className="sort-value">{renderSortLabel(sortOrder)}</div>
                <span className="sort-chevron">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M6 9l6 6 6-6" />
                  </svg>
                </span>

                {isSortOpen && (
                  <div className="sort-dropdown-menu">
                    {['Best Match', 'Prep Time (↓)', 'Prep Time (↑)', 'Missing Items (↓)', 'Missing Items (↑)'].map(f => (
                      <div
                        key={f}
                        className={`sort-option ${sortOrder === f ? 'selected' : ''}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSortOrder(f);
                          setIsSortOpen(false);
                        }}
                      >
                        {renderSortLabel(f)}
                        <span className="sort-option-check">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="recipes-container">
        {visibleRecipes.map((recipe, index) => (
          <RecipeCard
            key={recipe.title}
            recipe={recipe}
            index={index}
            onViewRecipe={onViewRecipe}
            userIngredients={userIngredients}
          />
        ))}
      </div>

      {hasMore && (
        <div className="show-more-wrapper">
          <button className="show-more-btn" onClick={handleShowMore}>
            <span>Show More Recipes</span>
            <svg
              className="show-more-icon"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
        </div>
      )}
    </>
  );
}

export default RecipeList;
