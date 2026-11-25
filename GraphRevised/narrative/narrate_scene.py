"""Write a scene's narration (scenes/NARRATION.md): one model call, then the check; one repair round.

    python -m GraphRevised.narrative.narrate_scene <scene.narration-input.json> [--persona browser]
        [--rules GraphRevised/scenes/NARRATION.md] [--model claude-opus-5-5] [--fresh] [--stamp]

Needs a named budget (CHRYSTALLUM_BUDGET; the spend meter prices and caps the call). The model sees the
narration rules and the scene's narration input, and returns lines keyed to statement ids. The check
(narrative/narration_check.py) runs on the result; if it finds problems, they go back to the model once.
A narration that passes is written beside the scene as <scene>.narration.<persona>.json; one that does
not is written as <scene>.narration.<persona>.rejected.json with its problems, for the curator. The
scene's id and contentHash are copied from the input, never from the model. Nothing goes into the graph:
a narration is a made presentation, never evidence.

Only what changed is rewritten. A narration records a fingerprint of each step it was written from
(`stepHashes`). When the scene changes, only the steps whose fingerprint changed go to the model; every
other step keeps its lines word for word, so their voiced clips stay valid (narrative/voice_scene.py
re-voices only lines whose text changed). If no step changed, nothing is called. The merged narration is
checked whole. --fresh rewrites every step; --stamp records the fingerprints on an existing narration
written for this exact scene version, calling nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from GraphRevised.narrative.narration_check import check

ROOT = Path(__file__).resolve().parents[1]
MODEL = "claude-opus-5-5"


class Line(BaseModel):
    id: str = Field(description="n<step order>.<n>, e.g. n6.1")
    kind: Literal["narration", "transition", "quote"]
    text: str
    keys: list[str] = Field(description="statement ids, or <stepId>:ordersOfBattle|routes|disputed|corrected; empty for a transition")
    basis: Literal["sourced", "inferred", "not-checked"] | None = Field(description="the weakest basis among the keys; null for a transition")
    voice: str | None = Field(description="for a quote line: the locator it reads; else null")
    estSeconds: float = Field(description="spoken length, about 2.6 words a second")


class Step(BaseModel):
    stepId: str
    lines: list[Line]


class Narration(BaseModel):
    steps: list[Step]


SYSTEM = """You write the narration for an animated history scene in Chrystallum, a history graph with strict provenance.
The rules below are the contract; follow them exactly. Return every step of the scene, in order, each with its lines.

Keys: a narration or quote line keys the statement ids it voices (statements[].id). To voice a step's two versions
of an order of battle or a route, its open debate, or its correction, key "<step id>:ordersOfBattle",
"<step id>:routes", "<step id>:disputed" or "<step id>:corrected". A transition carries no claim and keys nothing.
Never put a number, name or date in a line that is not in what that line keys (the statement, its quotations,
the step's title and time words). Put words in quotation marks only when they are copied exactly from a quotation
under the line's keys. Word an inferred line as a reading ("probably", "we have drawn"); a not-checked line must
say the sources we hold do not give it, or be left out. Mark each line's basis as the weakest of its keys.

THE RULES:
"""


def request(model: str, rules: str, scene_input: str, persona: str) -> dict:
    return {
        "model": model, "max_tokens": 16000,
        "system": [{"type": "text", "text": SYSTEM + rules}],
        "messages": [{"role": "user", "content": f"Persona: {persona}.\n\nThe scene (narration input):\n{scene_input}"}],
        "output_format": Narration,
        # a policy decline falls back to another model inside the same call (beta; not in this SDK's signature)
        "betas": ["server-side-fallback-2026-07-01"], "extra_body": {"fallbacks": "default"},
    }


def call(client, req: dict) -> tuple[Narration | None, dict]:
    response = client.beta.messages.parse(**req)
    meta = {"model": response.model, "stopReason": response.stop_reason, "requestId": response._request_id,
            "inputTokens": response.usage.input_tokens, "outputTokens": response.usage.output_tokens}
    return (None if response.stop_reason in ("refusal", "max_tokens") else response.parsed_output), meta


def step_hashes(scene: dict) -> dict[str, str]:
    """A fingerprint of each step as the narrator reads it: its id, words, quotations and keys."""
    return {st["id"]: hashlib.sha256(json.dumps(st, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
            for st in scene["steps"]}


def merge(scene: dict, persona: str, metas: list[dict], new_steps: list[dict], previous: dict | None,
          changed: set[str]) -> dict:
    """The narration in the scene's order: rewritten steps from the model, the rest kept from before."""
    new = {s["stepId"]: s for s in new_steps}
    kept = {s["stepId"]: s for s in (previous or {}).get("steps", [])}
    order = [st["id"] for st in scene["steps"]]
    steps = [new.get(i, {"stepId": i, "lines": []}) if i in changed else kept[i] for i in order]
    return {"sceneId": scene["id"], "sceneContentHash": scene["contentHash"], "language": "en", "persona": persona,
            "madeBy": f"narrative/narrate_scene.py with {metas[-1]['model']}",
            "madeAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "calls": metas,
            "rewritten": [i for i in order if i in changed], "kept": [i for i in order if i not in changed],
            "stepHashes": step_hashes(scene), "steps": steps}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scene_input", type=Path)
    parser.add_argument("--persona", default="browser", choices=["browser", "student", "scholar"])
    parser.add_argument("--rules", type=Path, default=ROOT / "scenes" / "NARRATION.md")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--fresh", action="store_true", help="rewrite every step, keeping nothing")
    parser.add_argument("--stamp", action="store_true",
                        help="record step fingerprints on the existing narration of this scene version; call nothing")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    scene_text = args.scene_input.read_text(encoding="utf-8")
    scene = json.loads(scene_text)
    stem = args.scene_input.name.replace(".narration-input.json", "")
    current = args.scene_input.with_name(f"{stem}.narration.{args.persona}.json")
    previous = json.loads(current.read_text(encoding="utf-8")) if current.exists() else None
    hashes = step_hashes(scene)

    if args.stamp:
        if not previous or previous.get("sceneContentHash") != scene["contentHash"]:
            raise SystemExit("--stamp needs a narration written for this exact scene version (its contentHash)")
        previous["stepHashes"] = hashes
        current.write_text(json.dumps(previous, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"stamped {current}: {len(hashes)} step fingerprints")
        return 0

    usable = previous if previous and previous.get("stepHashes") and not args.fresh else None
    changed = {i for i, h in hashes.items() if not usable or usable["stepHashes"].get(i) != h}
    if usable and not changed:
        print(f"no step changed: {current.name} kept, nothing called")
        return 0
    partial = scene_text if not usable else json.dumps(
        {**scene, "steps": [st for st in scene["steps"] if st["id"] in changed]}, ensure_ascii=False)
    print(f"rewriting {len(changed)} of {len(hashes)} steps" + ("" if usable else " (no earlier fingerprints to keep from)"))

    from GraphRevised.proposals.passage_reader import anthropic_client
    client = anthropic_client(run=f"narrate:{scene['id']}")
    req = request(args.model, args.rules.read_text(encoding="utf-8"), partial, args.persona)
    if usable:
        req["messages"][0]["content"] += ("\n\nThis is part of the scene: only the steps given changed. Return lines for "
                                          "these steps only; the other steps keep their narration.")
    parsed, meta = call(client, req)
    metas = [meta]
    if parsed is None:
        print(f"no narration: {meta['stopReason']}")
        return 1
    narration = merge(scene, args.persona, metas, [x.model_dump() for x in parsed.steps], usable, changed)
    result = check(narration, scene)
    if result["problems"]:  # one repair round: the problems go back with the first answer
        req["messages"] += [{"role": "assistant", "content": parsed.model_dump_json()},
                            {"role": "user", "content": "The check found these problems. Return the same steps again, "
                                                        "fixed, changing only what they require:\n- " + "\n- ".join(result["problems"])}]
        repaired, meta = call(client, req)
        metas.append(meta)
        if repaired is not None:
            narration = merge(scene, args.persona, metas, [x.model_dump() for x in repaired.steps], usable, changed)
            result = check(narration, scene)
    narration["check"] = {**result, "checkedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    out = current if not result["problems"] else args.scene_input.with_name(f"{stem}.narration.{args.persona}.rejected.json")
    out.write_text(json.dumps(narration, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out}: {len(result['problems'])} problems, {len(result['warnings'])} warnings; "
          f"{sum(len(s['lines']) for s in narration['steps'])} lines")
    for p in result["problems"][:20]:
        print("  problem:", p)
    return 1 if result["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
