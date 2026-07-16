"""
Agent provenance + bibliography for approved DI SubjectConcept proposals.

Design (Layer 4 write):
  - SubjectConcept.proposed_by = agent_id (denormalized)
  - (SubjectConcept)-[:PROPOSED_BY]->(Agent)  primary owner
  - SubjectConcept.scholarly_overview = review-queue prose
  - (SubjectConcept)-[:HAS_BIBLIO {rank}]->(CorpusWork)  supporting works

Agent resolution (per source_facet):
  1. Existing :Agent with ASSIGNED_TO_FACET
  2. Existing :SYS_SFAAgent with MANAGES_FACET
  3. MERGE canonical :Agent SFA_{FACET} + ASSIGNED_TO_FACET

Bio-primary: ownership follows source_facet; cross-facet overlap is a review flag,
not a second PROPOSED_BY edge (Phase 2 claims handle contested objects).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from proposal_backbone import normalize_corpus_work


def facet_agent_id(facet_key: str) -> str:
    return f"SFA_{facet_key.strip().upper()}"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _work_row(work: dict[str, Any]) -> dict[str, Any]:
    """Normalize supporting work from enriched proposal JSON."""
    if isinstance(work, str):
        row = normalize_corpus_work({"work_id": work})
    else:
        row = normalize_corpus_work(work)
    if not row.get("work_id"):
        return {}
    return row


def resolve_facet_agent(session: Any, facet_key: str, *, seed_qid: str) -> str | None:
    """Return agent_id for facet; MERGE canonical Agent if none exists."""
    facet_key = facet_key.strip().lower()
    if not facet_key:
        return None
    facet_upper = facet_key.upper()
    canonical_id = facet_agent_id(facet_key)

    row = session.run(
        """
        MATCH (f:Facet)
        WHERE toLower(f.key) = toLower($facet_key)
           OR toLower(f.label) = toLower($facet_key)
        WITH f LIMIT 1
        OPTIONAL MATCH (a:Agent)-[:ASSIGNED_TO_FACET]->(f)
        WITH f, collect(DISTINCT a.agent_id)[0] AS assigned_id
        OPTIONAL MATCH (sa:SYS_SFAAgent)-[:MANAGES_FACET]->(f)
        WITH f, assigned_id, collect(DISTINCT sa.agent_id)[0] AS sys_id
        RETURN f.key AS facet_key, assigned_id, sys_id
        """,
        facet_key=facet_key,
    ).single()

    if row and row.get("assigned_id"):
        return row["assigned_id"]
    if row and row.get("sys_id"):
        return row["sys_id"]

    session.run(
        """
        MERGE (a:Agent {agent_id: $agent_id})
        ON CREATE SET
            a.role = 'subject_facet_agent',
            a.domain_qid = $seed_qid,
            a.facet_key = $facet_key,
            a.created = datetime()
        SET a.updated = datetime(),
            a.label = coalesce(a.label, $label)
        WITH a
        MERGE (f:Facet {key: $facet_upper})
        ON CREATE SET f.label = $facet_label
        MERGE (a)-[:ASSIGNED_TO_FACET]->(f)
        """,
        agent_id=canonical_id,
        seed_qid=seed_qid,
        facet_key=facet_key,
        facet_upper=facet_upper,
        facet_label=facet_key.capitalize(),
        label=f"{facet_key.capitalize()} SFA",
    )
    return canonical_id


def write_proposal_provenance(
    session: Any,
    proposal: dict[str, Any],
    *,
    seed_qid: str,
    stats: dict[str, Any],
) -> None:
    """Attach agent ownership, scholarly overview, and bibliography to one SC."""
    subject_id = proposal.get("subject_id")
    if not subject_id:
        return

    facet_key = (proposal.get("source_facet") or "").lower()
    agent_id = resolve_facet_agent(session, facet_key, seed_qid=seed_qid)
    overview = (proposal.get("scholarly_overview") or "").strip()
    reviewed_at = proposal.get("reviewed_at") or _utc_now_iso()

    session.run(
        """
        MATCH (sc:SubjectConcept {subject_id: $subject_id})
        SET sc.proposed_by = $agent_id,
            sc.scholarly_overview = CASE WHEN $overview <> '' THEN $overview ELSE sc.scholarly_overview END,
            sc.overview_provider = CASE WHEN $overview <> '' THEN coalesce(sc.overview_provider, 'di_review_enrichment') ELSE sc.overview_provider END,
            sc.overview_at = CASE WHEN $overview <> '' THEN datetime($reviewed_at) ELSE sc.overview_at END,
            sc.updated = datetime()
        """,
        subject_id=subject_id,
        agent_id=agent_id,
        overview=overview,
        reviewed_at=reviewed_at,
    )

    if agent_id:
        session.run(
            """
            MATCH (sc:SubjectConcept {subject_id: $subject_id})
            MATCH (a)
            WHERE a.agent_id = $agent_id AND (a:Agent OR a:SYS_SFAAgent)
            MERGE (sc)-[r:PROPOSED_BY]->(a)
            SET r.role = 'primary',
                r.at = coalesce(r.at, datetime($reviewed_at)),
                r.confidence = $confidence
            """,
            subject_id=subject_id,
            agent_id=agent_id,
            reviewed_at=reviewed_at,
            confidence=float(proposal.get("confidence") or 0.5),
        )
        stats["proposed_by"] = stats.get("proposed_by", 0) + 1

    works = proposal.get("supporting_works") or []
    rank = 0
    for raw in works:
        row = _work_row(raw if isinstance(raw, dict) else {"work_id": str(raw)})
        if not row:
            continue
        rank += 1
        session.run(
            """
            MATCH (sc:SubjectConcept {subject_id: $subject_id})
            MERGE (cw:CorpusWork {work_id: $work_id})
            SET cw.title = $title,
                cw.authors = $authors,
                cw.year = $year,
                cw.source = $source,
                cw.source_url = $source_url,
                cw.doi = $doi,
                cw.citation_count = $citation_count,
                cw.seed_qid = $seed_qid,
                cw.facet_key = $facet_key,
                cw.updated = datetime()
            MERGE (sc)-[r:HAS_BIBLIO]->(cw)
            SET r.rank = $rank
            """,
            subject_id=subject_id,
            seed_qid=seed_qid,
            facet_key=facet_key,
            rank=rank,
            **row,
        )
        stats["has_biblio"] = stats.get("has_biblio", 0) + 1
