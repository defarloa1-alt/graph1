import { describe, expect, it } from 'vitest'
import { battleGraph } from './graphProjection'
import type { Assertion, Placement, Route, SubjectView, ViewNode } from './subjectView'

const focus: ViewNode = { id: 'chr:entity:battle-of-actium', label: 'Battle', status: 'resolved' }
const section: ViewNode = { id: 'section', label: 'Memory', status: 'candidate' }
const phase: ViewNode = { id: 'chr:entity:phase:battle-of-actium:meaning-memory', label: 'Legacy phase', status: 'provisional' }
const event: ViewNode = { id: 'depiction', label: 'Nicopolis', status: 'proposed' }
const parent: Placement = { id: 'part', label: 'part of battle', status: 'accepted', predicate: 'partOf', mode: null, evidence: [] }
const placement: Placement = { ...parent, id: 'placement', status: 'proposed' }
const topical: Route = { kind: 'subjectPlacement', assertionRole: 'ASSERTION_SUBJECT', events: [event], placements: [],
  section, sourceAssertion: placement, topicalPlacement: { status: 'accepted', reason: 'Memory', proposedBy: 'TD',
    proposedAt: 'time', sourceAssertionId: 'placement', decidedBy: 'TD', decidedAt: 'time', decisionBasis: 'Reviewed' } }
const old: Route = { kind: 'partOf', assertionRole: 'ASSERTION_SUBJECT', events: [event, phase, focus], placements: [placement, parent] }
const claim: Assertion = { id: 'claim', label: 'claim', predicate: 'occurred', status: 'proposed', mode: 'asserted',
  category: null, workId: null, workLabel: null, evidence: [], routes: [topical, old] }
const view: SubjectView = { subject: section, focus, broaderSubjectPaths: [], limitations: [], assertions: [claim, { ...claim, id: 'second' }] }

describe('battle graph projection', () => {
  it('deduplicates source depictions and preserves separate phase and topical statuses', () => {
    const graph = battleGraph(view)
    expect(graph.phases).toHaveLength(1)
    expect(graph.topics).toHaveLength(1)
    expect(graph.phases[0].placement.status).toBe('accepted')
    expect(graph.topics[0].event.status).toBe('proposed')
    expect(graph.topics[0].route.topicalPlacement?.status).toBe('accepted')
  })
  it('does not infer topical placements or identity links from phase paths', () => {
    const graph = battleGraph({ ...view, assertions: [{ ...claim, routes: [old] }] })
    expect(graph.phases).toHaveLength(1)
    expect(graph.topics).toHaveLength(0)
  })
  it('projects only phases for the current event', () => {
    const philippiFocus = { ...focus, id: 'chr:entity:battle-of-philippi' }
    const philippiPhase = { ...phase, id: 'chr:entity:phase:battle-of-philippi:engagement' }
    const philippiRoute = { ...old, events: [event, philippiPhase, philippiFocus] }
    const graph = battleGraph({ ...view, focus: philippiFocus, assertions: [{ ...claim, routes: [philippiRoute] }] })
    expect(graph.phases.map(p => p.event.id)).toEqual([philippiPhase.id])
  })
})
