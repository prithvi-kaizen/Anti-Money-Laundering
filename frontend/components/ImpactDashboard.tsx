"use client";
import React, { useEffect, useState } from 'react';
import { TrendingUp } from 'lucide-react';

export default function ImpactDashboard() {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetch('/api/metrics')
      .then(r => r.json()).then(setMetrics).catch(console.error);
  }, []);

  if (!metrics) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>
      LOADING METRICS...
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="panel-header">
        <TrendingUp size={12} style={{ color: 'var(--gold)' }} />
        BUSINESS IMPACT
      </div>
      <div style={{ flex: 1, padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: 8, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
          <div className="metric-card">
            <div style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', marginBottom: 3 }}>TIME / CASE</div>
            <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--green)' }}>{metrics.sentinel_time}</div>
            <div style={{ fontSize: 9, color: 'var(--text-muted)', textDecoration: 'line-through' }}>{metrics.manual_time}</div>
          </div>
          <div className="metric-card">
            <div style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', marginBottom: 3 }}>FP RATE</div>
            <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--green)' }}>{metrics.fp_rate_sentinel}</div>
            <div style={{ fontSize: 9, color: 'var(--text-muted)', textDecoration: 'line-through' }}>{metrics.fp_rate_baseline}</div>
          </div>
        </div>
        <div className="metric-card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 9, color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', marginBottom: 2 }}>ANNUAL SAVINGS</div>
          <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--gold)' }}>{metrics.annual_savings}</div>
        </div>
      </div>
    </div>
  );
}
