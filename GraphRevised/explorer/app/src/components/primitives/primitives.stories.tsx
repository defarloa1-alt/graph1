import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { KINDS } from "../../data/types";
import {
  AttestationBadge, Button, Chip, KindPill, Mock, Pill, Segment, Signpost, StatusPill,
} from "./primitives";

const meta: Meta = { title: "Primitives" };
export default meta;

const col: React.CSSProperties = { display: "flex", flexDirection: "column", gap: 12, maxWidth: 520 };
const row: React.CSSProperties = { display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" };

export const Buttons: StoryObj = {
  render: () => (
    <div style={row}>
      <Button primary>Stand here</Button>
      <Button>Read on Wikipedia ↗</Button>
      <Button>◎ Graph</Button>
      <Button disabled>←</Button>
    </div>
  ),
};

export const Segments: StoryObj = {
  render: function Render() {
    const [persona, setPersona] = useState<"scholar" | "student" | "browser">("scholar");
    const [view, setView] = useState<"graph" | "card" | "video">("card");
    return (
      <div style={col}>
        <Segment label="Who are you exploring as" value={persona} onChange={setPersona}
          options={[{ value: "scholar", label: "Scholar" }, { value: "student", label: "Student" }, { value: "browser", label: "Browsing" }]} />
        <Segment label="View" value={view} onChange={setView}
          options={[{ value: "graph", label: "◎ Graph" }, { value: "card", label: "▤ Card" }, { value: "video", label: "Video", later: true }]} />
      </div>
    );
  },
};

export const Chips: StoryObj = {
  render: () => (
    <div style={row}>
      <Chip>motive 22</Chip>
      <Chip pressed>interpretation 39</Chip>
      <Chip ghost>yours 0</Chip>
      <Chip>jump Cleopatra</Chip>
    </div>
  ),
};

export const Pills: StoryObj = {
  render: () => (
    <div style={col}>
      <div style={row}>{KINDS.map(k => <KindPill key={k} kind={k} />)}</div>
      <div style={row}>
        <StatusPill status="accepted" />
        <StatusPill status="proposed" />
        <StatusPill status="provisional" />
        <Pill>only sources say it</Pill>
        <Pill variant="solid">you are here</Pill>
        <Mock />
      </div>
    </div>
  ),
};

export const Attestation: StoryObj = {
  render: () => (
    <div style={row}>
      {["well attested (4 authors)", "attested (1 author)", "disputed (3 authors)", "one author's reading",
        "a reading shared by 2 authors", "imagined", "no evidence yet"].map(a => <AttestationBadge key={a} attestation={a} />)}
    </div>
  ),
};

export const Signposts: StoryObj = {
  render: function Render() {
    const [open, setOpen] = useState("Participants");
    const rows: [string, string][] = [["Participants", "15"], ["Places", "3"], ["Moments of the battle", "174"], ["Works about it", "6"]];
    return (
      <div style={{ ...col, maxWidth: 300, background: "var(--surface)", padding: 10, border: "1px solid var(--line)", borderRadius: "var(--r)" }}>
        <span className="label">Where to go from here</span>
        <div>
          {rows.map(([label, n]) => <Signpost key={label} label={label} count={n} pressed={open === label} onClick={() => setOpen(label)} />)}
          <Signpost label="Elsewhere in 31 BC" count="empty" />
          <Signpost unread label="Not yet read: the army's surrender" count="grow" />
        </div>
      </div>
    );
  },
};
