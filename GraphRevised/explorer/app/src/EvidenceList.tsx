import { SourceText } from './SourceText'
import type { SourceTextData } from './SourceText'

export interface EvidenceEntry extends SourceTextData {
  observationId: string
  evidenceState: string
  proposalStatus: string | null
  observationStatus?: string | null
  proposalId?: string | null
  workLabel?: string | null
  rationale?: string | null
}

export function EvidenceList({ items }: { items: EvidenceEntry[] }) {
  if (!items.length) return <p className="hint">No evidence recorded in this view.</p>
  const groups = new Map<string, EvidenceEntry[]>()
  for (const item of items) {
    const group = groups.get(item.observationId) || []
    group.push(item)
    groups.set(item.observationId, group)
  }
  return <div>
    <p className="hint">{items.length} evidence {items.length === 1 ? 'record' : 'records'} from {groups.size} distinct
      {groups.size === 1 ? ' observation' : ' observations'}. Repeated records or passages are not independent corroboration.</p>
    <ul className="evidence-list">{[...groups].map(([observationId, records]) => <li key={observationId}>
      <div className="identifier">Observation: {observationId}</div>
      {records.map((e, i) => <section className="evidence-record" key={`${e.evidenceState}-${e.proposalId || ''}-${i}`}>
        <SourceText source={e} evidence />
        {e.workLabel && <div>Work: {e.workLabel}</div>}
        <div>Evidence link: {e.evidenceState === 'supported' ? 'accepted support' : e.evidenceState === 'proposal' ? 'proposal evidence' : e.evidenceState}</div>
        {e.evidenceState === 'proposal' && <div>Proposal status: {e.proposalStatus || 'unknown'}</div>}
        {e.observationStatus !== undefined && <div>Observation status: {e.observationStatus || 'unknown'}</div>}
        {e.proposalId && <div className="identifier">Proposal: {e.proposalId}</div>}
        {e.rationale && <div>Rationale: {e.rationale}</div>}
      </section>)}
    </li>)}</ul>
  </div>
}
