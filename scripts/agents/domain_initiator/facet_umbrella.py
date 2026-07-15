#!/usr/bin/env python3
"""
Facet umbrella hierarchy for a SubjectDomain.

Creates one SubjectConcept facet umbrella per facet, wires:
  SubjectDomain -[:HAS_SUBJECT_CONCEPT]-> facet umbrella
  decomposition SC -[:PART_OF]-> facet umbrella
  SFA_TrainingRun -[:RELEVANT_TO_SUBJECT]-> facet umbrella
  SFA_SubScope -[:PROMOTED_TO]-> decomposition SC (by scope_key)

Used by propose.py --write and wire_facet_umbrellas.py (repair existing graph).
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


def facet_umbrella_subject_id(seed_qid: str, facet_key: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", facet_key.lower()).strip("_")
    return f"sc_{seed_qid.lower()}_facet_{slug}"


def facet_umbrella_cipher(seed_qid: str, facet_key: str) -> str:
    raw = f"{seed_qid}:facet_umbrella:{facet_key.lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def facet_umbrella_label(_seed_label: str, facet_label: str) -> str:
    """Domain context comes from HAS_SUBJECT_CONCEPT; label is facet-first only."""
    return f"Facet — {facet_label}"


def collect_facet_keys(
    proposals: list[dict],
    extra_facet_keys: list[str] | None = None,
) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for proposal in proposals:
        fk = (proposal.get("source_facet") or "").lower()
        if fk and fk not in seen:
            seen.add(fk)
            keys.append(fk)
    for fk in extra_facet_keys or []:
        norm = fk.lower()
        if norm and norm not in seen:
            seen.add(norm)
            keys.append(norm)
    return sorted(keys)


def prune_domain_direct_attachments(session: Any, seed_qid: str) -> dict[str, int]:
    """Keep SubjectDomain expand view clean: only facet umbrellas attach directly."""
    removed: dict[str, int] = {
        "removed_has_sc_bootstrap": 0,
        "removed_has_sc_geo": 0,
        "removed_scoped_to_decompositions": 0,
        "removed_scoped_to_umbrella": 0,
    }

    row = session.run(
        """
        MATCH (sd:SubjectDomain {seed_qid: $seed_qid})-[r:HAS_SUBJECT_CONCEPT]->(sc:SubjectConcept)
        WHERE sc.source = 'ccs_bootstrap'
        DELETE r
        RETURN count(*) AS deleted
        """,
        seed_qid=seed_qid,
    ).single()
    removed["removed_has_sc_bootstrap"] = row["deleted"] if row else 0

    row = session.run(
        """
        MATCH (sd:SubjectDomain {seed_qid: $seed_qid})-[r:HAS_SUBJECT_CONCEPT]->(sc:SubjectConcept)
        WHERE sc.source = 'geo_bootstrap'
        DELETE r
        RETURN count(*) AS deleted
        """,
        seed_qid=seed_qid,
    ).single()
    removed["removed_has_sc_geo"] = row["deleted"] if row else 0

    row = session.run(
        """
        MATCH (sc:SubjectConcept {source: 'di_proposal', seed_qid: $seed_qid})-[r:SCOPED_TO]->(:SubjectDomain {seed_qid: $seed_qid})
        DELETE r
        RETURN count(*) AS deleted
        """,
        seed_qid=seed_qid,
    ).single()
    removed["removed_scoped_to_decompositions"] = row["deleted"] if row else 0

    row = session.run(
        """
        MATCH (sc:SubjectConcept {source: 'di_facet_umbrella', seed_qid: $seed_qid})-[r:SCOPED_TO]->(:SubjectDomain {seed_qid: $seed_qid})
        DELETE r
        RETURN count(*) AS deleted
        """,
        seed_qid=seed_qid,
    ).single()
    removed["removed_scoped_to_umbrella"] = row["deleted"] if row else 0

    return removed


def distinguish_domain_from_period(session: Any, seed_qid: str) -> dict[str, str]:
    """SubjectDomain and Period often share the same label; make Browser navigation unambiguous."""
    row = session.run(
        """
        MATCH (sd:SubjectDomain {seed_qid: $seed_qid})
        SET sd.label = CASE
              WHEN sd.label CONTAINS 'Subject Domain' THEN sd.label
              ELSE coalesce(sd.label, 'Roman Republic') + ' · Subject Domain'
            END,
            sd.node_tier = 'subject_domain'
        RETURN sd.domain_id AS domain_id, sd.label AS label
        """,
        seed_qid=seed_qid,
    ).single()
    return dict(row) if row else {}


def wire_facet_hierarchy(
    session: Any,
    seed_qid: str,
    seed_label: str,
    facet_keys: list[str],
    decompositions: list[dict],
    *,
    dry_run: bool = False,
) -> dict:
    """Wire or rewire facet umbrellas and decomposition hierarchy."""
    stats: dict[str, Any] = {
        "domain_found": False,
        "umbrellas": len(facet_keys),
        "decompositions": len(decompositions),
        "part_of_rewired": 0,
        "scoped_to_domain": 0,
        "domain_has_sc_umbrellas": 0,
        "training_runs_linked": 0,
        "subscopes_linked": 0,
        "removed_scoped_to_period": 0,
        "removed_part_of_bootstrap": 0,
        "removed_has_sc_bootstrap": 0,
        "removed_has_sc_geo": 0,
        "removed_scoped_to_decompositions": 0,
        "removed_scoped_to_umbrella": 0,
    }

    domain_row = session.run(
        """
        MATCH (sd:SubjectDomain {seed_qid: $seed_qid})
        RETURN sd.domain_id AS domain_id, sd.label AS label
        LIMIT 1
        """,
        seed_qid=seed_qid,
    ).single()
    if not domain_row:
        stats["error"] = f"No SubjectDomain for seed_qid={seed_qid}"
        return stats
    stats["domain_found"] = True
    domain_label = domain_row["label"] or seed_label

    facet_labels: dict[str, str] = {}
    for row in session.run(
        "MATCH (f:Facet) RETURN f.key AS key, f.label AS label"
    ):
        if row["key"]:
            facet_labels[str(row["key"]).lower()] = row["label"] or row["key"]

    if dry_run:
        stats["umbrella_ids"] = [
            facet_umbrella_subject_id(seed_qid, fk) for fk in facet_keys
        ]
        for proposal in decompositions:
            fk = (proposal.get("source_facet") or "").lower()
            umbrella_id = facet_umbrella_subject_id(seed_qid, fk)
            stats["part_of_rewired"] += 1
            stats["domain_has_sc_umbrellas"] = len(facet_keys)
            if not proposal.get("_dry_run_subscope"):
                pass
        cnt = session.run(
            """
            MATCH (sc:SubjectConcept {source: 'di_proposal'})-[:SCOPED_TO]->(:Period {qid: $seed_qid})
            RETURN count(sc) AS c
            """,
            seed_qid=seed_qid,
        ).single()
        stats["removed_scoped_to_period"] = cnt["c"] if cnt else 0
        cnt2 = session.run(
            """
            MATCH (sc:SubjectConcept {source: 'di_proposal'})-[:PART_OF]->(p:SubjectConcept)
            WHERE p.source = 'ccs_bootstrap'
            RETURN count(sc) AS c
            """
        ).single()
        stats["removed_part_of_bootstrap"] = cnt2["c"] if cnt2 else 0
        tr = session.run(
            """
            MATCH (tr:SFA_TrainingRun {seed_qid: $seed_qid})
            RETURN count(tr) AS c
            """,
            seed_qid=seed_qid,
        ).single()
        stats["training_runs_linked"] = tr["c"] if tr else 0
        ss = session.run(
            """
            MATCH (ss:SFA_SubScope {seed_qid: $seed_qid})
            RETURN count(ss) AS c
            """,
            seed_qid=seed_qid,
        ).single()
        stats["subscopes_linked"] = ss["c"] if ss else 0
        cnt3 = session.run(
            """
            MATCH (sd:SubjectDomain {seed_qid: $seed_qid})-[r:HAS_SUBJECT_CONCEPT]->(sc:SubjectConcept)
            WHERE sc.source IN ['ccs_bootstrap', 'geo_bootstrap']
            RETURN count(r) AS c
            """
        ).single()
        stats["removed_has_sc_bootstrap"] = cnt3["c"] if cnt3 else 0
        cnt4 = session.run(
            """
            MATCH (sc:SubjectConcept {source: 'di_proposal', seed_qid: $seed_qid})-[:SCOPED_TO]->(:SubjectDomain {seed_qid: $seed_qid})
            RETURN count(sc) AS c
            """,
            seed_qid=seed_qid,
        ).single()
        stats["removed_scoped_to_decompositions"] = cnt4["c"] if cnt4 else 0
        cnt5 = session.run(
            """
            MATCH (sc:SubjectConcept {source: 'di_facet_umbrella', seed_qid: $seed_qid})-[:SCOPED_TO]->(:SubjectDomain {seed_qid: $seed_qid})
            RETURN count(sc) AS c
            """,
            seed_qid=seed_qid,
        ).single()
        stats["removed_scoped_to_umbrella"] = cnt5["c"] if cnt5 else 0
        return stats

    stats.update(prune_domain_direct_attachments(session, seed_qid))
    stats["domain_label"] = distinguish_domain_from_period(session, seed_qid)
    tagged = session.run(
        """
        MATCH (u:SubjectConcept {source: 'di_facet_umbrella', seed_qid: $seed_qid})
        SET u:FacetUmbrella, u.node_tier = 'facet_layer'
        RETURN count(u) AS tagged
        """,
        seed_qid=seed_qid,
    ).single()
    stats["facet_umbrella_labeled"] = tagged["tagged"] if tagged else 0

    # 1. Facet umbrella nodes
    for facet_key in facet_keys:
        umbrella_id = facet_umbrella_subject_id(seed_qid, facet_key)
        facet_label = facet_labels.get(facet_key, facet_key.title())
        label = facet_umbrella_label(domain_label, facet_label)
        cipher = facet_umbrella_cipher(seed_qid, facet_key)
        session.run(
            """
            MERGE (sc:SubjectConcept:FacetUmbrella {subject_id: $subject_id})
            SET sc.label = $label,
                sc.concept_cipher = $cipher,
                sc.seed_qid = $seed_qid,
                sc.source_facet = $facet_key,
                sc.proposal_type = 'facet_umbrella',
                sc.source = 'di_facet_umbrella',
                sc.node_tier = 'facet_layer',
                sc.status = 'approved',
                sc.approved_date = datetime(),
                sc.updated = datetime()
            WITH sc
            MATCH (sd:SubjectDomain {seed_qid: $seed_qid})
            MERGE (sd)-[:HAS_SUBJECT_CONCEPT]->(sc)
            WITH sc
            MATCH (f:Facet {key: toUpper($facet_key)})
            MERGE (sc)-[r:HAS_FACET]->(f)
            SET r.weight = 1.0,
                r.is_primary = true
            """,
            subject_id=umbrella_id,
            label=label,
            cipher=cipher,
            seed_qid=seed_qid,
            facet_key=facet_key,
        )
        stats["domain_has_sc_umbrellas"] += 1

    # 2. Rewire decomposition SCs
    for proposal in decompositions:
        subject_id = proposal.get("subject_id")
        facet_key = (proposal.get("source_facet") or "").lower()
        if not subject_id or not facet_key:
            continue
        umbrella_id = facet_umbrella_subject_id(seed_qid, facet_key)

        removed = session.run(
            """
            MATCH (sc:SubjectConcept {subject_id: $subject_id})-[r:SCOPED_TO]->()
            DELETE r
            RETURN count(*) AS deleted
            """,
            subject_id=subject_id,
        ).single()
        stats["removed_scoped_to_period"] += removed["deleted"] if removed else 0

        removed_part = session.run(
            """
            MATCH (sc:SubjectConcept {subject_id: $subject_id})-[r:PART_OF]->()
            DELETE r
            RETURN count(*) AS deleted
            """,
            subject_id=subject_id,
        ).single()
        stats["removed_part_of_bootstrap"] += removed_part["deleted"] if removed_part else 0

        session.run(
            """
            MATCH (sc:SubjectConcept {subject_id: $subject_id})
            MATCH (umbrella:SubjectConcept {subject_id: $umbrella_id})
            MERGE (sc)-[:PART_OF]->(umbrella)
            """,
            subject_id=subject_id,
            umbrella_id=umbrella_id,
        )
        stats["part_of_rewired"] += 1

    # 3. Link SFA training runs to facet umbrellas
    result = session.run(
        """
        MATCH (tr:SFA_TrainingRun {seed_qid: $seed_qid})
        MATCH (umbrella:SubjectConcept {source: 'di_facet_umbrella', seed_qid: $seed_qid})
        WHERE toUpper(tr.facet_key) = toUpper(umbrella.source_facet)
        MERGE (tr)-[:RELEVANT_TO_SUBJECT]->(umbrella)
        RETURN count(*) AS linked
        """,
        seed_qid=seed_qid,
    ).single()
    stats["training_runs_linked"] = result["linked"] if result else 0

    # 4. Link SFA_SubScope -> decomposition by scope_key
    result = session.run(
        """
        MATCH (ss:SFA_SubScope {seed_qid: $seed_qid})
        MATCH (sc:SubjectConcept {source: 'di_proposal', seed_qid: $seed_qid})
        WHERE sc.scope_key = ss.scope_key
        MERGE (ss)-[:PROMOTED_TO]->(sc)
        RETURN count(*) AS linked
        """,
        seed_qid=seed_qid,
    ).single()
    stats["subscopes_linked"] = result["linked"] if result else 0

    return stats


def fetch_training_facet_keys(session: Any, seed_qid: str) -> list[str]:
    rows = session.run(
        """
        MATCH (tr:SFA_TrainingRun {seed_qid: $seed_qid})
        RETURN DISTINCT toLower(tr.facet_key) AS facet_key
        ORDER BY facet_key
        """,
        seed_qid=seed_qid,
    )
    return [r["facet_key"] for r in rows if r.get("facet_key")]
