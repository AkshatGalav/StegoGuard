import React, { useState } from 'react';
import { X, Lock, Mail, User, Shield, LogIn, UserPlus } from 'lucide-react';

export default function AuthModal({ isOpen, onClose, onAuthSuccess, showToast }) {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password) return showToast('Please enter password', 'error');

    setLoading(true);
    try {
      const endpoint = isLoginMode ? '/api/auth/login' : '/api/auth/register';
      const formData = new FormData();
      if (isLoginMode) {
        formData.append('identifier', username || email);
      } else {
        if (!username || !email) {
          setLoading(false);
          return showToast('Username and email are required', 'error');
        }
        formData.append('username', username);
        formData.append('email', email);
      }
      formData.append('password', password);

      const res = await fetch(endpoint, { method: 'POST', body: formData });
      const data = await res.json();

      if (res.ok) {
        onAuthSuccess(data.user, data.token);
        showToast(isLoginMode ? `Welcome back, ${data.user.username}!` : 'Account created successfully!', 'success');
        onClose();
      } else {
        showToast(data.detail || 'Authentication failed', 'error');
      }
    } catch (err) {
      showToast('Server error during authentication', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 1000,
      backgroundColor: 'rgba(5, 8, 17, 0.85)',
      backdropFilter: 'blur(20px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px'
    }}>
      <div className="glass-card" style={{ maxWidth: '440px', width: '100%', position: 'relative', border: '1px solid var(--primary-cyan)' }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          <X size={20} />
        </button>

        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <Shield style={{ color: 'var(--primary-lime)', width: '48px', height: '48px', margin: '0 auto 12px' }} />
          <h2 className="card-title" style={{ justifyContent: 'center', fontSize: '1.5rem', marginBottom: '4px' }}>
            {isLoginMode ? 'User Sign In' : 'Create Sentinel Account'}
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            {isLoginMode ? 'Access your private cryptographic key vault' : 'Register your secure identity'}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {!isLoginMode && (
            <div className="form-group">
              <label className="form-label"><User size={14} style={{ verticalAlign: 'middle' }} /> Username</label>
              <input
                type="text"
                className="form-control"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. alex_sentinel"
                required
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">
              {isLoginMode ? <User size={14} style={{ verticalAlign: 'middle' }} /> : <Mail size={14} style={{ verticalAlign: 'middle' }} />}
              {isLoginMode ? ' Username or Email' : ' Email Address'}
            </label>
            <input
              type={isLoginMode ? 'text' : 'email'}
              className="form-control"
              value={isLoginMode ? username : email}
              onChange={(e) => isLoginMode ? setUsername(e.target.value) : setEmail(e.target.value)}
              placeholder={isLoginMode ? 'Enter username or email...' : 'alex@example.com'}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label"><Lock size={14} style={{ verticalAlign: 'middle' }} /> Password</label>
            <input
              type="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
            />
          </div>

          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%', marginTop: '12px' }}>
            {isLoginMode ? <LogIn size={18} /> : <UserPlus size={18} />}
            {loading ? 'Authenticating...' : (isLoginMode ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {isLoginMode ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => setIsLoginMode(!isLoginMode)}
            style={{ background: 'none', border: 'none', color: 'var(--primary-cyan)', fontWeight: 700, cursor: 'pointer', textDecoration: 'underline' }}
          >
            {isLoginMode ? 'Register Now' : 'Sign In'}
          </button>
        </div>
      </div>
    </div>
  );
}
