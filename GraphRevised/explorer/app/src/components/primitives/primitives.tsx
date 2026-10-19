// The small parts every card and bar is built from. Each one is a plain element with the
// wireframe's class, so the Figma components, the wireframe, and the app stay one design.
import type { ButtonHTMLAttributes, ReactNode } from "react";
import type { ClaimStatus, EntityStatus, Kind } from "../../data/types";
import { KindIcon } from "../../icons/icons";
import { STATUS_WORDS } from "../../words";
import "./primitives.css";

const cx = (...names: (string | false | null | undefined)[]) => names.filter(Boolean).join(" ");

export function Button({ primary, className, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { primary?: boolean }) {
  return <button type="button" className={cx("btn", primary && "primary", className)} {...props} />;
}

export interface SegmentOption<V extends string> { value: V; label: ReactNode; later?: boolean }

/** A one-of-several switch: persona, Graph or Card, theme. */
export function Segment<V extends string>({ options, value, onChange, label }: {
  options: SegmentOption<V>[]; value: V; onChange: (value: V) => void; label: string;
}) {
  return (
    <span className="seg" role="group" aria-label={label}>
      {options.map(o => (
        <button key={o.value} type="button" className={o.later ? "later" : undefined}
          aria-pressed={o.value === value} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </span>
  );
}

export function Chip({ pressed, ghost, className, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & {
  pressed?: boolean; ghost?: boolean;
}) {
  return <button type="button" className={cx("chip", ghost && "ghost", className)} aria-pressed={pressed} {...props} />;
}

export function Pill({ variant, children }: { variant?: "dashed" | "solid"; children: ReactNode }) {
  return <span className={cx("pill", variant)}>{children}</span>;
}

export function KindPill({ kind }: { kind: Kind }) {
  return <Pill><KindIcon kind={kind} />{kind}</Pill>;
}

/** Status in words, and redundantly in the border: dashed while proposed (32 decision 11). */
export function StatusPill({ status }: { status: ClaimStatus | EntityStatus }) {
  return <Pill variant={status === "proposed" ? "dashed" : undefined}>{STATUS_WORDS[status]}</Pill>;
}

/** Attestation is words the server works out, never a number (D-033). */
export function AttestationBadge({ attestation }: { attestation: string }) {
  return <span className="badge">{attestation}</span>;
}

/** A door out of where you stand: a group with its count, or "Not yet read". */
export function Signpost({ label, count, unread, pressed, onClick }: {
  label: ReactNode; count?: ReactNode; unread?: boolean; pressed?: boolean; onClick?: () => void;
}) {
  return (
    <button type="button" className={cx("signpost", unread && "unread")} aria-pressed={pressed} onClick={onClick}>
      {label}
      {count != null && <span className="n">{count}</span>}
    </button>
  );
}

/** Marks what is designed but not built (D-110). */
export function Mock({ children = "mock" }: { children?: ReactNode }) {
  return <span className="mock">{children}</span>;
}
