// The icons' markup, shared by the React icons and the Cytoscape node pictures.
import type { Kind, Lens } from "../data/types";

export const KIND_SVG: Record<Kind, string> = {
  Person: '<circle cx="8" cy="5" r="2.6"/><path d="M3 14c0-2.8 2.2-4.8 5-4.8s5 2 5 4.8"/>',
  Event: '<rect x="2.5" y="3.5" width="11" height="10" rx="1.5"/><path d="M2.5 6.5h11M5.5 2v3M10.5 2v3"/>',
  Place: '<path d="M8 14.5s4.5-4.6 4.5-8a4.5 4.5 0 0 0-9 0c0 3.4 4.5 8 4.5 8z"/><circle cx="8" cy="6.5" r="1.6"/>',
  Group: '<circle cx="5.5" cy="5.5" r="2"/><circle cx="11" cy="6" r="1.7"/><path d="M1.8 13.5c0-2.2 1.7-3.8 3.7-3.8s3.7 1.6 3.7 3.8M9.5 10c2 0 4.2 1.2 4.2 3.5"/>',
  Office: '<path d="M5.5 2.5v11M8 2.5v11M10.5 2.5v11M4.5 5h7M4.5 11h7M10.5 3l3-1.2v3.4z"/>',
  Work: '<path d="M2.5 3.5h4A1.5 1.5 0 0 1 8 5v8.5A1.5 1.5 0 0 0 6.5 12h-4zM13.5 3.5h-4A1.5 1.5 0 0 0 8 5v8.5A1.5 1.5 0 0 1 9.5 12h4z"/>',
  Concept: '<path d="M5.5 10.3a4 4 0 1 1 5 0V12h-5zM6 14h4"/>',
  Period: '<path d="M4 2h8M4 14h8M5 2.5c0 3 6 2.5 6 5.5s-6 2.5-6 5.5M11 2.5c0 3-6 2.5-6 5.5s6 2.5 6 5.5"/>',
  Polity: '<path d="M4 14V2M4 3h8l-1.5 2.5L12 8H4"/>',
  Type: '<path d="M2.5 2.5h5l6 6-5 5-6-6zM5.3 5.3h.01"/>',
};

export const LENS_SVG: Record<Lens, string> = {
  military: '<circle cx="8" cy="8.5" r="4.3"/><path d="M2.5 2.5l11 11M13.5 2.5l-11 11"/>',
  social: '<circle cx="4.8" cy="5.2" r="1.7"/><circle cx="11.2" cy="5.2" r="1.7"/><circle cx="8" cy="3.8" r="1.7"/><path d="M2.4 14v-3.2c0-1.4 1.1-2.4 2.4-2.4M13.6 14v-3.2c0-1.4-1.1-2.4-2.4-2.4M5.6 14V9.4C5.6 8 6.7 7 8 7s2.4 1 2.4 2.4V14"/>',
  political: '<path d="M2 6L8 2.5 14 6zM2.5 13.5h11M3.8 6.5v6.2M6.6 6.5v6.2M9.4 6.5v6.2M12.2 6.5v6.2"/>',
  economic: '<ellipse cx="6" cy="12.2" rx="3.4" ry="1.3"/><ellipse cx="6" cy="9.6" rx="3.4" ry="1.3"/><path d="M12 14V3.5M12 5.8l-1.6-1.6M12 5.8l1.6-1.6M12 8.8l-1.6-1.6M12 8.8l1.6-1.6"/>',
  religious: '<path d="M4 14h8M5 14V9.2h6V14M3.5 9.2h9M8 7.6c-1.4-1-1.4-2.6 0-4.6 1.4 2 1.4 3.6 0 4.6z"/>',
};

export const LENS_NAMES: Record<Lens, string> = {
  military: "Military", social: "Social", political: "Political", economic: "Economic", religious: "Religious",
};

/** The kind icon as an image for a Cytoscape node with no picture, stroked in the given ink. */
export function kindIconUri(kind: Kind, stroke: string): string {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none" stroke="${stroke}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">${KIND_SVG[kind]}</svg>`;
  return "data:image/svg+xml;utf8," + encodeURIComponent(svg);
}
