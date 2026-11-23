import React, { useState } from 'react';
import { Upload, Unlock, CheckCircle } from 'lucide-react';

export default function SecureDecode({ showToast }) {
  const [key, setKey] = useState('');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [decryptedMessage, setDecryptedMessage] = useState('');

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) {
      setFile(f);
      const reader = new FileReader();
      reader.onload = (evt) => setPreview(evt.target.result);
      reader.readAsDataURL(f);
    }
  };

  const handleDecode = async () => {
    if (!file) return showToast('Please upload a Stego PNG image!', 'error');
    if (!key) return showToast('Please enter the Base64 decryption key!', 'error');

    const formData = new FormData();
    formData.append('stego_image', file);
    formData.append('key_b64', key);

    setLoading(true);
    try {
      const res = await fetch('/api/decode', { method: 'POST', body: formData });
      const data = await res.json();
      if (res.ok) {
        setDecryptedMessage(data.decrypted_message);
        showToast('Payload extracted & decrypted successfully!', 'success');
      } else {
        showToast(data.detail || 'Decoding failed', 'error');
      }
    } catch (err) {
      showToast('Server error during decoding', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="card-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <div className="glass-card">
          <h3 className="card-title">1. Upload Stego Image</h3>
          <div className="upload-zone" onClick={() => document.getElementById('decode-input').click()}>
            <Upload className="upload-icon" />
            <p style={{ fontWeight: 600 }}>Drag & Drop Stego PNG Image</p>
            <input id="decode-input" type="file" accept="image/png" onChange={handleFileChange} style={{ display: 'none' }} />
          </div>

          {file && (
            <div className="file-preview">
              <img src={preview} alt="Preview" />
              <div>
                <p style={{ fontWeight: 600, fontSize: '0.88rem' }}>{file.name}</p>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{(file.size / 1024).toFixed(1)} KB</p>
              </div>
            </div>
          )}
        </div>

        <div className="glass-card">
          <h3 className="card-title">2. Decryption Key</h3>
          <div className="form-group">
            <label className="form-label">Enter 256-bit Decryption Key (Base64)</label>
            <input
              type="text"
              className="form-control code-font"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              placeholder="Paste Base64 key generated during encoding..."
            />
          </div>

          <button className="btn btn-primary" onClick={handleDecode} disabled={loading} style={{ width: '100%', marginTop: '16px' }}>
            <Unlock size={18} /> {loading ? 'Extracting Payload...' : 'Extract & Decrypt'}
          </button>
        </div>
      </div>

      {decryptedMessage && (
        <div className="glass-card" style={{ marginTop: '24px' }}>
          <h3 className="card-title" style={{ color: 'var(--success-green)' }}>
            <CheckCircle size={20} /> Authenticated Decryption Successful
          </h3>
          <div className="form-group">
            <label className="form-label">Decrypted Plaintext Message</label>
            <textarea
              className="form-control"
              readOnly
              value={decryptedMessage}
              style={{ color: 'var(--success-green)', fontWeight: 600 }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
