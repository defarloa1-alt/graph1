"""SFA CLI — Subject Facet Agent."""

import argparse
from pathlib import Path

FACET_CHOICES = [
    "ARCHAEOLOGICAL", "ARTISTIC", "BIOGRAPHICAL", "COMMUNICATION",
    "CULTURAL", "DEMOGRAPHIC", "DIPLOMATIC", "ECONOMIC",
    "ENVIRONMENTAL", "GEOGRAPHIC", "INTELLECTUAL", "LINGUISTIC",
    "MILITARY", "POLITICAL", "RELIGIOUS", "SCIENTIFIC",
    "SOCIAL", "TECHNOLOGICAL",
]

SCOPE_FACET_CHOICES = [
    "POLITICAL", "MILITARY", "GEOGRAPHIC", "ECONOMIC", "SOCIAL", "RELIGIOUS",
    "BIOGRAPHICAL", "INTELLECTUAL", "ARCHAEOLOGICAL", "LINGUISTIC", "DIPLOMATIC",
    "CULTURAL", "ENVIRONMENTAL", "TECHNOLOGICAL", "ARTISTIC", "SCIENTIFIC",
    "DEMOGRAPHIC", "COMMUNICATION",
]


def main():
    parser = argparse.ArgumentParser(
        description="Subject Facet Agent (SFA) — propose SubjectConcepts, scope federated view"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_propose = subparsers.add_parser("propose", help="Propose SubjectConcepts for a facet")
    p_propose.add_argument("--facet", required=True, choices=FACET_CHOICES,
                           help="Facet (POLITICAL has full evidence)")
    p_propose.add_argument("--seed", default="Q17167", help="Seed QID (default: Q17167)")
    p_propose.add_argument("--model", default="claude-sonnet-4-6", help="Claude model")

    p_scope = subparsers.add_parser("scope", help="Scope federated view for facet")
    p_scope.add_argument("--facet", required=True, choices=SCOPE_FACET_CHOICES)
    p_scope.add_argument("--seed", default="Q17167")
    p_scope.add_argument("--input", type=Path, default=None,
                         help="Path to federated JSON (default: latest in output/reports)")
    p_scope.add_argument("--model", default="claude-sonnet-4-6")

    args = parser.parse_args()

    if args.command == "propose":
        from .subject_concept_proposer import propose

        result = propose(facet=args.facet, seed_qid=args.seed, model=args.model)

        proposals = result.get("proposals", [])
        if proposals:
            print()
            print(f"-- {args.facet} PROPOSALS " + "-" * 50)
            for i, p in enumerate(proposals, 1):
                split_flag = " [SPLIT RECOMMENDED]" if p.get("d12_split_recommended") else ""
                print(f"  {i}. {p['proposed_label']}{split_flag}")
                print(f"     Scope: {p['proposed_scope'][:100]}...")
                print(f"     Confidence: {p.get('confidence', '?')}")
                print(f"     Anchor: {p.get('anchor_qid', 'none')} | LCC: {p.get('lcc_anchor', 'none')}")
                if p.get("d12_note"):
                    print(f"     D12: {p['d12_note'][:100]}...")
                print()
            sfa_notes = result.get("sfa_notes", "")
            if sfa_notes:
                print(f"SFA notes: {sfa_notes}")

    elif args.command == "scope":
        from .scope_federated_view import scope

        result = scope(facet=args.facet, seed_qid=args.seed, input_path=args.input, model=args.model)

        out = result.get("output", {})
        if "parse_error" not in out:
            print()
            print(f"-- SCOPED FOR {args.facet} " + "-" * 40)
            print(f"  Disciplines: {len(out.get('scoped_disciplines', []))}")
            print(f"  LCC:         {len(out.get('scoped_lcc', []))}")
            print(f"  LCSH:        {len(out.get('scoped_lcsh', []))}")
            print(f"  Entities:    {len(out.get('scoped_entities', []))}")
            if out.get("sfa_rationale"):
                print(f"  Rationale:   {out['sfa_rationale'][:80]}...")
