"use client";
import React, { useState, useEffect, useRef } from 'react';
import AlertQueue from '@/components/AlertQueue';
import EntityGraph from '@/components/EntityGraph';
import InvestigationPanel from '@/components/InvestigationPanel';
import ComplianceGuardrails from '@/components/ComplianceGuardrails';
import ImpactDashboard from '@/components/ImpactDashboard';
import AuditTrail from '@/components/AuditTrail';
import { Activity, Shield, AlertTriangle } from 'lucide-react';

export default function Dashboard() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<any>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [isTriaging, setIsTriaging] = useState(false);
  const [triageDone, setTriageDone] = useState(false);
  const [flags, setFlags] = useState<any[]>([]);
  const [overrides, setOverrides] = useState<any[]>([]);
  const investigationResult = useRef<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/alerts')
      .then(r => r.json()).then(setAlerts).catch(console.error);
  }, []);

  const handleSelectAlert = (alert: any) => {
    setSelectedAlert(alert);
    setTriageDone(false);
    setIsTriaging(false);
    setFlags([]);
    setOverrides([]);
    investigationResult.current = null;
    fetch(`http://localhost:8000/alerts/${alert.id}/graph`)
      .then(r => r.json()).then(setGraphData).catch(console.error);
  };

  const startTriage = async () => {
    if (!selectedAlert || isTriaging) return;
    setIsTriaging(true);
    setTriageDone(false);
    try {
      const res = await fetch(`http://localhost:8000/alerts/${selectedAlert.id}/investigate`, { method: 'POST' });
      const data = await res.json();
      setFlags(data.compliance_flags || []);
      setOverrides(data.guardrail_overrides || []);
      investigationResult.current = data;
      setTriageDone(true);
    } catch (e) {
      console.error(e);
      setTriageDone(true);
    }
  };

  const sarRecommended = flags.some(f => f.requires_sar) || overrides.length > 0;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '300px 1fr',
      gridTemplateRows: '52px 1fr',
      height: '100vh',
      width: '100vw',
      gap: '0',
      background: 'var(--bg-base)',
      overflow: 'hidden',
    }}>
      {/* ── TOP HEADER ── */}
      <div style={{
        gridColumn: '1 / -1',
        background: 'var(--bg-panel)',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 16px',
        gap: '16px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'var(--gold-dim)', border: '1px solid rgba(232,184,75,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'var(--gold)',
          }}>
            <Activity size={16} />
          </div>
          <div>
            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, fontSize: 13, letterSpacing: '0.15em', color: '#fff' }}>
              SENTINEL_v2
            </div>
            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: 'var(--gold)', letterSpacing: '0.2em' }}>
              AML INVESTIGATION PLATFORM
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px', marginLeft: '24px' }}>
          <span className="badge badge-green"><span className="pulse-dot" style={{ width: 5, height: 5 }} />LIVE</span>
          <span className="badge badge-blue">FATF COMPLIANT</span>
          <span className="badge badge-gold">FINCEN READY</span>
        </div>

        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '20px' }}>
          {selectedAlert && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: 'var(--text-muted)' }}>
                ACTIVE CASE
              </div>
              <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: 'var(--text-primary)', fontWeight: 600 }}>
                {selectedAlert.rule_triggered} · {selectedAlert.entity_id}
              </div>
              <span className={`badge ${selectedAlert.severity === 'CRITICAL' ? 'badge-red' : 'badge-orange'}`}>
                {selectedAlert.severity}
              </span>
              {sarRecommended && triageDone && (
                <span className="badge badge-red" style={{ animation: 'pulse 1.5s infinite' }}>⚠ FILE SAR</span>
              )}
            </div>
          )}
          {!selectedAlert && (
            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: 'var(--text-muted)' }}>
              SELECT ALERT TO BEGIN
            </div>
          )}
        </div>
      </div>

      {/* ── LEFT SIDEBAR ── */}
      <div style={{
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        background: 'var(--bg-panel)',
      }}>
        <AlertQueue alerts={alerts} onSelectAlert={handleSelectAlert} selectedId={selectedAlert?.id} />
        <div style={{ borderTop: '1px solid var(--border)', flexShrink: 0, height: '200px', overflow: 'hidden' }}>
          <ImpactDashboard />
        </div>
      </div>

      {/* ── MAIN CONTENT GRID ── */}
      <div style={{
        display: 'grid',
        gridTemplateRows: '1fr 1fr',
        gap: '1px',
        background: 'var(--border)',
        overflow: 'hidden',
      }}>
        {/* Row 1: Graph + Guardrails */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '1px', background: 'var(--border)', overflow: 'hidden' }}>
          {/* Entity Graph */}
          <div style={{ background: 'var(--bg-base)', overflow: 'hidden', position: 'relative' }}>
            <EntityGraph graphData={graphData} />
            {selectedAlert && !isTriaging && !triageDone && (
              <div style={{ position: 'absolute', bottom: 20, left: '50%', transform: 'translateX(-50%)' }}>
                <button className="triage-btn" onClick={startTriage}>
                  <Shield size={14} />
                  INITIALIZE TRIAGE
                </button>
              </div>
            )}
            {isTriaging && !triageDone && (
              <div style={{ position: 'absolute', bottom: 20, left: '50%', transform: 'translateX(-50%)', display: 'flex', alignItems: 'center', gap: 8, color: 'var(--gold)', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}>
                <div className="spinner" /> ANALYZING...
              </div>
            )}
          </div>

          {/* Compliance Guardrails */}
          <div style={{ background: 'var(--bg-base)', overflow: 'hidden' }}>
            <ComplianceGuardrails flags={flags} overrides={overrides} isTriaging={isTriaging} triageDone={triageDone} />
          </div>
        </div>

        {/* Row 2: Investigation Stream + Audit Trail */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '1px', background: 'var(--border)', overflow: 'hidden' }}>
          <div style={{ background: 'var(--bg-base)', overflow: 'hidden' }}>
            <InvestigationPanel
              alertId={selectedAlert?.id}
              shouldStream={triageDone}
              investigationResult={investigationResult.current}
            />
          </div>
          <div style={{ background: 'var(--bg-base)', overflow: 'hidden' }}>
            <AuditTrail alertId={selectedAlert?.id} isTriageDone={triageDone} />
          </div>
        </div>
      </div>
    </div>
  );
}
