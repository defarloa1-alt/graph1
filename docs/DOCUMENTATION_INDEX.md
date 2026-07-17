# Chrystallum Documentation Index

**Last Updated:** 2026-07-16 (root cleanup)  
**Canonical hub:** [README.md](README.md) — prefer that for day-to-day navigation.

---

## Quick start

1. [EPISTEMIC_MODEL.md](EPISTEMIC_MODEL.md) — Core epistemology  
2. [FACET_TRAINING_CONTRACT.md](FACET_TRAINING_CONTRACT.md) — Binding training rules  
3. [ARCHITECTURE_CURRENT.md](ARCHITECTURE_CURRENT.md) — Current system architecture  
4. [AGENTS.md](AGENTS.md) — Agent constraints  
5. [DOMAIN_QUICK_REFERENCE.md](DOMAIN_QUICK_REFERENCE.md) — Domain cheat sheet  

**Repository root keepers only:** `../README.md`, `../REQUIREMENTS.md`, `../DECISIONS.md`

---

## Active documentation (under `docs/`)

### Core
| Document | Purpose |
|----------|---------|
| [EPISTEMIC_MODEL.md](EPISTEMIC_MODEL.md) | Epistemic foundations |
| [ARCHITECTURE_CURRENT.md](ARCHITECTURE_CURRENT.md) | How the system works today |
| [AGENTS.md](AGENTS.md) | Rules for AI agents |
| [FACET_TRAINING_CONTRACT.md](FACET_TRAINING_CONTRACT.md) | Facet SFA training contract |
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Data dictionary |
| [NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md](NEO4J_NODE_AND_RELATIONSHIP_REFERENCE.md) | Node/relationship reference |

### Domain & versioning
| Document | Purpose |
|----------|---------|
| [DOMAIN_MANAGEMENT_GUIDE.md](DOMAIN_MANAGEMENT_GUIDE.md) | Domains |
| [VERSION_MANAGEMENT_GUIDE.md](VERSION_MANAGEMENT_GUIDE.md) | Version workflows |
| [DOMAIN_QUICK_REFERENCE.md](DOMAIN_QUICK_REFERENCE.md) | One-page domain sheet |
| [VERSION_CLI_REFERENCE.md](VERSION_CLI_REFERENCE.md) | CLI commands |
| [SFA_DOMAIN_INTEGRATION.md](SFA_DOMAIN_INTEGRATION.md) | SFAs + domains |

### Agents & claims
| Document | Purpose |
|----------|---------|
| [SCA_SFA_CONTRACT.md](SCA_SFA_CONTRACT.md) | SCA vs SFA |
| [BIOGRAPHIC_CLAIM_PIPELINE.md](BIOGRAPHIC_CLAIM_PIPELINE.md) | Claims track reference |
| [DOMAIN_INITIATOR.md](DOMAIN_INITIATOR.md) | DI pipeline |
| [agents/](agents/) | SCA instructions, harvest schema, MCP |

### Architecture specs
See [architecture/](architecture/) and [README.md](README.md) “Architecture specs” section.

---

## Code-adjacent docs

| Location | Purpose |
|----------|---------|
| `scripts/agents/military/README.md` | Military SFA ops |
| `scripts/agents/military/corpus/` | Source directories (not ingested corpus) |
| `scripts/agents/diplomatic/README.md` | Diplomatic SFA |
| `Geographic/README.md` | Place / geo backbone |
| `Key Files/Appendices/05_Architecture_Decisions/` | ADRs (incl. ADR-021/022/023) |

---

## Archived (do not train from)

`../Archive/docs-2026-07/` — see [Archive README](../Archive/docs-2026-07/README.md).

Includes: session handoffs, phase completion reports, superseded SFA training drafts, military implementation narratives, multi-agent / IGAR discovery notes, transcripts, security audit (credential strings).

---

## Decision log

Append-only decisions stay at repo root: [`../DECISIONS.md`](../DECISIONS.md)
