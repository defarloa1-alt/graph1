"""The curator's review desk: a local Gradio page for accepting and rejecting claims (interim, 2026-11-13).

The reader-facing stack is Neo4j -> Cytoscape -> React, designed in Figma. This
page is only the curator's tool: it calls proposals/store directly, so every
decision goes through the same checks as the review CLI.
"""
