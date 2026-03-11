import React, { useState } from 'react';
import Header from './Header';

function LoginPage({ onLogin, onSwitchToSignup }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Please enter both email and password.');
      return;
    }
    try {
      setSubmitting(true);
      setError('');
      if (onLogin) {
        await onLogin({ email, password });
      }
    } catch (err) {
      const message = err?.message || 'Could not sign you in. Please try again.';
      // Surface clearer copy for common auth issues
      if (message.toLowerCase().includes('invalid')) {
        setError('No account found for this email or the password is incorrect.');
      } else {
        setError(message);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app page-auth">
      <div className="app-container">
        <Header />

        <div className="content-wrapper">
          <div className="results-header" style={{ borderBottom: 'none', marginBottom: '24px' }}>
            <h2 className="results-title">
              <span className="results-label">Welcome back to</span>
              <span className="results-count">Pantry Match</span>
            </h2>
          </div>

          <form onSubmit={handleSubmit} className="search-area">
            <div className="search-box" style={{ flexDirection: 'column', alignItems: 'stretch' }}>
              <div className="search-icon-wrapper">
                <svg
                  className="search-icon"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M15.5 15.5L20 20"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <circle
                    cx="11"
                    cy="11"
                    r="5"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>

              <input
                type="email"
                className="search-field"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />

              <div className="input-wrap">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="search-field"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ paddingRight: 56 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="password-toggle-btn"
                >
                  {showPassword ? (
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M3 12C3 12 7 5 12 5C17 5 21 12 21 12C21 12 17 19 12 19C7 19 3 12 3 12Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M3 12C3 12 7 5 12 5C17 5 21 12 21 12C21 12 17 19 12 19C7 19 3 12 3 12Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                      <line x1="3" y1="21" x2="21" y2="3" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                    </svg>
                  )}
                </button>
              </div>

              <button type="submit" className="search-btn" disabled={submitting}>
                {submitting ? <span className="btn-loader-small" /> : 'Sign in'}
              </button>
            </div>

            {error && (
              <div className="alert alert-error">
                <svg
                  className="alert-icon"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M12 9V13"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M12 17H12.01"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M10.29 4.85999L3.81999 16C3.45734 16.6274 3.45818 17.4011 3.82225 18.0278C4.18632 18.6545 4.86144 19.0313 5.59 19.03H18.41C19.1386 19.0313 19.8137 18.6545 20.1777 18.0278C20.5418 17.4011 20.5426 16.6274 20.18 16L13.71 4.85999C13.34 4.24338 12.6896 3.86572 11.995 3.86572C11.3004 3.86572 10.65 4.24338 10.29 4.85999Z"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <span>{error}</span>
              </div>
            )}
          </form>

          <div className="auth-footer">
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToSignup}
              className="link-btn"
            >
              Create one
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;

