"use client";

import { useState } from "react";
import TimingChart from "./TimingChart";

interface Props {
  sar: any;
  risk: any;
  timing: any;
  loading: boolean;
}

export default function SARPanel({ sar, risk, timing, loading }: Props) {
  const [view, setView] = useState<"formatted" | "json" | "timing">("formatted");

  if (loading) {
    return (
      <>
        <div className="panel-header">
          <div className="panel-title">
            <span className="panel-title-dot" />
            SAR Report
          </div>
        </div>
        <div className="loading-overlay" style={{ position: "relative", flex: 1 }}>
          <div className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
          <div className="loading-text">Generating SAR report...</div>
        </div>
      </>
    );
  }

  if (!sar) {
    return (
      <>
        <div className="panel-header">
          <div className="panel-title">
            <span className="panel-title-dot" />
            SAR Report
          </div>
        </div>
        <div className="sar-placeholder">
          <div className="empty-state-icon">SAR</div>
          <div style={{ fontSize: 12, color: "var(--text-muted)" }}>No SAR Generated</div>
          <div style={{ fontSize: 11, color: "var(--text-dim)", maxWidth: 220, lineHeight: 1.5 }}>
            Select an alert and run an investigation to generate a structured SAR report
          </div>
        </div>
      </>
    );
  }

  const riskClass = (risk?.risk_level || "medium").toLowerCase();

  return (
    <>
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-title-dot" />
          SAR Report
        </div>
        <div className="view-toggle">
          <button
            className={`view-toggle-btn ${view === "formatted" ? "active" : ""}`}
            onClick={() => setView("formatted")}
          >
            Formatted
          </button>
          <button
            className={`view-toggle-btn ${view === "json" ? "active" : ""}`}
            onClick={() => setView("json")}
          >
            JSON
          </button>
          <button
            className={`view-toggle-btn ${view === "timing" ? "active" : ""}`}
            onClick={() => setView("timing")}
          >
            Timing
          </button>
        </div>
      </div>

      <div className="sar-content">
        {view === "json" ? (
          <div className="json-view">
            <pre>{JSON.stringify(sar, null, 2)}</pre>
          </div>
        ) : view === "timing" ? (
          <TimingChart timing={timing} />
        ) : (
          <>
            {/* SAR ID & Risk Badge */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 11, fontFamily: "'JetBrains Mono'", color: "var(--text-dim)", marginBottom: 6 }}>
                {sar.sar_id} · {new Date(sar.generated_at).toLocaleString()}
              </div>
              <div className={`sar-risk-badge badge ${riskClass}`} style={{ fontSize: 13 }}>
                Risk: {risk?.risk_score || sar.overall_risk_score}/100 — {risk?.risk_level || "N/A"}
                {` · ${((risk?.confidence || sar.overall_confidence) * 100).toFixed(0)}% confidence`}
              </div>
            </div>

            {/* Case Overview */}
            <div className="sar-section">
              <div className="sar-section-title">Case Overview</div>
              <div className="sar-text">{sar.case_overview}</div>
            </div>

            {/* Risk Indicators */}
            {sar.risk_indicators && sar.risk_indicators.length > 0 && (
              <div className="sar-section">
                <div className="sar-section-title">Risk Indicators</div>
                {sar.risk_indicators.map((driver: any, i: number) => (
                  <div key={i} className="risk-driver">
                    <div className="risk-driver-header">
                      <span className="risk-driver-name">{driver.indicator}</span>
                      <span className={`badge ${driver.severity.toLowerCase()}`}>{driver.severity}</span>
                    </div>
                    <div className="risk-driver-text">{driver.description}</div>
                    <div className="citation-confidence">
                      Confidence: {(driver.confidence * 100).toFixed(0)}% · Evidence: {driver.evidence_ids?.join(", ")}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Timeline */}
            {sar.timeline && sar.timeline.length > 0 && (
              <div className="sar-section">
                <div className="sar-section-title">Transaction Timeline</div>
                <div className="timeline">
                  {sar.timeline.slice(0, 12).map((item: any, i: number) => (
                    <div key={i} className={`timeline-item ${item.flagged ? "flagged" : ""}`}>
                      <div className="timeline-date">{new Date(item.date).toLocaleDateString()}</div>
                      <div className="timeline-event">
                        {item.event}
                        {item.pattern && (
                          <span className="alert-pattern" style={{ marginLeft: 6 }}>
                            {item.pattern.replace(/_/g, " ")}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Linked Entities */}
            {sar.linked_entities && sar.linked_entities.length > 0 && (
              <div className="sar-section">
                <div className="sar-section-title">Linked Entities</div>
                {sar.linked_entities.slice(0, 8).map((entity: any, i: number) => (
                  <div key={i} className="linked-entity">
                    <div>
                      <div className="linked-entity-name">{entity.name}</div>
                      <div className="linked-entity-meta">
                        {entity.relationship} · {entity.country}
                      </div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: 13, fontWeight: 600, fontFamily: "'JetBrains Mono'", color: "var(--text-primary)" }}>
                        ${entity.total_amount?.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                      </div>
                      <div className="linked-entity-meta">{entity.transaction_count} txns</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Evidence Citations */}
            {sar.evidence_citations && sar.evidence_citations.length > 0 && (
              <div className="sar-section">
                <div className="sar-section-title">Evidence Citations</div>
                {sar.evidence_citations.map((cite: any, i: number) => (
                  <div key={i} className="citation">
                    <div className="citation-header">
                      <span className="citation-id">{cite.evidence_id}</span>
                      <span className="citation-type">{cite.type}</span>
                    </div>
                    <div className="citation-text">{cite.description}</div>
                    <div className="citation-confidence">
                      Confidence: {(cite.confidence * 100).toFixed(0)}% · Sources: {cite.source_ids?.join(", ")}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Recommended Action */}
            <div className="sar-section">
              <div className="sar-section-title">Recommended Action</div>
              <div className="sar-text" style={{ fontWeight: 500 }}>{sar.recommended_action}</div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
