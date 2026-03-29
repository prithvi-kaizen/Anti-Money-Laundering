"use client";
import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';

export default function AlertQueue({ alerts, onSelectAlert, selectedId }: any) {
  const getSeverityClass = (sev: string) => sev === 'CRITICAL' ? 'badge-red' : 'badge-orange';
  const getIcon = (sev: string) => sev === 'CRITICAL'
    ? <AlertTriangle size={11} style={{ color: 'var(--red)' }} />
    : <Info size={11} style={{ color: 'var(--orange)' }} />;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden', flex: 1 }}>
      <div className="panel-header">
        <AlertTriangle size={12} style={{ color: 'var(--gold)' }} />
        ALERT QUEUE
        <span style={{ marginLeft: 'auto', background: 'var(--red-dim)', color: 'var(--red)', border: '1px solid var(--red)', borderRadius: 4, padding: '1px 7px', fontSize: 9, fontWeight: 700 }}>
          {alerts.length} OPEN
        </span>
      </div>
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {alerts.map((alert: any) => (
          <div
            key={alert.id}
            className={`alert-card ${selectedId === alert.id ? 'active' : ''}`}
            onClick={() => onSelectAlert(alert)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
              {getIcon(alert.severity)}
              <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, fontWeight: 600, color: 'var(--text-primary)', letterSpacing: '0.04em' }}>
                {alert.rule_triggered}
              </span>
              <span className={`badge ${getSeverityClass(alert.severity)}`} style={{ marginLeft: 'auto' }}>
                {alert.severity}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--text-muted)' }}>
              <span>Entity: <span style={{ color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>{alert.entity_id}</span></span>
              <span style={{ color: 'var(--gold)', fontFamily: 'JetBrains Mono, monospace' }}>{alert.status}</span>
            </div>
          </div>
        ))}
        {alerts.length === 0 && (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 12 }}>
            Loading alerts...
          </div>
        )}
      </div>
    </div>
  );
}
