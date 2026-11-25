"""Voice a scene's checked narration, one clip per line, through the ElevenLabs text-to-speech API.

    python -m GraphRevised.narrative.voice_scene --list-voices
    python -m GraphRevised.narrative.voice_scene <scene>.narration.<persona>.json --from-history [--apply]
    python -m GraphRevised.narrative.voice_scene <scene>.narration.<persona>.json --voice <voice_id> [--apply]
        [--model eleven_v4] [--pronunciations GraphRevised/curation/pronunciations.json]

Needs ELEVENLABS_API_KEY in the environment or in .env (only that key is read from .env; it is never printed).
Without --apply it prints what it would voice and how many characters that costs, and calls nothing.

Each line's text is sent exactly as written in the narration, except that names in the pronunciation list are
replaced by their respellings in the text sent to the voice (the caption keeps the written name). The line before
and after go with each call so the voice keeps one tone across clips. Clips go to
scenes/audio/<scene slug>/<persona>/<line id>.mp3; their lengths come from the API's timestamps. audio.json beside
them is the made-media record (26a shape 8, kind audio): generator, model, voice, date, the narration file and its
hash, the scene's contentHash, and per line its text, the text spoken, the file and its length. A clip whose text,
voice and model are unchanged is not voiced again. Audio is a made presentation, never evidence.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.elevenlabs.io/v1"
MODEL = "eleven_v4"
FORMAT = "mp3_44100_128"
# voices ElevenLabs made or a user designed from a description; other kinds are clones and need a look first
SAFE_CATEGORIES = {"premade", "generated"}


def api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        from dotenv import dotenv_values
        key = dotenv_values(ROOT.parent / ".env").get("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit("Set ELEVENLABS_API_KEY in the environment or in .env.")
    return key


def list_voices() -> int:
    import requests
    r = requests.get(f"{API}/voices", headers={"xi-api-key": api_key()}, timeout=60)
    r.raise_for_status()
    for v in sorted(r.json()["voices"], key=lambda v: (v.get("category") != "premade", v["name"])):
        labels = ", ".join(f"{k} {w}" for k, w in (v.get("labels") or {}).items())
        flag = "" if v.get("category") in SAFE_CATEGORIES else "  <- a clone: check it imitates no real person"
        print(f"{v['voice_id']}  {v['name']}  [{v.get('category')}]  {labels}{flag}")
    return 0


def mp3_seconds(data: bytes) -> float:
    """Length of an MPEG-1/2 Layer III file, by counting its frames (no decoder needed)."""
    i = 0
    if data[:3] == b"ID3":  # skip an ID3v2 tag
        i = 10 + ((data[6] & 127) << 21 | (data[7] & 127) << 14 | (data[8] & 127) << 7 | (data[9] & 127))
    rates = {3: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
             2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
    srates = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}
    seconds = 0.0
    while i + 4 <= len(data):
        if data[i] != 0xFF or data[i + 1] & 0xE0 != 0xE0:
            i += 1
            continue
        ver, layer = (data[i + 1] >> 3) & 3, (data[i + 1] >> 1) & 3
        br, sr, pad = data[i + 2] >> 4, (data[i + 2] >> 2) & 3, (data[i + 2] >> 1) & 1
        if layer != 1 or ver == 1 or br in (0, 15) or sr == 3:
            i += 1
            continue
        kbps, hz = rates[3 if ver == 3 else 2][br], srates[ver][sr]
        samples = 1152 if ver == 3 else 576
        i += samples // 8 * kbps * 1000 // hz + pad
        seconds += samples / hz
    return round(seconds, 2)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[‘’“”\"']", "", text)).strip().lower()


def from_history(narration_path: Path, table: dict[str, str], apply: bool) -> int:
    """Fetch clips already made in the ElevenLabs app (its History), matching each to a line by its text."""
    import requests
    raw = narration_path.read_bytes()
    narration = json.loads(raw)
    key = api_key()
    items, after = [], None
    while True:
        r = requests.get(f"{API}/history", headers={"xi-api-key": key}, timeout=60,
                         params={"page_size": 1000, **({"start_after_history_item_id": after} if after else {})})
        r.raise_for_status()
        body = r.json()
        items += body.get("history", [])
        if not body.get("has_more"):
            break
        after = body["last_history_item_id"]
    newest = {}
    for it in sorted(items, key=lambda it: it.get("date_unix", 0)):  # a later take of the same text wins
        newest[norm(it.get("text") or "")] = it
    lines = [l for s in narration["steps"] for l in s["lines"]]
    found, missing = [], []
    for l in lines:
        it = newest.get(norm(l["text"])) or newest.get(norm(respell(l["text"], table)))
        (found if it else missing).append((l, it))
    print(f"{len(items)} items in your History; {len(found)} of {len(lines)} lines matched")
    for l, _ in missing:
        print(f"  no clip for {l['id']}: {l['text'][:70]}")
    voices = {(it.get("voice_name"), it.get("voice_category"), it.get("model_id")) for _, it in found}
    for name, cat, model in voices:
        flag = "" if cat in SAFE_CATEGORIES else "  <- not a stock or designed voice: check it imitates no real person"
        print(f"  voice {name} [{cat}], model {model}{flag}")
    if not apply:
        print("dry run: nothing downloaded (add --apply)")
        return 0
    slug = narration["sceneId"].rsplit(":", 1)[-1]
    out = ROOT / "scenes" / "audio" / slug / narration.get("persona", "browser")
    out.mkdir(parents=True, exist_ok=True)
    clips = []
    for l, it in found:
        r = requests.get(f"{API}/history/{it['history_item_id']}/audio", headers={"xi-api-key": key}, timeout=120)
        r.raise_for_status()
        (out / f"{l['id']}.mp3").write_bytes(r.content)
        clips.append({"id": l["id"], "text": l["text"], "spoken": it.get("text"), "file": f"{l['id']}.mp3",
                      "seconds": mp3_seconds(r.content), "bytes": len(r.content), "voice": it.get("voice_id"),
                      "voiceName": it.get("voice_name"), "voiceCategory": it.get("voice_category"),
                      "model": it.get("model_id"), "historyItemId": it["history_item_id"],
                      "madeAt": datetime.fromtimestamp(it.get("date_unix", 0), timezone.utc).isoformat(timespec="seconds")})
    record = {
        "kind": "audio", "made": True, "evidence": False, "generator": "ElevenLabs (made in the app, fetched from its History)",
        "madeBy": "narrative/voice_scene.py --from-history", "fetchedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sceneId": narration["sceneId"], "sceneContentHash": narration["sceneContentHash"], "persona": narration.get("persona"),
        "narration": narration_path.name, "narrationSha256": hashlib.sha256(raw).hexdigest(),
        "missing": [l["id"] for l, _ in missing], "licence": "per the ElevenLabs plan in use; record it here",
        "seconds": round(sum(c["seconds"] for c in clips), 1), "clips": clips,
    }
    (out / "audio.json").write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out / 'audio.json'}: {len(clips)} clips, {record['seconds']} s")
    return 0


def respell(text: str, table: dict[str, str]) -> str:
    for name in sorted(table, key=len, reverse=True):  # longer names first
        text = re.sub(rf"\b{re.escape(name)}\b", table[name], text)
    return text


def voice_line(key: str, voice: str, model: str, text: str, before: str, after: str) -> tuple[bytes, float]:
    import requests
    r = requests.post(f"{API}/text-to-speech/{voice}/with-timestamps", params={"output_format": FORMAT},
                      headers={"xi-api-key": key}, timeout=180,
                      json={"text": text, "model_id": model, "previous_text": before or None, "next_text": after or None})
    if r.status_code != 200:
        raise SystemExit(f"ElevenLabs refused a line: {r.status_code} {r.text[:300]}")
    body = r.json()
    ends = (body.get("alignment") or {}).get("character_end_times_seconds") or [0.0]
    return base64.b64decode(body["audio_base64"]), round(max(ends), 2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("narration", type=Path, nargs="?")
    parser.add_argument("--voice", help="an ElevenLabs voice_id (see --list-voices)")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--pronunciations", type=Path, default=ROOT / "curation" / "pronunciations.json")
    parser.add_argument("--list-voices", action="store_true")
    parser.add_argument("--from-history", action="store_true",
                        help="fetch clips already made in the ElevenLabs app, matched to lines by their text")
    parser.add_argument("--apply", action="store_true", help="call the API; without it, only report")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if args.list_voices:
        return list_voices()
    if args.from_history and args.narration:
        table = json.loads(args.pronunciations.read_text(encoding="utf-8")).get("names", {}) if args.pronunciations.exists() else {}
        return from_history(args.narration, table, args.apply)
    if not args.narration or not args.voice:
        parser.error("give the narration file and --voice (or --list-voices)")

    raw = args.narration.read_bytes()
    narration = json.loads(raw)
    if narration.get("check", {}).get("problems"):
        raise SystemExit("This narration failed its check; voice only a narration that passed.")
    table = json.loads(args.pronunciations.read_text(encoding="utf-8")).get("names", {}) if args.pronunciations.exists() else {}
    slug = narration["sceneId"].rsplit(":", 1)[-1]
    out = ROOT / "scenes" / "audio" / slug / narration.get("persona", "browser")
    record_path = out / "audio.json"
    old = {c["id"]: c for c in json.loads(record_path.read_text(encoding="utf-8"))["clips"]} if record_path.exists() else {}

    lines = [l for s in narration["steps"] for l in s["lines"]]
    todo, clips = [], []
    for i, l in enumerate(lines):
        spoken = respell(l["text"], table)
        clip = {"id": l["id"], "text": l["text"], "spoken": spoken, "file": f"{l['id']}.mp3"}
        prev = old.get(l["id"])
        if prev and prev["text"] == l["text"] and prev["spoken"] == spoken and prev.get("voice") == args.voice \
                and prev.get("model") == args.model and (out / prev["file"]).exists():
            clips.append(prev)
        else:
            todo.append((i, clip))
            clips.append(clip)
    chars = sum(len(c["spoken"]) for _, c in todo)
    print(f"{len(lines)} lines; {len(lines) - len(todo)} already voiced; {len(todo)} to voice, {chars} characters")
    for _, c in todo:
        if c["spoken"] != c["text"]:
            print(f"  {c['id']} spoken as: {c['spoken']}")
    if not args.apply:
        print("dry run: nothing called (add --apply)")
        return 0

    key = api_key()
    import requests
    v = requests.get(f"{API}/voices/{args.voice}", headers={"xi-api-key": key}, timeout=60)
    v = v.json() if v.ok else {}
    out.mkdir(parents=True, exist_ok=True)
    for i, clip in todo:
        before = respell(lines[i - 1]["text"], table) if i else ""
        after = respell(lines[i + 1]["text"], table) if i + 1 < len(lines) else ""
        audio, seconds = voice_line(key, args.voice, args.model, clip["spoken"], before, after)
        (out / clip["file"]).write_bytes(audio)
        clip.update(seconds=seconds, bytes=len(audio), voice=args.voice, model=args.model,
                    madeAt=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        print(f"  {clip['id']}  {seconds:.1f} s")
    record = {
        "kind": "audio", "made": True, "evidence": False,
        "generator": "ElevenLabs text-to-speech API", "model": args.model, "voice": args.voice, "voiceName": v.get("name"), "voiceCategory": v.get("category"), "format": FORMAT,
        "madeBy": "narrative/voice_scene.py", "madeAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sceneId": narration["sceneId"], "sceneContentHash": narration["sceneContentHash"],
        "persona": narration.get("persona"), "narration": args.narration.name,
        "narrationSha256": hashlib.sha256(raw).hexdigest(),
        "pronunciations": {k: v for k, v in table.items() if any(re.search(rf"\b{re.escape(k)}\b", l["text"]) for l in lines)},
        "licence": "per the ElevenLabs plan in use; record it here",
        "seconds": round(sum(c.get("seconds", 0) for c in clips), 1), "clips": clips,
    }
    record_path.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {record_path}: {len(clips)} clips, {record['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
