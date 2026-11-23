import React, { useState } from 'react';
import { Key, Upload, Lock, Download, Check, HardDrive } from 'lucide-react';

export default function SecureEncode({ showToast }) {
  const [message, setMessage] = useState('');
  const [key, setKey] = useState('');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [imageMeta, setImageMeta] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleGenerateKey = () => {
    const randomBytes = new Uint8Array(32);
    window.crypto.getRandomValues(randomBytes);
    const b64 = btoa(String.fromCharCode.apply(null, randomBytes));
    setKey(b64);
    showToast('New 256-bit AES key generated!', 'success');
  };

  const handleCopyKey = () => {
    if (!key) return showToast('No key to copy!', 'error');
    navigator.clipboard.writeText(key);
    showToast('Key copied to clipboard!', 'success');
  };

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) {
      setFile(f);
      const reader = new FileReader();
      reader.onload = (evt) => {
        setPreview(evt.target.result);
        const img = new Image();
        img.src = evt.target.result;
        img.onload = () => {
          // LSB Capacity calculation: (width * height * 3 channels) / 8 bits
          const maxCapacityBytes = Math.floor((img.width * img.height * 3) / 8);
          setImageMeta({ width: img.width, height: img.height, maxCapacityBytes });
        };
      };
      reader.readAsDataURL(f);
    }
  };

  const handleEncode = async () => {
    if (!message) return showToast('Please enter a secret message!', 'error');
    if (!file) return showToast('Please select a cover image!', 'error');

    const formData = new FormData();
    formData.append('message', message);
    formData.append('cover_image', file);
    if (key) formData.append('key_b64', key);

    setLoading(true);
    try {
      const res = await fetch('/api/encode', { method: 'POST', body: formData });
      const data = await res.json();
      if (res.ok) {
        setKey(data.key_b64);
        setResult(data);
        showToast('Message encrypted & embedded successfully!', 'success');
      } else {
        showToast(data.detail || 'Encoding failed', 'error');
      }
    } catch (err) {
      showToast('Server error during encoding', 'error');
    } finally {
      setLoading(false);
    }
  };

  const payloadLength = new TextEncoder().encode(message).length;
  const capacityPct = imageMeta ? Math.min(100, Math.max(1, (payloadLength / imageMeta.maxCapacityBytes) * 100)) : 0;

  return (
    <div>
      <div className="card-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <div className="glass-card">
          <h3 className="card-title">1. Secret Message & AES Key</h3>
          <div className="form-group">
            <label className="form-label">Confidential Message to Embed</label>
            <textarea
              className="form-control"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your secret message here..."
            />
          </div>

          {imageMeta && (
            <div style={{ marginBottom: '20px', padding: '14px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: '14px', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-muted)' }}>
                <span><HardDrive size={14} style={{ verticalAlign: 'middle' }} /> LSB IMAGE CAPACITY</span>
                <span>{payloadLength} B / {imageMeta.maxCapacityBytes.toLocaleString()} B ({capacityPct.toFixed(1)}%)</span>
              </div>
              <div className="progress-container">
                <div className="progress-bar cyan" style={{ width: `${capacityPct}%` }} />
              </div>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">AES-256 Encryption Key (Base64)</label>
            <div className="input-with-copy">
              <input
                type="text"
                className="form-control code-font"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="Generate or paste 256-bit key..."
              />
              <button className="btn-copy" onClick={handleCopyKey}>Copy Key</button>
            </div>
          </div>

          <button className="btn btn-outline" onClick={handleGenerateKey} style={{ marginBottom: '16px' }}>
            <Key size={18} /> Generate Secure Key
          </button>
        </div>

        <div className="glass-card">
          <h3 className="card-title">2. Cover Image Upload</h3>
          <div className="upload-zone" onClick={() => document.getElementById('encode-input').click()}>
            <Upload className="upload-icon" />
            <p style={{ fontWeight: 600 }}>Drag & Drop Cover Image Here</p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Supports PNG, BMP (Max 10MB)</p>
            <input id="encode-input" type="file" accept="image/*" onChange={handleFileChange} style={{ display: 'none' }} />
          </div>

          {file && (
            <div className="file-preview">
              <img src={preview} alt="Preview" />
              <div>
                <p style={{ fontWeight: 600, fontSize: '0.88rem' }}>{file.name}</p>
                {imageMeta && <p style={{ fontSize: '0.78rem', color: 'var(--primary-lime)' }}>{imageMeta.width}x{imageMeta.height} px | Max {imageMeta.maxCapacityBytes.toLocaleString()} B</p>}
              </div>
            </div>
          )}

          <div style={{ marginTop: '24px' }}>
            <button className="btn btn-primary" onClick={handleEncode} disabled={loading} style={{ width: '100%' }}>
              <Lock size={18} /> {loading ? 'Processing Encryption...' : 'Encrypt & Embed Payload'}
            </button>
          </div>
        </div>
      </div>

      {result && (
        <div className="glass-card" style={{ marginTop: '24px' }}>
          <h3 className="card-title" style={{ color: 'var(--primary-lime)' }}>
            <Check size={20} /> Stego Image Generated Successfully!
          </h3>
          <div className="card-grid" style={{ gridTemplateColumns: '200px 1fr' }}>
            <img src={result.stego_image_b64} style={{ width: '100%', borderRadius: '12px', border: '1px solid var(--border-color)' }} alt="Stego" />
            <div>
              <p style={{ fontSize: '0.85rem', marginBottom: '8px' }}><strong>Payload SHA-256 Digest:</strong></p>
              <code style={{ color: 'var(--primary-cyan)', fontSize: '0.82rem', wordBreak: 'break-all' }}>{result.payload_hash}</code>
              <div style={{ marginTop: '20px' }}>
                <a href={result.stego_image_b64} download="stego_image.png" className="btn btn-secondary">
                  <Download size={18} /> Download Stego PNG
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
