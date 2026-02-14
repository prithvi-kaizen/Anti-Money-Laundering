"use client";

import { useEffect, useState } from "react";

interface Props {
  timing: any;
}

export default function TimingChart({ timing }: Props) {
  const [animatedWidth, setAnimatedWidth] = useState({ manual: 0, sentinel: 0 });

  useEffect(() => {
    if (!timing) return;
    const timer = setTimeout(() => {
      setAnimatedWidth({
        manual: 100,
        sentinel: (timing.sentinel_avg_minutes / timing.manual_avg_minutes) * 100,
      });
    }, 100);
    return () => clearTimeout(timer);
  }, [timing]);

  if (!timing) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">T</div>
        <div className="empty-state-title">Loading timing data...</div>
      </div>
    );
  }

  return (
    <div className="timing-chart">
      <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", marginBottom: 4 }}>
        Investigation Time Comparison
      </div>
      <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 16 }}>
        Based on {timing.sample_size} simulated investigations
      </div>

      <div className="timing-bars">
        <div className="timing-bar-row">
          <span className="timing-label">Manual</span>
          <div className="timing-bar-container">
            <div
              className="timing-bar manual"
              style={{ width: `${animatedWidth.manual}%` }}
            >
              {timing.manual_avg_minutes.toFixed(0)} min
            </div>
          </div>
        </div>

        <div className="timing-bar-row">
          <span className="timing-label">Sentinel</span>
          <div className="timing-bar-container">
            <div
              className="timing-bar sentinel"
              style={{ width: `${animatedWidth.sentinel}%` }}
            >
              {timing.sentinel_avg_minutes.toFixed(0)} min
            </div>
          </div>
        </div>
      </div>

      <div className="timing-reduction">
        <span className="timing-reduction-value">↓ {timing.reduction_percent.toFixed(0)}%</span>
        <span className="timing-reduction-label">reduction in investigation time</span>
      </div>
    </div>
  );
}
