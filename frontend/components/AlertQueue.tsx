"use client";

import { useState } from "react";

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

interface Props {
  alerts: Alert[];
  selectedId: string | null;
  onSelect: (alert: Alert) => void;
  onInvestigate: () => void;
  loading: boolean;
}

export default function AlertQueue({ alerts, selectedId, onSelect, onInvestigate, loading }: Props) {
  const [search, setSearch] = useState("");

  const filtered = alerts.filter(
    (a) =>
      a.entity_name.toLowerCase().includes(search.toLowerCase()) ||
      a.alert_id.toLowerCase().includes(search.toLowerCase()) ||
      a.trigger_pattern.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-title-dot" />
          Alert Queue
        </div>
        <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{alerts.length} alerts</span>
      </div>

      <div className="search-box">
        <input
          className="search-input"
          placeholder="Search alerts..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="panel-body">
        <div className="alert-list">
          {filtered.map((alert) => (
            <div
              key={alert.alert_id}
              className={`alert-card ${alert.risk_level.toLowerCase()} ${
                selectedId === alert.alert_id ? "selected" : ""
              }`}
              onClick={() => onSelect(alert)}
            >
              <div className="alert-card-header">
                <div>
                  <div className="alert-id">{alert.alert_id}</div>
                  <div className="alert-entity">{alert.entity_name}</div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
                  <span className={`risk-score ${alert.risk_level.toLowerCase()}`}>
                    {alert.risk_score}
                  </span>
                  <span className={`badge ${alert.risk_level.toLowerCase()}`}>
                    {alert.risk_level}
                  </span>
                </div>
              </div>
              <div className="alert-meta">
                <span className="alert-pattern">
                  {alert.trigger_pattern.replace(/_/g, " ")}
                </span>
                <span className="alert-country">{alert.country}</span>
                <span style={{ fontSize: 10, color: "var(--text-dim)" }}>
                  {alert.status}
                </span>
              </div>

              {selectedId === alert.alert_id && (
                <button
                  className={`btn-investigate ${loading ? "loading" : ""}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onInvestigate();
                  }}
                  disabled={loading}
                >
                  {loading ? (
                    <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
                      <span className="spinner" />
                      Investigating...
                    </span>
                  ) : (
                    "Generate Investigation"
                  )}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
