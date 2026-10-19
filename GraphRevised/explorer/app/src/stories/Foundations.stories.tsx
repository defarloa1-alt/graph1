import type { Meta, StoryObj } from "@storybook/react-vite";
import { KINDS, LENSES } from "../data/types";
import { KindIcon, LensIcon } from "../icons/icons";
import { LENS_NAMES } from "../icons/markup";

const meta: Meta = { title: "Foundations" };
export default meta;

const COLOURS: [string, string][] = [
  ["--bg", "page"], ["--surface", "panels and cards"], ["--fill", "hover, ranges"], ["--line", "hairlines"],
  ["--ink", "text"], ["--ink-2", "secondary text"], ["--ink-3", "muted, labels"],
  ["--strong", "pressed, primary"], ["--on-strong", "text on strong"],
];

const row: React.CSSProperties = { display: "flex", flexWrap: "wrap", gap: 12, alignItems: "flex-end" };
const section: React.CSSProperties = { display: "flex", flexDirection: "column", gap: 10, marginBottom: 28 };

export const Colours: StoryObj = {
  render: () => (
    <div style={section}>
      <span className="label">Greyscale (Figma: Color, Light and Dark)</span>
      <div style={row}>
        {COLOURS.map(([v, use]) => (
          <div key={v} style={{ width: 92 }}>
            <div style={{ height: 44, background: `var(${v})`, border: "1px solid var(--line)", borderRadius: "var(--r)" }} />
            <div className="mono" style={{ fontSize: "var(--fs-label)" }}>{v}</div>
            <div className="muted">{use}</div>
          </div>
        ))}
      </div>
      <span className="label">Lenses: colour only for the lens in use (D-118)</span>
      <div style={row}>
        {LENSES.map(l => (
          <div key={l} style={{ width: 92, color: `var(--lens-${l})` }}>
            <div style={{ height: 44, background: `var(--lens-${l})`, borderRadius: "var(--r)" }} />
            <div style={{ display: "flex", gap: 4, alignItems: "center", fontWeight: 700 }}><LensIcon lens={l} />{LENS_NAMES[l]}</div>
          </div>
        ))}
      </div>
    </div>
  ),
};

const TYPE: [string, string, string][] = [
  ["--fs-read", "Reading: the account, notes, quotations", "body"],
  ["--fs-title", "Card title", "body"],
  ["--fs-body", "Body", "body"],
  ["--fs-small", "Small", "body"],
  ["--fs-chrome", "Chrome: buttons, sidebars, the stage row", "body"],
  ["--fs-label", "LABEL", "mono"],
  ["--fs-mono", "MONO: PILLS, LOCATORS", "mono"],
  ["--fs-canvas", "Canvas labels", "body"],
];

export const Type: StoryObj = {
  render: () => (
    <div style={section}>
      <span className="label">Type scale (D-121): chrome ~20% smaller, reading text ~13</span>
      {TYPE.map(([v, text, face]) => (
        <div key={v} style={{ display: "grid", gridTemplateColumns: "110px 1fr", alignItems: "baseline", gap: 12 }}>
          <span className="mono muted" style={{ fontSize: "var(--fs-label)" }}>{v}</span>
          <span style={{ fontSize: `var(${v})`, fontFamily: face === "mono" ? "var(--font-mono)" : undefined }}>
            {text} · Mark Antony participated in Battle of Actium
          </span>
        </div>
      ))}
    </div>
  ),
};

export const Icons: StoryObj = {
  render: () => (
    <div style={section}>
      <span className="label">Kinds (D-123)</span>
      <div style={row}>
        {KINDS.map(k => (
          <span key={k} style={{ display: "inline-flex", flexDirection: "column", alignItems: "center", gap: 4, width: 64 }}>
            <KindIcon kind={k} size={22} />
            <span>{k}</span>
          </span>
        ))}
      </div>
      <span className="label">At text size, beside a name</span>
      <div style={row}>
        {KINDS.map(k => <span key={k}><KindIcon kind={k} /> {k}</span>)}
      </div>
    </div>
  ),
};
