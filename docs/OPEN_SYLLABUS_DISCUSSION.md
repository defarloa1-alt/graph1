# Open Syllabus and Discipline Taxonomy

## What is Open Syllabus?

The [Open Syllabus Project](https://www.opensyllabus.org/) is a non-profit archive of college course syllabi. As of 2024–2025:

- **~7.5M syllabi** (22.6B words)
- **8,648 institutions** across 152 countries
- **~70 academic fields** derived from CIP (Classification of Instructional Programs) codes
- **57M assigned readings** across 5.2M unique titles

Courses are classified into disciplines using CIP codes from the U.S. Department of Education. The taxonomy is **empirically grounded** in what colleges actually teach.

## Our Approach vs Open Syllabus

| Aspect | Our discipline registry | Open Syllabus |
|--------|------------------------|---------------|
| Source | Wikidata + LCSH + academic majors | CIP codes + syllabus corpus |
| Breadth | ~1,300 masters (curated) | ~70 fields |
| Granularity | Fine (e.g. "Arabic literature", "Buddhist studies") | Coarse (CIP top-level) |
| Authority | Library/authority IDs (LCSH, DDC, AAT, etc.) | U.S. federal classification |
| Use case | Subject backbone, entity linking | Curriculum analysis, reading lists |

## How Open Syllabus Could Complement Our Registry

1. **Validation** – Check which of our disciplines appear in real curricula. High Open Syllabus count → likely a real, taught field.
2. **Prioritization** – Enrich or curate first those disciplines that show up frequently in syllabi.
3. **Crosswalk** – Map CIP codes to our `master_id` (lcsh_id, ddc, etc.) for interoperability.
4. **Reading lists** – Use Open Syllabus assigned readings to suggest canonical texts per discipline.

## CIP Code Example

CIP codes are hierarchical. Example:

- `09.0101` – Communication, General
- `09.0102` – Mass Communication/Media Studies
- `23.0101` – Chinese Language and Literature

Our LCSH `sh85024301` (Chinese) and `sh85043777` (English-language literature) would map to different CIP codes. Building a CIP ↔ LCSH/DDC crosswalk would allow querying Open Syllabus by our discipline keys.

## What Open Syllabus Actually Exposes

You can't get front matter *from* Open Syllabus itself, but you can use its IDs (ISBN/DOI/OS work IDs) as a bridge to copies of the book where LoC data lives. [Dataset docs](https://opensyllabus.github.io/osp-dataset-docs/index.html)

- Open Syllabus stores full-text syllabi, but the public/data interfaces expose only *metadata and title records*, not the underlying PDFs or book front matter. [About OS](https://blog.opensyllabus.org/about-os)
- For assigned texts, their pipeline links syllabus citations to a background database of ~150M books/articles, keyed by ISBN, DOI, publisher data, etc. [OSP API](https://johnskinnerportfolio.com/blog/ospapi/)

So the realistic path is: **Open Syllabus → ISBN/DOI/OS title ID → external bibliographic services that expose MARC/LoC fields.**

## Pipeline to LoC / LCSH / LCC via ISBN

For each Open Syllabus title:

1. **Query the Open Syllabus API** for co-assignments or title data by ISBN/DOI.
   - The documented API supports endpoints like `/coassignments/isbn/{ISBN}` or `/coassignments/doi/{DOI}` that return JSON with a canonical title record including identifiers. [Dataset docs](https://opensyllabus.github.io/osp-dataset-docs/index.html)

2. From that JSON, extract an **ISBN (or DOI)** for the work, then:
   - Hit **Library of Congress** APIs (e.g., `https://lccn.loc.gov/` and Z39.50/JSON services) or
   - Hit **WorldCat/OCLC** APIs (if you have access) using the ISBN. [USC metadata](https://www2.archivists.org/sites/all/files/USC_at_metadata.pdf)

3. In the returned bibliographic record, read:
   - LCCN and **LCC class** (call number).
   - **LCSH** subject headings (e.g., MARC 650 fields).
   - Any explicit LoC identifiers in `<identifier type="lccn">` etc. for MADS/RDF. [LoC identifiers](https://www.loc.gov/standards/mads/userguide/identifier.html)

This effectively uses the ISBN as a *foreign key* from Open Syllabus into LoC.

## Strategy for Our System

- In the "canonical readings" pipeline:
  - Start from Galaxy/Open Syllabus ranked titles for a discipline.
  - For each, fetch via API → get ISBN → call LoC/WorldCat → ingest LCC/LCSH/LCCN into the Work node.
- Store on the Work node:
  - `isbn`, `doi`, `osp_id` (Open Syllabus internal ID), `lccn`, `lcc_class`, `lcsh_ids`.
- Optionally, reconcile the LoC record with Wikidata (via ISBN/LoC IDs) to get a richer authority cluster.

**Summary:** Open Syllabus won't give you front matter or LoC IDs directly, but it reliably yields identifiers (especially ISBNs/DOIs) that let you hop to LoC records where those IDs and classifications already live. [About OS](https://blog.opensyllabus.org/about-os)

## TODO

- [ ] Build CIP ↔ master_id (lcsh_id, ddc, lcc) crosswalk using `Subjects/CIP/cip_code,cip_title,lcc_classes,lcsh_term.csv`
- [ ] Implement Open Syllabus → ISBN → LoC/WorldCat pipeline for canonical readings per discipline
- [ ] Add `osp_id`, `isbn`, `doi`, `lccn`, `lcc_class`, `lcsh_ids` to Work node schema where applicable

## Data Access

- [Open Syllabus Dataset Docs](https://opensyllabus.github.io/osp-dataset-docs/)
- [Schema](https://docs.opensyllabus.org/schema.html)
- Data: gzip JSON-lines, partitioned (~1% per file)
