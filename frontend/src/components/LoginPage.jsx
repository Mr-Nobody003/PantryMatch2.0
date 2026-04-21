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
          <div className="results-header" style={{ borderBottom: 'none', marginBottom: '40px', display: 'flex', justifyContent: 'center' }}>
            <h2 className="results-title" style={{ display: 'flex', flexDirection: 'column', gap: '0', alignItems: 'center', textAlign: 'center', margin: 0, border: 'none', background: 'transparent', padding: 0, boxShadow: 'none' }}>
              <span className="results-label" style={{ fontSize: '1.3rem', color: '#8a7e71', fontWeight: 600, letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '2px' }}>Welcome back to</span>
              <span className="results-count" style={{ fontSize: '3.6rem', fontWeight: 900, background: 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-1.5px', wordSpacing: '0.05em', lineHeight: '1.1' }}>Pantry Match</span>
            </h2>
          </div>

          <form onSubmit={handleSubmit} className="search-area" style={{ maxWidth: '640px', width: '100%', margin: '0 auto' }}>
            <div className="search-box" style={{ flexDirection: 'column', alignItems: 'stretch', gap: '16px', padding: '36px', borderRadius: '24px', boxShadow: '0 16px 50px rgba(0,0,0,0.08)' }}>
              
              <div className="input-wrap">
                <input
                  type="email"
                  className="search-field"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{ fontSize: '1.45rem', padding: '20px', background: '#fcfcfc', borderRadius: '14px', border: '1px solid #eee' }}
                />
              </div>

              <div className="input-wrap">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="search-field"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ fontSize: '1.45rem', padding: '20px 64px 20px 20px', background: '#fcfcfc', borderRadius: '14px', border: '1px solid #eee' }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="password-toggle-btn"
                >
                  {showPassword ? (
                     <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '24px', height: '24px' }}>
                      <path d="M3 12C3 12 7 5 12 5C17 5 21 12 21 12C21 12 17 19 12 19C7 19 3 12 3 12Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ) : (
                     <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '24px', height: '24px' }}>
                      <path d="M3 12C3 12 7 5 12 5C17 5 21 12 21 12C21 12 17 19 12 19C7 19 3 12 3 12Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
                      <line x1="3" y1="21" x2="21" y2="3" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                    </svg>
                  )}
                </button>
              </div>

              <button type="submit" className="search-btn" disabled={submitting} style={{ fontSize: '1.6rem', padding: '22px', marginTop: '16px', borderRadius: '16px', fontWeight: 800, letterSpacing: '0.5px' }}>
                {submitting ? <span className="btn-loader-small" /> : 'Sign In'}
              </button>
            </div>

            {error && (
              <div className="alert alert-error" style={{ fontSize: '1.1rem', padding: '16px', marginTop: '20px', borderRadius: '12px' }}>
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

          <div className="auth-footer" style={{ fontSize: '1.2rem', marginTop: '28px', color: '#6b6457', fontWeight: '500' }}>
            Don't have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToSignup}
              className="link-btn"
              style={{ fontSize: '1.2rem', marginLeft: '8px', fontWeight: '700' }}
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

