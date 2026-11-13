import type { ViewNode } from './subjectView'
import type { SourceTextData } from './SourceText'

export interface TimelineEvidence extends SourceTextData { observationId: string; evidenceState: string; proposalStatus: string | null }
export interface TimelineMention extends SourceTextData {
  observationId: string; annotationStatus?: string | null; observationStatus?: string | null; work?: string | null
}
export interface TimelineEvent extends ViewNode { sourceWorkId: string; mentions: TimelineMention[] }
export interface TimelineClaim {
  id: string; predicate: string; status: string; mode: string | null; subjectId: string; objectId: string | null
  workId: string | null; timeExpression: string | null; timeEdtf: string | null; relativeOffset: string | null
  startEarliestJdn: number | null; endLatestJdn: number | null; evidence: TimelineEvidence[]
}
export interface TimelineData {
  sources: { workId: string; voice: string | null }[]
  events: TimelineEvent[]
  assertions: TimelineClaim[]
}

function obj(v: unknown): v is Record<string, unknown> { return typeof v === 'object' && v !== null && !Array.isArray(v) }
function str(v: unknown): v is string { return typeof v === 'string' }
function nullableString(v: unknown): v is string | null { return v === null || str(v) }
function nullableNumber(v: unknown): v is number | null { return v === null || (typeof v === 'number' && Number.isFinite(v)) }
function sourceText(v: Record<string, unknown>): boolean {
  return (v.quotation === undefined || nullableString(v.quotation))
    && (v.passageText === undefined || nullableString(v.passageText))
    && (v.editionCitation === undefined || nullableString(v.editionCitation))
    && (v.rights === undefined || nullableString(v.rights))
    && (v.textAvailability === undefined || str(v.textAvailability))
}

function isTimelineData(v: unknown): v is TimelineData {
  if (!obj(v) || !Array.isArray(v.sources) || !Array.isArray(v.events) || !Array.isArray(v.assertions)) return false
  return v.sources.every((x: unknown) => obj(x) && str(x.workId) && nullableString(x.voice))
    && v.events.every((x: unknown) => obj(x) && str(x.id) && nullableString(x.label) && nullableString(x.status) && str(x.sourceWorkId)
      && Array.isArray(x.mentions) && x.mentions.every((m: unknown) => obj(m) && str(m.observationId) && nullableString(m.locator) && nullableString(m.passage) && sourceText(m)
        && (m.annotationStatus === undefined || nullableString(m.annotationStatus))
        && (m.observationStatus === undefined || nullableString(m.observationStatus))
        && (m.work === undefined || nullableString(m.work))))
    && v.assertions.every((x: unknown) => obj(x) && str(x.id) && str(x.predicate) && str(x.status) && nullableString(x.mode)
      && str(x.subjectId) && nullableString(x.objectId) && nullableString(x.workId)
      && nullableString(x.timeExpression) && nullableString(x.timeEdtf) && nullableString(x.relativeOffset)
      && nullableNumber(x.startEarliestJdn) && nullableNumber(x.endLatestJdn) && Array.isArray(x.evidence)
      && x.evidence.every((e: unknown) => obj(e) && str(e.observationId) && nullableString(e.passage)
        && nullableString(e.locator) && str(e.evidenceState) && nullableString(e.proposalStatus) && sourceText(e)))
}

export function parseTimeline(v: unknown): TimelineData {
  if (!isTimelineData(v)) throw new Error('Invalid source timeline data')
  return v
}

export function sourceLane(data: TimelineData, workId: string) {
  const events = data.events.filter(e => e.sourceWorkId === workId)
  const ids = new Set(events.map(e => e.id))
  const claims = data.assertions.filter(a => a.workId === workId && a.mode === 'attributed'
    && (a.status === 'accepted' || a.status === 'proposed'))
  const dates = claims.filter(a => a.predicate === 'occurred' && ids.has(a.subjectId))
  const order = claims.filter(a => a.predicate === 'happenedBefore' && ids.has(a.subjectId) && a.objectId && ids.has(a.objectId))
  const positioned = new Set([
    ...dates.filter(a => a.timeEdtf && a.startEarliestJdn !== null && a.endLatestJdn !== null).map(a => a.subjectId),
    ...order.flatMap(a => [a.subjectId, a.objectId!]),
  ])
  return { events, dates, order, unknown: events.filter(e => !positioned.has(e.id)) }
}

export function matchesBetween(data: TimelineData, left: string, right: string) {
  const l = new Set(data.events.filter(e => e.sourceWorkId === left).map(e => e.id))
  const r = new Set(data.events.filter(e => e.sourceWorkId === right).map(e => e.id))
  return data.assertions.filter(a => a.predicate === 'depictsSameAs' && a.objectId
    && (a.status === 'proposed' || a.status === 'accepted')
    && ((l.has(a.subjectId) && r.has(a.objectId)) || (r.has(a.subjectId) && l.has(a.objectId))))
}
