#!/usr/bin/env python3
"""
Tests for SCA salience: loaders, base_score, path_coherence, select_doors.
Uses unit tests only (no Neo4j, no API calls).
"""
import json
import tempfile
from pathlib import Path

import pytest

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.backbone.subject.sca_salience_doors import (
    load_anchors,
    load_hierarchy,
    compute_depth,
    load_entity_counts,
    load_harvest_status,
    load_narrative_paths,
    base_score,
    path_coherence,
    select_doors,
)


class TestLoadAnchors:
    def test_list_format(self):
        anchors = [
            {"qid": "Q17167", "label": "Roman Republic", "confidence": "curated", "primary_facet": "ROOT"},
            {"qid": "Q7188", "label": "Government", "confidence": "llm:0.95", "primary_facet": "POLITICAL"},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(anchors, f)
            path = Path(f.name)
        try:
            result = load_anchors(path)
            assert result["Q17167"]["label"] == "Roman Republic"
            assert result["Q17167"]["confidence"] == "curated"
            assert result["Q7188"]["primary_facet"] == "POLITICAL"
        finally:
            path.unlink()

    def test_wrapped_format(self):
        anchors = [{"qid": "Q17167", "label": "Roman Republic"}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"anchors": anchors}, f)
            path = Path(f.name)
        try:
            result = load_anchors(path)
            assert "Q17167" in result
        finally:
            path.unlink()


class TestLoadHierarchy:
    def test_broader_than(self):
        data = {
            "broader_than": [
                {"child_qid": "Q7188", "parent_qid": "Q17167"},
                {"child_qid": "Q105427", "parent_qid": "Q7188"},
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)
        try:
            parents, children = load_hierarchy(path)
            assert parents["Q7188"] == ["Q17167"]
            assert parents["Q105427"] == ["Q7188"]
            assert children["Q17167"] == ["Q7188"]
            assert children["Q7188"] == ["Q105427"]
        finally:
            path.unlink()


class TestComputeDepth:
    def test_simple_tree(self):
        parents = {"Q7188": ["Q17167"], "Q105427": ["Q7188"]}
        children = {"Q17167": ["Q7188"], "Q7188": ["Q105427"]}
        depth = compute_depth("Q17167", parents, children)
        assert depth["Q17167"] == 0
        assert depth["Q7188"] == 1
        assert depth["Q105427"] == 2


class TestLoadEntityCounts:
    def test_member_of_edges(self):
        edges = [
            {"subject_qid": "Q7188", "entity_qid": "Q1"},
            {"subject_qid": "Q7188", "entity_qid": "Q2"},
            {"subject_qid": "Q105427", "entity_qid": "Q3"},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(edges, f)
            path = Path(f.name)
        try:
            counts = load_entity_counts(path)
            assert counts["Q7188"] == 2
            assert counts["Q105427"] == 1
        finally:
            path.unlink()


class TestLoadHarvestStatus:
    def test_completed(self):
        data = {"completed": ["Q17167", "Q7188"], "failed": {}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)
        try:
            status = load_harvest_status(path)
            assert status == {"Q17167", "Q7188"}
        finally:
            path.unlink()

    def test_missing_file(self):
        status = load_harvest_status(Path("/nonexistent/harvest_progress.json"))
        assert status == set()


class TestBaseScore:
    def test_high_entity_density(self):
        s = base_score("Q7188", entity_count=100, confidence="curated", harvest_confirmed=True, depth=1)
        assert s >= 0.75  # entity 0.35 + confidence 0.225 + harvest 0.20 = 0.775

    def test_zero_entities(self):
        s = base_score("Q7188", entity_count=0, confidence="curated", harvest_confirmed=False, depth=1)
        assert 0 < s < 0.5

    def test_depth_penalty(self):
        s1 = base_score("Q", 50, "curated", True, depth=1)
        s2 = base_score("Q", 50, "curated", True, depth=3)
        assert s2 < s1


class TestLoadNarrativePaths:
    def test_load_paths(self):
        data = {
            "paths": [
                {"id": "p1", "path": ["Q7188", "Q20720797", "Q1993655"]},
                {"id": "p2", "path": ["Q1392538", "Q8464"]},
            ]
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)
        try:
            result = load_narrative_paths(path)
            assert len(result) == 2
            assert result[0] == ["Q7188", "Q20720797", "Q1993655"]
        finally:
            path.unlink()

    def test_missing_file(self):
        assert load_narrative_paths(Path("/nonexistent/paths.json")) == []


class TestPathCoherence:
    def test_viable_children(self):
        children = {"Q7188": ["Q105427", "Q39686", "Q213810"]}
        entity_counts = {"Q105427": 10, "Q39686": 8, "Q213810": 3}
        harvest_confirmed = {"Q105427", "Q39686"}
        s = path_coherence("Q7188", children, entity_counts, harvest_confirmed, min_entities=5)
        assert s > 0

    def test_no_children(self):
        s = path_coherence("Q7188", {}, {}, set())
        assert s >= 0

    def test_narrative_boost(self):
        """Doors that start curated paths get a narrative boost."""
        narrative_paths = [["Q7188", "Q20720797"], ["Q1392538", "Q8464"]]
        s_with = path_coherence("Q7188", {}, {}, set(), narrative_paths=narrative_paths)
        s_without = path_coherence("Q7188", {}, {}, set(), narrative_paths=None)
        assert s_with > s_without


class TestSelectDoors:
    def test_diversity(self):
        anchors = {
            "Q7188": {"label": "Government", "primary_facet": "POLITICAL"},
            "Q207544": {"label": "Geography", "primary_facet": "GEOGRAPHIC"},
            "Q1392538": {"label": "Society", "primary_facet": "SOCIAL"},
        }
        candidates = [("Q7188", 0.9), ("Q207544", 0.85), ("Q1392538", 0.7)]
        doors = select_doors(candidates, anchors, n=3)
        assert len(doors) == 3
        facets = {d["primary_facet"] for d in doors}
        assert len(facets) == 3  # all different

    def test_min_entities_excludes_sparse_clusters(self):
        """SubjectConcepts with < min_entities are structurally present but not navigable."""
        from scripts.backbone.subject.sca_salience_doors import main
        import sys

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            anchors = [
                {"qid": "Q17167", "label": "Roman Republic", "primary_facet": "ROOT"},
                {"qid": "Q7188", "label": "Government", "primary_facet": "POLITICAL"},
                {"qid": "Q201452", "label": "Diplomacy", "primary_facet": "POLITICAL"},
                {"qid": "Q186916", "label": "Chronology", "primary_facet": "TEMPORAL"},
            ]
            (root / "anchors.json").write_text(json.dumps(anchors), encoding="utf-8")
            hierarchy = {"broader_than": [
                {"child_qid": "Q7188", "parent_qid": "Q17167"},
                {"child_qid": "Q201452", "parent_qid": "Q17167"},
                {"child_qid": "Q186916", "parent_qid": "Q17167"},
            ]}
            (root / "hierarchy.json").write_text(json.dumps(hierarchy), encoding="utf-8")
            edges = (
                [{"subject_qid": "Q7188", "entity_qid": f"Q{i}"} for i in range(50)]
                + [{"subject_qid": "Q201452", "entity_qid": "Q999"}]
                + [{"subject_qid": "Q186916", "entity_qid": "Q998"}]
            )
            (root / "member_of_edges.json").write_text(json.dumps(edges), encoding="utf-8")
            (root / "harvest_progress.json").write_text(
                json.dumps({"completed": ["Q7188", "Q201452", "Q186916"]}), encoding="utf-8"
            )
            (root / "narrative_paths.json").write_text(json.dumps({"paths": []}), encoding="utf-8")
            out_path = root / "doors.json"

            old_argv = sys.argv
            try:
                sys.argv = [
                    "sca_salience_doors.py",
                    "--root", "Q17167",
                    "--doors", "5",
                    "--anchors", str(root / "anchors.json"),
                    "--hierarchy", str(root / "hierarchy.json"),
                    "--edges", str(root / "member_of_edges.json"),
                    "--harvest-progress", str(root / "harvest_progress.json"),
                    "--narrative-paths", str(root / "narrative_paths.json"),
                    "--output", str(out_path),
                    "--min-entities", "10",
                    "--no-neo4j",
                ]
                main()
            finally:
                sys.argv = old_argv

            report = json.loads(out_path.read_text(encoding="utf-8"))
            door_qids = {d["qid"] for d in report["doors"]}
            assert "Q7188" in door_qids
            assert "Q201452" not in door_qids
            assert "Q186916" not in door_qids
            assert report["min_entities_threshold"] == 10
