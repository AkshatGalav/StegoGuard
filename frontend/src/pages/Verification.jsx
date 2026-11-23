import React, { useState } from 'react';
import { Key, ShieldCheck, Check, AlertCircle } from 'lucide-react';

export default function Verification({ showToast }) {
  const [activeTab, setActiveTab] = useState('hash');

  // SHA-256 state
  const [hashText, setHashText] = useState('');
  const [expectedHash, setExpectedHash] = useState('');
  const [computedHash, setComputedHash] = useState('');
  const [hashVerified, setHashVerified] = useState(null);

  // RSA state
  const [privKey, setPrivKey] = useState('');
  const [pubKey, setPubKey] = useState('');

  // Sign state
  const [signPayload, setSignPayload] = useState('');
  const [signatureB64, setSignatureB64] = useState('');

  // Verify state
  const [verPayload, setVerPayload] = useState('');
  const [verSigB64, setVerSigB64] = useState('');
  const [verPubKey, setVerPubKey] = useState('');
  const [verResult, setVerResult] = useState(null);

  const handleCalculateHash = async () => {
    if (!hashText) return showToast('Please enter text to hash!', 'error');

    const formData = new FormData();
    formData.append('text', hashText);
    if (expectedHash) formData.append('expected_hash', expectedHash);

    try {
      const res = await fetch('/api/verification/hash', { method: 'POST', body: formData });
      const data = await res.json();
      if (res.ok) {
        setComputedHash(data.computed_hash);
        setHashVerified(data.is_verified);
        showToast('SHA-256 Digest calculated!', 'success');
      }
    } catch (err) {
      showToast('Hash calculation failed', 'error');
    }
  };

  const handleGenerateRSA = async () => {
    try {
      const res = await fetch('/api/verification/generate-keys', { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setPrivKey(data.private_key);
        setPubKey(data.public_key);
        setVerPubKey(data.public_key);
        showToast('New RSA-2048 key pair generated!', 'success');
      }
    } catch (err) {
      showToast('RSA Key generation failed', 'error');
    }
  };

  const handleSign = async () => {
    if (!signPayload || !privKey) return showToast('Provide payload and private key!', 'error');

    const formData = new FormData();
    formData.append('payload', signPayload);
    formData.append('private_key_pem', privKey);

    try {
      const res = await fetch('/api/verification/sign', { method: 'POST', body: formData });
      const data = await res.json();
      if (res.ok) {
        setSignatureB64(data.signature_b64);
        setVerPayload(signPayload);
        setVerSigB64(data.signature_b64);
        showToast('Digital signature generated!', 'success');
      } else {
        showToast(data.detail || 'Signing failed', 'error');
      }
    } catch (err) {
      showToast('Signing error', 'error');
    }
  };

  const handleVerify = async () => {
    if (!verPayload || !verSigB64 || !verPubKey) return showToast('Provide payload, signature, and public key!', 'error');

    const formData = new FormData();
    formData.append('payload', verPayload);
    formData.append('signature_b64', verSigB64);
    formData.append('public_key_pem', verPubKey);

    try {
      const res = await fetch('/api/verification/verify', { method: 'POST', body: formData });
      const data = await res.json();
      if (res.ok) {
        setVerResult(data.is_valid);
        showToast(data.is_valid ? 'Signature Verified!' : 'Signature Invalid!', data.is_valid ? 'success' : 'error');
      }
    } catch (err) {
      showToast('Verification failed', 'error');
    }
  };

  return (
    <div>
      <div className="sub-tabs">
        <button className={`sub-tab-btn ${activeTab === 'hash' ? 'active' : ''}`} onClick={() => setActiveTab('hash')}>1. SHA-256 Hashing</button>
        <button className={`sub-tab-btn ${activeTab === 'keys' ? 'active' : ''}`} onClick={() => setActiveTab('keys')}>2. RSA Key Generator</button>
        <button className={`sub-tab-btn ${activeTab === 'sign' ? 'active' : ''}`} onClick={() => setActiveTab('sign')}>3. Digital Signing</button>
        <button className={`sub-tab-btn ${activeTab === 'verify' ? 'active' : ''}`} onClick={() => setActiveTab('verify')}>4. Signature Verification</button>
      </div>

      {activeTab === 'hash' && (
        <div className="glass-card">
          <h3 className="card-title">SHA-256 Cryptographic Hash Calculation</h3>
          <div className="form-group">
            <label className="form-label">Enter Text to Hash</label>
            <textarea className="form-control" value={hashText} onChange={(e) => setHashText(e.target.value)} placeholder="Type text..." />
          </div>
          <div className="form-group">
            <label className="form-label">Expected Hash (Optional Verification)</label>
            <input type="text" className="form-control code-font" value={expectedHash} onChange={(e) => setExpectedHash(e.target.value)} placeholder="Paste expected SHA-256 hash..." />
          </div>
          <button className="btn btn-primary" onClick={handleCalculateHash}>Calculate SHA-256 Digest</button>

          {computedHash && (
            <div style={{ marginTop: '20px' }}>
              <p className="form-label">Calculated Digest:</p>
              <code style={{ color: 'var(--primary-cyan)', fontSize: '0.9rem', wordBreak: 'break-all' }}>{computedHash}</code>
              {hashVerified === true && <p style={{ color: 'var(--success-green)', fontWeight: 700, marginTop: '12px' }}>✅ Integrity Verified: Hash matches expected digest!</p>}
              {hashVerified === false && <p style={{ color: 'var(--danger-red)', fontWeight: 700, marginTop: '12px' }}>🚨 Integrity Violation: Hash mismatch detected!</p>}
            </div>
          )}
        </div>
      )}

      {activeTab === 'keys' && (
        <div className="glass-card">
          <h3 className="card-title">RSA-2048 Asymmetric Key Pair Generator</h3>
          <button className="btn btn-primary" onClick={handleGenerateRSA} style={{ marginBottom: '20px' }}>
            <Key size={18} /> Generate RSA-2048 Key Pair
          </button>
          <div className="card-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div>
              <label className="form-label">Private Key (PEM)</label>
              <textarea className="form-control code-font" readOnly value={privKey} style={{ height: '200px' }} />
            </div>
            <div>
              <label className="form-label">Public Key (PEM)</label>
              <textarea className="form-control code-font" readOnly value={pubKey} style={{ height: '200px' }} />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'sign' && (
        <div className="glass-card">
          <h3 className="card-title">Digital Payload Signing</h3>
          <div className="form-group">
            <label className="form-label">Payload Data to Sign</label>
            <textarea className="form-control" value={signPayload} onChange={(e) => setSignPayload(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">RSA Private Key (PEM)</label>
            <textarea className="form-control code-font" value={privKey} onChange={(e) => setPrivKey(e.target.value)} style={{ height: '120px' }} />
          </div>
          <button className="btn btn-primary" onClick={handleSign}>🔏 Sign Payload</button>

          {signatureB64 && (
            <div style={{ marginTop: '20px' }}>
              <label className="form-label">Base64 Digital Signature</label>
              <textarea className="form-control code-font" readOnly value={signatureB64} style={{ color: 'var(--primary-cyan)' }} />
            </div>
          )}
        </div>
      )}

      {activeTab === 'verify' && (
        <div className="glass-card">
          <h3 className="card-title">Signature Authenticity Verification</h3>
          <div className="form-group">
            <label className="form-label">Payload Data</label>
            <textarea className="form-control" value={verPayload} onChange={(e) => setVerPayload(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Base64 Digital Signature</label>
            <input type="text" className="form-control code-font" value={verSigB64} onChange={(e) => setVerSigB64(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Sender RSA Public Key (PEM)</label>
            <textarea className="form-control code-font" value={verPubKey} onChange={(e) => setVerPubKey(e.target.value)} style={{ height: '120px' }} />
          </div>
          <button className="btn btn-primary" onClick={handleVerify}>Verify Signature</button>

          {verResult !== null && (
            <div style={{ marginTop: '20px', fontWeight: 800, fontSize: '1.1rem' }}>
              {verResult ? (
                <span style={{ color: 'var(--success-green)' }}>✅ Signature Verified: Authenticity and origin confirmed!</span>
              ) : (
                <span style={{ color: 'var(--danger-red)' }}>🚨 Signature Invalid: Payload or key mismatch detected!</span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
