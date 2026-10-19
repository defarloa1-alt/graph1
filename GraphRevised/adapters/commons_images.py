"""Images for entities, from the Wikidata records already preserved, described by Wikimedia Commons.

Wikidata's image (P18) names a Commons file; it does not say what the file is.
A Roman bust of Agrippa, a 1672 painting of Actium, and a generic "Roman girl"
standing in for Domitia are all P18. So each file's Commons description
(author, licence, date, categories) is fetched, kept as a source payload
outside version control, and the file is classed by rules a reader can check:

- ``of-the-time``: made in antiquity (a bust, a coin, an inscription);
- ``later-imagining``: a painting, engraving, or illustration made later;
- ``place-today``: a photograph or view of a place as it is now;
- ``edition``: a page or cover of a work;
- ``map``: a modern map (of a campaign, a battle, a region);
- ``doubtful``: the file may not show this entity (a stand-in, an uncertain
  identification); never shown, listed for the curator;
- ``unclassed``: none of the rules applied.

No new harvest: the QIDs and file names come from the preserved Wikidata
records (phase-*-source). Images never go into Neo4j (D-096); this writes
``explorer/images/images.json`` and shrunken copies for the wireframe, both
git-ignored. Graph records come later, through proposals.

    python -m GraphRevised.adapters.commons_images
"""

from __future__ import annotations

import glob
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .wikidata_identity import polite_get

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "exports" / "graph.cyjs"
CACHE = ROOT / "cache" / "commons"
IMAGES = ROOT / "explorer" / "images"
API = "https://commons.wikimedia.org/w/api.php"
THUMB_WIDTH = 320

ANCIENT = re.compile(r"\b(bust|busts|portrait head|statue|statues|coin|coins|denarius|denarii|aureus|aurei|"
                     r"tetradrachm|relief|reliefs|inscription|inscriptions|fresco|frescoes|mosaic|mosaics|"
                     r"sarcophagus|cameo|ancient roman|roman republican|ptolemaic|hellenistic|augustan)\b", re.I)
LATER = re.compile(r"\b(painting|paintings|engraving|engravings|lithograph|lithographs|etching|illustration|"
                   r"illustrations|drawing|drawings|woodcut|print|prints|tapestry|1[4-9]th[- ]century|"
                   r"20th[- ]century|21st[- ]century)\b", re.I)
EDITION = re.compile(r"\b(title page|frontispiece|book cover|manuscript|codex|volume|edition|page)\b", re.I)
PLACE = re.compile(r"\b(view|panorama|aerial|landscape|photograph|beach|coast|harbou?r|ruins|site|town|city)\b", re.I)
MAP = re.compile(r"\b(map|maps|campaigns?|plan of|\.svg$|\.png$)", re.I)
MUSEUM = re.compile(r"\b(Louvre Ma\d+|Glyptothek|Musei Capitolini|Altes Museum|Musei Vaticani|Museo|Mus[ée]e|Museum|"
                    r"British Museum|Ny Carlsberg)\b", re.I)
DOUBT = re.compile(r"\b(possibly|perhaps|probably|presumed|so-called|identified as|unidentified|or uncle|"
                   r"or father|traditionally|generic|wearing lunula)\b", re.I)


def _text(value: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def _date(value: str | None) -> str | None:
    """Commons dates, without the Wikidata QuickStatements residue some carry ("1672 date QS:P571,...")."""
    if not value:
        return None
    return re.sub(r"\s*(date\s*)?QS:\S+", "", value).strip() or None


def preserved_images() -> dict[str, dict]:
    """QID -> {label, file, property} from the newest preserved record of each QID."""
    newest: dict[str, tuple[int, str]] = {}
    for path in glob.glob(str(ROOT / "phase-*-source" / "wikidata-Q*-r*.json")):
        m = re.search(r"wikidata-(Q\d+)-r(\d+)\.json$", path)
        if m and (m.group(1) not in newest or int(m.group(2)) > newest[m.group(1)][0]):
            newest[m.group(1)] = (int(m.group(2)), path)
    out = {}
    for qid, (_, path) in newest.items():
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        entity = (data.get("entities") or {}).get(qid) or data
        claims = entity.get("claims") or {}
        label = ((entity.get("labels") or {}).get("en") or {}).get("value", qid)
        for prop in ("P18", "P242"):  # the image, else a locator map
            for claim in claims.get(prop, []):
                value = ((claim.get("mainsnak") or {}).get("datavalue") or {}).get("value")
                if value and claim.get("rank") != "deprecated":
                    out[qid] = {"label": label, "file": value, "property": prop}
                    break
            if qid in out:
                break
    return out


def entities_by_qid() -> dict[str, dict]:
    """QID -> the export's entity (id, label, kind), through its Wikidata authority record."""
    nodes = json.loads(EXPORT.read_text(encoding="utf-8"))["elements"]["nodes"]
    out = {}
    for node in nodes:
        n = node["data"]
        for line in n.get("authorityLines") or []:
            m = re.search(r"Wikidata record: .*\((Q\d+)\)", line)
            if m:
                out[m.group(1)] = {"id": n["id"], "label": n.get("fullLabel") or n.get("label"), "kind": n.get("kind")}
    return out


def fetch_metadata(files: list[str]) -> dict[str, dict]:
    """Commons imageinfo for each file, cached as fetched (one payload per batch of 50)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    out = {}
    for i in range(0, len(files), 50):
        batch = sorted(files[i:i + 50])
        key = hashlib.sha256("|".join(batch).encode()).hexdigest()[:16]
        path = CACHE / f"imageinfo-{key}.json"
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            response = polite_get(API, params={
                "action": "query", "format": "json", "formatversion": "2", "prop": "imageinfo",
                "iiprop": "url|extmetadata|size|mime", "iiurlwidth": str(THUMB_WIDTH),
                "titles": "|".join("File:" + f for f in batch)})
            payload = {"retrieved": datetime.now(timezone.utc).isoformat(), "files": batch, "response": response.json()}
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        normalized = {n["to"]: n["from"] for n in payload["response"]["query"].get("normalized", [])}
        for page in payload["response"]["query"]["pages"]:
            info = (page.get("imageinfo") or [None])[0]
            name = normalized.get(page["title"], page["title"]).removeprefix("File:")
            if info:
                out[name] = info
    return out


def classify(entity: dict, wikidata_label: str, file: str, prop: str, info: dict) -> tuple[str, str]:
    """(class, the rule that decided it), from the file's own Commons description."""
    meta = info.get("extmetadata") or {}
    words = " ".join(_text((meta.get(k) or {}).get("value")) for k in ("ObjectName", "ImageDescription", "Categories"))
    words = f"{file} {words}"
    if prop == "P242":
        return "place-today", "a locator map (P242)"
    if DOUBT.search(words):
        return "doubtful", f"Commons says '{DOUBT.search(words).group(0)}'"
    if entity["kind"] == "Person":
        names = [w for w in re.findall(r"[A-Za-z]{4,}", f"{entity['label']} {wikidata_label}")
                 if w.lower() not in {"marcus", "gaius", "lucius", "publius", "gnaeus", "quintus", "titus", "the"}]
        if names and not any(re.search(rf"\b{re.escape(w)}", words, re.I) for w in names):
            return "doubtful", "the file never names the person"
    if LATER.search(words):
        return "later-imagining", f"Commons calls it '{LATER.search(words).group(0)}'"
    if ANCIENT.search(words):
        return "of-the-time", f"Commons calls it '{ANCIENT.search(words).group(0)}'"
    if entity["kind"] in ("Event", "Polity", "Period") and MAP.search(file):
        return "map", "a map or diagram file"
    if entity["kind"] == "Work":
        return "edition", "an image of a work is an edition of it"
    if entity["kind"] == "Place":
        return "place-today", "an image of a place, not a painting or map"
    if entity["kind"] == "Person" and MUSEUM.search(words):
        return "of-the-time", f"a museum object ('{MUSEUM.search(words).group(0)}')"
    return "unclassed", "no rule applied"


CAPTION = {
    "of-the-time": "From their time",
    "later-imagining": "A later imagining",
    "place-today": "The place today",
    "edition": "An edition",
    "map": "A modern map",
    "unclassed": "An image from Wikimedia Commons, not yet classed",
}


def run() -> dict:
    images = preserved_images()
    entities = entities_by_qid()
    wanted = {q: v for q, v in images.items() if q in entities}
    metadata = fetch_metadata(sorted({v["file"] for v in wanted.values()}))
    (IMAGES / "commons").mkdir(parents=True, exist_ok=True)
    manifest, review = [], []
    for qid, image in sorted(wanted.items()):
        entity, info = entities[qid], metadata.get(image["file"])
        if not info:
            review.append({"entity": entity["id"], "file": image["file"], "why": "Commons returned no file"})
            continue
        meta = info.get("extmetadata") or {}
        get = lambda k: _text((meta.get(k) or {}).get("value")) or None  # noqa: E731
        klass, rule = classify(entity, image["label"], image["file"], image["property"], info)
        row = {"entity": entity["id"], "label": entity["label"], "qid": qid, "commonsFile": image["file"],
               "class": klass, "rule": rule, "object": get("ObjectName"), "date": _date(get("DateTimeOriginal")),
               "author": get("Artist"), "licence": get("LicenseShortName"),
               "attributionRequired": get("AttributionRequired") == "true",
               "page": info.get("descriptionurl")}
        if klass == "doubtful":
            review.append({**row, "why": rule})
            continue
        name = hashlib.sha256(image["file"].encode()).hexdigest()[:16] + ".jpg"
        target = IMAGES / "commons" / name
        if not target.exists():
            target.write_bytes(polite_get(info.get("thumburl") or info["url"], timeout=60).content)
        caption = CAPTION[klass]
        if klass == "later-imagining" and row["author"]:
            caption += f": {row['author']}" + (f", {row['date']}" if row["date"] else "")
        elif row["object"]:
            caption += f": {row['object']}"
        manifest.append({**row, "file": f"commons/{name}", "depicts": caption,
                         "source": f"Wikimedia Commons, {image['file']} (via Wikidata {image['property']} of {qid})",
                         "canvas": klass in ("of-the-time", "place-today")})
    (IMAGES / "images.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    (IMAGES / "images-review.json").write_text(json.dumps(review, ensure_ascii=False, indent=1), encoding="utf-8")
    counts: dict[str, int] = {}
    for row in manifest + [r for r in review if "class" in r]:
        counts[row["class"]] = counts.get(row["class"], 0) + 1
    return {"with image": len(images), "in the graph": len(wanted), "shown": len(manifest),
            "to review": len(review), "classes": counts}


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
