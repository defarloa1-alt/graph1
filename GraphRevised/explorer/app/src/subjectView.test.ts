import { describe, expect, it } from 'vitest'
import { matches, parseSubjectView, safeLocator } from './subjectView'

const focus = { id: 'chr:entity:battle-of-actium', label: 'Battle of Actium', status: 'resolved' }
const subject = { id: 'chr:subject:history-of-battle-of-actium', label: 'Actium', status: 'provisional' }
const evidence = { observationId: 'obs', passage: 'Dio 51', locator: 'https://example.org/passage',
  observationStatus: 'observed', workId: 'dio', workLabel: 'Dio', evidenceState: 'proposal',
  proposalId: 'proposal', proposalStatus: 'rejected', rationale: 'curator rationale' }
const placement = { id: 'placement', label: 'event part of Actium', status: 'proposed',
  predicate: 'partOf', mode: null, evidence: [evidence] }
const claim = { id: 'claim', label: 'Nicopolis founded', status: 'proposed', predicate: 'occurred',
  mode: 'attributed', category: 'factual', workId: 'dio', workLabel: 'Dio',
  evidence: [evidence], routes: [{ kind: 'partOf', assertionRole: 'ASSERTION_SUBJECT',
    events: [{ id: 'event', label: 'Nicopolis', status: 'proposed' }, focus], placements: [placement] }] }
const fixture = { subject, focus, broaderSubjectPaths: [[subject]], limitations: ['Proposed is not accepted.'], assertions: [claim] }
const filters = { query: '', status: '', predicate: '', source: '', route: '' }

describe('Actium Subject view', () => {
  it('preserves placement and evidence status', () => {
    const view = parseSubjectView(fixture)
    expect(view.assertions[0].routes[0].placements[0].status).toBe('proposed')
    expect(view.assertions[0].evidence[0].proposalStatus).toBe('rejected')
  })
  it('preserves source text metadata and accepts older snapshots', () => {
    const old = parseSubjectView(fixture).assertions[0].evidence[0]
    expect(old.textAvailability).toBeUndefined()
    const enriched = { ...evidence, quotation: 'quote', passageText: 'passage',
      editionCitation: 'edition', rights: 'rights', textAvailability: 'available' }
    const item = parseSubjectView({ ...fixture, assertions: [{ ...claim, evidence: [enriched] }] }).assertions[0].evidence[0]
    expect([item.quotation, item.passageText, item.editionCitation, item.rights]).toEqual(['quote', 'passage', 'edition', 'rights'])
    expect(() => parseSubjectView({ ...fixture, assertions: [{ ...claim, evidence: [{ ...enriched, passageText: 123 }] }] })).toThrow()
    const shared = parseSubjectView({ ...fixture, sourcePassages: { obs: 'Shared passage' } })
    expect(shared.assertions[0].evidence[0].passageText).toBe('Shared passage')
    expect(shared.assertions[0].routes[0].placements[0].evidence[0].passageText).toBe('Shared passage')
    expect(() => parseSubjectView({ ...fixture, sourcePassages: { obs: 123 } })).toThrow()
  })
  it('hydrates shared passages for timeline mentions and evidence', () => {
    const timeline = { sources: [{ workId: 'dio', voice: 'Dio' }],
      events: [{ id: 'event', label: 'Event', status: 'proposed', sourceWorkId: 'dio',
        mentions: [{ observationId: 'obs', passage: 'Dio 51', locator: null, textAvailability: 'available' }] }],
      assertions: [{ id: 'timeline-claim', predicate: 'occurred', status: 'proposed', mode: 'attributed',
        subjectId: 'event', objectId: null, workId: 'dio', timeExpression: null, timeEdtf: null, relativeOffset: null,
        startEarliestJdn: null, endLatestJdn: null, evidence: [{ observationId: 'obs', passage: 'Dio 51', locator: null,
          evidenceState: 'proposal', proposalStatus: 'submitted', textAvailability: 'available' }] }] }
    const view = parseSubjectView({ ...fixture, sourceTimeline: timeline, sourcePassages: { obs: 'Shared passage' } })
    expect(view.sourceTimeline?.events[0].mentions[0].passageText).toBe('Shared passage')
    expect(view.sourceTimeline?.assertions[0].evidence[0].passageText).toBe('Shared passage')
  })
  it('filters by claim, status, predicate, source and route together', () => {
    const item = parseSubjectView(fixture).assertions[0]
    expect(matches(item, { query: 'nicopolis', status: 'proposed', predicate: 'occurred', source: 'Dio', route: 'partOf' })).toBe(true)
    expect(matches(item, { ...filters, status: 'accepted' })).toBe(false)
    expect(matches(item, { ...filters, source: 'Hale' })).toBe(false)
    expect(matches(item, { ...filters, route: 'focus' })).toBe(false)
  })
  it('rejects invalid snapshots and broken routes', () => {
    expect(() => parseSubjectView({})).toThrow()
    expect(() => parseSubjectView({ ...fixture, focus: { ...focus, id: 'other' } })).toThrow('not a supported')
    expect(() => parseSubjectView({ ...fixture, assertions: [{ ...claim, routes: [{ ...claim.routes[0], placements: [] }] }] })).toThrow('invalid placement path')
  })
  it('accepts versioned other-event views but rejects malformed or unsupported identities', () => {
    const philippi = { ...fixture, viewType: 'event-subject-view-v1', inquiryId: 'chr:inquiry:philippi',
      subject: { ...subject, id: 'chr:subject:history-of-philippi' },
      focus: { ...focus, id: 'chr:entity:battle-of-philippi' } }
    expect(parseSubjectView(philippi).focus.id).toBe('chr:entity:battle-of-philippi')
    expect(() => parseSubjectView({ ...philippi, inquiryId: '' })).toThrow('Invalid event Subject view identity')
    expect(() => parseSubjectView({ ...philippi, viewType: 'event-subject-view-v2' })).toThrow('not a supported')
    expect(() => parseSubjectView({ ...philippi, viewType: undefined })).toThrow('not a supported')
  })
  it('only makes web locators clickable', () => {
    expect(safeLocator('https://example.org/passage')).toBe('https://example.org/passage')
    expect(safeLocator('javascript:alert(1)')).toBeNull()
    expect(safeLocator('local-file')).toBeNull()
  })
  it('preserves a topical route and its independent review status', () => {
    const topical = { kind: 'subjectPlacement', assertionRole: 'ASSERTION_SUBJECT', events: [focus],
      placements: [], section: subject, sourceAssertion: placement,
      topicalPlacement: { status: 'proposed', reason: 'Aftermath', proposedBy: 'TD', proposedAt: 'time',
        sourceAssertionId: 'placement' } }
    const view = parseSubjectView({ ...fixture, assertions: [{ ...claim, routes: [topical] }] })
    expect(view.assertions[0].routes[0].topicalPlacement?.status).toBe('proposed')
    expect(view.assertions[0].routes[0].sourceAssertion?.evidence[0].proposalStatus).toBe('rejected')
    expect(matches(view.assertions[0], { ...filters, route: 'subjectPlacement' })).toBe(true)
  })
})
