# Dual facet grounding — historical domain + global discipline

**Status:** Design lock candidate for Chrystal 2  
**Precedent:** Military already uses `roman_republic` + `military_theory` (`docs/FACET_TRAINING_CONTRACT.md`).

## Idea

Every subject facet needs **two** grounding surfaces:

| Layer | Example (Military) | Example (Economic) | What lives there |
|-------|--------------------|--------------------|------------------|
| **Historical / pack domain** | `roman_republic` | `roman_republic` or `meiji_japan` | Time-bound facts: Cannae, lex agraria, Meiji land tax |
| **Global discipline** | `military_theory` | `economic_theory` (or `global_economic`) | Durable discipline truths: envelopment, supply & demand, properties of gold |

An SFA LLM is trained (grounded) in the **discipline** as best practice. When it proposes Claims, it must choose the correct **SubjectDomain**:

- RR-specific → SubjectDomain `roman_republic` (`kind: historical_pack`)
- Timeless / cross-era → SubjectDomain `military_theory` / `economic_theory` (`kind: global_theory`)

That split is what lets the graph **connect past and present** without collapsing theory into one polity pack.

**Neo label:** both are `:SubjectDomain`. There is no separate `:Domain` node (see `TERMINOLOGY.md`).

## Naming (proposal)

Prefer explicit pairs, not a second Facet key in the 18:

- Facet catalog stays: `MILITARY`, `ECONOMIC`, `POLITICAL`, … (18)
- Domains: `{pack_id}` + `global_{facet}` or `{discipline}_theory`

Examples:

| Facet | Pack domain | Global domain |
|-------|-------------|---------------|
| MILITARY | `roman_republic` | `military_theory` (exists) |
| ECONOMIC | `roman_republic` | `economic_theory` |
| RELIGIOUS | `roman_republic` | `religious_studies` / `global_religious` |
| GEOGRAPHIC | `roman_republic` | careful — geo may stay pack-scoped; “laws of geography” rare |
| BIOGRAPHIC | usually pack-only | optional `prosopographic_method` for method Claims |

Avoid inventing a second `:Facet` node per discipline unless dispatch truly needs it. The **domain_id on the Claim** (pointing at a SubjectDomain) carries the split.

## Training implication

1. SFA slot under Biographic/Military/… is created inert at Domain schema time.  
2. Before write Claims, SFA is **grounded** on global discipline corpus (theory texts, handbooks).  
3. Historical corpus (Plutarch, DPRR, Meiji gazettes) grounds pack Claims.  
4. Same agent mind; two write targets. Cross-links: historical Claim may `USES` / cite a theory endpoint in `military_theory`.

## What this is not

- Not “Person MEMBER_OF Social SC.”  
- Not dumping Wikipedia physics into Republic SubjectDomain.  
- Not requiring every facet’s global domain to be populated on day one (`military_theory` stayed empty until a claim needed an endpoint).

## Chrystal 2 bootstrap impact

- Ship **Facet × 18** + pack **SubjectDomain** when WD lands.  
- Register **global_theory SubjectDomains** lazily (or stub `military_theory` early as the proven pattern).  
- Schema specialist / Claim shape must include `domain_id` ∈ {pack, global_*}.  
- Librarian places pack SubjectDomain in biblio universe; theory SubjectDomains may use broader LCSH (e.g. “Military art and science”) distinct from “Rome—History—Republic.”

## Open decisions

1. Naming: `military_theory` vs `global_military` for all facets?  
2. Political+Social merge vs each having its own global (`political_theory`, `social_theory`)?  
3. When to create empty global Domain nodes — at facet ship, or on first theory Claim?
