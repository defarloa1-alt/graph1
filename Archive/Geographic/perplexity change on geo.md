perplexity change on geo
Here’s the narrative version of the process—what you did, why each step exists, and what the “two TSVs” are really accomplishing.

---

## The goal

You started with a simple spreadsheet idea:

> “I have a list of named periods with start/end years. I want them to be as universal as possible, linkable in a graph, and map-aware.”

The problem is that “periods” are *not* uniform objects like “a person was born on X.” Many are **regional conventions**. So the process is really about turning a **human list** into a **graph-ready, provenance-aware model** that can survive ambiguity.

---

## Step 1 — Treat your list as “labels + claims,” not truth

Your original table is a set of *claims*:

* “Bronze Age = -3300 to -1200”
* “Iron Age = -1200 to 600”
* etc.

Those claims are already useful for visualization, but if you want *universality*, you need:

1. stable identifiers (QIDs),
2. a way to say “this date range is for **this** region,”
3. a way to connect to geography.

So the first mindset shift is:

> Keep your dates as a working/default view, but anchor everything to Wikidata IDs so you can refine and regionalize later.

---

## Step 2 — Resolve each period name (or Wikipedia URL) to a Wikidata QID

This is the “identity” step.

For every row:

* use the Wikipedia URL (best) or label (fallback)
* find the matching Wikidata item
* store its **QID** (e.g., Bronze Age = Q11761)

Once you have a QID, your graph can treat the row as “about *this thing*,” not “about this string.”

Why this matters:

* it dedupes synonyms (“Hellenistic period” vs “Hellenistic Age”)
* it lets you attach properties from Wikidata later
* it keeps your system stable even if labels change

---

## Step 3 — Preserve your hierarchy, but translate it into graph terms

Your spreadsheet has `parent_period` as text (“Early Bronze Age → Bronze Age”).

In Wikidata terms, the closest clean mapping is typically:

* **part of (P361)** for containment (“X is part of Y”)

So in the enriched table you add:

* `parent_qid` (Bronze Age Q11761)
* and conceptually your graph gets:
  `Early Bronze Age —[part of]→ Bronze Age`

This becomes the backbone for navigation (“show me the subperiods”).

---

## Step 4 — Add a “geo scope” for each period row

This is where the universality issue hits.

For periods like “Classical Greece,” the scope is obvious: Greece.
For “Bronze Age,” the scope depends on the definition you’re using.

So the process chooses a **geo anchor** per row:

* a region/place QID (Greece Q41, Middle East Q7204, etc.)
* plus lat/lon from that region’s **P625** so you can map it.

This doesn’t mean “the period only happened there.”
It means:

> “If we need a default spatial handle for this period entry, this is the region we mean.”

And you explicitly note when it’s a regional convention (Near East Bronze Age phases).

This is what turns your flat list into something that can be:

* filtered by region,
* shown on a map,
* compared across regions.

---

## Step 5 — Split the work into **two tables** because there are two different “truths”

This is the core design move.

### Table A: “Enriched periods table”

One row per your input row.

This table answers:

* “What is this thing?” (QID)
* “How do I link it?” (parent QID)
* “What’s a reasonable default start/end for the way this row is being used?”
* “What geo anchor do I use to place it on a map?”

This table is optimized for:

* your UI stacks
* quick filtering
* sanity checks

### Table B: “Regionalized bounds table”

This is where universality actually lives.

This table answers:

* “What are the start/end bounds **in a specific region**?”

So it’s keyed like:

> **(period QID, region QID) → start/end**

This matches how Wikidata represents it when it’s careful:

* the **start time (P580)** / **end time (P582)** statements are qualified with
  **applies to part (P518)**

Meaning:

> “These dates are true when you’re talking about *this part of the world* (or this subdomain).”

So the second table is what prevents the biggest failure mode:

* treating “Bronze Age” as one global range.

---

## Step 6 — How this becomes graph-native

When you load into Neo4j, you’re basically creating two layers:

### Period concept nodes

One per QID:

* `(:Period {qid:"Q11761", label:"Bronze Age"})`

### Period occurrence (scoped claim) nodes

One per row in your **regional bounds** table:

* `(:PeriodOccurrence {start:-3300, end:-1200})`
* connect it to:

  * the Period concept (`INSTANCE_OF`)
  * the Region (`APPLIES_TO` or `IN_REGION`)

So your graph can represent:

* “Bronze Age” as a concept
* “Bronze Age in Europe: -3200 to -600” as a scoped occurrence
* “Bronze Age in East Asia: -3100 to -300” as another scoped occurrence

That’s the “universalization”: you stop forcing one timeline onto the whole world.

---

## Step 7 — Why this approach scales

Once you adopt the two-table approach:

* You can keep adding new period labels without breaking anything.
* You can add new regional bounds as you discover them.
* You can even keep multiple competing bounds (by source/confidence) later.

Most importantly, your UI gets what it needs:

* a default timeline stack (from the enriched table)
* plus an accurate comparative timeline (from the regional bounds table)

---

## The punchline

The process is basically:

1. **Identify** each row (Wikipedia → QID)
2. **Structure** it (parent → P361 / hierarchy)
3. **Anchor** it spatially (geo scope → region QID + coordinates)
4. **Separate** “one-row display defaults” from “region-specific truth”
5. **Model** region-specific truth the same way Wikidata does (P518-qualified bounds)

That’s why it works: it respects the fact that “periods” are partly social constructs while still turning them into a rigorous, graph-friendly dataset.

If you want, I can turn that narrative into a short “data pipeline spec” you can paste into your repo (inputs → transforms → outputs → how Neo4j uses them).
