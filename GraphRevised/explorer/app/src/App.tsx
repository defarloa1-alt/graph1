import { Fragment, useMemo, useState } from 'react'
import type { ChangeEvent } from 'react'
import { matches, parseSubjectView, sources } from './subjectView'
import { EvidenceList } from './EvidenceList'
import type { Assertion, Filters, SubjectView } from './subjectView'
import { BattleGraph } from './BattleGraph'
import { SourceTimeline } from './SourceTimeline'
import './styles/subject-view.css'

const PAGE_SIZE = 25
const emptyFilters: Filters = { query: '', status: '', predicate: '', source: '', route: '' }

function Detail({ assertion }: { assertion: Assertion }) {
  return <div className="detail">
    <p className="identifier">{assertion.id}</p>
    <p>Assertion status: <span className={`status ${assertion.status}`}>{assertion.status}</span></p>
    <p>Mode: {assertion.mode} · Category: {assertion.category || 'not recorded'}
      {assertion.workLabel && <> · Attributed to: {assertion.workLabel}</>}</p>
    <h3>Assertion evidence</h3><EvidenceList items={assertion.evidence} />
    <h3>Why this appears in the Subject</h3>
    {assertion.routes.map((route, i) => <section className="route" key={i}>
      <strong>{route.kind === 'focus' ? 'Direct focus reference' : route.kind === 'subjectPlacement' ? 'Topical Subject placement' : 'Event placement path'}</strong>
      <span> · assertion role: {route.assertionRole}</span>
      {route.topicalPlacement && <div className="placement">
        <p>Subject: {route.section?.label || route.section?.id} · Subject status: {route.section?.status || 'unknown'}</p>
        <p>Topical placement status: {route.topicalPlacement.status} · {route.topicalPlacement.reason}</p>
        <p>Proposed by {route.topicalPlacement.proposedBy} at {route.topicalPlacement.proposedAt}</p>
        {route.topicalPlacement.decidedBy && <p>Decided by {route.topicalPlacement.decidedBy} at {route.topicalPlacement.decidedAt} · {route.topicalPlacement.decisionBasis}</p>}
        <p>Source placement assertion: {route.sourceAssertion?.label || route.topicalPlacement.sourceAssertionId}
          {' · '}Assertion status: {route.sourceAssertion?.status || 'missing'}</p>
        {route.sourceAssertion && <EvidenceList items={route.sourceAssertion.evidence} />}
      </div>}
      <ol>{route.events.map((event, index) => <li key={`${event.id}-${index}`}>
        <strong>{event.label || event.id}</strong> · Event status: <span className="status">{event.status || 'unknown'}</span>
        {route.placements[index] && <div className="placement">
          <div>partOf: {route.placements[index].label || route.placements[index].id}
            {' · '}Placement assertion status: <span className="status">{route.placements[index].status || 'unknown'}</span>
            {' · '}{route.placements[index].mode || 'asserted'}</div>
          <div className="identifier">{route.placements[index].id}</div>
          <EvidenceList items={route.placements[index].evidence} />
        </div>}
      </li>)}</ol>
    </section>)}
  </div>
}

export default function App() {
  const [view, setView] = useState<SubjectView | null>(null)
  const [fileName, setFileName] = useState('')
  const [error, setError] = useState('')
  const [filters, setFilters] = useState<Filters>(emptyFilters)
  const [page, setPage] = useState(0)
  const [selected, setSelected] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'graph' | 'table' | 'timeline' | 'compare'>('graph')

  async function loadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    try {
      const parsed = parseSubjectView(JSON.parse(await file.text()) as unknown)
      setView(parsed); setFileName(file.name); setFilters(emptyFilters); setPage(0); setSelected(null); setError('')
    } catch (e) {
      setError(`Could not load ${file.name}: ${e instanceof Error ? e.message : 'unknown error'}`)
    }
  }
  function filter(key: keyof Filters, value: string) {
    setFilters(current => ({ ...current, [key]: value })); setPage(0); setSelected(null)
  }
  const filtered = useMemo(() => view?.assertions.filter(a => matches(a, filters)) || [], [view, filters])
  const predicates = useMemo(() => [...new Set(view?.assertions.map(a => a.predicate))].sort(), [view])
  const sourceNames = useMemo(() => [...new Set(view?.assertions.flatMap(sources))].sort(), [view])
  const pages = Math.ceil(filtered.length / PAGE_SIZE)
  const shown = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  return <main className="subject-app">
    <header className="page-header">
      <div><p className="eyebrow">Chrystallum · Read-only research view</p><h1>Event Subject assertions</h1>
        <p>Explore claims, their sources, and the paths that make them relevant to the Subject.</p></div>
      <label className="file-button">Open view JSON<input type="file" accept=".json,application/json" onChange={loadFile} /></label>
    </header>
    <p className="notice">This view reads a local snapshot in your browser. It does not write to Neo4j or accept claims.</p>
    <details className="status-guide"><summary>How to read statuses and evidence</summary>
      <p>Assertion status applies to a claim. A placement has its own status. Proposal status applies to a review of evidence; observation status records the source observation, not whether the claim is true.</p>
      <p>The same observation can appear under multiple claims and routes, or as both a proposal record and accepted support. Repetition does not establish independent corroboration.</p>
    </details>
    {error && <p className="error" role="alert">{error}</p>}
    {!view ? <section className="empty"><h2>Open an event Subject view</h2>
      <p>Choose an existing event Subject snapshot from GraphRevised\explorer\snapshots. For Actium, create that folder if needed and generate a fresh snapshot with a new filename from the repository root:</p>
      <code>python -m GraphRevised.discovery.actium_subject_view --output GraphRevised\explorer\snapshots\actium-view-new.json</code>
      <p>Files stay on your device; they may contain unpublished graph data.</p></section> : <>
      <section className="overview">
        <div><span className="eyebrow">Subject</span><h2>{view.subject.label || view.subject.id}</h2>
          <p>Subject: {view.subject.status || 'status unknown'} · Focus: {view.focus.label || view.focus.id} ({view.focus.status || 'status unknown'})</p>
          <p>Snapshot: {fileName} · {view.assertions.length.toLocaleString()} assertions</p></div>
        <details><summary>Subject hierarchy and scope</summary>
          {view.broaderSubjectPaths.map((path, i) => <p key={i}>{path.map(n => `${n.label || n.id} [${n.status || 'unknown'}]`).join(' → ')}</p>)}
          <ul>{view.limitations.map(item => <li key={item}>{item}</li>)}</ul>
        </details>
      </section>
      <nav className="view-switch" aria-label="View mode">
        <button type="button" aria-pressed={viewMode === 'graph'} onClick={() => setViewMode('graph')}>Graph</button>
        <button type="button" aria-pressed={viewMode === 'table'} onClick={() => setViewMode('table')}>Assertion table</button>
        <button type="button" aria-pressed={viewMode === 'timeline'} onClick={() => setViewMode('timeline')}>Source timeline</button>
        <button type="button" aria-pressed={viewMode === 'compare'} onClick={() => setViewMode('compare')}>Compare sources</button>
      </nav>
      {viewMode === 'graph' ? <BattleGraph key={fileName} view={view} /> : viewMode === 'timeline' || viewMode === 'compare'
        ? view.sourceTimeline ? <SourceTimeline key={`${fileName}-${viewMode}`} data={view.sourceTimeline} compare={viewMode === 'compare'} />
          : <p className="notice">This snapshot predates source timelines. Generate and open a fresh snapshot for this inquiry.</p>
        : <>
      <section aria-label="Filter assertions" className="filters">
        <label className="search">Search<input type="search" value={filters.query} onChange={e => filter('query', e.target.value)} placeholder="Claim, event, source, locator or ID" /></label>
        <label>Assertion status<select value={filters.status} onChange={e => filter('status', e.target.value)}>
          <option value="">All statuses</option><option value="proposed">Proposed</option><option value="accepted">Accepted</option></select></label>
        <label>Predicate<select value={filters.predicate} onChange={e => filter('predicate', e.target.value)}>
          <option value="">All predicates</option>{predicates.map(p => <option key={p}>{p}</option>)}</select></label>
        <label>Source<select value={filters.source} onChange={e => filter('source', e.target.value)}>
          <option value="">All sources</option>{sourceNames.map(s => <option key={s}>{s}</option>)}</select></label>
        <label>Route<select value={filters.route} onChange={e => filter('route', e.target.value)}>
          <option value="">All routes</option><option value="focus">Direct focus</option><option value="partOf">Event placement</option><option value="subjectPlacement">Topical Subject placement</option></select></label>
        <button type="button" onClick={() => { setFilters(emptyFilters); setPage(0); setSelected(null) }}>Clear filters</button>
      </section>
      <div className="table-heading"><h2>Assertions</h2><p aria-live="polite">{filtered.length.toLocaleString()} matching · {view.assertions.length.toLocaleString()} total</p></div>
      <div className="table-wrap"><table><thead><tr><th scope="col">Assertion</th><th scope="col">Assertion status</th><th scope="col">Predicate</th><th scope="col">Source / voice</th><th scope="col">Routes</th><th scope="col"><span className="sr-only">Details</span></th></tr></thead>
        <tbody>{shown.map(a => <Fragment key={a.id}><tr><td>{a.label || a.id}</td><td><span className={`status ${a.status}`}>{a.status}</span></td>
          <td>{a.predicate}</td><td>{a.workLabel || (sources(a).length ? sources(a).join(', ') : 'Not recorded')}</td>
          <td>{a.routes.length}</td><td><button type="button" aria-expanded={selected === a.id} onClick={() => setSelected(selected === a.id ? null : a.id)}>
            {selected === a.id ? 'Hide details' : 'Show details'}<span className="sr-only"> for {a.label || a.id}</span></button></td></tr>
          {selected === a.id && <tr><td colSpan={6}><section className="detail-panel" aria-label="Assertion details">
            <h2>{a.label || a.id}</h2><Detail assertion={a} />
          </section></td></tr>}</Fragment>)}</tbody></table>
        {!shown.length && <p className="empty-results">No assertions match these filters.</p>}
      </div>
      <nav className="pagination" aria-label="Assertion pages">
        <button type="button" disabled={page === 0} onClick={() => { setPage(page - 1); setSelected(null) }}>Previous</button>
        <span>{pages ? `Page ${page + 1} of ${pages}` : 'No pages'}</span>
        <button type="button" disabled={page + 1 >= pages} onClick={() => { setPage(page + 1); setSelected(null) }}>Next</button>
      </nav>
      </>}
    </>}
  </main>
}
