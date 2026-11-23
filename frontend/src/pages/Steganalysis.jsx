import React, { useState } from 'react';
import { Search, Upload, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function Steganalysis({ showToast }) {
  const [model, setModel] = useState('Random Forest');
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (f) {
      setFile(f);
      const reader = new FileReader();
      reader.onload = (evt) => setPreview(evt.target.result);
      reader.readAsDataURL(f);
    }
  };

  const handleSteganalysis = async () => {
    if (!file) return showToast('Please upload a suspect image!', 'error');

    const formData = new FormData();
    formData.append('image', file);
    formData.append('model_name', model);

    setLoading(true);
    try {
      const res = await fetch('/api/steganalysis', { method: 'POST', body: formData });
      const data = await res.json();
      if (res.ok) {
        setResult(data);
        showToast('Steganalysis feature extraction complete!', 'success');
      } else {
        showToast(data.detail || 'Steganalysis failed', 'error');
      }
    } catch (err) {
      showToast('Server error during steganalysis', 'error');
    } finally {
      setLoading(false);
    }
  };

  const probPct = result ? (result.stego_probability * 100) : 0;

  return (
    <div>
      <div className="card-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <div className="glass-card">
          <h3 className="card-title">1. Image & Model Selection</h3>
          <div className="form-group">
            <label className="form-label">Select Classical ML Model</label>
            <select className="form-control" value={model} onChange={(e) => setModel(e.target.value)}>
              <option value="Random Forest">Random Forest Classifier (Recommended)</option>
              <option value="Logistic Regression">Logistic Regression Classifier</option>
              <option value="Support Vector Machine">Support Vector Machine (SVM)</option>
            </select>
          </div>

          <div className="upload-zone" onClick={() => document.getElementById('steg-input').click()}>
            <Search className="upload-icon" />
            <p style={{ fontWeight: 600 }}>Drag & Drop Suspect Image</p>
            <input id="steg-input" type="file" accept="image/*" onChange={handleFileChange} style={{ display: 'none' }} />
          </div>

          {file && (
            <div className="file-preview">
              <img src={preview} alt="Preview" />
              <div>
                <p style={{ fontWeight: 600, fontSize: '0.88rem' }}>{file.name}</p>
              </div>
            </div>
          )}

          <button className="btn btn-primary" onClick={handleSteganalysis} disabled={loading} style={{ width: '100%', marginTop: '20px' }}>
            <Search size={18} /> {loading ? 'Extracting 29 Features & Predicting...' : '⚡ Run Steganalysis'}
          </button>
        </div>

        <div className="glass-card">
          <h3 className="card-title">2. Steganalysis Prediction Output</h3>
          {!result ? (
            <div style={{ color: 'var(--text-muted)', padding: '40px', textAlign: 'center' }}>
              Upload an image and click <strong>Run Steganalysis</strong> to analyze 29 features and evaluate payload probability.
            </div>
          ) : (
            <div>
              <div className="card-grid" style={{ gridTemplateColumns: '1fr 1fr', marginBottom: '16px' }}>
                <div className="metric-box">
                  <p className="metric-label">CLASSIFICATION RESULT</p>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginTop: '8px' }}>
                    {result.prediction === 1 ? (
                      <span style={{ color: 'var(--danger-red)', fontWeight: 900, fontSize: '1.2rem' }}>
                        <ShieldAlert size={20} inline="true" /> Stego Image Detected
                      </span>
                    ) : (
                      <span style={{ color: 'var(--primary-lime)', fontWeight: 900, fontSize: '1.2rem' }}>
                        <CheckCircle2 size={20} inline="true" /> Clean Cover Image
                      </span>
                    )}
                  </div>
                </div>

                <div className="metric-box">
                  <p className="metric-label">STEGO PROBABILITY</p>
                  <p className="metric-value">{probPct.toFixed(1)}%</p>
                </div>
              </div>

              {/* Animated Threat Probability Fill Gauge */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>
                  <span>ANOMALY PROBABILITY SCORE</span>
                  <span>{probPct.toFixed(1)}%</span>
                </div>
                <div className="progress-container">
                  <div
                    className={`progress-bar ${probPct > 50 ? 'amber' : 'green'}`}
                    style={{ width: `${probPct}%` }}
                  />
                </div>
              </div>

              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <strong>Image Hash (SHA-256):</strong> <code style={{ color: 'var(--primary-cyan)', fontSize: '0.8rem' }}>{result.image_hash}</code>
              </p>
            </div>
          )}
        </div>
      </div>

      {result && result.features && (
        <div className="glass-card" style={{ marginTop: '24px' }}>
          <h3 className="card-title">Extracted Statistical Image Features (29 Metrics)</h3>
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Feature Metric Name</th>
                  <th>Extracted Value</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(result.features).map(([k, v]) => (
                  <tr key={k}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{k}</td>
                    <td style={{ color: 'var(--primary-cyan)', fontFamily: 'var(--font-mono)' }}>
                      {typeof v === 'number' ? v.toFixed(4) : v}
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>Spatial Statistical Anomaly Metric</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
