// The words the explorer shows for stored values, in one place. The wireframe (v8, reviewed by the
// curator) shows the stored status words; 32 decision 11 names other labels (APPROVED; PROPOSED —
// NOT REVIEWED), so a change of wording is a change here only.
import type { Category, ClaimStatus, EntityStatus, Mode } from "./data/types";

export const STATUS_WORDS: Record<ClaimStatus | EntityStatus, string> = {
  accepted: "accepted",
  proposed: "proposed",
  rejected: "rejected",
  superseded: "superseded",
  contested: "contested",
  provisional: "provisional",
  resolved: "resolved",
  deprecated: "deprecated",
};

export const CATEGORY_WORDS: Record<Category, string> = {
  factual: "fact",
  interpretive: "interpretive",
  imaginative: "imaginative",
};

export const MODE_WORDS: Record<Mode, string> = {
  asserted: "we state it",
  attributed: "only sources say it",
};
