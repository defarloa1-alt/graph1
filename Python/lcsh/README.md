# LCSH Folder Layout

This folder groups Python LCSH workflows into clear buckets.

- `scripts/`: LCSH retrieval, parsing, import, and diagnostics scripts.
- `key/`: Optional local source artifacts for parsing (for example `subjects.skosrdf.nt.gz`).
- `output/`: Generated LCSH working artifacts.
  - `lcsh_ids.txt`
  - `lcsh_subjects_complete.csv`
  - `lcsh_class_d_complete.csv`

Archived stale scripts moved to `Archive/Python/LCSH`:
- `retrieve_lcsh_class_d.py`
- `test_lcsh_url.py`
