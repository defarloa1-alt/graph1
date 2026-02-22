# GNN Experiment Protocol (2026-02-18)

Status: `ARB-GNN-001` protocol baseline.

## Objective
Define a reproducible, non-production GNN experiment protocol for:
1. link prediction
2. claim plausibility ranking

This protocol is for research evaluation only and does not authorize canonical graph writes.

## Scope
In scope:
- Offline experiments on frozen graph snapshots.
- Baseline-vs-GNN comparison using fixed metrics.
- Reproducible run metadata and artifact outputs.

Out of scope:
- Production inference path.
- Real-time model serving.
- Autonomous promotion decisions.

## Experiment Tasks (v1)
1. Link prediction
- Predict missing relationships among known nodes.

2. Plausibility ranking
- Rank claim candidates by modeled plausibility score.

## Baseline Models (Required)
1. Heuristic baseline
- deterministic rule score from existing policy/federation features.

2. Embedding baseline
- non-GNN vector similarity ranking from embedding pipeline outputs.

3. Simple classifier baseline
- logistic regression or gradient-boosted tree on engineered features.

Purpose:
- GNN results must beat simple baselines, not just random guess.

## GNN Candidate Models (v1)
1. `GraphSAGE`
2. `GAT`
3. `R-GCN` (if relation-type support is needed for link prediction)

Start with one model (`GraphSAGE`) before adding others.

## Data Split Strategy
1. Temporal-aware split (preferred)
- Train on earlier period slice.
- Validate/test on later slice.

2. Edge split for link prediction
- Positive edges sampled from observed relations.
- Negative edges sampled with typed constraints.

3. Node leakage controls
- prevent direct train/test overlap on target edges.
- keep relation-type distribution stable across splits.

## Metrics
Link prediction:
- `MRR`
- `Hits@1`
- `Hits@3`
- `Hits@10`
- `AUC-ROC` (optional)

Plausibility ranking:
- `Precision@k`
- `Recall@k`
- `NDCG@k`
- calibration error (optional)

Operational metrics:
- training runtime
- inference runtime
- model size

## Experiment Artifact Contract
Each run should emit:
- `experiment_id`
- `dataset_snapshot_id`
- `model_name`
- `model_version`
- `split_strategy`
- `seed`
- metrics summary
- confusion/error slices by relation type
- reproducibility metadata (library versions, config hash)

Target path (planned):
- `JSON/reports/gnn_experiments/<experiment_id>.json`

## Governance and Safety
- Experiment outputs are advisory only.
- No direct promotion or canonical writes from GNN scores.
- All downstream use must remain within `U -> Pi -> Commit`.
- Keep `GNN` track decoupled from critical extraction/promotion path.

## Execution Sequence (v1)
1. Freeze dataset snapshot and split definitions.
2. Run baseline models and record metrics.
3. Run first GNN model with fixed seed.
4. Compare GNN vs baseline deltas.
5. Publish experiment report and recommendation.

## Success Criteria (`ARB-GNN-001`)
- Baseline model list is explicit.
- Train/test split strategy is explicit.
- Metrics are explicit and task-aligned.
- Governance boundary (non-production) is explicit.
