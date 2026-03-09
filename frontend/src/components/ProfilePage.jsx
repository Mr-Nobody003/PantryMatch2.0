import React, { useEffect, useState } from 'react';
import Header from './Header';
import { api } from '../services/api';

function ProfilePage({
  user,
  token,
  onNavigate,
  onLogout,
  onToast,
  onRunSearch,
  onOpenSavedRecipe,
  onSavedChanged,
  onPreferencesSaved,
}) {
  const [preferences, setPreferences] = useState(user?.preferences || { diet: 'none' });
  const [savingPrefs, setSavingPrefs] = useState(false);
  const [prefsError, setPrefsError] = useState('');

  const [savedRecipes, setSavedRecipes] = useState([]);
  const [history, setHistory] = useState([]);
  const [loadingExtras, setLoadingExtras] = useState(true);
  const [extrasError, setExtrasError] = useState('');
  const [deletingId, setDeletingId] = useState(null);
  const [clearing, setClearing] = useState(false);
  const [animatingOutId, setAnimatingOutId] = useState(null);

  useEffect(() => {
    let isMounted = true;
    const loadData = async () => {
      try {
        const [recipes, hist] = await Promise.all([
          api.getSavedRecipes(token),
          api.getSearchHistory(token),
        ]);
        if (!isMounted) return;
        setSavedRecipes(recipes);
        setHistory(hist);
      } catch (err) {
        if (!isMounted) return;
        setExtrasError(err.message || 'Failed to load profile data');
      } finally {
        if (isMounted) setLoadingExtras(false);
      }
    };
    if (token) {
      loadData();
    }
    return () => {
      isMounted = false;
    };
  }, [token]);

  const uniqueByKey = (items, keyFn) => {
    const seen = new Set();
    const out = [];
    for (const item of items) {
      const k = keyFn(item);
      if (!k || seen.has(k)) continue;
      seen.add(k);
      out.push(item);
    }
    return out;
  };

  const displaySaved = uniqueByKey(savedRecipes, (r) => (r?.title || '').trim().toLowerCase());
  const displayHistory = uniqueByKey(history, (h) =>
    (h?.query || '').trim().replace(/\s+/g, ' ').toLowerCase()
  );

  const handleRemoveSaved = async (id) => {
    try {
      setDeletingId(id);
      await api.deleteSavedRecipe(token, id);
      setAnimatingOutId(id);
      setTimeout(() => {
        setSavedRecipes((prev) => prev.filter((r) => r.id !== id));
        onSavedChanged?.();
        setAnimatingOutId(null);
      }, 180);
      onToast?.({ type: 'success', title: 'Removed', message: 'Deleted from favorites.' });
    } catch (err) {
      onToast?.({
        type: 'error',
        title: 'Couldn’t remove',
        message: err?.message || 'Please try again.',
      });
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearSaved = async () => {
    try {
      setClearing(true);
      await api.clearSavedRecipes(token);
      setSavedRecipes([]);
      onSavedChanged?.();
      onToast?.({ type: 'success', title: 'Cleared', message: 'All saved recipes removed.' });
    } catch (err) {
      onToast?.({
        type: 'error',
        title: 'Couldn’t clear',
        message: err?.message || 'Please try again.',
      });
    } finally {
      setClearing(false);
    }
  };

  const handleRemoveHistory = async (id) => {
    try {
      setDeletingId(id);
      await api.deleteSearchHistoryItem(token, id);
      setAnimatingOutId(id);
      setTimeout(() => {
        setHistory((prev) => prev.filter((h) => h.id !== id));
        setAnimatingOutId(null);
      }, 180);
      onToast?.({ type: 'success', title: 'Removed', message: 'Deleted from recent searches.' });
    } catch (err) {
      onToast?.({
        type: 'error',
        title: 'Couldn’t remove',
        message: err?.message || 'Please try again.',
      });
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearHistory = async () => {
    try {
      setClearing(true);
      await api.clearSearchHistory(token);
      setHistory([]);
      onToast?.({ type: 'success', title: 'Cleared', message: 'Search history cleared.' });
    } catch (err) {
      onToast?.({
        type: 'error',
        title: 'Couldn’t clear',
        message: err?.message || 'Please try again.',
      });
    } finally {
      setClearing(false);
    }
  };

  const handleSavePreferences = async () => {
    try {
      setSavingPrefs(true);
      setPrefsError('');
      const updated = await api.updatePreferences(token, preferences);
      setPreferences(updated);
      onPreferencesSaved?.(updated);
      onToast?.({ type: 'success', title: 'Preferences saved' });
    } catch (err) {
      setPrefsError(err.message || 'Failed to save preferences');
      onToast?.({
        type: 'error',
        title: 'Couldn’t save preferences',
        message: err?.message || 'Please try again.',
      });
    } finally {
      setSavingPrefs(false);
    }
  };

  return (
    <div className="app">
      <div className="app-container">
        <Header user={user} onNavigate={onNavigate} onLogout={onLogout} />

        <div className="content-wrapper">
          <div className="results-header">
            <h2 className="results-title">
              <span className="results-count">Your Kitchen</span>
              <span className="results-label">Profile & activity</span>
            </h2>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(0, 1.1fr) minmax(0, 1fr)',
              gap: 32,
            }}
          >
            <section className="adaptation-panel">
              <h3
                style={{
                  marginTop: 0,
                  marginBottom: 16,
                  fontSize: 24,
                  fontWeight: 700,
                  color: '#2c2416',
                }}
              >
                Taste & dietary preferences
              </h3>
              <p
                style={{
                  margin: '0 0 16px',
                  fontSize: 18,
                  color: '#6b6457',
                }}
              >
                Tell PantryMatch how you like to cook. We&apos;ll use this to personalize future
                features.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 420 }}>
                <label style={{ fontSize: 18, color: '#4a4539', fontWeight: 600 }}>
                  Dietary preference
                </label>
                <select
                  value={preferences?.diet || 'none'}
                  onChange={(e) => setPreferences({ ...(preferences || {}), diet: e.target.value })}
                  className="adaptation-field"
                  style={{ maxWidth: '100%' }}
                >
                  <option value="none">No specific preference</option>
                  <option value="vegetarian">Vegetarian</option>
                  <option value="nonvegetarian">Non-Vegetarian</option>
                </select>

                <label style={{ fontSize: 18, color: '#4a4539', fontWeight: 600, marginTop: 8 }}>
                  Spice tolerance
                </label>
                <select
                  value={preferences?.spice || 'none'}
                  onChange={(e) =>
                    setPreferences({ ...(preferences || {}), spice: e.target.value })
                  }
                  className="adaptation-field"
                  style={{ maxWidth: '100%' }}
                >
                  <option value="none">No specific preference</option>
                  <option value="spicy">Spicy</option>
                  <option value="nonspicy">Non-Spicy</option>
                </select>
              </div>

              <button
                type="button"
                className="adaptation-submit"
                style={{ marginTop: 20 }}
                onClick={handleSavePreferences}
                disabled={savingPrefs}
              >
                {savingPrefs ? <span className="btn-loader-small" /> : 'Save preferences'}
              </button>

              {prefsError && (
                <p style={{ marginTop: 12, color: '#991b1b', fontSize: 16 }}>{prefsError}</p>
              )}
            </section>

            <section className="detected-summary">
              <h3
                style={{
                  marginTop: 0,
                  marginBottom: 16,
                  fontSize: 22,
                  fontWeight: 700,
                  color: '#2c2416',
                }}
              >
                Activity overview
              </h3>

              {loadingExtras ? (
                <div className="videos-loading-state">
                  <span className="btn-loader" />
                  <span>Loading your saved recipes and history…</span>
                </div>
              ) : extrasError ? (
                <p style={{ margin: 0, color: '#991b1b' }}>{extrasError}</p>
              ) : (
                <>
                  <div className="detected-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                      <h4 className="detected-label">Saved recipes</h4>
                      {displaySaved.length > 0 ? (
                        <button
                          type="button"
                          className="link-btn"
                          onClick={handleClearSaved}
                          disabled={clearing}
                        >
                          Clear
                        </button>
                      ) : null}
                    </div>
                    {displaySaved.length === 0 ? (
                      <p className="detected-empty">
                        You haven&apos;t saved any recipes yet. Open a recipe and hit &quot;Save
                        to favorites&quot; to keep it here.
                      </p>
                    ) : (
                      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                        {displaySaved.slice(0, 8).map((r) => (
                          <li
                            key={r.id}
                            className={`list-row ${animatingOutId === r.id ? 'is-removing' : ''}`}
                            style={{
                              padding: '10px 10px',
                              borderBottom: '1px solid #f0ede5',
                              fontSize: 16,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              gap: 12,
                            }}
                          >
                            <div style={{ minWidth: 0, flex: 1 }}>
                              <div style={{ fontWeight: 800, color: '#2c2416' }}>{r.title}</div>
                              {r.time ? (
                                <div style={{ color: '#6b6457', fontSize: 14 }}>{r.time} mins</div>
                              ) : null}
                              <div style={{ color: '#6b6457', fontSize: 13 }}>Saved recipe</div>
                            </div>

                            <div className="row-actions" style={{ minWidth: 150, justifyContent: 'flex-end' }}>
                              <button
                                type="button"
                                className="icon-btn"
                                aria-label="View recipe"
                                title="View this saved recipe"
                                onClick={() => onOpenSavedRecipe?.(r)}
                                disabled={clearing || deletingId === r.id || animatingOutId === r.id}
                              >
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                  <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" />
                                  <circle cx="12" cy="12" r="3" />
                                </svg>
                              </button>
                              <button
                                type="button"
                                className="icon-btn"
                                aria-label="Remove from favorites"
                                title="Remove from favorites"
                                onClick={() => handleRemoveSaved(r.id)}
                                disabled={deletingId === r.id || clearing}
                              >
                                {deletingId === r.id ? (
                                  <span className="btn-loader-small" />
                                ) : (
                                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M3 6h18" />
                                    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                    <path d="M9 10v8" />
                                    <path d="M15 10v8" />
                                    <path d="M5 6l1 14a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-14" />
                                  </svg>
                                )}
                              </button>
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>

                  <div className="detected-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                      <h4 className="detected-label">Recent searches</h4>
                      {displayHistory.length > 0 ? (
                        <button
                          type="button"
                          className="link-btn"
                          onClick={handleClearHistory}
                          disabled={clearing}
                        >
                          Clear
                        </button>
                      ) : null}
                    </div>
                    {displayHistory.length === 0 ? (
                      <p className="detected-empty">
                        Your next search will appear here so you can quickly revisit it.
                      </p>
                    ) : (
                      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                        {displayHistory.slice(0, 10).map((h) => (
                          <li
                            key={h.id}
                            className={`list-row ${animatingOutId === h.id ? 'is-removing' : ''}`}
                            style={{
                              padding: '8px 10px',
                              borderBottom: '1px dashed #f1e6d7',
                              fontSize: 16,
                              color: '#4a4539',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                              gap: 12,
                            }}
                          >
                            <button
                              type="button"
                              className="link-btn"
                              style={{
                                minWidth: 0,
                                flex: 1,
                                textAlign: 'left',
                                fontWeight: 700,
                                color: '#4a4539',
                              }}
                              onClick={() => onRunSearch?.(h.query)}
                              disabled={clearing || deletingId === h.id || animatingOutId === h.id}
                            >
                              {h.query}
                            </button>
                            <div className="row-actions" style={{ minWidth: 150, justifyContent: 'flex-end' }}>
                              <button
                                type="button"
                                className="icon-btn"
                                aria-label="Search again"
                                title="Run this search again"
                                onClick={() => onRunSearch?.(h.query)}
                                disabled={clearing || deletingId === h.id || animatingOutId === h.id}
                              >
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                  <path d="M21 12a9 9 0 1 1-2.64-6.36" />
                                  <polyline points="21 3 21 9 15 9" />
                                </svg>
                              </button>
                              <button
                                type="button"
                                className="icon-btn"
                                aria-label="Remove from history"
                                title="Remove from history"
                                onClick={() => handleRemoveHistory(h.id)}
                                disabled={deletingId === h.id || clearing}
                              >
                                {deletingId === h.id ? (
                                  <span className="btn-loader-small" />
                                ) : (
                                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path d="M3 6h18" />
                                    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                    <path d="M9 10v8" />
                                    <path d="M15 10v8" />
                                    <path d="M5 6l1 14a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-14" />
                                  </svg>
                                )}
                              </button>
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </>
              )}
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;

