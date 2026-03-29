"use client";
import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { Share2, AlertTriangle } from 'lucide-react';

interface GraphNode {
  id: string;
  name?: string;
  type?: string;
  risk_weight?: number;
  is_sdn?: boolean;
  is_shell_suspect?: boolean;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  amount?: number;
  tx_type?: string;
}

export default function EntityGraph({ graphData }: { graphData: any }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; node: GraphNode } | null>(null);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const rawNodes: GraphNode[] = (graphData?.nodes ?? []).map((d: any) => ({ ...d }));
    const rawLinks: GraphLink[] = (graphData?.links ?? []).map((d: any) => ({
      source: typeof d.source === 'object' ? d.source.id : String(d.source),
      target: typeof d.target === 'object' ? d.target.id : String(d.target),
      amount: d.amount ?? 0,
      tx_type: d.tx_type ?? 'wire',
    }));

    if (rawNodes.length === 0) return;

    const { width, height } = containerRef.current.getBoundingClientRect();
    const W = width || 700;
    const H = height || 400;

    svg.attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H);

    // ── DEFS ──
    const defs = svg.append('defs');

    // Glow filter
    const glowFilter = defs.append('filter').attr('id', 'node-glow').attr('x', '-50%').attr('y', '-50%').attr('width', '200%').attr('height', '200%');
    glowFilter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'blur');
    const glowMerge = glowFilter.append('feMerge');
    glowMerge.append('feMergeNode').attr('in', 'blur');
    glowMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Arrow marker
    defs.append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 26)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 5)
      .attr('markerHeight', 5)
      .append('path')
      .attr('d', 'M 0,-5 L 10,0 L 0,5')
      .attr('fill', '#334155');

    // Link gradient
    const linkGrad = defs.append('linearGradient')
      .attr('id', 'link-grad')
      .attr('gradientUnits', 'userSpaceOnUse');
    linkGrad.append('stop').attr('offset', '0%').attr('stop-color', '#1e3a5f');
    linkGrad.append('stop').attr('offset', '100%').attr('stop-color', '#2e90fa').attr('stop-opacity', 0.3);

    // ── SIMULATION ──
    const simulation = d3.forceSimulation<GraphNode>(rawNodes)
      .force('link', d3.forceLink<GraphNode, GraphLink>(rawLinks)
        .id((d) => d.id)
        .distance(d => {
          const link = d as any;
          const amt = link.amount ?? 0;
          return Math.max(80, 160 - Math.log(amt + 1) * 8);
        })
        .strength(0.5))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(W / 2, H / 2))
      .force('collision', d3.forceCollide<GraphNode>().radius(d => (d.type === 'company' ? 28 : 22)))
      .force('x', d3.forceX(W / 2).strength(0.05))
      .force('y', d3.forceY(H / 2).strength(0.05));

    // ── LINKS ──
    const maxAmt = d3.max(rawLinks, (d: any) => d.amount as number) || 1;
    const strokeScale = d3.scaleLog().domain([1, maxAmt + 1]).range([1, 5]).clamp(true);

    const linkSel = svg.append('g').attr('class', 'links')
      .selectAll('line')
      .data(rawLinks)
      .join('line')
      .attr('stroke', '#1e3a5f')
      .attr('stroke-width', (d: any) => strokeScale(d.amount + 1))
      .attr('stroke-opacity', 0.7)
      .attr('marker-end', 'url(#arrowhead)');

    // Amount labels on links
    const linkLabelSel = svg.append('g').attr('class', 'link-labels')
      .selectAll('text')
      .data(rawLinks)
      .join('text')
      .attr('text-anchor', 'middle')
      .attr('font-size', '8')
      .attr('font-family', 'JetBrains Mono, monospace')
      .attr('fill', '#334155')
      .text((d: any) => d.amount > 0 ? `$${(d.amount / 1000).toFixed(0)}k` : '');

    // ── NODES ──
    const nodeSel = svg.append('g').attr('class', 'nodes')
      .selectAll<SVGGElement, GraphNode>('g')
      .data(rawNodes)
      .join('g')
      .attr('cursor', 'pointer')
      .call(
        d3.drag<SVGGElement, GraphNode>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
          })
          .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
          })
      )
      .on('mouseenter', (event, d) => {
        const rect = containerRef.current!.getBoundingClientRect();
        setTooltip({ x: event.clientX - rect.left + 12, y: event.clientY - rect.top - 10, node: d });
      })
      .on('mouseleave', () => setTooltip(null));

    // Node circles
    const getNodeColor = (d: GraphNode) => {
      if (d.is_sdn) return '#f04438';
      if (d.type === 'company') return '#1e3a5f';
      if (d.risk_weight! > 0) return '#431407';
      return '#0f1e36';
    };

    const getNodeStroke = (d: GraphNode) => {
      if (d.is_sdn) return '#f04438';
      if (d.is_shell_suspect) return '#f79009';
      if (d.risk_weight! > 0) return '#f79009';
      if (d.type === 'company') return '#2e90fa';
      return '#1e3a5f';
    };

    const getRadius = (d: GraphNode) => d.type === 'company' ? 22 : 16;

    nodeSel.append('circle')
      .attr('r', d => getRadius(d) + 4)
      .attr('fill', d => getNodeStroke(d))
      .attr('opacity', 0.08);

    nodeSel.append('circle')
      .attr('r', getRadius)
      .attr('fill', getNodeColor)
      .attr('stroke', getNodeStroke)
      .attr('stroke-width', d => (d.is_sdn || d.is_shell_suspect) ? 2 : 1)
      .attr('stroke-dasharray', d => d.is_shell_suspect ? '4,3' : 'none')
      .attr('filter', d => d.is_sdn ? 'url(#node-glow)' : 'none');

    // Icon inside node
    nodeSel.append('text')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-size', d => d.type === 'company' ? '14' : '11')
      .attr('fill', d => d.is_sdn ? '#fca5a5' : '#94a3b8')
      .text(d => d.type === 'company' ? '🏢' : '👤');

    // Name label below
    nodeSel.append('text')
      .attr('text-anchor', 'middle')
      .attr('y', d => getRadius(d) + 14)
      .attr('font-size', '9')
      .attr('font-family', 'JetBrains Mono, monospace')
      .attr('fill', '#64748b')
      .text(d => (d.name || d.id).slice(0, 14));

    // SDN badge
    nodeSel.filter(d => d.is_sdn!)
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('y', d => -(getRadius(d) + 8))
      .attr('font-size', '8')
      .attr('font-family', 'JetBrains Mono, monospace')
      .attr('fill', '#f04438')
      .text('⚠ SDN');

    // ── TICK ──
    simulation.on('tick', () => {
      linkSel
        .attr('x1', (d: any) => (d.source as GraphNode).x ?? 0)
        .attr('y1', (d: any) => (d.source as GraphNode).y ?? 0)
        .attr('x2', (d: any) => (d.target as GraphNode).x ?? 0)
        .attr('y2', (d: any) => (d.target as GraphNode).y ?? 0);

      linkLabelSel
        .attr('x', (d: any) => (((d.source as GraphNode).x ?? 0) + ((d.target as GraphNode).x ?? 0)) / 2)
        .attr('y', (d: any) => (((d.source as GraphNode).y ?? 0) + ((d.target as GraphNode).y ?? 0)) / 2 - 5);

      nodeSel.attr('transform', d => `translate(${d.x ?? 0},${d.y ?? 0})`);
    });

    // Run some ticks before showing to avoid initial explosion
    simulation.tick(20);

    return () => { simulation.stop(); };
  }, [graphData]);

  const hasNodes = graphData?.nodes?.length > 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
      <div className="panel-header">
        <Share2 size={12} style={{ color: 'var(--gold)' }} />
        ENTITY RELATIONSHIP GRAPH
        {hasNodes && (
          <span style={{ marginLeft: 8, fontFamily: 'JetBrains Mono, monospace', fontSize: 9, color: 'var(--text-muted)' }}>
            {graphData.nodes.length} NODES · {graphData.links?.length ?? 0} EDGES
          </span>
        )}
        {hasNodes && graphData.nodes.some((n: any) => n.is_sdn) && (
          <span className="badge badge-red" style={{ marginLeft: 'auto', fontSize: 9 }}>⚠ SDN HIT</span>
        )}
        {hasNodes && graphData.nodes.some((n: any) => n.is_shell_suspect) && (
          <span className="badge badge-orange" style={{ marginLeft: 'auto', fontSize: 9 }}>SHELL DETECTED</span>
        )}
      </div>

      <div ref={containerRef} style={{ flex: 1, position: 'relative', overflow: 'hidden', background: 'radial-gradient(ellipse at 50% 50%, #0d1829 0%, var(--bg-base) 80%)' }}>
        {!hasNodes && (
          <div style={{
            position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center', gap: 12, color: 'var(--text-muted)',
          }}>
            <Share2 size={32} style={{ opacity: 0.15 }} />
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>SELECT AN ALERT TO VIEW ENTITY GRAPH</span>
          </div>
        )}
        <svg ref={svgRef} style={{ width: '100%', height: '100%', display: 'block' }} />

        {/* Tooltip */}
        {tooltip && (
          <div style={{
            position: 'absolute',
            left: tooltip.x, top: tooltip.y,
            background: 'var(--bg-panel)',
            border: '1px solid var(--border-bright)',
            borderRadius: 6,
            padding: '8px 12px',
            pointerEvents: 'none',
            zIndex: 100,
            minWidth: 160,
          }}>
            <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: 'var(--gold)', marginBottom: 4, fontWeight: 700 }}>
              {tooltip.node.id}
            </div>
            <div style={{ fontSize: 10, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              <div>Name: {tooltip.node.name}</div>
              <div>Type: {tooltip.node.type}</div>
              <div>Risk: {tooltip.node.risk_weight! > 0 ? <span style={{ color: 'var(--orange)' }}>HIGH</span> : <span style={{ color: 'var(--green)' }}>LOW</span>}</div>
              {tooltip.node.is_sdn && <div style={{ color: 'var(--red)', fontWeight: 700 }}>⚠ OFAC SDN LIST</div>}
              {tooltip.node.is_shell_suspect && <div style={{ color: 'var(--orange)' }}>⚠ SHELL SUSPECT</div>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
