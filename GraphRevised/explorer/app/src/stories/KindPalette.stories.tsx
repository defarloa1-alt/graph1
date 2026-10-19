// PROPOSAL, not adopted: colour by kind (26 §8 leaves it undecided). For the curator's review.
import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { Chip, Mock } from "../components/primitives/primitives";
import type { Kind, Lens } from "../data/types";
import { KindIcon, LensIcon } from "../icons/icons";
import { LENS_NAMES } from "../icons/markup";

const meta: Meta = { title: "Proposals/Kind palette" };
export default meta;

// Three families, not ten colours: on a graph any two nodes can sit side by side, and only three
// hues stay apart for every reader there (checked with the dataviz validator, all pairs, both modes).
// Cool hues only, so no family is mistaken for a lens (the lenses are warm).
const FAMILIES = [
  { key: "who", name: "Who", kinds: ["Person", "Group", "Office"] as Kind[], light: "#2a78d6", dark: "#3987e5" },
  { key: "when", name: "What happened", kinds: ["Event", "Period"] as Kind[], light: "#1baf7a", dark: "#1baf7a" },
  { key: "where", name: "Where", kinds: ["Place", "Polity"] as Kind[], light: "#008300", dark: "#008300" },
  { key: "text", name: "Texts and ideas", kinds: ["Work", "Concept", "Type"] as Kind[], light: null, dark: null },
];

const familyOf = (k: Kind) => FAMILIES.find(f => f.kinds.includes(k))!;

const css = `
.kp { --who: #2a78d6; --when: #1baf7a; --where: #008300; --text: var(--ink-2); }
:root[data-theme="dark"] .kp { --who: #3987e5; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .kp { --who: #3987e5; } }
.kp.lens-on { --who: var(--ink-2); --when: var(--ink-2); --where: var(--ink-2); }
.kp-node { display: inline-flex; flex-direction: column; align-items: center; gap: 4px; width: 70px; text-align: center; font-size: var(--fs-canvas); line-height: 1.2; }
.kp-disc { width: 30px; height: 30px; border-radius: 50%; background: var(--surface); border: 2px solid var(--c); color: var(--c); display: grid; place-items: center; }
.kp-disc.proposed { border-style: dashed; opacity: .55; }
.kp-name { display: inline-flex; gap: 4px; align-items: center; }
.kp-name svg { color: var(--c); }
.kp-edge { stroke: var(--ink-3); stroke-width: 1.5; }
.kp-edge.lens { stroke: var(--lens-military); stroke-width: 2.5; }
`;

const NODES: { label: string; kind: Kind; status?: string; x: number; y: number }[] = [
  { label: "Battle of Actium", kind: "Event", x: 250, y: 110 },
  { label: "Mark Antony", kind: "Person", x: 90, y: 40 },
  { label: "Cleopatra", kind: "Person", x: 90, y: 180 },
  { label: "Antony's fleet", kind: "Group", x: 420, y: 40 },
  { label: "Actium promontory", kind: "Place", x: 420, y: 180 },
  { label: "Roman Republic", kind: "Polity", status: "proposed", x: 250, y: 230 },
  { label: "Plutarch, Life of Antony", kind: "Work", x: 250, y: 10 },
  { label: "decisive battle", kind: "Concept", x: 540, y: 110 },
];

function Canvas({ lens }: { lens: Lens | null }) {
  const at = (l: string) => NODES.find(n => n.label === l)!;
  const lines: [string, string, boolean][] = [
    ["Mark Antony", "Battle of Actium", true], ["Cleopatra", "Battle of Actium", true], ["Antony's fleet", "Battle of Actium", true],
    ["Battle of Actium", "Actium promontory", true], ["Battle of Actium", "Roman Republic", false],
    ["Battle of Actium", "Plutarch, Life of Antony", false], ["Battle of Actium", "decisive battle", false],
  ];
  return (
    <div style={{ position: "relative", width: 620, height: 280, background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "var(--r)" }}>
      <svg width={620} height={280} style={{ position: "absolute", inset: 0 }}>
        {lines.map(([a, b, military]) => (
          <line key={a + b} className={`kp-edge ${lens === "military" && military ? "lens" : ""}`}
            x1={at(a).x + 35} y1={at(a).y + 15} x2={at(b).x + 35} y2={at(b).y + 15} />
        ))}
      </svg>
      {NODES.map(n => (
        <span key={n.label} className="kp-node" style={{ position: "absolute", left: n.x, top: n.y, ["--c" as string]: `var(--${familyOf(n.kind).key})` }}>
          <span className={`kp-disc ${n.status === "proposed" ? "proposed" : ""}`}><KindIcon kind={n.kind} size={14} /></span>
          {n.label}
        </span>
      ))}
    </div>
  );
}

export const Proposal: StoryObj = {
  render: function Render() {
    const [lens, setLens] = useState<Lens | null>(null);
    return (
      <div className={`kp ${lens ? "lens-on" : ""}`} style={{ display: "flex", flexDirection: "column", gap: 16, maxWidth: 680 }}>
        <style>{css}</style>
        <div>
          <span className="label">Proposal · not adopted</span> <Mock>for review</Mock>
          <p style={{ maxWidth: 620 }}>
            Ten kinds are too many colours to tell apart. This groups them into three coloured families and one
            uncoloured family; the icon still says the exact kind. Colour sits in the ring and the icon only, never
            the text. When a lens is on, the kind colours go grey, so the lens is the only colour on the stage.
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
          {FAMILIES.map(f => (
            <div key={f.key} style={{ ["--c" as string]: `var(--${f.key})`, display: "flex", flexDirection: "column", gap: 4 }}>
              <div style={{ height: 6, borderRadius: 3, background: f.light ? "var(--c)" : "var(--line)" }} />
              <strong>{f.name}</strong>
              {f.kinds.map(k => <span key={k} className="kp-name"><KindIcon kind={k} />{k}</span>)}
              <span className="mono muted" style={{ fontSize: "var(--fs-mono)" }}>{f.light ? `${f.light} / ${f.dark}` : "ink, no colour"}</span>
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <span className="label">Lens</span>
          <Chip pressed={!lens} onClick={() => setLens(null)}>none</Chip>
          <Chip pressed={lens === "military"} onClick={() => setLens("military")}>
            <span style={{ color: "var(--lens-military)", display: "inline-flex", gap: 4, alignItems: "center" }}><LensIcon lens="military" />{LENS_NAMES.military}</span>
          </Chip>
        </div>
        <Canvas lens={lens} />
        <div className="muted" style={{ maxWidth: 620 }}>
          <strong>Checked</strong> (dataviz validator, all pairs, light #ffffff and dark #1c2023 surfaces): worst pair
          green and aqua, ΔE 15.6 normal vision and 15.2 deuteranopia (targets 15 and 8). Aqua sits at 2.8:1 on white,
          so every node keeps its label beside it. <strong>Why kind colour steps back under a lens:</strong> the
          green family and the economic lens's gold read as the same colour to protanopes (ΔE 1.3).
          <br /><strong>Open for you:</strong> is a Polity "where" or "who"? Is an Office "who"?
        </div>
      </div>
    );
  },
};
