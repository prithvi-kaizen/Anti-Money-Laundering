"use client";

interface AuditEntry {
  entry_id: string;
  alert_id: string;
  timestamp: string;
  action: string;
  module: string;
  input_summary: string;
  output_summary: string;
  evidence_ids: string[];
  duration_ms: number;
}

interface AuditTrail {
  alert_id: string;
  entries: AuditEntry[];
  total_duration_ms: number;
}

interface Props {
  trail: AuditTrail | null;
  loading: boolean;
}

export default function AuditLog({ trail, loading }: Props) {
  if (loading) {
    return (
      <>
        <div className="panel-header">
          <div className="panel-title">
            <span className="panel-title-dot" />
            Audit Log
          </div>
        </div>
        <div className="panel-body" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div className="loading-text">Recording audit trail...</div>
        </div>
      </>
    );
  }

  return (
    <>
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-title-dot" />
          Audit Log
        </div>
        {trail && (
          <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "'JetBrains Mono'" }}>
            {trail.entries.length} entries · {trail.total_duration_ms}ms total
          </span>
        )}
      </div>
      <div className="panel-body">
        {!trail || trail.entries.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">LOG</div>
            <div className="empty-state-title">No Audit Trail</div>
            <div className="empty-state-text">
              Run an investigation to generate an audit trail of all data retrievals and analyses
            </div>
          </div>
        ) : (
          <>
            {/* Header row */}
            <div
              className="audit-entry"
              style={{
                fontWeight: 700,
                fontSize: 10,
                color: "var(--text-dim)",
                textTransform: "uppercase",
                letterSpacing: "1px",
                borderBottom: "1px solid var(--border-primary)",
                paddingBottom: 10,
                marginBottom: 4,
              }}
            >
              <span>Timestamp</span>
              <span>Action</span>
              <span>Module</span>
              <span>Detail</span>
              <span style={{ textAlign: "right" }}>Duration</span>
            </div>
            <div className="audit-list">
              {trail.entries.map((entry) => (
                <div key={entry.entry_id} className="audit-entry">
                  <span className="audit-timestamp">
                    {new Date(entry.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="audit-action">{entry.action.replace(/_/g, " ")}</span>
                  <span className="audit-module">{entry.module}</span>
                  <span className="audit-detail" title={entry.output_summary}>
                    {entry.output_summary}
                  </span>
                  <span className="audit-duration">
                    {entry.duration_ms > 0 ? `${entry.duration_ms}ms` : "—"}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </>
  );
}
