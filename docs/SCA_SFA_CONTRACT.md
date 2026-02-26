# SCA–SFA Contract

## The Dialogue

**SCA → SFA:** "Here is the structured harvest. 58 SubjectConcepts, 35 edges, 15 unconfirmed, seven narrative paths. Entity counts from cluster assignment."

**SFA → Graph:** "I accept this as the empirical base. I am adding: within-facet concepts the harvest missed, cross-facet relationships Wikidata doesn't encode, and framework overlays (traversal instructions for specific interpretive contexts)."

**SFA → SCA:** "Re-run salience scoring with these additions."

## Division of Labor

| | SCA | SFA |
|---|-----|-----|
| **Role** | Grounded empirical structure | Historical interpretive judgment |
| **Provides** | Harvest evidence, confidence, entry doors, pre-computed paths | Within-facet additions, cross-facet proposals, framework overlays |
| **Does not** | Validate taxonomy | Discover paths at query time |

## SFA Proposals

SFA proposals go into the graph with provenance:

- `source: "sfa_inference"`
- `confidence: 0.75`
- Contestable by other SFAs with different frameworks

They are treated as claims, not ground truth. The same epistemics that apply to historical claims apply to the SFA's structural proposals.

## Examples

- **Within-facet:** SCA has Q1887031 (mos maiorum) under INTELLECTUAL; SFA proposes *pietas* and *fides* as distinct children.
- **Cross-facet:** Religion and Government are separate in the taxonomy; SFA proposes a relationship (auspices as veto mechanism) that Wikidata doesn't model.
- **Framework overlay:** "Under a Polybian lens, POLITICAL and MILITARY are a single system" — traversal instruction, not graph change.

## The Loop

The self-describing system completes its loop when SFA proposals flow back into the graph and SCA re-scores with those additions. Neither can do the other's job.
