"use client";

import { useRef, useEffect, useCallback } from "react";

interface GraphNode {
  id: string;
  label: string;
  type: string;
  risk: boolean;
  country: string;
  metadata?: any;
}

interface GraphEdge {
  source: string;
  target: string;
  label: string;
  amount?: number;
  tx_id?: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  alert_id: string;
}

interface SimNode extends GraphNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
}

interface Props {
  graph: GraphData | null;
  loading: boolean;
}

export default function EntityGraph({ graph, loading }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const nodesRef = useRef<SimNode[]>([]);
  const hoveredRef = useRef<SimNode | null>(null);
  const mouseRef = useRef({ x: 0, y: 0 });

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !graph) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    const W = rect.width;
    const H = rect.height;

    const nodes = nodesRef.current;
    const edges = graph.edges;

    // Physics simulation step
    const k = 0.005; // spring constant
    const repulsion = 3000;
    const damping = 0.85;
    const centerForce = 0.01;

    // Repulsion between all nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x;
        const dy = nodes[j].y - nodes[i].y;
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const force = repulsion / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        nodes[i].vx -= fx;
        nodes[i].vy -= fy;
        nodes[j].vx += fx;
        nodes[j].vy += fy;
      }
    }

    // Spring forces along edges
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    for (const edge of edges) {
      const s = nodeMap.get(edge.source);
      const t = nodeMap.get(edge.target);
      if (!s || !t) continue;
      const dx = t.x - s.x;
      const dy = t.y - s.y;
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const force = k * (dist - 120);
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      s.vx += fx;
      s.vy += fy;
      t.vx -= fx;
      t.vy -= fy;
    }

    // Center gravity + update positions
    for (const node of nodes) {
      node.vx += (W / 2 - node.x) * centerForce;
      node.vy += (H / 2 - node.y) * centerForce;
      node.vx *= damping;
      node.vy *= damping;
      node.x += node.vx;
      node.y += node.vy;
      node.x = Math.max(node.radius, Math.min(W - node.radius, node.x));
      node.y = Math.max(node.radius, Math.min(H - node.radius, node.y));
    }

    // Clear
    ctx.fillStyle = "#0e0e10";
    ctx.fillRect(0, 0, W, H);

    // Draw grid
    ctx.strokeStyle = "rgba(39, 39, 42, 0.3)";
    ctx.lineWidth = 0.5;
    for (let x = 0; x < W; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, H);
      ctx.stroke();
    }
    for (let y = 0; y < H; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }

    // Draw edges
    for (const edge of edges) {
      const s = nodeMap.get(edge.source);
      const t = nodeMap.get(edge.target);
      if (!s || !t) continue;

      const isSuspicious = edge.label.includes("$") && parseFloat(edge.label.replace(/[$,]/g, "")) > 50000;

      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(t.x, t.y);
      ctx.strokeStyle = isSuspicious
        ? "rgba(229, 77, 77, 0.35)"
        : "rgba(201, 168, 76, 0.15)";
      ctx.lineWidth = isSuspicious ? 1.5 : 0.8;
      ctx.stroke();

      // Arrow
      const angle = Math.atan2(t.y - s.y, t.x - s.x);
      const midX = (s.x + t.x) / 2;
      const midY = (s.y + t.y) / 2;
      const arrowSize = 6;
      ctx.beginPath();
      ctx.moveTo(midX + arrowSize * Math.cos(angle), midY + arrowSize * Math.sin(angle));
      ctx.lineTo(
        midX - arrowSize * Math.cos(angle - Math.PI / 6),
        midY - arrowSize * Math.sin(angle - Math.PI / 6)
      );
      ctx.lineTo(
        midX - arrowSize * Math.cos(angle + Math.PI / 6),
        midY - arrowSize * Math.sin(angle + Math.PI / 6)
      );
      ctx.closePath();
      ctx.fillStyle = isSuspicious ? "rgba(229, 77, 77, 0.4)" : "rgba(201, 168, 76, 0.2)";
      ctx.fill();

      // Edge label
      if (edge.label) {
        ctx.font = "9px 'JetBrains Mono'";
        ctx.fillStyle = "rgba(113, 113, 122, 0.6)";
        ctx.textAlign = "center";
        ctx.fillText(edge.label, midX, midY - 6);
      }
    }

    // Draw nodes
    for (const node of nodes) {
      const isHovered = hoveredRef.current?.id === node.id;
      const isPrimary = node.metadata?.is_primary;

      // Glow effect for risk nodes
      if (node.risk) {
        const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.radius * 3);
        gradient.addColorStop(0, "rgba(229, 77, 77, 0.12)");
        gradient.addColorStop(1, "rgba(229, 77, 77, 0)");
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius * 3, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
      }

      // Node circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius + (isHovered ? 2 : 0), 0, Math.PI * 2);

      if (node.risk) {
        ctx.fillStyle = isPrimary ? "#d43d3d" : "#e54d4d";
      } else if (node.type === "account") {
        ctx.fillStyle = "#737380";
      } else {
        ctx.fillStyle = isPrimary ? "#b89840" : "#c9a84c";
      }
      ctx.fill();

      // Border
      ctx.strokeStyle = isHovered ? "#e8e8ec" : isPrimary ? "rgba(201,168,76,0.5)" : "rgba(255,255,255,0.06)";
      ctx.lineWidth = isPrimary ? 1.5 : 0.8;
      ctx.stroke();

      // Label
      ctx.font = `${isHovered ? "bold " : ""}10px Inter`;
      ctx.fillStyle = isHovered ? "#e8e8ec" : "#71717a";
      ctx.textAlign = "center";
      const labelStr = node.label.length > 18 ? node.label.substring(0, 16) + "…" : node.label;
      ctx.fillText(labelStr, node.x, node.y + node.radius + 14);
    }

    // Tooltip for hovered node
    if (hoveredRef.current) {
      const node = hoveredRef.current;
      const tooltipW = 180;
      const tooltipH = 60;
      let tx = node.x + 15;
      let ty = node.y - tooltipH - 5;
      if (tx + tooltipW > W) tx = node.x - tooltipW - 15;
      if (ty < 0) ty = node.y + 20;

      ctx.fillStyle = "rgba(17, 17, 19, 0.95)";
      ctx.strokeStyle = "rgba(201, 168, 76, 0.2)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(tx, ty, tooltipW, tooltipH, 6);
      ctx.fill();
      ctx.stroke();

      ctx.font = "bold 11px Inter";
      ctx.fillStyle = "#e8e8ec";
      ctx.textAlign = "left";
      ctx.fillText(node.label, tx + 10, ty + 18);

      ctx.font = "10px Inter";
      ctx.fillStyle = "#a1a1aa";
      ctx.fillText(`Type: ${node.type} | ${node.country || "N/A"}`, tx + 10, ty + 34);
      ctx.fillText(node.risk ? "High Risk" : "Normal", tx + 10, ty + 50);
    }

    animRef.current = requestAnimationFrame(draw);
  }, [graph]);

  useEffect(() => {
    if (!graph || !graph.nodes.length) {
      if (animRef.current) cancelAnimationFrame(animRef.current);
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const W = rect.width || 600;
    const H = rect.height || 400;

    // Initialize simulation nodes
    nodesRef.current = graph.nodes.map((n, i) => ({
      ...n,
      x: W / 2 + (Math.random() - 0.5) * 200,
      y: H / 2 + (Math.random() - 0.5) * 200,
      vx: 0,
      vy: 0,
      radius: n.type === "account" ? 8 : n.metadata?.is_primary ? 16 : 12,
    }));

    hoveredRef.current = null;
    animRef.current = requestAnimationFrame(draw);

    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [graph, draw]);

  // Mouse move handler for hover detection
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      mouseRef.current = { x: mx, y: my };

      let found: SimNode | null = null;
      for (const node of nodesRef.current) {
        const dx = mx - node.x;
        const dy = my - node.y;
        if (Math.sqrt(dx * dx + dy * dy) < node.radius + 5) {
          found = node;
          break;
        }
      }
      hoveredRef.current = found;
      canvas.style.cursor = found ? "pointer" : "default";
    };

    canvas.addEventListener("mousemove", handleMouseMove);
    return () => canvas.removeEventListener("mousemove", handleMouseMove);
  }, []);

  if (!graph) {
    return (
      <div className="graph-canvas-container">
        {loading ? (
          <div className="loading-overlay">
            <div className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
            <div className="loading-text">Building entity graph...</div>
          </div>
        ) : (
          <div className="graph-placeholder">
            <div className="graph-placeholder-icon" style={{ fontSize: 12, letterSpacing: 2, fontWeight: 600 }}>GRAPH</div>
            <div className="graph-placeholder-text">
              Select an alert and click Generate Investigation
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="graph-canvas-container">
      <canvas ref={canvasRef} className="graph-canvas" />
    </div>
  );
}
