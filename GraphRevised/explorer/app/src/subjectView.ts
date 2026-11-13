import type { SourceTextData } from './SourceText'

export interface ViewNode { id: string; label: string | null; status: string | null }
export interface Evidence extends SourceTextData {
  observationId: string
  observationStatus: string | null; workId: string | null; workLabel: string | null
  evidenceState: string; proposalId: string | null; proposalStatus: string | null; rationale: string | null
}
export interface Placement {
  id: string; label: string | null; status: string | null; predicate: string | null
  mode: string | null; evidence: Evidence[]
}
export interface TopicalPlacement {
  status: string; reason: string; proposedBy: string; proposedAt: string; sourceAssertionId: string
  decidedBy: string | null; decisionBasis: string | null; decidedAt: string | null
}
export interface Route {
  kind: string; assertionRole: string; events: ViewNode[]; placements: Placement[]
  section?: ViewNode; topicalPlacement?: TopicalPlacement; sourceAssertion?: Placement | null
}
export interface Assertion {
  id: string; label: string | null; status: string; predicate: string
  mode: string; category: string | null; workId: string | null; workLabel: string | null
  routes: Route[]; evidence: Evidence[]
}
export interface SubjectView {
  subject: ViewNode; focus: ViewNode; broaderSubjectPaths: ViewNode[][]
  limitations: string[]; assertions: Assertion[]; sourceTimeline?: TimelineData
}

function object(value: unknown, where: string): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) throw new Error(`${where} must be an object`)
  return value as Record<string, unknown>
}
function string(value: unknown, where: string): string {
  if (typeof value !== 'string') throw new Error(`${where} must be a string`)
  return value
}
function nullable(value: unknown, where: string): string | null {
  if (value === null) return null
  return string(value, where)
}
function optionalNullable(value: unknown, where: string): string | null | undefined {
  return value === undefined ? undefined : nullable(value, where)
}
function array<T>(value: unknown, where: string, parse: (item: unknown, where: string) => T): T[] {
  if (!Array.isArray(value)) throw new Error(`${where} must be an array`)
  return value.map((item, index) => parse(item, `${where}[${index}]`))
}
function node(value: unknown, where: string): ViewNode {
  const o = object(value, where)
  return { id: string(o.id, `${where}.id`), label: nullable(o.label, `${where}.label`), status: nullable(o.status, `${where}.status`) }
}
function evidence(value: unknown, where: string): Evidence {
  const o = object(value, where)
  return {
    observationId: string(o.observationId, `${where}.observationId`),
    passage: nullable(o.passage, `${where}.passage`), locator: nullable(o.locator, `${where}.locator`),
    quotation: optionalNullable(o.quotation, `${where}.quotation`), passageText: optionalNullable(o.passageText, `${where}.passageText`),
    editionCitation: optionalNullable(o.editionCitation, `${where}.editionCitation`), rights: optionalNullable(o.rights, `${where}.rights`),
    textAvailability: o.textAvailability === undefined ? undefined : string(o.textAvailability, `${where}.textAvailability`),
    observationStatus: nullable(o.observationStatus, `${where}.observationStatus`),
    workId: nullable(o.workId, `${where}.workId`), workLabel: nullable(o.workLabel, `${where}.workLabel`),
    evidenceState: string(o.evidenceState, `${where}.evidenceState`),
    proposalId: nullable(o.proposalId, `${where}.proposalId`),
    proposalStatus: nullable(o.proposalStatus, `${where}.proposalStatus`), rationale: nullable(o.rationale, `${where}.rationale`),
  }
}
function placement(value: unknown, where: string): Placement {
  const o = object(value, where)
  return { ...node(o, where), predicate: nullable(o.predicate, `${where}.predicate`),
    mode: nullable(o.mode, `${where}.mode`), evidence: array(o.evidence, `${where}.evidence`, evidence) }
}
function route(value: unknown, where: string): Route {
  const o = object(value, where)
  const result: Route = { kind: string(o.kind, `${where}.kind`), assertionRole: string(o.assertionRole, `${where}.assertionRole`),
    events: array(o.events, `${where}.events`, node), placements: array(o.placements, `${where}.placements`, placement) }
  if (result.events.length !== result.placements.length + 1) throw new Error(`${where} has an invalid placement path`)
  if (result.kind === 'subjectPlacement') {
    result.section = node(o.section, `${where}.section`)
    const p = object(o.topicalPlacement, `${where}.topicalPlacement`)
    result.topicalPlacement = {
      status: string(p.status, `${where}.status`), reason: string(p.reason, `${where}.reason`),
      proposedBy: string(p.proposedBy, `${where}.proposedBy`), proposedAt: string(p.proposedAt, `${where}.proposedAt`),
      sourceAssertionId: string(p.sourceAssertionId, `${where}.sourceAssertionId`),
      decidedBy: p.decidedBy == null ? null : string(p.decidedBy, `${where}.decidedBy`),
      decisionBasis: p.decisionBasis == null ? null : string(p.decisionBasis, `${where}.decisionBasis`),
      decidedAt: p.decidedAt == null ? null : string(p.decidedAt, `${where}.decidedAt`),
    }
    result.sourceAssertion = o.sourceAssertion === null ? null : placement(o.sourceAssertion, `${where}.sourceAssertion`)
  }
  return result
}
function assertion(value: unknown, where: string): Assertion {
  const o = object(value, where)
  return { id: string(o.id, `${where}.id`), label: nullable(o.label, `${where}.label`),
    status: string(o.status, `${where}.status`), predicate: string(o.predicate, `${where}.predicate`),
    mode: string(o.mode, `${where}.mode`), category: nullable(o.category, `${where}.category`),
    workId: nullable(o.workId, `${where}.workId`), workLabel: nullable(o.workLabel, `${where}.workLabel`),
    routes: array(o.routes, `${where}.routes`, route), evidence: array(o.evidence, `${where}.evidence`, evidence) }
}
export function parseSubjectView(value: unknown): SubjectView {
  const o = object(value, 'view')
  const view = { subject: node(o.subject, 'subject'), focus: node(o.focus, 'focus'),
    broaderSubjectPaths: array(o.broaderSubjectPaths, 'broaderSubjectPaths', (v, w) => array(v, w, node)),
    limitations: array(o.limitations, 'limitations', string), assertions: array(o.assertions, 'assertions', assertion),
    sourceTimeline: o.sourceTimeline === undefined ? undefined : parseTimeline(o.sourceTimeline) }
  const legacyActium = o.viewType === undefined && view.subject.id === 'chr:subject:history-of-battle-of-actium'
    && view.focus.id === 'chr:entity:battle-of-actium'
  if (!legacyActium && o.viewType !== 'event-subject-view-v1') {
    throw new Error('This is not a supported event Subject assertion view')
  }
  if (!legacyActium && (!view.subject.id.startsWith('chr:subject:') || view.subject.id === 'chr:subject:'
    || !view.focus.id.startsWith('chr:entity:') || view.focus.id === 'chr:entity:'
    || typeof o.inquiryId !== 'string' || !o.inquiryId.startsWith('chr:inquiry:') || o.inquiryId === 'chr:inquiry:')) {
    throw new Error('Invalid event Subject view identity')
  }
  if (o.sourcePassages !== undefined) {
    const passages = object(o.sourcePassages, 'sourcePassages')
    for (const [id, text] of Object.entries(passages)) string(text, `sourcePassages.${id}`)
    const hydrate = (items: (SourceTextData & { observationId: string })[]) => {
      for (const item of items) {
        if (Object.hasOwn(passages, item.observationId)) item.passageText = string(passages[item.observationId], `sourcePassages.${item.observationId}`)
      }
    }
    for (const claim of view.assertions) {
      hydrate(claim.evidence)
      for (const path of claim.routes) {
        for (const p of path.placements) hydrate(p.evidence)
        if (path.sourceAssertion) hydrate(path.sourceAssertion.evidence)
      }
    }
    if (view.sourceTimeline) {
      for (const event of view.sourceTimeline.events) hydrate(event.mentions)
      for (const claim of view.sourceTimeline.assertions) hydrate(claim.evidence)
    }
  }
  return view
}

export function sources(a: Assertion): string[] {
  return [...new Set([a.workLabel, ...a.evidence.map(e => e.workLabel)].filter((s): s is string => !!s))]
}
export interface Filters { query: string; status: string; predicate: string; source: string; route: string }
export function matches(a: Assertion, f: Filters): boolean {
  const q = f.query.trim().toLocaleLowerCase()
  const text = [a.id, a.label, a.predicate, a.workLabel, ...a.evidence.flatMap(e => [e.passage, e.workLabel, e.locator]),
    ...a.routes.flatMap(r => r.events.map(e => e.label))].filter(Boolean).join(' ').toLocaleLowerCase()
  return (!q || text.includes(q)) && (!f.status || a.status === f.status)
    && (!f.predicate || a.predicate === f.predicate) && (!f.source || sources(a).includes(f.source))
    && (!f.route || a.routes.some(r => r.kind === f.route))
}

export function safeLocator(value: string | null): string | null {
  if (!value) return null
  try {
    const url = new URL(value)
    return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : null
  } catch {
    return null
  }
}
import { parseTimeline } from './timelineModel'
import type { TimelineData } from './timelineModel'
