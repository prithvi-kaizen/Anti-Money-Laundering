"use client";
import React, { useEffect, useState } from 'react';
import { ClipboardList } from 'lucide-react';

export default function AuditTrail({ alertId, isTriageDone }: any) {
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    if (!alertId || !isTriageDone) return;
    fetch(`http://localhost:8000/alerts/${alertId}/audit`)
      .then(r => r.json())
      .then(setLogs)
      .catch(console.error);
  }, [alertId, isTriageDone]);

  useEffect(() => {
    setLogs([]);
  }, [alertId]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="panel-header">
        <ClipboardList size={12} style={{ color: 'var(--gold)' }} />
        AUDIT TRAIL
        {logs.length > 0 && (
          <span style={{ marginLeft: 'auto', fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: 'var(--green)' }}>
            {logs.length} ENTRIES
          </span>
        )}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 12px' }}>
        {!alertId && (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>
            NO CASE SELECTED
          </div>
        )}
        {alertId && !isTriageDone && (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>
            AWAITING TRIAGE
          </div>
        )}
        {logs.map((log: any, i: number) => (
          <div key={i} className="audit-row">
            <div style={{ color: 'var(--text-muted)', marginBottom: 3, fontSize: 9 }}>
              {new Date(log.timestamp).toISOString().replace('T', ' ').slice(0, 19)} UTC
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3 }}>
              <span style={{ color: 'var(--gold)', fontWeight: 600, letterSpacing: '0.06em' }}>
                {log.step?.toUpperCase() || 'STEP'}
              </span>
              <span className={`badge ${log.decision?.includes('FILE_SAR') || log.decision?.includes('OVERRIDE') ? 'badge-red' : 'badge-green'}`}
                style={{ fontSize: 8 }}>
                {log.decision}
              </span>
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: 9 }} title={`Hash: ${log.output_hash}`}>
              HASH: {log.output_hash?.substring(0, 20)}…
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
