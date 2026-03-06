"""
SCA CLI — Subject Classification Agent

Usage:
    python -m scripts.agents.sca landscape Q17167 --taxonomy ... --lateral ...
"""

import argparse

from .landscape_synthesis import synthesize


def main():
    parser = argparse.ArgumentParser(
        description="Subject Classification Agent (SCA) — domain landscape synthesis"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # landscape subcommand
    p_landscape = subparsers.add_parser("landscape", help="Synthesize domain landscape")
    p_landscape.add_argument("seed_qid", help="Seed QID (e.g. Q17167)")
    p_landscape.add_argument("--taxonomy", required=True, help="Path to taxonomy JSON")
    p_landscape.add_argument("--lateral", required=True, help="Path to lateral JSON")
    p_landscape.add_argument("--output", default="output/sca_landscape/", help="Output directory")
    p_landscape.add_argument("--model", default="claude-sonnet-4-6", help="Claude model ID")

    args = parser.parse_args()

    if args.command == "landscape":
        result = synthesize(
            seed_qid=args.seed_qid,
            taxonomy_path=args.taxonomy,
            lateral_path=args.lateral,
            output_dir=args.output,
            model=args.model,
        )

        landscape = result.get("landscape", {})
        if "landscape_narrative" in landscape:
            print("\n" + "=" * 70)
            print("LANDSCAPE NARRATIVE:")
            print("=" * 70)
            print(landscape["landscape_narrative"])
            print()

            facet_pointers = landscape.get("facet_pointers", {})
            high = [k for k, v in facet_pointers.items() if v.get("relevance") == "high"]
            medium = [k for k, v in facet_pointers.items() if v.get("relevance") == "medium"]
            print(f"Facet relevance — HIGH ({len(high)}): {', '.join(high)}")
            print(f"                  MED  ({len(medium)}): {', '.join(medium)}")

            candidates = landscape.get("taxonomy_candidates", [])
            print(f"\nTaxonomy candidates flagged: {len(candidates)}")
            for c in candidates:
                print(f"  {c['qid']} {c['label']} ({c['tier']}): {c['reuse_reason'][:60]}")
