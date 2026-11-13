import { describe, expect, it } from 'vitest'
import { matchesBetween, parseTimeline, sourceLane } from './timelineModel'
import type { TimelineClaim, TimelineData } from './timelineModel'

const claim = (id: string, predicate: string, subjectId: string, objectId: string | null, workId: string | null): TimelineClaim => ({
  id, predicate, subjectId, objectId, workId, status: 'proposed', mode: workId ? 'attributed' : 'asserted',
  timeExpression: null, timeEdtf: null, relativeOffset: null, startEarliestJdn: null, endLatestJdn: null, evidence: [],
})
const data: TimelineData = {
  sources: [{ workId: 'w1', voice: 'Dio' }, { workId: 'w2', voice: 'Hale' }],
  events: [
    { id: 'a', label: 'A', status: 'proposed', sourceWorkId: 'w1', mentions: [] },
    { id: 'b', label: 'B', status: 'proposed', sourceWorkId: 'w1', mentions: [] },
    { id: 'c', label: 'C', status: 'proposed', sourceWorkId: 'w1', mentions: [] },
    { id: 'd', label: 'D', status: 'proposed', sourceWorkId: 'w2', mentions: [] },
  ],
  assertions: [claim('order', 'happenedBefore', 'a', 'b', 'w1'), claim('match', 'depictsSameAs', 'a', 'd', null),
    claim('wrong-voice', 'happenedBefore', 'b', 'c', 'w2')],
}
describe('source chronology', () => {
  it('only uses attributed order for the source and keeps unconnected events unknown', () => {
    const lane = sourceLane(data, 'w1')
    expect(lane.order.map(x => x.id)).toEqual(['order'])
    expect(lane.unknown.map(x => x.id)).toEqual(['c'])
  })
  it('keeps events with unnormalized time expressions in the unknown-order group', () => {
    const time = { ...claim('time', 'occurred', 'c', null, 'w1'), timeExpression: 'afterwards' }
    const lane = sourceLane({ ...data, assertions: [...data.assertions, time] }, 'w1')
    expect(lane.dates.map(x => x.id)).toEqual(['time'])
    expect(lane.unknown.map(x => x.id)).toEqual(['c'])
  })
  it('compares only explicit cross-source assertions and preserves status', () => {
    expect(matchesBetween(data, 'w1', 'w2').map(x => [x.id, x.status])).toEqual([['match', 'proposed']])
    expect(matchesBetween(data, 'w1', 'w1')).toHaveLength(0)
  })
  it('refuses malformed timeline data', () => {
    expect(() => parseTimeline({ ...data, assertions: [{}] })).toThrow('Invalid source timeline data')
    expect(parseTimeline(data).events).toHaveLength(4)
  })
})
