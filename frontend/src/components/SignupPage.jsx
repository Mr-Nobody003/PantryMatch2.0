import React, { useState } from 'react';
import Header from './Header';

function SignupPage({ onSignup, onSwitchToLogin }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !password.trim() || !confirmPassword.trim()) {
      setError('Please fill in all fields.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    try {
      setSubmitting(true);
      setError('');
      if (onSignup) {
        await onSignup({ name, email, password });
      }
    } catch (err) {
      const message = err?.message || 'Could not create your account. Please try again.';
      if (message.toLowerCase().includes('already exists')) {
        setError('An account with this email already exists. Try signing in instead.');
      } else {
        setError(message);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="app">
      <div className="app-container">
        <Header />

        <div className="content-wrapper">
          <div className="results-header" style={{ borderBottom: 'none', marginBottom: '24px' }}>
            <h2 className="results-title">
              <span className="results-label">Join</span>
              <span className="results-count">Pantry Match</span>
            </h2>
          </div>

          <form onSubmit={handleSubmit} className="search-area">
            <div className="search-box" style={{ flexDirection: 'column', alignItems: 'stretch' }}>
              <input
                type="text"
                className="search-field"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />

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
                  placeholder="Password (min 6 characters)"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{ paddingRight: 56 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="input-action"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>

              <div className="input-wrap">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  className="search-field"
                  placeholder="Confirm password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  style={{ paddingRight: 56 }}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword((v) => !v)}
                  aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                  className="input-action"
                >
                  {showConfirmPassword ? 'Hide' : 'Show'}
                </button>
              </div>

              <button type="submit" className="search-btn" disabled={submitting}>
                {submitting ? <span className="btn-loader-small" /> : 'Create account'}
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
            Already have an account?{' '}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="link-btn"
            >
              Sign in
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SignupPage;

