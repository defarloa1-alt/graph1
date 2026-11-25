"""Check a scene narration against its scene (scenes/NARRATION.md): it may say only what the scene says.

    python -m GraphRevised.narrative.narration_check <narration.json> <scene.narration-input.json>

Problems fail the narration; warnings are for the curator to read. The checks:

- the narration is for this version of the scene (its contentHash), and every step has lines;
- every line's keys are statements of its own step, or the step's alternatives (`<step>:ordersOfBattle`,
  `<step>:routes`), debate (`<step>:disputed`) or correction (`<step>:corrected`); a transition has none;
- a line's basis is the weakest of its keys' bases, and its wording fits that basis: an inferred line is
  worded as a reading, a not-checked line says the sources do not give it;
- words in quotation marks are verbatim from a passage quoted under the line's keys; a quote line names
  the locator it reads;
- every number in a line is in the text it keys (a statement, its quotations, the step's title and time);
- a corrected sentence is never narrated;
- capitalised names that are not in the keyed text are warnings (a name of the time, or a stray one).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

RANK = {"sourced": 0, "inferred": 1, "illustrative": 2, "not-checked": 3}
EXTRA = ("ordersOfBattle", "routes", "disputed", "corrected")
HEDGES = ("probably", "likely", "seems", "seem", "perhaps", "may have", "might", "appears", "we have drawn",
          "we draw", "our line", "our reading", "we think", "presumably", "it is our", "most likely")
UNSOURCED = ("not in the sources", "no passage", "not given", "does not say", "do not say", "traditionally",
             "usual account", "by tradition", "is said", "we have not found", "no source", "not found")
NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
                "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand",
                "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"}
QUOTED = re.compile(r"[“\"]([^”\"]{3,})[”\"]")
NUMBERS = re.compile(r"\d+(?:[.,]\d+)?")
NAME = re.compile(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-z]{2,})\b")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("’", "'").replace("‘", "'")).strip().lower()


def _units(step: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """What a line in this step may key: its statements, and its alternatives, debate and correction."""
    units = {s["id"]: {"basis": s["basis"], "text": s["text"], "voices": s.get("voices", [])} for s in step["statements"]}
    for key in ("ordersOfBattle", "routes"):
        if step.get(key):
            voices = [v for a in step[key]["alternatives"] for v in a.get("voices", [])]
            words = " ".join([step[key].get("note", "")] + [json.dumps(a, ensure_ascii=False) for a in step[key]["alternatives"]])
            units[f"{step['id']}:{key}"] = {"basis": "sourced", "text": words, "voices": voices}
    if step.get("disputed"):
        d = step["disputed"]
        units[f"{step['id']}:disputed"] = {"basis": "sourced", "voices": [],
                                           "text": d["words"] + " " + " ".join(q["label"] for q in d["questions"])}
    if step.get("corrected"):
        units[f"{step['id']}:corrected"] = {"basis": "sourced", "voices": [v for c in step["corrected"] for v in c.get("voices", [])],
                                            "text": " ".join(c["why"] for c in step["corrected"])}
    return units


def check(narration: dict[str, Any], scene: dict[str, Any]) -> dict[str, list[str]]:
    problems: list[str] = []
    warnings: list[str] = []
    if narration.get("sceneContentHash") != scene.get("contentHash"):
        problems.append("the narration is for another version of the scene (contentHash differs)")
    steps = {s["id"]: s for s in scene["steps"]}
    told = {s["stepId"]: s for s in narration.get("steps", [])}
    for sid in steps:
        if sid not in told or not told[sid].get("lines"):
            problems.append(f"{sid}: no lines")
    for sid in told:
        if sid not in steps:
            problems.append(f"{sid}: not a step of this scene")
    for sid, told_step in told.items():
        step = steps.get(sid)
        if not step:
            continue
        units = _units(step)
        context = " ".join([step.get("title", ""), step.get("timeWords", "")])
        was = [_norm(c["was"]) for c in step.get("corrected", [])]
        for line in told_step.get("lines", []):
            where = f"{sid} {line.get('id')}"
            text, keys, kind = line.get("text", ""), line.get("keys", []), line.get("kind")
            if kind not in ("narration", "transition", "quote"):
                problems.append(f"{where}: kind {kind!r}")
            if kind == "transition":
                if keys:
                    problems.append(f"{where}: a transition keys nothing")
                if NUMBERS.search(text):
                    problems.append(f"{where}: a transition carries a number")
                continue
            unknown = [k for k in keys if k not in units]
            if not keys or unknown:
                problems.append(f"{where}: keys {unknown or 'missing'} are not this step's")
                continue
            keyed = [units[k] for k in keys]
            weakest = max((u["basis"] for u in keyed), key=RANK.get)
            if line.get("basis") != weakest:
                problems.append(f"{where}: basis {line.get('basis')!r}, but its keys make it {weakest!r}")
            low = _norm(text)
            if weakest == "inferred" and not any(h in low for h in HEDGES):
                problems.append(f"{where}: inferred, but worded as fact (no hedge)")
            if weakest == "not-checked" and not any(h in low for h in UNSOURCED):
                problems.append(f"{where}: not checked, but does not say the sources do not give it")
            source_text = " ".join([context] + [u["text"] for u in keyed]
                                   + [v.get("quotation", "") + " " + v.get("accordingTo", "") + " " + v.get("locator", "")
                                      for u in keyed for v in u["voices"]])
            quotations = [_norm(v.get("quotation", "")) for u in keyed for v in u["voices"]]
            for q in QUOTED.findall(text):
                if not any(_norm(q).strip(" .,;") in qt for qt in quotations):
                    problems.append(f"{where}: quoted words are not verbatim from a keyed passage: {q[:60]!r}")
            if kind == "quote" and line.get("voice") not in {v.get("locator") for u in keyed for v in u["voices"]}:
                problems.append(f"{where}: a quote line names no keyed locator")
            src = _norm(source_text)
            for n in NUMBERS.findall(text):
                if n not in source_text:
                    problems.append(f"{where}: the number {n} is not in what it keys")
            for w in re.findall(r"[a-z]+", low):
                if w in NUMBER_WORDS and w not in src and w not in ("one", "first", "second"):
                    problems.append(f"{where}: the number word {w!r} is not in what it keys")
            for c in was:
                words = c.split()
                for i in range(max(0, len(words) - 5)):
                    if " ".join(words[i:i + 6]) in low:
                        problems.append(f"{where}: narrates a corrected sentence")
                        break
            for name in set(NAME.findall(text)):
                if name.lower() not in src:
                    warnings.append(f"{where}: {name!r} is not in what the line keys")
            if not isinstance(line.get("estSeconds"), (int, float)) or line["estSeconds"] <= 0:
                problems.append(f"{where}: estSeconds missing")
    return {"problems": problems, "warnings": warnings}


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2:
        print(__doc__)
        return 2
    result = check(json.loads(Path(args[0]).read_text(encoding="utf-8")), json.loads(Path(args[1]).read_text(encoding="utf-8")))
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 1 if result["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
