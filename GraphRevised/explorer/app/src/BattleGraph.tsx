import { useMemo, useState } from 'react'
import { battleGraph } from './graphProjection'
import { EvidenceList } from './EvidenceList'
import type { SubjectView } from './subjectView'
import './styles/battle-graph.css'

type Selected = { kind: 'phase' | 'topic'; id: string }

function wrap(label: string): string[] {
  const lines: string[] = []
  for (const word of label.split(' ')) {
    const last = lines.length - 1
    if (last < 0 || lines[last].length + word.length + 1 > 39) lines.push(word)
    else lines[last] += ` ${word}`
  }
  return lines
}

function GraphNode({ x, y, label, subtitle, kind, onClick }: {
  x: number; y: number; label: string; subtitle: string; kind: string; onClick?: () => void
}) {
  const lines = wrap(label)
  return <g transform={`translate(${x} ${y})`} className={`graph-node ${kind}`}
    role={onClick ? 'button' : undefined} tabIndex={onClick ? 0 : undefined}
    aria-label={onClick ? `${label}, ${subtitle}. Show details` : undefined}
    onClick={onClick} onKeyDown={onClick ? e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick() } } : undefined}>
    <rect width="350" height="70" rx="8" />
    {lines.slice(0, 2).map((line, i) => <text key={i} x="14" y={23 + i * 18} className="graph-label">{line}</text>)}
    <text x="14" y="58" className="graph-subtitle">{subtitle}</text>
    <title>{label} — {subtitle}</title>
  </g>
}

export function BattleGraph({ view }: { view: SubjectView }) {
  const { phases, topics } = useMemo(() => battleGraph(view), [view])
  const [selected, setSelected] = useState<Selected | null>(null)
  const [showPhases, setShowPhases] = useState(false)
  const [showTopics, setShowTopics] = useState(false)
  const activePhase = selected?.kind === 'phase' ? phases.find(p => p.placement.id === selected.id) : undefined
  const activeTopic = selected?.kind === 'topic' ? topics.find(t => t.event.id === selected.id) : undefined
  const section = topics[0]?.route.section
  const legacy = view.focus.id === 'chr:entity:battle-of-actium' ? phases.find(p => p.event.id.endsWith(':meaning-memory')) : undefined
  const height = 315 + Math.max(showPhases ? phases.length : 0, showTopics ? topics.length : 0) * 90
  const evidence = activeTopic?.route.sourceAssertion?.evidence || activePhase?.placement.evidence || []

  return <section className="graph-view" aria-label="Event graph view">
    <div className="graph-heading"><div><h2>Event and its Subject</h2>
      <p>A focused view of the Subject, its event, and recorded placements. Select a node for details.</p></div>
      <div className="graph-controls">
        <button type="button" aria-pressed={showPhases} onClick={() => setShowPhases(!showPhases)}>{showPhases ? 'Hide' : 'Show'} event phase links ({phases.length})</button>
        <button type="button" aria-pressed={showTopics} disabled={!section} onClick={() => setShowTopics(!showTopics)}>{showTopics ? 'Hide' : 'Show'} topical depictions ({topics.length})</button>
      </div>
    </div>
    <p className="graph-key"><span className="graph-key-subject">Subject</span> <span className="graph-key-event">Event</span>
      <span className="graph-key-depiction">Source depiction</span> · Arrow points toward the focus, broader Subject, or containing event/Subject.</p>
    {legacy && <p className="graph-warning">Existing model warning: “Meaning and memory” is also recorded as an event <strong>part of the battle</strong> ({legacy.placement.status || 'status unknown'}). That older assertion has not been retired. The topical Subject placement does not mean these events occurred during the battle.</p>}
    {!section && <p className="graph-warning">This snapshot has no topical Subject routes. A child Subject must be selected when generating the view, and it must have placements.</p>}
    <div className="graph-scroll" tabIndex={0} aria-label="Scrollable event relationship graph">
      <svg viewBox={`0 0 1160 ${height}`} width="1160" height={height} role="img" aria-label="Graph of the event, its Subject, and selected phase and topical links">
        <defs><marker id="graph-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L8,4 L0,8 Z" fill="context-stroke" /></marker></defs>
        <path className="graph-edge" d="M405 103 L190 180" markerEnd="url(#graph-arrow)" />
        <text className="graph-edge-label" x="235" y="135">focuses on</text>
        {section && <><path className="graph-edge" d="M790 180 L600 103" markerEnd="url(#graph-arrow)" />
          <text className="graph-edge-label" x="655" y="135">narrower than</text></>}
        <GraphNode x={405} y={35} label={view.subject.label || view.subject.id} subtitle={`SUBJECT · ${view.subject.status || 'unknown'}`} kind="subject" />
        <GraphNode x={15} y={180} label={view.focus.label || view.focus.id} subtitle={`EVENT · ${view.focus.status || 'unknown'}`} kind="event" />
        {section && <GraphNode x={795} y={180} label={section.label || section.id} subtitle={`SUBJECT · ${section.status || 'unknown'}`} kind="subject" />}
        {showPhases && phases.map((p, i) => {
          const y = 315 + i * 90
          return <g key={p.placement.id}>
            <path className="graph-edge phase-edge" d={`M190 ${y} C 375 ${y - 30}, 375 290, 190 250`} markerEnd="url(#graph-arrow)" />
            <GraphNode x={15} y={y} label={p.event.label || p.event.id}
              subtitle={`EVENT ${p.event.status || 'unknown'} · partOf ${p.placement.status || 'unknown'}`}
              kind="phase" onClick={() => setSelected({ kind: 'phase', id: p.placement.id })} />
          </g>
        })}
        {showTopics && topics.map((t, i) => {
          const y = 315 + i * 90
          return <g key={t.event.id}>
            <path className="graph-edge topical-edge" d={`M970 ${y} C 785 ${y - 30}, 785 290, 970 250`} markerEnd="url(#graph-arrow)" />
            <GraphNode x={795} y={y} label={t.event.label || t.event.id}
              subtitle={`DEPICTION ${t.event.status || 'unknown'} · in subject ${t.route.topicalPlacement?.status || 'unknown'}`}
              kind="depiction" onClick={() => setSelected({ kind: 'topic', id: t.event.id })} />
          </g>
        })}
      </svg>
    </div>
    {(activePhase || activeTopic) && <section className="graph-details" aria-label="Selected graph node details">
      <h3>{activePhase?.event.label || activeTopic?.event.label}</h3>
      {activePhase && <><p>Event status: {activePhase.event.status || 'unknown'} · Historical <code>partOf</code> assertion: {activePhase.placement.status || 'unknown'}</p>
        <p>{activePhase.placement.label}</p><p className="identifier">{activePhase.placement.id}</p></>}
      {activeTopic && <><p>Depicted event: {activeTopic.event.status || 'unknown'} · Topical placement: {activeTopic.route.topicalPlacement?.status}</p>
        <p>{activeTopic.route.topicalPlacement?.reason}</p>
        <p>Source placement assertion: {activeTopic.route.sourceAssertion?.status || 'missing'} · Accepting a topical placement does not accept a historical event claim.</p>
        <p className="identifier">{activeTopic.event.id}</p></>}
      <h4>Recorded evidence</h4>
      <EvidenceList items={evidence} />
    </section>}
    <p className="hint">This is a bounded overview, not the full graph. Phase links and topical placements retain their separate statuses. Open the assertion table for all claims and routes.</p>
  </section>
}
