"""
Facet Console — harvest job representation

File-based HarvestJob storage. Each job is appended to
output/facet_harvest_jobs/{facet_label}/jobs.jsonl
Idempotent: same (discipline_qid, facet_label, repo_key) = same job_id, no overwrite.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

_root = Path(__file__).resolve().parents[3]
JOBS_DIR = _root / "output" / "facet_harvest_jobs"

REPOS_TEMPLATES = {
    "OPENALEX_WORKS": "https://api.openalex.org/works?filter=concepts.id:{oa_id}&sort=cited_by_count:desc&per_page=25",
    "OPENALEX_CONCEPT": "https://api.openalex.org/concepts/{oa_id}",
    "OPEN_LIBRARY": "https://openlibrary.org/subjects/{slug}.json?limit=50",
    "OPEN_SYLLABUS": "https://api.opensyllabus.org/v1/fields?q={slug}",
    "LCSH_HEADING": "https://id.loc.gov/authorities/subjects/{lcsh}.html",
    "WORLDCAT": "https://www.worldcat.org/search?q=su%3A{label}",
    "INTERNET_ARCHIVE": "https://archive.org/search?query=subject%3A%22{label}%22&mediatype=texts",
    "PERSEUS": "https://catalog.perseus.org/catalog?utf8=&search[query]={label}",
    "HATHI_TRUST": "https://catalog.hathitrust.org/Search/Home?lookfor={label}&type=subject",
}


def _slug(label: str) -> str:
    return label.lower().replace(" ", "-").replace(",", "")


def _expand_url(template: str, discipline: dict) -> str:
    params = {
        "oa_id": discipline.get("oa_id", ""),
        "lcsh": discipline.get("lcsh", ""),
        "label": discipline.get("label", ""),
        "slug": _slug(discipline.get("label", "")),
    }
    return template.format(**params)


def create_harvest_job(
    discipline_qid: str,
    discipline_label: str,
    facet_label: str,
    repo_key: str,
    discipline: dict,
    campaign_id: str | None = None,
) -> dict:
    """
    Create a harvest job. Appends to JSONL; does not overwrite existing.
    Returns the job dict.
    """
    template = REPOS_TEMPLATES.get(repo_key)
    if not template:
        return {}
    url = _expand_url(template, discipline)

    job_id = str(uuid.uuid4())
    job = {
        "job_id": job_id,
        "discipline_qid": discipline_qid,
        "discipline_label": discipline_label,
        "facet_label": facet_label,
        "repo_key": repo_key,
        "url": url,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "completed_at": None,
        "campaign_id": campaign_id,
    }

    out_dir = JOBS_DIR / facet_label.replace(" ", "_")
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs_file = out_dir / "jobs.jsonl"
    with open(jobs_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(job, ensure_ascii=False) + "\n")

    return job


def list_harvest_jobs(facet_label: str, status: str | None = None) -> list[dict]:
    """List harvest jobs for a facet. Optionally filter by status."""
    out_dir = JOBS_DIR / facet_label.replace(" ", "_")
    jobs_file = out_dir / "jobs.jsonl"
    if not jobs_file.exists():
        return []
    jobs = []
    with open(jobs_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            j = json.loads(line)
            if status is None or j.get("status") == status:
                jobs.append(j)
    return jobs
