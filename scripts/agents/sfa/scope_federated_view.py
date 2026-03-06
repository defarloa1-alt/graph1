"""SFA Scope Federated View."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

def _get_api_key():
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key and (_root / ".env").exists():
        for line in (_root / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found")
    return api_key

def call_claude(system_prompt, user_message, model="claude-sonnet-4-6", max_tokens=12000):
    import anthropic
    client = anthropic.Anthropic(api_key=_get_api_key())
    msg = client.messages.create(model=model, max_tokens=max_tokens,
        system=system_prompt, messages=[{"role": "user", "content": user_message}])
    return msg.content[0].text

def load_federated(input_path, reports_dir):
    if input_path and Path(input_path).exists():
        with open(input_path, encoding="utf-8") as f:
            return json.load(f)
    files = sorted(Path(reports_dir).glob("federated_roman_republic_*.json"))
    if not files:
        raise FileNotFoundError(f"No federated export in {reports_dir}")
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)

def build_context(federated):
    sections = federated.get("sections", {})
    lines = [f"DOMAIN: Roman Republic ({federated.get('seed_qid', 'Q17167')})", ""]
    for p in sections.get("positioned_as", []):
        lines.append(f"  {p['qid']} {p['label']} ({p.get('rel_type')})")
    lines.extend(["", "── DISCIPLINES ──"])
    for d in sections.get("disciplines_relevant", [])[:50]:
        ids = [f"{k}={v}" for k, v in [("Dewey", d.get("dewey")), ("LCC", d.get("lcc")), ("LCSH", d.get("lcsh_id"))] if v]
        lines.append(f"  {d['qid']} {d.get('label','')[:50]}: {', '.join(ids)}")
    lines.extend(["", "── ENTITY ONTOLOGY ──"])
    for e in sections.get("entity_ontology", [])[:40]:
        lines.append(f"  {e['qid']} {e.get('label','')[:50]} ({e.get('entity_type','')})")
    if sections.get("lcc_classes"):
        for l in sections["lcc_classes"][:30]:
            lines.append(f"  {l.get('code')} {l.get('label','')[:60]}")
    if sections.get("lcsh_headings"):
        for l in sections["lcsh_headings"][:30]:
            lines.append(f"  {l.get('lcsh_id')} {l.get('label','')[:60]}")
    return "\n".join(lines)

SYSTEM_PROMPT = """You are SFA_{facet} for Chrystallum. Scope the federated view for the {facet} facet.
Rules: FOCUS on {facet} only. Exclude items belonging to other facets.
OUTPUT: Return ONLY valid JSON: {{"facet":"{facet}","seed_qid":"{seed_qid}",
  "scoped_disciplines":[{{"qid":"Q...","label":"...","rationale":"..."}}],
  "scoped_lcc":[{{"code":"...","label":"...","rationale":"..."}}],
  "scoped_lcsh":[{{"lcsh_id":"...","label":"...","rationale":"..."}}],
  "scoped_entities":[{{"qid":"Q...","label":"...","rationale":"..."}}],
  "sfa_rationale":"2-3 sentences"}}
"""

def scope(facet, seed_qid="Q17167", input_path=None, reports_dir=None, model="claude-sonnet-4-6"):
    reports_dir = Path(reports_dir or _root / "output" / "reports")
    federated = load_federated(input_path, reports_dir)
    context = build_context(federated)
    system = SYSTEM_PROMPT.format(facet=facet, seed_qid=seed_qid)
    user = f"Scope for {facet} facet.\n\n{context}"
    print(f"SFA_{facet}: scoping for {seed_qid}")
    raw = call_claude(system, user, model=model)
    stripped = raw.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        stripped = "\n".join(lines[1:])
        if stripped.rstrip().endswith("```"):
            stripped = stripped[:stripped.rfind("```")].rstrip()
    try:
        result = json.loads(stripped)
    except json.JSONDecodeError as e:
        result = {"parse_error": str(e), "raw": raw}
    out_dir = _root / "output" / "sfa_scoped"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{facet}_{seed_qid}_{ts}.json"
    envelope = {"facet": facet, "seed_qid": seed_qid, "scoped_at": datetime.now(timezone.utc).isoformat(),
        "input_export": str(input_path) if input_path else "latest", "output": result}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {out_path}")
    return envelope
