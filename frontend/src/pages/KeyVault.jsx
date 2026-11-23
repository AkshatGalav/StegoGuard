import React, { useState, useEffect } from 'react';
import { Key, Shield, Trash2, Plus, Copy, Download } from 'lucide-react';

export default function KeyVault({ token, showToast }) {
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(true);

  // New key form state
  const [keyName, setKeyName] = useState('');
  const [keyType, setKeyType] = useState('AES-256');
  const [keyData, setKeyData] = useState('');

  const loadVaultKeys = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch('/api/vault/keys', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (res.ok) {
        setKeys(data.keys || []);
      }
    } catch (err) {
      console.error('Failed to load vault keys', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVaultKeys();
  }, [token]);

  const handleSaveKey = async (e) => {
    e.preventDefault();
    if (!keyName || !keyData) return showToast('Please enter key name and key content!', 'error');

    const formData = new FormData();
    formData.append('key_name', keyName);
    formData.append('key_type', keyType);
    formData.append('key_data', keyData);

    try {
      const res = await fetch('/api/vault/keys', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        showToast('Key saved to your private vault!', 'success');
        setKeyName('');
        setKeyData('');
        loadVaultKeys();
      } else {
        showToast(data.detail || 'Failed to save key', 'error');
      }
    } catch (err) {
      showToast('Error saving key to vault', 'error');
    }
  };

  const handleDeleteKey = async (keyId) => {
    try {
      const res = await fetch(`/api/vault/keys/${keyId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        showToast('Key removed from vault!', 'success');
        loadVaultKeys();
      }
    } catch (err) {
      showToast('Failed to delete key', 'error');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showToast('Copied to clipboard!', 'success');
  };

  return (
    <div>
      <div className="card-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        {/* Save Key to Vault */}
        <div className="glass-card">
          <h3 className="card-title"><Plus size={20} style={{ color: 'var(--primary-lime)' }} /> Save Key to Vault</h3>
          <form onSubmit={handleSaveKey}>
            <div className="form-group">
              <label className="form-label">Key Name / Identifier</label>
              <input
                type="text"
                className="form-control"
                value={keyName}
                onChange={(e) => setKeyName(e.target.value)}
                placeholder="e.g. Master Stego AES Key"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Key Type</label>
              <select className="form-control" value={keyType} onChange={(e) => setKeyType(e.target.value)}>
                <option value="AES-256">AES-256 Symmetric Key (Base64)</option>
                <option value="RSA-2048-PRIVATE">RSA-2048 Private Key (PEM)</option>
                <option value="RSA-2048-PUBLIC">RSA-2048 Public Key (PEM)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Key Content / Data</label>
              <textarea
                className="form-control code-font"
                value={keyData}
                onChange={(e) => setKeyData(e.target.value)}
                placeholder="Paste key string here..."
                required
              />
            </div>

            <button className="btn btn-primary" type="submit" style={{ width: '100%' }}>
              <Shield size={18} /> Save Key to Private Vault
            </button>
          </form>
        </div>

        {/* Vault Summary Status */}
        <div className="glass-card">
          <h3 className="card-title"><Key size={20} style={{ color: 'var(--primary-cyan)' }} /> Vault Summary</h3>
          <div className="card-grid" style={{ gridTemplateColumns: '1fr 1fr', marginBottom: '16px' }}>
            <div className="metric-box">
              <div className="metric-value">{keys.length}</div>
              <div className="metric-label">STORED KEYS</div>
            </div>
            <div className="metric-box">
              <div className="metric-value">AES / RSA</div>
              <div className="metric-label">SUPPORTED FORMATS</div>
            </div>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', lineHeight: '1.6' }}>
            Your cryptographic keys are isolated strictly under your account. Never share your private keys or master passphrases.
          </p>
        </div>
      </div>

      {/* Keys List */}
      <div className="glass-card" style={{ marginTop: '24px' }}>
        <h3 className="card-title">Saved Cryptographic Keys ({keys.length})</h3>
        {loading ? (
          <div style={{ color: 'var(--text-muted)' }}>Loading keys...</div>
        ) : keys.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', padding: '24px', textAlign: 'center' }}>
            No keys saved in your vault yet. Use the form above to store your AES or RSA keys!
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Key Name</th>
                  <th>Type</th>
                  <th>Key Data</th>
                  <th>Date Saved</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {keys.map((k) => (
                  <tr key={k.id}>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{k.id}</td>
                    <td style={{ fontWeight: 700 }}>{k.key_name}</td>
                    <td>
                      <span style={{ background: 'rgba(0, 255, 136, 0.12)', color: 'var(--primary-lime)', padding: '4px 10px', borderRadius: '8px', fontSize: '0.8rem', fontWeight: 700 }}>
                        {k.key_type}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', maxWdith: '300px', wordBreak: 'break-all' }}>
                      {k.key_data.length > 40 ? k.key_data.substring(0, 40) + '...' : k.key_data}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{k.created_at.substring(0, 10)}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button className="btn-copy" style={{ position: 'static', transform: 'none' }} onClick={() => copyToClipboard(k.key_data)}>
                          <Copy size={14} />
                        </button>
                        <button className="btn-copy" style={{ position: 'static', transform: 'none', color: 'var(--danger-red)' }} onClick={() => handleDeleteKey(k.id)}>
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
