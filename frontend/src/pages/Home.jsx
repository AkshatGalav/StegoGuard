import React from 'react';
import { Shield, Lock, Unlock, Search, CheckCircle, BarChart3, Database } from 'lucide-react';

export default function Home({ onNavigate }) {
  return (
    <div>
      <div className="card-grid">
        <div className="glass-card" style={{ cursor: 'pointer' }} onClick={() => onNavigate('tab-encode')}>
          <h3 className="card-title"><Lock style={{ color: 'var(--primary-cyan)' }} /> Secure Encode</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.6' }}>
            Encrypt text using <strong>AES-256-GCM</strong> authenticated encryption and conceal ciphertext inside PNG/BMP cover images via <strong>LSB spatial steganography</strong>.
          </p>
        </div>

        <div className="glass-card" style={{ cursor: 'pointer' }} onClick={() => onNavigate('tab-decode')}>
          <h3 className="card-title"><Unlock style={{ color: 'var(--primary-cyan)' }} /> Secure Decode</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.6' }}>
            Extract embedded stego payloads and validate <strong>AES-GCM MAC tags</strong> before decrypting the original plaintext secret message.
          </p>
        </div>

        <div className="glass-card" style={{ cursor: 'pointer' }} onClick={() => onNavigate('tab-steganalysis')}>
          <h3 className="card-title"><Search style={{ color: 'var(--primary-cyan)' }} /> ML Steganalysis</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: '1.6' }}>
            Analyze suspect images with trained classical ML models (<strong>Random Forest, Logistic Regression, SVM</strong>) using 29 statistical & texture anomaly features.
          </p>
        </div>
      </div>

      <div className="glass-card">
        <h3 className="card-title"><Shield style={{ color: 'var(--success-green)' }} /> Security Principles & Architecture</h3>
        <ul style={{ color: 'var(--text-muted)', paddingLeft: '20px', lineHeight: '1.8', fontSize: '0.92rem' }}>
          <li><strong>Layered Protection:</strong> Payload is encrypted with AES-256-GCM prior to embedding, preserving confidentiality if steganography is detected.</li>
          <li><strong>Digital Signatures:</strong> Uses RSA-2048 PSS signatures to guarantee payload authenticity and non-repudiation.</li>
          <li><strong>Privacy Audit History:</strong> SQLite audit log tracks image digests and operation timestamps without storing secret text or keys.</li>
        </ul>
      </div>
    </div>
  );
}
