// The shapes the explorer receives (26-UI-DATA-CONTRACT.md). Shapes 2 (fact) and 3 (voice) are
// what export/cytoscape.py emits today; the rest follow the contract as it is specified.

export const KINDS = [
  "Person", "Event", "Place", "Group", "Office", "Work", "Concept", "Period", "Polity", "Type",
  "Question", "Position", "Law", "Decree",
] as const;
export type Kind = (typeof KINDS)[number];

export type EntityStatus = "proposed" | "provisional" | "resolved" | "deprecated";
export type ClaimStatus = "accepted" | "proposed" | "rejected" | "superseded" | "contested";
export type Category = "factual" | "interpretive" | "imaginative";
export type Mode = "asserted" | "attributed";

export const LENSES = ["military", "social", "political", "economic", "religious"] as const;
export type Lens = (typeof LENSES)[number];

export type Persona = "scholar" | "student" | "browser";

/** One quotation behind a voice: the source's own words, where, and a link to read them (D-127). */
export interface Quote {
  source: string;
  locator: string | null;
  url?: string | null;
  quotation: string | null;
  /** evidence not yet reviewed */
  pending?: boolean;
}

export interface ReviewStep {
  operation: string;
  status: string;
  decidedBy: string | null;
  decidedAt?: string | null;
}

/** Shape 3: one claim behind a fact, "according to" a Work or our own statement. */
export interface Voice {
  accordingTo: string | null;
  status: ClaimStatus;
  mode?: Mode;
  time?: string | null;
  role?: string | null;
  context?: string | null;
  /** how a Work holds a Position (44): originates, adopts, modifies */
  stance?: Stance | null;
  /** how a Position stood in scholarship over the voice's time (44) */
  reception?: Reception | null;
  quotes: Quote[];
  review: ReviewStep[];
}

export type Stance = "originates" | "adopts" | "modifies";
export type Reception = "dominant" | "contested" | "minority" | "abandoned";

/** One step of a Position's timeline (44 §3): a Work that held or rejected it, and when. The
 *  holder is the Work, named by its author; `reporter` is the Work that says so when it is not
 *  the holder itself. Ancient holders come first, then the rest by date. */
export interface PositionStep {
  verb: "holds" | "rejects";
  holder: string;
  name: string;
  time: string | null;
  start: number | null;
  ancient: boolean;
  stance: Stance | null;
  reporter: string | null;
  status: ClaimStatus;
  claimId: string;
}

export interface PositionReception {
  reception: Reception | string;
  time: string | null;
  according: string | null;
  status: ClaimStatus;
  claimId: string;
}

/** What a Position node carries besides its facts (export/cytoscape.py). `history` is the
 *  Position's attestation: who held and rejected it, when, in words; never "well attested". */
export interface PositionData {
  history: string;
  timeline: PositionStep[];
  receptions: PositionReception[];
}

/** Shape 2: one line on the canvas, every claim with the same subject, predicate, and object. */
export interface Fact {
  id: string;
  source: string;
  target: string | null;
  label: string;
  sentence: string;
  predicate?: string;
  category: Category;
  status: ClaimStatus;
  mode: Mode;
  /** words, never a number (D-033) */
  attestation: string;
  times: string[];
  voices: Voice[];
}
