import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import { EvidenceList } from './EvidenceList'
import type { EvidenceEntry } from './EvidenceList'

const source: EvidenceEntry = {
  observationId: 'obs-1', passage: 'Reference', locator: null, textAvailability: 'available',
  passageText: 'Passage', quotation: 'Quote', evidenceState: 'supported', proposalStatus: null,
  observationStatus: 'observed',
}

describe('evidence display', () => {
  it('groups the same observation without hiding distinct evidence or review records', () => {
    const html = renderToStaticMarkup(<EvidenceList items={[source,
      { ...source, evidenceState: 'proposal', proposalStatus: 'accepted', proposalId: 'p1', rationale: 'review basis' },
      { ...source, evidenceState: 'proposal', proposalStatus: 'rejected', proposalId: 'p2', quotation: 'Other quote' },
      { ...source, observationId: 'obs-2' }]} />)
    expect(html).toContain('4 evidence records from 2 distinct observations')
    expect(html).toContain('Evidence link: ')
    expect(html).toContain('accepted support')
    expect(html).toContain('Proposal status: ')
    expect(html).toContain('accepted')
    expect(html).toContain('rejected')
    expect(html).toContain('p1')
    expect(html).toContain('p2')
    expect(html).toContain('Other quote')
    expect(html).toContain('review basis')
    expect(html).toContain('Observation status: ')
    expect(html).toContain('not independent corroboration')
  })

  it('handles evidence from older timelines without inventing observation status', () => {
    const { observationStatus: _, ...older } = source
    const html = renderToStaticMarkup(<EvidenceList items={[older]} />)
    expect(html).toContain('1 evidence record from 1 distinct observation')
    expect(html).not.toContain('Observation status:')
    expect(renderToStaticMarkup(<EvidenceList items={[]} />)).toContain('No evidence recorded')
  })
})
