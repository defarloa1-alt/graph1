"""Write a scene's narration (scenes/NARRATION.md): one model call, then the check; one repair round.

    python -m GraphRevised.narrative.narrate_scene <scene.narration-input.json> [--persona browser]
        [--rules GraphRevised/scenes/NARRATION.md] [--model claude-opus-5-5]

Needs a named budget (CHRYSTALLUM_BUDGET; the spend meter prices and caps the call). The model sees the
narration rules and the scene's narration input, and returns lines keyed to statement ids. The check
(narrative/narration_check.py) runs on the result; if it finds problems, they go back to the model once.
A narration that passes is written beside the scene as <scene>.narration.<persona>.json; one that does
not is written as <scene>.narration.<persona>.rejected.json with its problems, for the curator. The
scene's id and contentHash are copied from the input, never from the model. Nothing goes into the graph:
a narration is a made presentation, never evidence.
"""

from __future__ import annotations

import argparse
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


def assemble(parsed: Narration, scene: dict, persona: str, metas: list[dict]) -> dict:
    return {"sceneId": scene["id"], "sceneContentHash": scene["contentHash"], "language": "en", "persona": persona,
            "madeBy": f"narrative/narrate_scene.py with {metas[-1]['model']}",
            "madeAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "calls": metas,
            "steps": [s.model_dump() for s in parsed.steps]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scene_input", type=Path)
    parser.add_argument("--persona", default="browser", choices=["browser", "student", "scholar"])
    parser.add_argument("--rules", type=Path, default=ROOT / "scenes" / "NARRATION.md")
    parser.add_argument("--model", default=MODEL)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    from GraphRevised.proposals.passage_reader import anthropic_client

    scene_text = args.scene_input.read_text(encoding="utf-8")
    scene = json.loads(scene_text)
    client = anthropic_client(run=f"narrate:{scene['id']}")
    req = request(args.model, args.rules.read_text(encoding="utf-8"), scene_text, args.persona)
    parsed, meta = call(client, req)
    metas = [meta]
    if parsed is None:
        print(f"no narration: {meta['stopReason']}")
        return 1
    narration = assemble(parsed, scene, args.persona, metas)
    result = check(narration, scene)
    if result["problems"]:  # one repair round: the problems go back with the first answer
        req["messages"] += [{"role": "assistant", "content": parsed.model_dump_json()},
                            {"role": "user", "content": "The check found these problems. Return the whole narration again, "
                                                        "fixed, changing only what they require:\n- " + "\n- ".join(result["problems"])}]
        repaired, meta = call(client, req)
        metas.append(meta)
        if repaired is not None:
            narration, result = assemble(repaired, scene, args.persona, metas), None
            result = check(narration, scene)
    narration["check"] = {**result, "checkedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    stem = args.scene_input.name.replace(".narration-input.json", "")
    out = args.scene_input.with_name(f"{stem}.narration.{args.persona}{'.rejected' if result['problems'] else ''}.json")
    out.write_text(json.dumps(narration, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out}: {len(result['problems'])} problems, {len(result['warnings'])} warnings; "
          f"{sum(len(s['lines']) for s in narration['steps'])} lines")
    for p in result["problems"][:20]:
        print("  problem:", p)
    return 1 if result["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
