#!/usr/bin/env python3
"""Embedding pilot scaffold for Chrystallum.

This script does not train a production model. It emits a deterministic
metadata artifact that defines the pilot run contract for future embedding
pipelines.
"""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List


CONTRACT_VERSION = "embedding_pilot_contract_v1"
SCRIPT_VERSION = "0.1.0-scaffold"
DEFAULT_COHORTS = ["Human", "Event", "Place", "SubjectConcept"]
DEFAULT_OUTPUT = Path("JSON/embeddings/embedding_pilot_metadata.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cohorts",
        nargs="+",
        default=DEFAULT_COHORTS,
        help="Node cohorts included in this pilot artifact.",
    )
    parser.add_argument(
        "--vector-dim",
        type=int,
        default=384,
        help="Planned embedding dimensionality for the pilot contract.",
    )
    parser.add_argument(
        "--distance-metric",
        choices=["cosine", "dot", "euclidean"],
        default="cosine",
        help="Planned similarity metric.",
    )
    parser.add_argument(
        "--model-family",
        default="placeholder_text_graph_hybrid",
        help="Placeholder model family label for metadata tracking.",
    )
    parser.add_argument(
        "--model-version",
        default="v0_pilot",
        help="Model version label for metadata tracking.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic seed for future reproducibility.",
    )
    parser.add_argument(
        "--refresh-cadence",
        default="weekly_batch",
        help="Planned refresh cadence.",
    )
    parser.add_argument(
        "--run-label",
        default="embedding_pilot_baseline",
        help="Stable label for this run profile.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON artifact path.",
    )
    return parser.parse_args()


def stable_fingerprint(fields: Dict[str, Any]) -> str:
    payload = json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(payload.encode("utf-8")).hexdigest()


def build_metadata(args: argparse.Namespace) -> Dict[str, Any]:
    cohorts: List[str] = sorted({str(item) for item in args.cohorts})
    fingerprint_basis = {
        "contract_version": CONTRACT_VERSION,
        "script_version": SCRIPT_VERSION,
        "run_label": args.run_label,
        "cohorts": cohorts,
        "vector_dim": args.vector_dim,
        "distance_metric": args.distance_metric,
        "model_family": args.model_family,
        "model_version": args.model_version,
        "seed": args.seed,
        "refresh_cadence": args.refresh_cadence,
    }
    run_fingerprint = stable_fingerprint(fingerprint_basis)

    return {
        "metadata_header": {
            "contract_version": CONTRACT_VERSION,
            "artifact_type": "embedding_pilot_run_metadata",
            "script_version": SCRIPT_VERSION,
            "run_label": args.run_label,
            "run_fingerprint": run_fingerprint,
            "determinism_mode": "strict_input_hash",
        },
        "pilot_config": {
            "cohorts": cohorts,
            "vector_dim": args.vector_dim,
            "distance_metric": args.distance_metric,
            "model_family": args.model_family,
            "model_version": args.model_version,
            "seed": args.seed,
            "refresh_cadence": args.refresh_cadence,
        },
        "output_contract": {
            "vector_key": "node_id",
            "vector_field": "embedding",
            "required_fields": [
                "node_id",
                "node_label",
                "node_type",
                "embedding",
            ],
            "quality_metrics_required": [
                "coverage_ratio",
                "sample_topk_sanity",
            ],
        },
        "training_state": {
            "status": "scaffold_no_training_executed",
            "checkpoint_written": False,
            "vectors_written": False,
        },
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    if args.vector_dim <= 0:
        raise SystemExit("vector-dim must be > 0")
    metadata = build_metadata(args)
    write_json(args.output, metadata)
    print(f"artifact={args.output.as_posix()}")
    print(f"run_fingerprint={metadata['metadata_header']['run_fingerprint']}")
    print("status=scaffold_complete")


if __name__ == "__main__":
    main()
