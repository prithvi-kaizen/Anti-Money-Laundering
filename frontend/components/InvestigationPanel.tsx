"use client";
import React, { useEffect, useState, useRef } from 'react';
import { FileText, Loader, CheckCircle } from 'lucide-react';

function highlightCitations(text: string) {
  const patterns = [
    /31 CFR \d+\.\d+/g,
    /FATF Recommendation \d+/g,
    /BSA \d+ U\.S\.C\. \d+\([a-z]\)/g,
    /OFAC \d+ CFR Part \d+/g,
    /31 CFR Part \d+/g,
  ];

  const result: React.ReactNode[] = [];
  let i = 0;
  const allMatches: { index: number; end: number; match: string }[] = [];

  patterns.forEach(pattern => {
    pattern.lastIndex = 0;
    let m;
    while ((m = pattern.exec(text)) !== null) {
      allMatches.push({ index: m.index, end: m.index + m[0].length, match: m[0] });
    }
  });

  allMatches.sort((a, b) => a.index - b.index);

  allMatches.forEach((m, idx) => {
    if (m.index < i) return;
    if (m.index > i) result.push(text.slice(i, m.index));
    result.push(<span key={idx} className="citation">{m.match}</span>);
    i = m.end;
  });

  if (i < text.length) result.push(text.slice(i));
  return result;
}

export default function InvestigationPanel({ alertId, shouldStream, investigationResult }: any) {
  const [text, setText] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [done, setDone] = useState(false);
  const bodyRef = useRef<HTMLDivElement>(null);
  const prevAlertId = useRef<string | null>(null);

  useEffect(() => {
    if (alertId !== prevAlertId.current) {
      setText('');
      setDone(false);
      setStreaming(false);
      prevAlertId.current = alertId;
    }
  }, [alertId]);

  useEffect(() => {
    if (!shouldStream || !alertId || done || streaming) return;

    setStreaming(true);
    setText('');

    const controller = new AbortController();

    fetch(`/api/alerts/${alertId}/investigate/stream`, {
      signal: controller.signal,
    }).then(async (res) => {
      const reader = res.body?.getReader();
      if (!reader) { setStreaming(false); setDone(true); return; }
      const decoder = new TextDecoder();
      while (true) {
        const { done: doneReading, value } = await reader.read();
        if (doneReading) break;
        const chunk = decoder.decode(value, { stream: true });
        setText(prev => prev + chunk);
        if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
      }
      setStreaming(false);
      setDone(true);
    }).catch(() => {
      setStreaming(false);
      setDone(true);
    });

    return () => controller.abort();
  }, [shouldStream, alertId]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="panel-header">
        <FileText size={12} style={{ color: 'var(--gold)' }} />
        AI INVESTIGATION STREAM
        <span style={{ marginLeft: 8, fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: 'var(--text-muted)' }}>
          llama-3.3-70b · Groq
        </span>
        <span style={{ marginLeft: 'auto' }}>
          {streaming && <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--gold)' }}><Loader size={11} style={{ animation: 'spin 1s linear infinite' }} />GENERATING...</span>}
          {done && <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--green)' }}><CheckCircle size={11} />COMPLETE</span>}
        </span>
      </div>

      <div ref={bodyRef} style={{ flex: 1, overflowY: 'auto', padding: '16px 18px' }}>
        {!alertId && (
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, color: 'var(--text-muted)' }}>
            <FileText size={32} style={{ opacity: 0.15 }} />
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>SELECT AN ALERT AND RUN TRIAGE</span>
          </div>
        )}
        {alertId && !shouldStream && !text && (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>
            SAR WILL STREAM AFTER TRIAGE
          </div>
        )}
        {text && (
          <div className="stream-text">{highlightCitations(text)}</div>
        )}
        {streaming && (
          <span style={{
            display: 'inline-block',
            width: 2,
            height: 14,
            background: 'var(--gold)',
            marginLeft: 2,
            animation: 'pulse 0.8s infinite',
            verticalAlign: 'text-bottom',
          }} />
        )}
      </div>
    </div>
  );
}
