import React, { useState, useEffect } from 'react';
import { Shield, Lock, Unlock, Search, CheckCircle, BarChart3, Database, Key, LogIn, LogOut, User, ArrowUp } from 'lucide-react';

import Home from './pages/Home';
import SecureEncode from './pages/SecureEncode';
import SecureDecode from './pages/SecureDecode';
import Steganalysis from './pages/Steganalysis';
import Verification from './pages/Verification';
import Analytics from './pages/Analytics';
import AuditLogs from './pages/AuditLogs';
import KeyVault from './pages/KeyVault';
import AuthModal from './components/AuthModal';

export default function App() {
  const [activeSection, setActiveSection] = useState('home');
  const [toast, setToast] = useState(null);
  const [showBackToTop, setShowBackToTop] = useState(false);

  // Authentication State
  const [token, setToken] = useState(() => localStorage.getItem('stegoguard_token') || '');
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Verify stored JWT token on load
  useEffect(() => {
    if (token) {
      fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'SUCCESS') {
            setCurrentUser(data.user);
          } else {
            handleLogout();
          }
        })
        .catch(() => handleLogout());
    }
  }, [token]);

  useEffect(() => {
    const handleScroll = () => {
      setShowBackToTop(window.scrollY > 300);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleAuthSuccess = (user, jwtToken) => {
    setCurrentUser(user);
    setToken(jwtToken);
    localStorage.setItem('stegoguard_token', jwtToken);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setToken('');
    localStorage.removeItem('stegoguard_token');
    showToast('Signed out of session', 'success');
  };

  const scrollToSection = (id) => {
    setActiveSection(id);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const navLinks = [
    { id: 'home', label: 'Home', icon: Shield },
    { id: 'encode', label: 'Encode', icon: Lock },
    { id: 'decode', label: 'Decode', icon: Unlock },
    { id: 'steganalysis', label: 'Steganalysis', icon: Search },
    { id: 'verification', label: 'Verification', icon: CheckCircle },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'vault', label: 'Key Vault', icon: Key, reqAuth: true },
    { id: 'audit', label: 'Audit History', icon: Database },
  ];

  return (
    <div>
      {/* Top Glassmorphic Sticky Header */}
      <header className="top-navbar">
        <div className="top-nav-brand">
          <Shield style={{ color: 'var(--primary-lime)' }} size={24} />
          <h2>StegoGuard Quantum</h2>
        </div>

        <nav>
          <ul className="top-nav-links">
            {navLinks.map((link) => {
              if (link.reqAuth && !currentUser) return null;
              const IconComp = link.icon;
              return (
                <li key={link.id}>
                  <button
                    className={`top-nav-link ${activeSection === link.id ? 'active' : ''}`}
                    onClick={() => scrollToSection(link.id)}
                  >
                    <IconComp size={15} style={{ verticalAlign: 'middle', marginRight: '6px' }} />
                    {link.label}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* User Auth Action Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {currentUser ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{
                background: 'rgba(0, 255, 136, 0.12)',
                border: '1px solid rgba(0, 255, 136, 0.3)',
                padding: '6px 14px',
                borderRadius: '20px',
                fontSize: '0.82rem',
                fontWeight: 700,
                color: 'var(--primary-lime)'
              }}>
                <User size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} />
                {currentUser.username} [{currentUser.role}]
              </span>
              <button
                className="btn btn-outline"
                onClick={handleLogout}
                style={{ padding: '6px 14px', fontSize: '0.82rem', borderColor: 'var(--danger-red)', color: 'var(--danger-red)' }}
              >
                <LogOut size={14} /> Sign Out
              </button>
            </div>
          ) : (
            <button
              className="btn btn-primary"
              onClick={() => setIsAuthModalOpen(true)}
              style={{ padding: '8px 18px', fontSize: '0.88rem' }}
            >
              <LogIn size={16} /> Sign In / Register
            </button>
          )}
        </div>
      </header>

      {/* Main Workspace Area */}
      <main className="main-content">
        <header className="hero-banner">
          <div className="status-badge">
            <span className="pulse-dot"></span>
            <span>{currentUser ? `LOGGED IN AS ${currentUser.username.toUpperCase()}` : 'GUEST SESSION ACTIVE'}</span>
          </div>
          <h1 className="page-title">StegoGuard Sentinel Workspace</h1>
          <p className="page-subtitle">Classical Machine Learning Steganalysis & AEAD Encrypted Covert Embedding</p>
        </header>

        {/* Section 1: Home */}
        <section id="home" className="section-block">
          <Home onNavigate={scrollToSection} />
        </section>

        {/* Section 2: Secure Encode */}
        <section id="encode" className="section-block">
          <h2 className="card-title" style={{ fontSize: '1.8rem', color: 'var(--primary-lime)', marginBottom: '20px' }}>
            <Lock size={24} /> 1. Secure Payload Embedding (AES-256-GCM + LSB)
          </h2>
          <SecureEncode showToast={showToast} token={token} />
        </section>

        {/* Section 3: Secure Decode */}
        <section id="decode" className="section-block">
          <h2 className="card-title" style={{ fontSize: '1.8rem', color: 'var(--primary-cyan)', marginBottom: '20px' }}>
            <Unlock size={24} /> 2. Secure Payload Extraction & Decryption
          </h2>
          <SecureDecode showToast={showToast} token={token} />
        </section>

        {/* Section 4: Steganalysis */}
        <section id="steganalysis" className="section-block">
          <h2 className="card-title" style={{ fontSize: '1.8rem', color: 'var(--warning-amber)', marginBottom: '20px' }}>
            <Search size={24} /> 3. Classical Machine Learning Steganalysis
          </h2>
          <Steganalysis showToast={showToast} token={token} />
        </section>

        {/* Section 5: Verification */}
        <section id="verification" className="section-block">
          <h2 className="card-title" style={{ fontSize: '1.8rem', color: 'var(--accent-purple)', marginBottom: '20px' }}>
            <CheckCircle size={24} /> 4. Integrity & Digital Signatures (SHA-256 / RSA-2048)
          </h2>
          <Verification showToast={showToast} token={token} />
        </section>

        {/* Section 6: Key Vault (Authenticated Users Only) */}
        {currentUser && (
          <section id="vault" className="section-block">
            <h2 className="card-title" style={{ fontSize: '1.8rem', color: 'var(--primary-lime)', marginBottom: '20px' }}>
              <Key size={24} /> 5. Personal Cryptographic Key Vault
            </h2>
            <KeyVault token={token} showToast={showToast} />
          </section>
        )}

        {/* Section 7: Analytics */}
        <section id="analytics" className="section-block">
          <h2 className="card-title" style={{ fontSize: '1.8rem', color: 'var(--primary-cyan)', marginBottom: '20px' }}>
            <BarChart3 size={24} /> 6. Model Analytics & Feature Importance
          </h2>
          <Analytics />
        </section>

        {/* Section 8: Audit Logs */}
        <section id="audit" className="section-block">
          <h2 className="card-title" style={{ fontSize: '1.8rem', color: 'var(--text-main)', marginBottom: '20px' }}>
            <Database size={24} /> 7. Privacy-Compliant Audit Log History
          </h2>
          <AuditLogs showToast={showToast} token={token} />
        </section>
      </main>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
        showToast={showToast}
      />

      {/* Floating Back to Top Button */}
      {showBackToTop && (
        <button className="back-to-top" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} title="Back to Top">
          <ArrowUp size={24} />
        </button>
      )}

      {/* Toast Notifications Popup */}
      {toast && (
        <div className="toast-container">
          <div className={`toast ${toast.type}`}>
            <span>{toast.type === 'success' ? '✅' : '🚨'}</span>
            <span>{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  );
}
