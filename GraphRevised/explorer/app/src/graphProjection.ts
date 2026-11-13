import type { Placement, Route, SubjectView, ViewNode } from './subjectView'

export interface PhaseNode { event: ViewNode; placement: Placement }
export interface TopicNode { event: ViewNode; route: Route }

export function battleGraph(view: SubjectView): { phases: PhaseNode[]; topics: TopicNode[] } {
  const phases = new Map<string, PhaseNode>()
  const topics = new Map<string, TopicNode>()
  const phasePrefix = `chr:entity:phase:${view.focus.id.startsWith('chr:entity:') ? view.focus.id.slice('chr:entity:'.length) : view.focus.id}:`
  for (const assertion of view.assertions) {
    for (const route of assertion.routes) {
      if (route.kind === 'subjectPlacement' && route.section && route.topicalPlacement) {
        topics.set(route.events[0].id, { event: route.events[0], route })
      }
      if (route.kind !== 'partOf') continue
      for (let i = 0; i < route.placements.length; i++) {
        const event = route.events[i]
        if (event.id.startsWith(phasePrefix) && route.events[i + 1].id === view.focus.id) {
          phases.set(route.placements[i].id, { event, placement: route.placements[i] })
        }
      }
    }
  }
  const byLabel = <T extends { event: ViewNode }>(a: T, b: T) =>
    (a.event.label || a.event.id).localeCompare(b.event.label || b.event.id)
  return { phases: [...phases.values()].sort(byLabel), topics: [...topics.values()].sort(byLabel) }
}
