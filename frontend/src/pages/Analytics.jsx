import React, { useEffect, useState } from 'react';
import { BarChart3 } from 'lucide-react';

export default function Analytics() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/api/analytics')
      .then(res => res.json())
      .then(d => setData(d))
      .catch(err => console.error(err));
  }, []);

  if (!data) return <div style={{ color: 'var(--text-muted)' }}>Loading analytics...</div>;

  return (
    <div>
      <div className="card-grid">
        {data.metrics && data.metrics.map((m, idx) => (
          <div className="glass-card" key={idx}>
            <h4 style={{ fontFamily: 'var(--font-heading)', color: 'var(--primary-cyan)', fontSize: '1.1rem', marginBottom: '16px' }}>
              {m.model_name || m.Model}
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div className="metric-box">
                <div className="metric-value">{((m.accuracy || m.Accuracy || 0) * 100).toFixed(1)}%</div>
                <div className="metric-label">ACCURACY</div>
              </div>
              <div className="metric-box">
                <div className="metric-value">{((m.precision || m.Precision || 0) * 100).toFixed(1)}%</div>
                <div className="metric-label">PRECISION</div>
              </div>
              <div className="metric-box">
                <div className="metric-value">{((m.recall || m.Recall || 0) * 100).toFixed(1)}%</div>
                <div className="metric-label">RECALL</div>
              </div>
              <div className="metric-box">
                <div className="metric-value">{(m.f1_score || m.F1_Score || 0).toFixed(3)}</div>
                <div className="metric-label">F1-SCORE</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="glass-card">
        <h3 className="card-title">Random Forest Top 10 Feature Importances</h3>
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Feature Metric Name</th>
                <th>Importance Index</th>
              </tr>
            </thead>
            <tbody>
              {data.rf_top_features && data.rf_top_features.map((f, i) => (
                <tr key={i}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{f.feature}</td>
                  <td style={{ color: 'var(--primary-cyan)', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{f.importance.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
