import React, { useEffect, useState } from 'react';
import { Trash2 } from 'lucide-react';

export default function AuditLogs({ showToast }) {
  const [records, setRecords] = useState([]);

  const loadLogs = () => {
    fetch('/api/audit-logs')
      .then(res => res.json())
      .then(d => setRecords(d.records || []))
      .catch(err => console.error(err));
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const handleClearLogs = async () => {
    try {
      const res = await fetch('/api/audit-logs', { method: 'DELETE' });
      if (res.ok) {
        showToast('Audit logs cleared!', 'success');
        loadLogs();
      }
    } catch (err) {
      showToast('Failed to clear logs', 'error');
    }
  };

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 className="card-title" style={{ marginBottom: 0 }}>SQLite Audit Log History</h3>
        <button className="btn btn-outline" onClick={handleClearLogs} style={{ color: 'var(--danger-red)', borderColor: 'var(--danger-red)' }}>
          <Trash2 size={16} /> Clear Audit Logs
        </button>
      </div>

      <div className="data-table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Timestamp (UTC)</th>
              <th>Operation</th>
              <th>Input File</th>
              <th>Image Hash</th>
              <th>Payload Hash</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {records.length > 0 ? (
              records.map(r => (
                <tr key={r.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{r.id}</td>
                  <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{r.timestamp}</td>
                  <td>
                    <span style={{ background: 'rgba(0, 242, 254, 0.1)', color: 'var(--primary-cyan)', padding: '4px 10px', borderRadius: '6px', fontWeight: 600, fontSize: '0.8rem' }}>
                      {r.operation_type}
                    </span>
                  </td>
                  <td>{r.input_filename || '-'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>{r.image_hash ? r.image_hash.substring(0, 16) + '...' : '-'}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>{r.payload_hash ? r.payload_hash.substring(0, 16) + '...' : '-'}</td>
                  <td><span style={{ color: 'var(--success-green)', fontWeight: 700 }}>{r.status}</span></td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>No audit records found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
