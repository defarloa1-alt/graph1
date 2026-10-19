// Kind and lens icons, drawn on a 16px grid for small sizes (D-123, D-118). One markup string per
// icon serves both the React icon and the Cytoscape node picture. The lens icons stand in for the
// IconScout sheet until its licence is confirmed (handoff, next UI item 5).
import type { Kind, Lens } from "../data/types";
import { KIND_SVG, LENS_SVG } from "./markup";

interface IconProps { size?: number; className?: string; title?: string }

function Svg({ size, className, title, markup }: IconProps & { markup: string }) {
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 16 16" fill="none"
      stroke="currentColor" strokeWidth={1.4} strokeLinecap="round" strokeLinejoin="round"
      role={title ? "img" : undefined} aria-label={title} aria-hidden={title ? undefined : true}
      dangerouslySetInnerHTML={{ __html: markup }} />
  );
}

export function KindIcon({ kind, size = 11, ...props }: IconProps & { kind: Kind }) {
  return <Svg size={size} markup={KIND_SVG[kind]} {...props} />;
}

export function LensIcon({ lens, size = 13, ...props }: IconProps & { lens: Lens }) {
  return <Svg size={size} markup={LENS_SVG[lens]} {...props} />;
}
