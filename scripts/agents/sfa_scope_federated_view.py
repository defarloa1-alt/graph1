#!/usr/bin/env python3
"""
SFA Scope Federated View — Reason over full federated view, produce scoped list for facet.
PREFERRED: python -m scripts.agents.sfa scope --facet POLITICAL [--seed Q17167]

Takes the full federated export (disciplines, LCC, LCSH, entities) and uses LLM
reasoning to filter down to a facet-relevant scoped list. This is the SFA learning
phase: reduce the broad view to what matters for this facet.

Usage:
  python scripts/agents/sfa_scope_federated_view.py --facet POLITICAL
  python scripts/agents/sfa_scope_federated_view.py --facet POLITICAL --input output/reports/federated_roman_republic_20260302_164839.json
  python scripts/agents/sfa_scope_federated_view.py --facet MILITARY --seed Q17167

Output: output/sfa_scoped/{facet}_{seed}_{timestamp}.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root))


def _get_api_key() -> str:
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        env_path = _root / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment or .env")
    return api_key


def call_claude(system_prompt: str, user_message: str, model: str = "claude-sonnet-4-6", max_tokens: int = 12000) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=_get_api_key())
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


def load_federated(input_path: Path | None, reports_dir: Path) -> dict:
    """Load most recent federated export, or from specified path."""
    if input_path and input_path.exists():
        with open(input_path, encoding="utf-8") as f:
            return json.load(f)
    files = sorted(reports_dir.glob("federated_roman_republic_*.json"))
    if not files:
        raise FileNotFoundError(
            f"No federated export found in {reports_dir}. Run export_federated_roman_republic.py first."
        )
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


def build_context(federated: dict) -> str:
    """Build context string for the LLM (truncate if too large)."""
    sections = federated.get("sections", {})
    lines = [
        f"DOMAIN: Roman Republic ({federated.get('seed_qid', 'Q17167')})",
        "",
        "── POSITIONED_AS (subject anchors) ──",
    ]
    for p in sections.get("positioned_as", []):
        lines.append(f"  {p['qid']} {p['label']} ({p.get('rel_type')})")
    lines.extend(["", "── DISCIPLINES (sample with Dewey/LCC/LCSH/FAST) ──"])
    for d in sections.get("disciplines_relevant", [])[:50]:
        ids = [f"{k}={v}" for k, v in [("Dewey", d.get("dewey")), ("LCC", d.get("lcc")), ("LCSH", d.get("lcsh_id")), ("FAST", d.get("fast_id"))] if v]
        lines.append(f"  {d['qid']} {d.get('label', '')[:50]}: {', '.join(ids)}")
    lines.extend(["", "── ENTITY ONTOLOGY (institutions, places, events) ──"])
    for e in sections.get("entity_ontology", [])[:40]:
        lines.append(f"  {e['qid']} {e.get('label', '')[:50]} ({e.get('entity_type', '')})")
    if sections.get("lcc_classes"):
        lines.extend(["", "── LCC CLASSES (sample) ──"])
        for l in sections["lcc_classes"][:30]:
            lines.append(f"  {l.get('code')} {l.get('label', '')[:60]}")
    if sections.get("lcsh_headings"):
        lines.extend(["", "── LCSH HEADINGS ──"])
        for l in sections["lcsh_headings"][:30]:
            lines.append(f"  {l.get('lcsh_id')} {l.get('label', '')[:60]}")
    return "\n".join(lines)


SYSTEM_PROMPT = """\
You are SFA_{facet}, the Subject Facet Agent for the {facet} facet of Chrystallum — a federated \
historical knowledge graph covering the Roman Republic (509–27 BCE).

There are 18 facet agents: POLITICAL, LEGAL, SOCIAL, ARTISTIC, MILITARY, GEOGRAPHIC, etc. Each has \
its own scope. You scope ONLY for the {facet} perspective.

Your task: REASON over the full federated view and produce a SCOPED LIST for the {facet} facet. \
Filter down to what is relevant when viewed through the {facet} lens — not through Legal, Social, \
Artistic, or other facets.

Rules:
1. FOCUS on the {facet} perspective only. Exclude items that belong primarily to other facets.
   - POLITICAL: governance, power structures, sovereignty, institutions, citizenship as political status. \
     Include law only where it is an instrument of political power (e.g. quaestiones as political battleground). \
     Exclude legal doctrine per se (that is LEGAL facet). Exclude social structure per se (SOCIAL facet). \
     Exclude artistic merit per se (ARTISTIC facet).
   - LEGAL: would focus on law, courts, procedure — you are NOT the Legal facet.
   - SOCIAL: would focus on classes, patronage, family — you are NOT the Social facet.
   - ARTISTIC: would focus on art, monuments, iconography as art — you are NOT the Artistic facet.
2. When in doubt, ask: "Is this primarily about {facet}?" If it could equally belong to another facet, \
   include only if the {facet} angle is dominant.
3. Include LCC/LCSH/entities that support {facet} claims, not adjacent facets.
4. Provide brief rationale tying each inclusion to the {facet} perspective.
5. Keep the scoped list manageable: 15–40 disciplines, 10–25 LCC, 10–20 LCSH, 10–25 entities.

OUTPUT: Return ONLY valid JSON matching this schema — no prose, no markdown fences:
{{
  "facet": "{facet}",
  "seed_qid": "{seed_qid}",
  "scoped_disciplines": [
    {{"qid": "Q...", "label": "...", "dewey": "...", "lcc": "...", "lcsh_id": "...", "fast_id": "...", "rationale": "1 sentence"}}
  ],
  "scoped_lcc": [
    {{"code": "...", "label": "...", "rationale": "1 sentence"}}
  ],
  "scoped_lcsh": [
    {{"lcsh_id": "...", "label": "...", "rationale": "1 sentence"}}
  ],
  "scoped_entities": [
    {{"qid": "Q...", "label": "...", "entity_type": "...", "rationale": "1 sentence"}}
  ],
  "sfa_rationale": "2–3 sentences: overall scope reasoning for this facet"
}}
"""


def scope(facet: str, seed_qid: str = "Q17167", input_path: Path | None = None,
          reports_dir: Path | None = None, model: str = "claude-sonnet-4-6") -> dict:
    reports_dir = reports_dir or _root / "output" / "reports"
    federated = load_federated(input_path, reports_dir)
    context = build_context(federated)

    system = SYSTEM_PROMPT.format(facet=facet, seed_qid=seed_qid)
    user = f"Scope the federated view for the {facet} facet of Roman Republic.\n\n{context}"

    print(f"SFA_{facet}: scoping federated view for {seed_qid}")
    print(f"  Context: {len(context)} chars")
    raw = call_claude(system, user, model=model)

    # Parse JSON
    stripped = raw.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        stripped = "\n".join(lines[1:])
        if stripped.rstrip().endswith("```"):
            stripped = stripped[: stripped.rfind("```")].rstrip()
    try:
        result = json.loads(stripped)
    except json.JSONDecodeError as e:
        print(f"  WARNING: JSON parse failed ({e})")
        result = {"parse_error": str(e), "raw": raw}

    # Save
    out_dir = _root / "output" / "sfa_scoped"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{facet}_{seed_qid}_{ts}.json"
    envelope = {
        "facet": facet,
        "seed_qid": seed_qid,
        "scoped_at": datetime.now(timezone.utc).isoformat(),
        "input_export": str(input_path) if input_path else "latest",
        "output": result,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {out_path}")

    return envelope


def main():
    parser = argparse.ArgumentParser(description="SFA scope federated view for facet")
    parser.add_argument("--facet", required=True,
                        choices=["POLITICAL", "MILITARY", "GEOGRAPHIC", "ECONOMIC", "SOCIAL", "RELIGIOUS",
                                 "BIOGRAPHICAL", "INTELLECTUAL", "ARCHAEOLOGICAL", "LINGUISTIC", "DIPLOMATIC",
                                 "CULTURAL", "ENVIRONMENTAL", "TECHNOLOGICAL", "ARTISTIC", "SCIENTIFIC",
                                 "DEMOGRAPHIC", "COMMUNICATION"],
                        help="Facet to scope for")
    parser.add_argument("--seed", default="Q17167",
                        help="Seed QID (default: Q17167)")
    parser.add_argument("--input", type=Path, default=None,
                        help="Path to federated JSON (default: latest in output/reports)")
    parser.add_argument("--model", default="claude-sonnet-4-6",
                        help="Claude model")
    args = parser.parse_args()

    result = scope(facet=args.facet, seed_qid=args.seed, input_path=args.input, model=args.model)

    out = result.get("output", {})
    if "parse_error" not in out:
        print()
        print(f"-- SCOPED FOR {args.facet} " + "-" * 40)
        print(f"  Disciplines: {len(out.get('scoped_disciplines', []))}")
        print(f"  LCC:         {len(out.get('scoped_lcc', []))}")
        print(f"  LCSH:        {len(out.get('scoped_lcsh', []))}")
        print(f"  Entities:   {len(out.get('scoped_entities', []))}")
        if out.get("sfa_rationale"):
            print(f"  Rationale:   {out['sfa_rationale'][:80]}...")


if __name__ == "__main__":
    main()
