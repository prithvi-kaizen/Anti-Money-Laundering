"use client";

import { useState, useEffect, useCallback } from "react";
import AlertQueue from "@/components/AlertQueue";
import EntityGraph from "@/components/EntityGraph";
import SARPanel from "@/components/SARPanel";
import AuditLog from "@/components/AuditLog";
import TimingChart from "@/components/TimingChart";

const API = "/api";

interface Alert {
  alert_id: string;
  entity_name: string;
  entity_type: string;
  country: string;
  risk_score: number;
  risk_level: string;
  trigger_pattern: string;
  status: string;
  created_date: string;
  summary: string;
}

interface InvestigationResult {
  sar: any;
  risk_explanation: any;
  graph: any;
  audit_trail: any;
}

export default function Dashboard() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [timing, setTiming] = useState<any>(null);

  useEffect(() => {
    fetch(`${API}/alerts`)
      .then((r) => r.json())
      .then((data) => setAlerts(data.alerts || []))
      .catch(console.error);

    fetch(`${API}/timing`)
      .then((r) => r.json())
      .then(setTiming)
      .catch(console.error);
  }, []);

  const handleSelectAlert = useCallback((alert: Alert) => {
    setSelectedAlert(alert);
    setInvestigation(null);
  }, []);

  const handleInvestigate = useCallback(async () => {
    if (!selectedAlert) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/alerts/${selectedAlert.alert_id}/investigate`, {
        method: "POST",
      });
      const data = await res.json();
      setInvestigation(data);
    } catch (err) {
      console.error("Investigation failed:", err);
    } finally {
      setLoading(false);
    }
  }, [selectedAlert]);

  const criticalCount = alerts.filter((a) => a.risk_level === "CRITICAL").length;
  const highCount = alerts.filter((a) => a.risk_level === "HIGH").length;
  const newCount = alerts.filter((a) => a.status === "NEW").length;

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo">
            <div className="logo-icon">S</div>
            <span className="logo-text">SENTINEL</span>
            <span className="logo-badge">AML</span>
          </div>
        </div>
        <div className="header-stats">
          <div className="header-stat">
            <span className="header-stat-value" style={{ color: "#f87171" }}>
              {criticalCount}
            </span>
            <span className="header-stat-label">Critical</span>
          </div>
          <div className="header-stat">
            <span className="header-stat-value" style={{ color: "#fbbf24" }}>
              {highCount}
            </span>
            <span className="header-stat-label">High</span>
          </div>
          <div className="header-stat">
            <span className="header-stat-value" style={{ color: "#60a5fa" }}>
              {newCount}
            </span>
            <span className="header-stat-label">New</span>
          </div>
          <div className="header-stat">
            <span className="header-stat-value" style={{ color: "#94a3b8" }}>
              {alerts.length}
            </span>
            <span className="header-stat-label">Total</span>
          </div>
        </div>
      </header>

      {/* Left: Alert Queue */}
      <div className="panel sidebar">
        <AlertQueue
          alerts={alerts}
          selectedId={selectedAlert?.alert_id || null}
          onSelect={handleSelectAlert}
          onInvestigate={handleInvestigate}
          loading={loading}
        />
      </div>

      {/* Center: Entity Graph */}
      <div className="panel graph-panel">
        <div className="panel-header">
          <div className="panel-title">
            <span className="panel-title-dot" />
            Entity Graph
          </div>
          {investigation?.graph && (
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
              {investigation.graph.nodes?.length || 0} nodes · {investigation.graph.edges?.length || 0} edges
            </span>
          )}
        </div>
        <EntityGraph graph={investigation?.graph || null} loading={loading} />
        <div className="graph-legend">
          <div className="legend-item">
            <div className="legend-dot" style={{ background: "#c9a84c" }} />
            Entity
          </div>
          <div className="legend-item">
            <div className="legend-dot" style={{ background: "#737380" }} />
            Account
          </div>
          <div className="legend-item">
            <div className="legend-dot" style={{ background: "#e54d4d" }} />
            High Risk
          </div>
          <div className="legend-item">
            <div className="legend-dot" style={{ background: "#4ead7a" }} />
            Normal
          </div>
        </div>
      </div>

      {/* Right: SAR Panel */}
      <div className="panel sar-panel">
        <SARPanel
          sar={investigation?.sar || null}
          risk={investigation?.risk_explanation || null}
          timing={timing}
          loading={loading}
        />
      </div>

      {/* Bottom: Audit Log */}
      <div className="panel audit-panel">
        <AuditLog trail={investigation?.audit_trail || null} loading={loading} />
      </div>
    </div>
  );
}
