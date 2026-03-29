"use client";
import React from 'react';
import { ShieldAlert, Shield, AlertTriangle } from 'lucide-react';

const SEVERITY_CLASS: Record<string, string> = {
  CRITICAL: 'critical',
  HIGH: 'high',
  MEDIUM: 'medium',
};

const SEVERITY_BADGE: Record<string, string> = {
  CRITICAL: 'badge-red',
  HIGH: 'badge-orange',
  MEDIUM: 'badge-gold',
};

export default function ComplianceGuardrails({ flags, overrides, isTriaging, triageDone }: any) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="panel-header">
        <Shield size={12} style={{ color: 'var(--gold)' }} />
        COMPLIANCE GUARDRAILS
        {triageDone && flags.length > 0 && (
          <span className="badge badge-red" style={{ marginLeft: 'auto' }}>{flags.length} FLAGS</span>
        )}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '10px 12px' }}>
        {!isTriaging && !triageDone && (
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, color: 'var(--text-muted)' }}>
            <Shield size={32} style={{ opacity: 0.2 }} />
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>AWAITING TRIAGE</span>
          </div>
        )}

        {isTriaging && !triageDone && (
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, color: 'var(--gold)' }}>
            <div className="spinner" style={{ width: 24, height: 24, borderTopColor: 'var(--gold)' }} />
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>EVALUATING RULES...</span>
          </div>
        )}

        {triageDone && (
          <>
            {flags.length === 0 && overrides.length === 0 && (
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '12px', background: 'var(--green-dim)', borderRadius: 6, border: '1px solid var(--green)' }}>
                <Shield size={16} style={{ color: 'var(--green)' }} />
                <span style={{ color: 'var(--green)', fontSize: 12 }}>No compliance flags triggered</span>
              </div>
            )}

            {flags.map((f: any, i: number) => (
              <div key={i} className={`flag-card ${SEVERITY_CLASS[f.severity] || 'medium'}`} style={{ marginBottom: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 5 }}>
                  <AlertTriangle size={12} style={{ color: f.severity === 'CRITICAL' ? 'var(--red)' : 'var(--orange)', flexShrink: 0 }} />
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '0.05em', flex: 1 }}>
                    {f.rule_id.replace(/_/g, ' ')}
                  </span>
                  <span className={`badge ${SEVERITY_BADGE[f.severity] || 'badge-gold'}`}>
                    {f.severity}
                  </span>
                  {f.requires_sar && (
                    <span className="badge badge-red" style={{ fontSize: 9 }}>SAR REQUIRED</span>
                  )}
                </div>
                <p style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 7 }}>{f.description}</p>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: 4, background: 'var(--gold-dim)', border: '1px solid rgba(232,184,75,0.2)', borderRadius: 4, padding: '3px 8px' }}>
                  <span style={{ color: 'var(--gold)', fontSize: 9, fontFamily: 'JetBrains Mono, monospace' }}>
                    → {f.regulatory_citation}
                  </span>
                </div>
              </div>
            ))}

            {overrides.map((o: any, i: number) => (
              <div key={`o-${i}`} style={{ marginTop: 10, background: 'rgba(240,68,56,0.06)', border: '1px solid var(--red)', borderRadius: 6, padding: '10px 12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 6 }}>
                  <ShieldAlert size={13} style={{ color: 'var(--red)' }} />
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, fontWeight: 700, color: 'var(--red)', letterSpacing: '0.06em' }}>
                    GUARDRAIL OVERRIDE ACTIVE
                  </span>
                </div>
                <p style={{ fontSize: 11, color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: 6 }}>{o.reason}</p>
                <div style={{ fontSize: 9, color: 'var(--gold)', fontFamily: 'JetBrains Mono, monospace' }}>
                  {o.regulatory_basis?.join(' · ')}
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
