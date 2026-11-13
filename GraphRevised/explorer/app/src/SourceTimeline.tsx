import { useMemo, useState } from 'react'
import { matchesBetween, sourceLane } from './timelineModel'
import type { TimelineClaim, TimelineData, TimelineEvent } from './timelineModel'
import { SourceText } from './SourceText'
import { EvidenceList } from './EvidenceList'
import './styles/source-timeline.css'

function ClaimEvidence({ claim }: { claim: TimelineClaim }) {
  return <details><summary>Evidence and assertion details</summary>
    <p className="identifier">{claim.id}</p>
    <p>Assertion status: {claim.status}</p>
    <EvidenceList items={claim.evidence} />
  </details>
}

function EventSources({ event }: { event: TimelineEvent | undefined }) {
  if (!event) return null
  return <details><summary>Source mentions for {event.label || event.id} ({event.mentions.length})</summary>
    <p className="hint">Mentions identify passages associated with the depiction; they are not necessarily evidence for this particular claim.</p>
    {event.mentions.length ? <ul>{event.mentions.map((mention, i) => <li key={`${mention.observationId}-${i}`}>
      <SourceText source={mention} evidence={false} />
      {mention.work && <div>Work: {mention.work}</div>}
      <div>Mention: {mention.annotationStatus || 'status unknown'} · Observation: {mention.observationStatus || 'status unknown'}</div>
    </li>)}</ul> : <p>No source mentions recorded in this snapshot.</p>}
  </details>
}

function Lane({ data, workId }: { data: TimelineData; workId: string }) {
  const lane = useMemo(() => sourceLane(data, workId), [data, workId])
  const labels = new Map(lane.events.map(e => [e.id, e.label || e.id]))
  const events = new Map(lane.events.map(e => [e.id, e]))
  const label = (id: string | null) => id ? labels.get(id) || id : 'unknown'
  const dated = [...lane.dates].filter(a => a.timeEdtf && a.startEarliestJdn !== null && a.endLatestJdn !== null)
    .sort((a, b) => a.startEarliestJdn! - b.startEarliestJdn!)
  const words = lane.dates.filter(a => !dated.includes(a))
  return <article className="source-lane">
    <p>{lane.events.length} source depictions · {lane.dates.length} date claims · {lane.order.length} order claims</p>
    <h3>Normalized dates</h3>
    <p className="hint">Dates use EDTF astronomical year numbering: -0028 is 29 BCE; ~ means approximate. Sorted by earliest bound; overlapping or uncertain ranges are not a definite order.</p>
    {dated.length ? <ul className="timeline-items">{dated.map(a => <li key={a.id}>
      <strong>{label(a.subjectId)}</strong><div>{a.timeEdtf} · <span className={`status ${a.status}`}>{a.status}</span></div>
      {a.timeExpression && <div>Source expression: {a.timeExpression}</div>}<ClaimEvidence claim={a} /><EventSources event={events.get(a.subjectId)} />
    </li>)}</ul> : <p className="hint">No normalized date claims for this source in this view.</p>}
    <h3>Source time expressions without a normalized date</h3>
    <p className="hint">These are not positioned on a calendar axis.</p>
    {words.length ? <ul className="timeline-items">{words.map(a => <li key={a.id}>
      <strong>{label(a.subjectId)}</strong><div>{a.timeExpression || 'No source expression'}{a.relativeOffset && ` · offset ${a.relativeOffset}`} · <span className={`status ${a.status}`}>{a.status}</span></div>
      <ClaimEvidence claim={a} /><EventSources event={events.get(a.subjectId)} />
    </li>)}</ul> : <p className="hint">None recorded.</p>}
    <h3>Source-stated order</h3>
    <p className="hint">Each arrow is a separate claim; the list order does not imply a continuous sequence.</p>
    {lane.order.length ? <ul className="timeline-items">{lane.order.map(a => <li key={a.id}>
      <strong>{label(a.subjectId)}</strong> → <strong>{label(a.objectId)}</strong>
      <div>happened before · <span className={`status ${a.status}`}>{a.status}</span></div><ClaimEvidence claim={a} />
      <EventSources event={events.get(a.subjectId)} /><EventSources event={a.objectId ? events.get(a.objectId) : undefined} />
    </li>)}</ul> : <p className="hint">No source-stated order claims in this view.</p>}
    <details><summary>Events with no normalized date or order claim ({lane.unknown.length})</summary>
      <p className="hint">Their order is unknown in this view. Some also appear above with an unnormalized time expression.</p>
      <ul>{lane.unknown.map(e => <li key={e.id}>{e.label || e.id} · {e.status || 'unknown'}<EventSources event={e} /></li>)}</ul>
    </details>
  </article>
}

export function SourceTimeline({ data, compare }: { data: TimelineData; compare: boolean }) {
  const sources = data.sources.filter(s => data.events.some(e => e.sourceWorkId === s.workId))
  const [left, setLeft] = useState(sources[0]?.workId || '')
  const [right, setRight] = useState(sources[1]?.workId || '')
  const links = useMemo(() => matchesBetween(data, left, right), [data, left, right])
  const eventById = new Map(data.events.map(e => [e.id, e]))
  const options = sources.map(s => <option key={s.workId} value={s.workId}>{s.voice || s.workId}</option>)
  if (!sources.length) return <p>No source depictions are in this snapshot.</p>
  return <section className="timeline-view" aria-label={compare ? 'Compare source timelines' : 'Source timeline'}>
    <h2>{compare ? 'Compare source timelines' : 'Timeline by source'}</h2>
    <p>Source-specific claims only. Dates, order and identity remain separate; proposed claims are not accepted facts.</p>
    <p className="notice">Only events reached by this Subject view are shown. Lists do not infer order from narration, subject placement, causation, lexical similarity or matching depictions. Source dependence is not independent corroboration.</p>
    <div className="timeline-columns">
      <section><label className="timeline-select">{compare ? 'First source' : 'Source'}<select value={left} onChange={e => setLeft(e.target.value)}>{options}</select></label>
        <Lane data={data} workId={left} /></section>
      {compare && <section><label className="timeline-select">Second source<select value={right} onChange={e => setRight(e.target.value)}>{options}</select></label>
        <Lane data={data} workId={right} /></section>}
    </div>
    {compare && <section className="timeline-matches"><h3>Cross-source depiction matches</h3>
      <p>Only recorded identity assertions; these do not transfer dates or establish independent corroboration.</p>
      {left === right ? <p>Choose two different sources to compare matches.</p> : links.length ? <ul className="timeline-items">{links.map(a => <li key={a.id}>
        <strong>{eventById.get(a.subjectId)?.label || a.subjectId}</strong> ↔ <strong>{eventById.get(a.objectId || '')?.label || a.objectId}</strong>
        <div>depicts same action · <span className={`status ${a.status}`}>{a.status}</span></div><ClaimEvidence claim={a} />
      </li>)}</ul> : <p>No recorded matches between these sources in this snapshot.</p>}
    </section>}
  </section>
}
