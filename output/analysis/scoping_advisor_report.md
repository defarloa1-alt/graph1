# Federation Scoping: Advisor Report

**Generated after full harvest + cluster assignment.**

## Summary

| Metric | Value |
|--------|-------|
| Total MEMBER_OF edges | 9,144 |
| Scoped (temporal + domain + legacy) | 8,338 |
| Unscoped (noise) | 806 |
| % Unscoped | 8.8% |

**Scoping rule:** Entities with Trismegistos (P1696), LGPN (P1838), Pleiades (P1584), or DPRR (P6863/dprr_imported) → temporal_scoped. VIAF (P214) + domain backlink → domain_scoped. No federation IDs → unscoped.

## Per-Cluster Distribution

| SubjectConcept | Label | Total | Temporal | Domain | Unscoped | % Unscoped |
|----------------|-------|--------|----------|--------|----------|------------|
| Q899409 | Families, Gentes, and Prosopography | 5363 | 4863 | 0 | 0 | 0.0% |
| Q11469 | Landholding, Agriculture, and Estates | 666 | 2 | 85 | 84 | 12.6% |
| Q2277 | Transition to Empire | 500 | 27 | 122 | 39 | 7.8% |
| Q11019 | Trade routes and maritime networks | 455 | 0 | 14 | 3 | 0.7% |
| Q131416 | Priesthoods and sacred colleges | 279 | 0 | 40 | 120 | 43.0% |
| Q1541 | Forums, public speech, persuasion | 268 | 0 | 76 | 118 | 44.0% |
| Q211364 | Popular/admin offices: Tribune, Aedile,  | 253 | 0 | 0 | 1 | 0.4% |
| Q17167 | Roman Republic | 228 | 2 | 55 | 113 | 49.6% |
| Q337547 | Public ritual, auspices, legitimacy | 190 | 2 | 109 | 79 | 41.6% |
| Q182547 | Provinces and Administration | 171 | 79 | 84 | 1 | 0.6% |
| Q207544 | Geography, Provinces, and Expansion | 148 | 0 | 2 | 99 | 66.9% |
| Q726929 | Courts, trials, legal procedure | 118 | 0 | 0 | 0 | 0.0% |
| Q952064 | Markets, money, and exchange | 103 | 0 | 9 | 11 | 10.7% |
| Q236885 | Dictatorship & extraordinary commands | 80 | 0 | 12 | 63 | 78.8% |
| Q657326 | Social orders (Patrician, Plebeian, Equi | 40 | 0 | 0 | 0 | 0.0% |
| Q212943 | Religious Offices, Priesthoods, and Auth | 24 | 0 | 10 | 12 | 50.0% |
| Q1764124 | External wars (interstate/expansionary) | 21 | 0 | 0 | 20 | 95.2% |
| Q1747183 | Internal wars (civil/social/rebellion) | 20 | 0 | 13 | 4 | 20.0% |
| Q7188 | Government and Constitutional Structure | 19 | 0 | 6 | 13 | 68.4% |
| Q2065169 | Political violence, proscriptions, purge | 19 | 0 | 0 | 1 | 5.3% |
| Q1200427 | Culture, Ideas, and Communication | 19 | 0 | 2 | 0 | 0.0% |
| Q271108 | Factional politics (Optimates/Populares  | 18 | 0 | 1 | 17 | 94.4% |
| Q15265460 | Economy and Resource Systems | 17 | 0 | 0 | 0 | 0.0% |
| Q39686 | Offices and Magistracies (Cursus Honorum | 16 | 0 | 0 | 1 | 6.2% |
| Q2345364 | Historiography, Sources, and Historical  | 16 | 0 | 0 | 0 | 0.0% |
| ... | ... | ... | ... | ... | ... | ... |

## Noise Hotspots (Top 10 by % Unscoped)

| SubjectConcept | Label | Total | Unscoped | % Unscoped | Notes |
|----------------|-------|--------|----------|------------|-------|
| Q1764124 | External wars (interstate/expansionary) | 21 | 20 | 95.2% | Legitimate unscoped (events) |
| Q271108 | Factional politics (Optimates/Populares frami | 18 | 17 | 94.4% | Legitimate unscoped (events) |
| Q236885 | Dictatorship & extraordinary commands | 80 | 63 | 78.8% |  |
| Q7188 | Government and Constitutional Structure | 19 | 13 | 68.4% |  |
| Q207544 | Geography, Provinces, and Expansion | 148 | 99 | 66.9% |  |
| Q212943 | Religious Offices, Priesthoods, and Authority | 24 | 12 | 50.0% |  |
| Q17167 | Roman Republic | 228 | 113 | 49.6% |  |
| Q1541 | Forums, public speech, persuasion | 268 | 118 | 44.0% |  |
| Q131416 | Priesthoods and sacred colleges | 279 | 120 | 43.0% |  |
| Q337547 | Public ritual, auspices, legitimacy | 190 | 79 | 41.6% |  |

**Legitimate unscoped:** Q1764124 (External wars), Q271108 (Factional politics) — wars/battles/events. Current federation sources (DPRR, Pleiades, Trismegistos, LGPN) are person/place/inscription authorities; they don't model events. No action needed.

## Trustworthy Clusters (unscoped_pct < 65% AND scoped >= 10)

| SubjectConcept | Label | Scoped | % Unscoped | Notes |
|----------------|-------|--------|------------|-------|
| Q899409 | Families, Gentes, and Prosopography | 5363 | 0.0% |  |
| Q726929 | Courts, trials, legal procedure | 118 | 0.0% | Courts/trials — legal procedure entities with VIAF. |
| Q657326 | Social orders (Patrician, Plebeian, Equi | 40 | 0.0% |  |
| Q1200427 | Culture, Ideas, and Communication | 19 | 0.0% |  |
| Q15265460 | Economy and Resource Systems | 17 | 0.0% |  |
| Q2345364 | Historiography, Sources, and Historical  | 16 | 0.0% |  |
| Q1367629 | Ritual Practice, Omens, and Public Cerem | 13 | 0.0% |  |
| Q1593880 | Institutions of slavery and manumission | 13 | 0.0% |  |
| Q1392538 | Society and Social Structure | 12 | 0.0% |  |
| Q211364 | Popular/admin offices: Tribune, Aedile,  | 252 | 0.4% |  |
| Q182547 | Provinces and Administration | 170 | 0.6% | Best cluster. P1584 Pleiades driving temporal anchors. |
| Q11019 | Trade routes and maritime networks | 452 | 0.7% |  |
| Q2065169 | Political violence, proscriptions, purge | 18 | 5.3% |  |
| Q39686 | Offices and Magistracies (Cursus Honorum | 15 | 6.2% |  |
| Q2277 | Transition to Empire | 461 | 7.8% |  |
| Q185816 | Naval warfare and sea operations | 10 | 9.1% |  |
| Q952064 | Markets, money, and exchange | 92 | 10.7% |  |
| Q11469 | Landholding, Agriculture, and Estates | 582 | 12.6% |  |
| Q1747183 | Internal wars (civil/social/rebellion) | 16 | 20.0% |  |
| Q337547 | Public ritual, auspices, legitimacy | 111 | 41.6% | Strong VIAF + ritual/religious authority backlinks. |
| Q131416 | Priesthoods and sacred colleges | 159 | 43.0% |  |
| Q1541 | Forums, public speech, persuasion | 150 | 44.0% | VIAF on orators and jurists. |
| Q17167 | Roman Republic | 115 | 49.6% |  |
| Q212943 | Religious Offices, Priesthoods, and Auth | 12 | 50.0% | Borderline — 9 scoped, just under threshold. Monitor. |

## Impact on Door Selection

**Without `--use-scoped-counts`:** SCA ranks doors by raw entity count.

**With `--use-scoped-counts`:** SCA ranks by scoped count only. Noisy clusters (high % unscoped) drop in rank.

Example: Q7188 (Government) — 982 total, 69 scoped. Without scoping it dominates; with scoping it is deprioritized.

Example: Q899409 (Families/Prosopography) — 5363 total, 5363 scoped, 0.0% unscoped. DPRR federation made this the strongest cluster (post-DPRR baseline 2026-02-25).

## Diagnostic Notes

**Failure mode 1 — Named entity clusters with no federation IDs:** Q899409 Families, Q7188 Government, Q2277 Transition to Empire — these contain real domain-relevant persons, gentes, magistrates. They fail scoping because the harvester didn't reach Trismegistos/LGPN/Pleiades records for them. Fix: targeted re-harvest following the property chains that worked for Q182547 and Q337547. Those two clusters got scoped via Pleiades (geographic places) and VIAF (named religious authorities). The same approach applied to persons in Q899409 via LGPN should work.

**Failure mode 2 — Conceptual entity clusters:** Q211364 Popular offices, Q39686 Cursus Honorum, Q952064 Markets — these contain Wikidata items for *concepts* (the office of Tribune, the institution of the cursus honorum) rather than *instances* (specific tribunes, specific market transactions). Federation IDs will never fire on these because they are not persons or places. The schema's entity_scoping design already anticipated this — conceptual entities scope via domain graph proximity, not federation IDs. But the harvester isn't applying that rule yet.

**Template for scoped re-harvest:** The trustworthy clusters (Q182547, Q337547, Q1541, Q726929) share a common pattern: they contain named individuals or geographic places with Pleiades IDs or VIAF records. Trace the property chains that brought Pleiades and VIAF into those clusters and replicate deliberately across the person-heavy clusters. Separate handling for conceptual entity clusters using domain proximity scoping (see entity_scoping in schema v3.5).

---

*Report generated: 2026-02-25*
*Generated by `scripts/analysis/scoping_advisor_report.py`*