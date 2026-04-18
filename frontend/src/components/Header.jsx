import React, { useState } from 'react';

function Header({ user, onNavigate, onLogout }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleNavigate = (view) => {
    setMenuOpen(false);
    onNavigate && onNavigate(view);
  };

  const handleLogoutClick = () => {
    setMenuOpen(false);
    onLogout && onLogout();
  };

  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo-section">
          <div className="logo-circle">
            <span className="logo-text">PM</span>
          </div>
          <div className="logo-content">
            <h1 className="logo-title">PANTRY MATCH</h1>
            <p className="logo-subtitle">Recipe Retrieval Using Image of Ingredients</p>
          </div>
        </div>

        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div
              style={{
                textAlign: 'right',
                color: '#fff',
                fontSize: 26,
                maxWidth: 340,
                whiteSpace: 'normal',
              }}
            >
              <div style={{ fontWeight: 800, lineHeight: 1.3 }}>
                Hi, {user.name}
              </div>
              <div style={{ fontSize: 18, opacity: 0.9, lineHeight: 1.4, fontWeight: 500 }}>
                Ready to cook something new?
              </div>
            </div>
            <div className="header-user-menu">
              <button
                type="button"
                className="header-user-toggle"
                onClick={() => setMenuOpen((open) => !open)}
                aria-haspopup="menu"
                aria-expanded={menuOpen}
                title="Account menu"
              >
                <div className="header-avatar">
                  <span>{user.name?.[0]?.toUpperCase() || 'U'}</span>
                </div>
                <span className="header-user-label">Menu</span>
                <svg
                  className={`header-caret ${menuOpen ? 'is-open' : ''}`}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </button>
              {menuOpen && (
                <div className="header-user-dropdown" role="menu">
                  <button
                    type="button"
                    className="header-dropdown-item"
                    onClick={() => handleNavigate('main')}
                    role="menuitem"
                  >
                    <span className="header-dropdown-icon home-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M3 11.5L12 3l9 8.5" />
                        <path d="M5 10.5V21h14V10.5" />
                        <path d="M10 21v-6h4v6" />
                      </svg>
                    </span>
                    <span>Home</span>
                  </button>
                  <button
                    type="button"
                    className="header-dropdown-item"
                    onClick={() => handleNavigate('profile')}
                    role="menuitem"
                  >
                    <span className="header-dropdown-icon profile-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <circle cx="12" cy="8" r="4" />
                        <path d="M4 20c1.5-3 4-5 8-5s6.5 2 8 5" />
                      </svg>
                    </span>
                    <span>Profile</span>
                  </button>
                  <button
                    type="button"
                    className="header-dropdown-item header-dropdown-item--danger"
                    onClick={handleLogoutClick}
                    role="menuitem"
                  >
                    <span className="header-dropdown-icon logout-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M9 21H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3" />
                        <path d="M16 17l5-5-5-5" />
                        <path d="M21 12H9" />
                      </svg>
                    </span>
                    <span>Logout</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;

