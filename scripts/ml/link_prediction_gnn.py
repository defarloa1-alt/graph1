#!/usr/bin/env python3
"""GNN experiment runner scaffold for Chrystallum (non-production).

This script does not train or deploy a production GNN. It emits deterministic
experiment metadata for link-prediction/plausibility research runs.
"""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List


CONTRACT_VERSION = "gnn_experiment_contract_v1"
SCRIPT_VERSION = "0.1.0-scaffold"
DEFAULT_OUTPUT = Path("JSON/reports/gnn_experiments/gnn_experiment_metadata.json")
DEFAULT_BASELINES = ["heuristic_rule_score", "embedding_similarity", "logistic_regression"]
DEFAULT_METRICS_LINK = ["MRR", "Hits@1", "Hits@3", "Hits@10"]
DEFAULT_METRICS_PLAUSIBILITY = ["Precision@10", "Recall@10", "NDCG@10"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--experiment-id",
        default="gnn_experiment_smoke",
        help="Stable experiment identifier.",
    )
    parser.add_argument(
        "--task",
        choices=["link_prediction", "plausibility_ranking"],
        default="link_prediction",
        help="Primary task type for this experiment profile.",
    )
    parser.add_argument(
        "--model-name",
        choices=["GraphSAGE", "GAT", "R-GCN"],
        default="GraphSAGE",
        help="GNN model family under test.",
    )
    parser.add_argument(
        "--model-version",
        default="v0_protocol_smoke",
        help="Model version tag for experiment bookkeeping.",
    )
    parser.add_argument(
        "--dataset-snapshot-id",
        default="dataset_snapshot_pending",
        help="Frozen dataset snapshot identifier.",
    )
    parser.add_argument(
        "--split-strategy",
        choices=["temporal_aware", "edge_holdout"],
        default="temporal_aware",
        help="Evaluation split strategy.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic seed.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Planned epoch count for future training runs.",
    )
    parser.add_argument(
        "--hidden-dim",
        type=int,
        default=128,
        help="Planned hidden dimension for model configuration.",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.001,
        help="Planned optimizer learning rate.",
    )
    parser.add_argument(
        "--baselines",
        nargs="+",
        default=DEFAULT_BASELINES,
        help="Baseline models required for comparison.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON artifact path.",
    )
    return parser.parse_args()


def stable_fingerprint(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(canonical.encode("utf-8")).hexdigest()


def build_metrics(task: str) -> List[str]:
    if task == "link_prediction":
        return list(DEFAULT_METRICS_LINK)
    return list(DEFAULT_METRICS_PLAUSIBILITY)


def build_metadata(args: argparse.Namespace) -> Dict[str, Any]:
    if args.hidden_dim <= 0:
        raise ValueError("hidden-dim must be > 0")
    if args.epochs <= 0:
        raise ValueError("epochs must be > 0")
    if args.learning_rate <= 0:
        raise ValueError("learning-rate must be > 0")

    baselines = sorted({str(item) for item in args.baselines})
    metrics = build_metrics(args.task)
    fingerprint_basis = {
        "contract_version": CONTRACT_VERSION,
        "script_version": SCRIPT_VERSION,
        "experiment_id": args.experiment_id,
        "task": args.task,
        "model_name": args.model_name,
        "model_version": args.model_version,
        "dataset_snapshot_id": args.dataset_snapshot_id,
        "split_strategy": args.split_strategy,
        "seed": args.seed,
        "epochs": args.epochs,
        "hidden_dim": args.hidden_dim,
        "learning_rate": args.learning_rate,
        "baselines": baselines,
        "metrics": metrics,
    }
    run_fingerprint = stable_fingerprint(fingerprint_basis)

    return {
        "metadata_header": {
            "contract_version": CONTRACT_VERSION,
            "artifact_type": "gnn_experiment_run_metadata",
            "script_version": SCRIPT_VERSION,
            "experiment_id": args.experiment_id,
            "run_fingerprint": run_fingerprint,
            "determinism_mode": "strict_input_hash",
            "production_scope": "non_production_only",
        },
        "experiment_config": {
            "task": args.task,
            "model_name": args.model_name,
            "model_version": args.model_version,
            "dataset_snapshot_id": args.dataset_snapshot_id,
            "split_strategy": args.split_strategy,
            "seed": args.seed,
            "epochs": args.epochs,
            "hidden_dim": args.hidden_dim,
            "learning_rate": args.learning_rate,
        },
        "baseline_requirements": baselines,
        "metric_contract": metrics,
        "governance": {
            "advisory_only": True,
            "canonical_write_allowed": False,
            "promotion_path": "U->Pi->Commit",
        },
        "training_state": {
            "status": "scaffold_no_training_executed",
            "model_checkpoint_written": False,
            "predictions_written": False,
        },
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    metadata = build_metadata(args)
    write_json(args.output, metadata)
    print(f"artifact={args.output.as_posix()}")
    print(f"run_fingerprint={metadata['metadata_header']['run_fingerprint']}")
    print("status=scaffold_complete")


if __name__ == "__main__":
    main()
