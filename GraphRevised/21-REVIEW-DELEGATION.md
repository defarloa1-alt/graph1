# Review Delegation Policy (interim)

**Status:** agreed with the curator, 2026-10-12. Interim until the Phase C
automatic acceptance policy ([docs/Response - Use Cases.md](docs/Response%20-%20Use%20Cases.md))
is written and enforced in code.

## 1. Why a policy is needed

The core rule is that agents propose and only a curator accepts. When the
curator delegates review to Claude, a model reviews another model's proposals
(the passage reader is also Claude), so their errors may be correlated rather
than independent. In an exploration graph a wrong edge creates false paths,
not one wrong fact. Delegation is therefore limited to decisions that a
verbatim quotation lets anyone check, and every delegated decision stays
identifiable.

## 2. Scope

| Claude may decide (when delegated) | Only the curator decides |
|---|---|
| Accept participation and place claims whose verbatim quotation plainly shows presence in the event or its location | Identity: which real person, place, or group a name denotes, and every identity-queue choice |
| Reject evidence (not the claim) as `unsupported`, leaving the claim open | Predicate and model changes, and anything under the design-mode policy (the open `commanded` claims) |
| Bookkeeping: duplicates, stored copies of the same evidence | Interpretive, causal, or contested claims; roles; command and authority |
| | Any proposal flagged UNCERTAIN unless the quotation alone resolves the doubt |
| | Rejecting a claim (`reject --claim`), superseding, retracting, and reopening |
| | Promoting an attributed claim to asserted (E12) |

When a case is not clearly in the left column, Claude leaves it open and says
why.

## 3. How delegated decisions are recorded

- `decidedBy` is `Claude (delegated by <curator>)`, never the curator's own
  name, so delegated decisions can be listed and audited separately.
- Every decision has a basis that cites the quotation it relies on, and every
  rejection a reason code.
- The delegation itself is per request: the curator asks for a review, and
  the policy limits what that review may decide.

## 4. Correction

A wrong delegated acceptance is undone by the curator with `review retract
<assertion> --reason <code>`: the claim becomes `rejected`, keeps its evidence
links as audit history, and can be reopened. A retraction is refused while
the claim has open Proposals.

## 5. Spot checks

The curator periodically samples delegated decisions. The first delegated
review (2026-10-12) accepted nine proposals and rejected one piece of
evidence; it is listed in [18 §17](18-PHASE-5-PROPOSALS.md). Its least
obvious decision is Eurycles (67.2), where pursuit of Antony's flight was
counted as part of the engagement.
