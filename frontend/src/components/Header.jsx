import React from 'react';

function Header({ user, onNavigate, onLogout }) {
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
                fontSize: 18,
              }}
            >
              <div style={{ fontWeight: 600 }}>Hi, {user.name}</div>
              <div style={{ fontSize: 14, opacity: 0.9 }}>Ready to cook something new?</div>
            </div>
            <button
              type="button"
              onClick={() => onNavigate && onNavigate('main')}
              className="tile-action"
              style={{
                padding: '10px 18px',
                fontSize: 16,
                background: '#fff5f0',
                color: '#ff6b35',
              }}
            >
              Home
            </button>
            <button
              type="button"
              onClick={() => onNavigate && onNavigate('profile')}
              className="tile-action"
              style={{
                padding: '10px 18px',
                fontSize: 16,
              }}
            >
              Profile
            </button>
            <button
              type="button"
              onClick={onLogout}
              className="tile-action"
              style={{
                padding: '10px 18px',
                fontSize: 16,
                background: '#ff6b35',
              }}
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

export default Header;

