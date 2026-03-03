import { useState, useCallback } from "react";

const NODE_TYPE_STYLES = {
  Discipline:      { fill: "#F5E6D3", stroke: "#8B6914", text: "#4A3500" },
  ScaffoldNode:    { fill: "#2A2A3A", stroke: "#7B68EE", text: "#C8C0F0" },
  SubjectConcept:  { fill: "#1E3A2A", stroke: "#4CAF50", text: "#A8D8B4" },
  Claim:           { fill: "#3A1E1E", stroke: "#E57373", text: "#F0C0C0" },
  Enriched:        { fill: "#2A3040", stroke: "#64B5F6", text: "#B0D0F0" },
  Converged:       { fill: "#1A2E1A", stroke: "#81C784", text: "#C0E8C0" },
  Triple:          { fill: "#0D2137", stroke: "#42A5F5", text: "#90CAF9" },
};

const EDGE_STYLES = {
  BROADER_THAN:    { color: "#8B6914", dash: null,    label: "BROADER_THAN" },
  SUBCLASS_OF:     { color: "#7B68EE", dash: "6 3",   label: "SUBCLASS_OF" },
  NARROWER_THAN:   { color: "#4CAF50", dash: null,    label: "NARROWER_THAN" },
  FROM:            { color: "#9E9E9E", dash: "3 3",   label: "FROM" },
  TO:              { color: "#9E9E9E", dash: "3 3",   label: "TO" },
  PROPOSED_BY:     { color: "#E57373", dash: "4 2",   label: "PROPOSED_BY" },
  ABOUT_SUBJECT:   { color: "#CE93D8", dash: "4 2",   label: "ABOUT_SUBJECT" },
  EVIDENCED_BY:    { color: "#FFB74D", dash: "4 2",   label: "EVIDENCED_BY" },
  HAS_PART:        { color: "#4DB6AC", dash: null,     label: "HAS_PART" },
};

const STEPS = [
  {
    id: 0,
    title: "The Existing Graph",
    subtitle: "What already exists before any harvesting begins",
    description: "The Political SFA agent queries the graph and finds political science already exists as a Discipline node with rich authority anchors (lcsh_id, fast_id, ddc, aat_id). It also discovers BROADER_THAN edges to 4 child Discipline nodes that were harvested in an earlier pass. These are canonical — they're already in the domain graph, not scaffolding.",
    nodes: [
      { id: "ps", label: "political science", type: "Discipline", x: 400, y: 180,
        props: ["qid: Q36442", "lcsh_id: sh85104440", "fast_id: fst01069781", "ddc: 320", "aat_id: 300054438"] },
      { id: "pa", label: "public administration", type: "Discipline", x: 180, y: 340,
        props: ["qid: Q31728"] },
      { id: "psoc", label: "political sociology", type: "Discipline", x: 340, y: 380,
        props: ["qid: Q745692", "lcsh_id: sh85104468"] },
      { id: "ppsy", label: "political psychology", type: "Discipline", x: 460, y: 380,
        props: ["qid: Q1596387", "lcsh_id: sh85104450"] },
      { id: "panth", label: "political anthropology", type: "Discipline", x: 620, y: 340,
        props: ["qid: Q27778", "lcsh_id: sh85104335"] },
    ],
    edges: [
      { from: "ps", to: "pa", rel: "BROADER_THAN", props: [] },
      { from: "ps", to: "psoc", rel: "BROADER_THAN", props: [] },
      { from: "ps", to: "ppsy", rel: "BROADER_THAN", props: [] },
      { from: "ps", to: "panth", rel: "BROADER_THAN", props: [] },
    ],
    activeSource: null,
    query: "MATCH (d:Discipline {qid:'Q36442'})-[r:BROADER_THAN]->(child:Discipline) RETURN d, r, child",
    sidebar: {
      title: "Node type: Discipline",
      entityType: "Discipline",
      desc: "Already canonical in the graph. Has authority properties (lcsh_id, fast_id, ddc, aat_id, gnd_id) for multi-source anchoring. Linked via BROADER_THAN (≈Wikidata P279 inverse).",
      properties: ["qid (Wikidata ID)", "label (human-readable)", "lcsh_id, fast_id, ddc, aat_id, gnd_id", "federation_labels (source list)"],
    }
  },
  {
    id: 1,
    title: "Wikidata Backlink Harvest → ScaffoldNodes",
    subtitle: "New discoveries land as scaffolding, not canonical nodes",
    description: "The agent queries Wikidata backlinks for Q36442 (P279 subclass_of). Items that DON'T already exist in the graph arrive as ScaffoldNode instances per ADR-006. Each gets a wd_property linking it to its Wikidata origin. The edges between them are reified as ScaffoldEdge nodes using FROM/TO pattern — because edges can't carry full provenance, but nodes can.",
    nodes: [
      { id: "ps", label: "political science", type: "Discipline", x: 400, y: 120,
        props: ["qid: Q36442", "lcsh_id: sh85104440"] },
      { id: "pt", label: "political theory", type: "ScaffoldNode", x: 120, y: 260,
        props: ["qid: Q9357091", "source: wikidata", "wd_property: P279", "harvest_ts: 2026-03-02T..."] },
      { id: "cp", label: "comparative politics", type: "ScaffoldNode", x: 300, y: 280,
        props: ["qid: Q189657", "source: wikidata", "wd_property: P279"] },
      { id: "ir", label: "international relations", type: "ScaffoldNode", x: 500, y: 280,
        props: ["qid: Q166542", "source: wikidata", "wd_property: P279"] },
      { id: "pm", label: "political methodology", type: "ScaffoldNode", x: 680, y: 260,
        props: ["qid: Q7210356", "source: wikidata", "wd_property: P279"] },
      { id: "se1", label: "ScaffoldEdge", type: "ScaffoldNode", x: 220, y: 170, small: true,
        props: ["wd_property: P279", "direction: inbound"] },
      { id: "se2", label: "ScaffoldEdge", type: "ScaffoldNode", x: 360, y: 185, small: true,
        props: ["wd_property: P279", "direction: inbound"] },
      { id: "se3", label: "ScaffoldEdge", type: "ScaffoldNode", x: 470, y: 185, small: true,
        props: ["wd_property: P279", "direction: inbound"] },
      { id: "se4", label: "ScaffoldEdge", type: "ScaffoldNode", x: 580, y: 170, small: true,
        props: ["wd_property: P279", "direction: inbound"] },
    ],
    edges: [
      { from: "se1", to: "ps", rel: "TO", props: [] },
      { from: "se1", to: "pt", rel: "FROM", props: [] },
      { from: "se2", to: "ps", rel: "TO", props: [] },
      { from: "se2", to: "cp", rel: "FROM", props: [] },
      { from: "se3", to: "ps", rel: "TO", props: [] },
      { from: "se3", to: "ir", rel: "FROM", props: [] },
      { from: "se4", to: "ps", rel: "TO", props: [] },
      { from: "se4", to: "pm", rel: "FROM", props: [] },
    ],
    activeSource: "Wikidata",
    query: "SPARQL → Wikidata: SELECT ?item WHERE { ?item wdt:P279 wd:Q36442 }",
    sidebar: {
      title: "Node type: ScaffoldNode + ScaffoldEdge",
      entityType: "ScaffoldNode",
      desc: "ADR-006 mandates that agent discoveries land in scaffolding, NOT the canonical graph. ScaffoldEdge reifies the relationship as a node so it can carry provenance. The FROM/TO pattern: (ScaffoldEdge)-[:FROM]->(subject), (ScaffoldEdge)-[:TO]->(object).",
      properties: ["qid (Wikidata ID)", "source (federation origin)", "wd_property (Wikidata property)", "harvest_ts (timestamp)", "direction (inbound/outbound)"],
    }
  },
  {
    id: 2,
    title: "Recursive Harvest: Political Theory Backlinks",
    subtitle: "Level 2 — theories arrive as deeper ScaffoldNodes",
    description: "The agent recurses into Q9357091 (political theory). Its backlinks yield the actual theories: democratic peace theory, elite theory, Duverger's law, capability approach. These are CONCEPTUAL entities — they'll likely become SubjectConcept nodes after promotion, not Discipline nodes. The entity type distinction matters: Discipline = a field of study, SubjectConcept = an authority-aligned concept within a field.",
    nodes: [
      { id: "ps", label: "political science", type: "Discipline", x: 400, y: 60,
        props: ["qid: Q36442"] },
      { id: "pt", label: "political theory", type: "ScaffoldNode", x: 180, y: 180,
        props: ["qid: Q9357091"], active: true },
      { id: "cp", label: "comparative politics", type: "ScaffoldNode", x: 400, y: 160,
        props: ["qid: Q189657"], dimmed: true },
      { id: "ir", label: "intl relations", type: "ScaffoldNode", x: 620, y: 180,
        props: ["qid: Q166542"], dimmed: true },
      { id: "dpt", label: "democratic peace theory", type: "ScaffoldNode", x: 60, y: 320,
        props: ["qid: Q1186378", "source: wikidata", "wd_property: P279", "depth: 2"] },
      { id: "et", label: "elite theory", type: "ScaffoldNode", x: 200, y: 360,
        props: ["qid: Q1728701", "source: wikidata", "wd_property: P279", "depth: 2"] },
      { id: "dl", label: "Duverger's law", type: "ScaffoldNode", x: 340, y: 340,
        props: ["qid: Q637376", "source: wikidata", "wd_property: P31", "depth: 2"] },
      { id: "ca", label: "capability approach", type: "ScaffoldNode", x: 130, y: 440,
        props: ["qid: Q430460", "source: wikidata", "wd_property: P279", "depth: 2"] },
      { id: "ni", label: "new institutionalism", type: "ScaffoldNode", x: 310, y: 440,
        props: ["qid: Q730099", "source: wikidata", "wd_property: P279", "depth: 2"] },
    ],
    edges: [
      { from: "pt", to: "ps", rel: "SUBCLASS_OF", props: ["via ScaffoldEdge"] },
      { from: "dpt", to: "pt", rel: "SUBCLASS_OF", props: ["wd_property: P279"] },
      { from: "et", to: "pt", rel: "SUBCLASS_OF", props: ["wd_property: P279"] },
      { from: "dl", to: "pt", rel: "SUBCLASS_OF", props: ["wd_property: P31"] },
      { from: "ca", to: "pt", rel: "SUBCLASS_OF", props: ["wd_property: P279"] },
      { from: "ni", to: "pt", rel: "SUBCLASS_OF", props: ["wd_property: P279"] },
    ],
    activeSource: "Wikidata",
    query: "SPARQL → Wikidata: SELECT ?item WHERE { ?item wdt:P279|wdt:P31 wd:Q9357091 }",
    sidebar: {
      title: "Entity type question: Discipline vs SubjectConcept",
      entityType: "ScaffoldNode → ?",
      desc: "D6 (entity class validity) determines promotion target. \"Democratic peace theory\" is a concept, not a field of study. Probable target: SubjectConcept. \"Comparative politics\" IS a field → target: Discipline. The SFA agent must evaluate each ScaffoldNode's destination type before proposing Claims.",
      properties: ["depth (recursion level from root)", "wd_property (P279=subclass, P31=instance)", "Promotion target decided at D6 gate"],
    }
  },
  {
    id: 3,
    title: "LCSH Authority Cross-Reference",
    subtitle: "D4: Route to canonical authorities — enrich, don't create",
    description: "Per D4 (LocalFirstCanonicalAuthorities), the agent now queries id.loc.gov for each ScaffoldNode's QID. Nodes with LCSH matches gain authority properties — lcsh_id, fast_id. This is a PROPERTY ENRICHMENT operation, not node creation. The ScaffoldNode is the same node, just carrying more evidence. Enriched nodes have higher confidence at D10 promotion time.",
    nodes: [
      { id: "ps", label: "political science", type: "Discipline", x: 400, y: 80,
        props: ["qid: Q36442", "lcsh_id: sh85104440"] },
      { id: "pt", label: "political theory", type: "Enriched", x: 180, y: 200,
        props: ["qid: Q9357091", "source: wikidata", "+ gnd_id: 4076229-4", "federation_labels: [wikidata, gnd]"] },
      { id: "cp", label: "comparative politics", type: "Enriched", x: 400, y: 200,
        props: ["qid: Q189657", "+ lcsh_id: sh85029055", "+ fast_id: fst00871468", "federation_labels: [wikidata, lcsh, fast]"] },
      { id: "dpt", label: "democratic peace theory", type: "Enriched", x: 80, y: 350,
        props: ["qid: Q1186378", "+ lcsh_id: sh2008003526", "federation_labels: [wikidata, lcsh]"] },
      { id: "et", label: "elite theory", type: "Enriched", x: 280, y: 380,
        props: ["qid: Q1728701", "+ lcsh_id: sh85042538", "federation_labels: [wikidata, lcsh]"] },
      { id: "dl", label: "Duverger's law", type: "ScaffoldNode", x: 480, y: 350,
        props: ["qid: Q637376", "federation_labels: [wikidata]", "NO LCSH MATCH"] },
      { id: "ca", label: "capability approach", type: "ScaffoldNode", x: 660, y: 350,
        props: ["qid: Q430460", "federation_labels: [wikidata]", "NO LCSH MATCH"] },
    ],
    edges: [
      { from: "pt", to: "ps", rel: "SUBCLASS_OF", props: [] },
      { from: "cp", to: "ps", rel: "SUBCLASS_OF", props: [] },
      { from: "dpt", to: "pt", rel: "SUBCLASS_OF", props: [] },
      { from: "et", to: "pt", rel: "SUBCLASS_OF", props: [] },
      { from: "dl", to: "pt", rel: "SUBCLASS_OF", props: [] },
      { from: "ca", to: "pt", rel: "SUBCLASS_OF", props: [] },
    ],
    activeSource: "LCSH/FAST",
    query: "id.loc.gov: /authorities/subjects/label/{label} → match lcsh_id, fast_id",
    sidebar: {
      title: "Operation: Property enrichment",
      entityType: "ScaffoldNode (enriched)",
      desc: "No new nodes. The ScaffoldNode gains authority-tier properties. federation_labels array tracks which sources have validated this node. At D10, confidence = f(federation_labels.length, authority_tier). A node with [wikidata, lcsh, fast] scores higher than [wikidata] alone.",
      properties: ["lcsh_id (Library of Congress)", "fast_id (OCLC FAST)", "gnd_id (German National Library)", "federation_labels (array of confirming sources)"],
    }
  },
  {
    id: 4,
    title: "LCSH Narrower Terms → New ScaffoldNodes",
    subtitle: "LCSH gives a DIFFERENT decomposition than Wikidata",
    description: "Now the agent traverses LCSH's own hierarchy — narrower terms under sh85104440. LCSH adds concepts Wikidata missed: political obligation, political participation, political culture. These arrive as NEW ScaffoldNodes with lcsh_id but NO qid initially. The agent must then attempt entity resolution (D14) to check if they match existing Wikidata items.",
    nodes: [
      { id: "ps", label: "political science", type: "Discipline", x: 400, y: 80,
        props: ["qid: Q36442"] },
      { id: "et", label: "elite theory", type: "Enriched", x: 160, y: 220,
        props: ["wikidata ✓  lcsh ✓"] },
      { id: "cp", label: "comparative politics", type: "Enriched", x: 400, y: 200,
        props: ["wikidata ✓  lcsh ✓  fast ✓"] },
      { id: "pol_oblig", label: "political obligation", type: "ScaffoldNode", x: 640, y: 220,
        props: ["lcsh_id: sh85104398", "NO qid yet", "source: lcsh", "needs D14 entity resolution"] },
      { id: "pol_part", label: "political participation", type: "ScaffoldNode", x: 140, y: 380,
        props: ["lcsh_id: sh85104352", "source: lcsh"] },
      { id: "pol_cult", label: "political culture", type: "ScaffoldNode", x: 340, y: 400,
        props: ["lcsh_id: sh85104388", "source: lcsh"] },
      { id: "leg", label: "legitimacy of governments", type: "ScaffoldNode", x: 540, y: 380,
        props: ["lcsh_id: sh85075846", "source: lcsh"] },
    ],
    edges: [
      { from: "ps", to: "et", rel: "BROADER_THAN", props: ["converged: WD+LCSH"] },
      { from: "ps", to: "cp", rel: "BROADER_THAN", props: ["converged: WD+LCSH+FAST"] },
      { from: "ps", to: "pol_oblig", rel: "NARROWER_THAN", props: ["source: lcsh NT"] },
      { from: "ps", to: "pol_part", rel: "NARROWER_THAN", props: ["source: lcsh NT"] },
      { from: "ps", to: "pol_cult", rel: "NARROWER_THAN", props: ["source: lcsh NT"] },
      { from: "ps", to: "leg", rel: "NARROWER_THAN", props: ["source: lcsh NT"] },
    ],
    activeSource: "LCSH/FAST",
    query: "id.loc.gov: /authorities/subjects/sh85104440 → madsrdf:hasNarrowerAuthority",
    sidebar: {
      title: "Edge type: NARROWER_THAN vs BROADER_THAN",
      entityType: "ScaffoldNode (LCSH-origin)",
      desc: "Existing BROADER_THAN edges map Wikidata P279. New LCSH narrower terms use NARROWER_THAN (the inverse). Both already exist in the graph (9,880 BROADER_THAN, already in use). LCSH-origin ScaffoldNodes lack qid — they need D14 (entity resolution, ≥0.75 confidence + ≥0.8 fuzzy match) before they can be reconciled with Wikidata items.",
      properties: ["lcsh_id (primary identifier)", "source: lcsh", "needs_resolution: true", "Edge: NARROWER_THAN {source: lcsh}"],
    }
  },
  {
    id: 5,
    title: "Claims: Proposing Promotions",
    subtitle: "ScaffoldNodes become Claims for human review",
    description: "The agent now generates Claim nodes for each ScaffoldNode it wants to promote. Each Claim has a cipher (content-addressable hash per ADR-001), confidence score, authority_source, and claim_type. The Claim links to its subject via ABOUT_SUBJECT and to its evidence via HAS_TRACE → RetrievalContext. Nothing enters the canonical graph without passing D10's four gates.",
    nodes: [
      { id: "ps", label: "political science", type: "Discipline", x: 400, y: 60,
        props: ["qid: Q36442"] },
      { id: "cp_scaffold", label: "comparative politics", type: "ScaffoldNode", x: 180, y: 200,
        props: ["qid: Q189657", "federation_labels: [wd, lcsh, fast]"] },
      { id: "dpt_scaffold", label: "democratic peace theory", type: "ScaffoldNode", x: 620, y: 200,
        props: ["qid: Q1186378", "federation_labels: [wd, lcsh]"] },
      { id: "clm1", label: "Claim: promote cp → Discipline", type: "Claim", x: 180, y: 380,
        props: ["cipher: SHA256(subject=Q189657|...", "confidence: 0.92", "status: proposed", "claim_type: entity_promotion", "authority_source: wikidata+lcsh+fast"] },
      { id: "clm2", label: "Claim: promote dpt → SubjectConcept", type: "Claim", x: 620, y: 380,
        props: ["cipher: SHA256(subject=Q1186378|...", "confidence: 0.88", "status: proposed", "claim_type: entity_promotion", "authority_source: wikidata+lcsh"] },
      { id: "agent", label: "Political SFA Agent", type: "ScaffoldNode", x: 400, y: 480,
        props: ["agent_type: Subject-Facet Assignment", "facet: POLITICAL"], small: true },
    ],
    edges: [
      { from: "clm1", to: "cp_scaffold", rel: "ABOUT_SUBJECT", props: ["target_type: Discipline"] },
      { from: "clm2", to: "dpt_scaffold", rel: "ABOUT_SUBJECT", props: ["target_type: SubjectConcept"] },
      { from: "clm1", to: "agent", rel: "PROPOSED_BY", props: [] },
      { from: "clm2", to: "agent", rel: "PROPOSED_BY", props: [] },
      { from: "cp_scaffold", to: "ps", rel: "SUBCLASS_OF", props: [] },
      { from: "dpt_scaffold", to: "ps", rel: "SUBCLASS_OF", props: [] },
    ],
    activeSource: "D10 Claim Promotion Pipeline",
    query: "D10 gates: confidence ≥ 0.9 AND posterior ≥ 0.9 AND provenance EXISTS AND human_approval = true",
    sidebar: {
      title: "Node type: Claim",
      entityType: "Claim",
      desc: "The Claim is the atomic unit of knowledge assertion. cipher = SHA256(subject|object|rel|facet) per ADR-001, making it content-addressable and deduplicable across institutions. claim_type: entity_promotion means 'promote this ScaffoldNode to a canonical entity.' D10's four AND gates must all pass.",
      properties: ["claim_id", "cipher (content-addressable hash)", "confidence (0.0–1.0)", "status (proposed→reviewed→promoted|rejected)", "claim_type (entity_promotion|facet_assignment|...)", "authority_source", "source_agent"],
    }
  },
  {
    id: 6,
    title: "Post-Promotion: Canonical Subgraph",
    subtitle: "After D10 approval — scaffold becomes knowledge",
    description: "Human reviewer approves the claims. ScaffoldNodes are promoted via PROMOTED_FROM edges into canonical entities — some as Discipline nodes, others as SubjectConcept nodes. The promoted nodes inherit all authority properties accumulated during enrichment. BROADER_THAN and NARROWER_THAN edges replace the scaffold FROM/TO pattern. The abstract concept 'political science' now has a living, validated, multi-source subgraph.",
    nodes: [
      { id: "ps", label: "political science", type: "Discipline", x: 400, y: 60,
        props: ["qid: Q36442", "lcsh_id, fast_id, ddc, aat_id"] },
      { id: "cp", label: "comparative politics", type: "Discipline", x: 160, y: 180,
        props: ["qid: Q189657", "PROMOTED", "federation_labels: [wd, lcsh, fast]"] },
      { id: "pt", label: "political theory", type: "Discipline", x: 400, y: 180,
        props: ["qid: Q9357091", "PROMOTED", "federation_labels: [wd, gnd]"] },
      { id: "ir", label: "international relations", type: "Discipline", x: 640, y: 180,
        props: ["qid: Q166542", "PROMOTED", "federation_labels: [wd, lcsh]"] },
      { id: "dpt", label: "democratic peace theory", type: "SubjectConcept", x: 100, y: 330,
        props: ["qid: Q1186378", "PROMOTED → SubjectConcept", "federation_labels: [wd, lcsh]"] },
      { id: "et", label: "elite theory", type: "SubjectConcept", x: 300, y: 360,
        props: ["qid: Q1728701", "PROMOTED → SubjectConcept"] },
      { id: "ni", label: "new institutionalism", type: "SubjectConcept", x: 500, y: 360,
        props: ["qid: Q730099", "PROMOTED → SubjectConcept"] },
      { id: "dl", label: "Duverger's law", type: "SubjectConcept", x: 700, y: 330,
        props: ["qid: Q637376", "PROMOTED → SubjectConcept"] },
      { id: "pol_part", label: "political participation", type: "SubjectConcept", x: 200, y: 470,
        props: ["lcsh_id: sh85104352", "PROMOTED → SubjectConcept", "qid: resolved via D14"] },
      { id: "leg", label: "legitimacy", type: "SubjectConcept", x: 500, y: 470,
        props: ["lcsh_id: sh85075846", "PROMOTED → SubjectConcept"] },
    ],
    edges: [
      { from: "ps", to: "cp", rel: "BROADER_THAN", props: ["canonical"] },
      { from: "ps", to: "pt", rel: "BROADER_THAN", props: ["canonical"] },
      { from: "ps", to: "ir", rel: "BROADER_THAN", props: ["canonical"] },
      { from: "dpt", to: "pt", rel: "NARROWER_THAN", props: ["canonical"] },
      { from: "et", to: "pt", rel: "NARROWER_THAN", props: ["canonical"] },
      { from: "ni", to: "cp", rel: "NARROWER_THAN", props: ["canonical"] },
      { from: "dl", to: "cp", rel: "NARROWER_THAN", props: ["canonical"] },
      { from: "pol_part", to: "ps", rel: "NARROWER_THAN", props: ["canonical"] },
      { from: "leg", to: "ps", rel: "NARROWER_THAN", props: ["canonical"] },
    ],
    activeSource: "Canonical Graph",
    query: "Post-D10: ScaffoldNode -[:PROMOTED_FROM]-> Discipline|SubjectConcept",
    sidebar: {
      title: "Two canonical types emerge",
      entityType: "Discipline + SubjectConcept",
      desc: "Fields of study → Discipline (comparative politics, political theory, IR). Concepts within fields → SubjectConcept (democratic peace theory, elite theory, Duverger's law). The distinction matters: Discipline nodes appear in DisciplineRegistry and structure the D9 constitution layer. SubjectConcepts carry multi-tier confidence scores and wire to the facet system via ABOUT_SUBJECT on Claims.",
      properties: [
        "Discipline: qid, label, lcsh_id, fast_id, ddc, aat_id, gnd_id, federation_labels",
        "SubjectConcept: qid, label, entity_count, facets, federation_labels",
        "Edge: BROADER_THAN / NARROWER_THAN (canonical, replaces scaffold FROM/TO)"
      ],
    }
  },
];

function NodeBox({ node, isNew }) {
  const style = NODE_TYPE_STYLES[node.type] || NODE_TYPE_STYLES.ScaffoldNode;
  const dimmed = node.dimmed;
  const active = node.active;
  const w = node.small ? 90 : Math.max(node.label.length * 7.2 + 28, 100);
  const h = node.small ? 22 : 30;

  return (
    <g style={{ opacity: dimmed ? 0.25 : 1, transition: "all 0.5s ease" }}>
      {active && (
        <rect x={node.x - w/2 - 4} y={node.y - h/2 - 4} width={w+8} height={h+8} rx={8}
          fill="none" stroke={style.stroke} strokeWidth={2} strokeDasharray="4 3" opacity={0.6} />
      )}
      <rect x={node.x - w/2} y={node.y - h/2} width={w} height={h} rx={5}
        fill={style.fill} stroke={style.stroke} strokeWidth={1.5}
        style={{ filter: isNew ? "drop-shadow(0 0 4px " + style.stroke + ")" : undefined }} />
      <text x={node.x} y={node.y + 1} textAnchor="middle" dominantBaseline="middle"
        fill={style.text} style={{ fontSize: node.small ? "8px" : "9.5px", fontFamily: "'JetBrains Mono', 'Fira Code', monospace", fontWeight: 500 }}>
        {node.label}
      </text>
      {!node.small && (
        <text x={node.x} y={node.y + h/2 + 10} textAnchor="middle" dominantBaseline="middle"
          fill={style.stroke} opacity={0.7}
          style={{ fontSize: "7.5px", fontFamily: "'JetBrains Mono', monospace", fontStyle: "italic" }}>
          :{node.type}
        </text>
      )}
    </g>
  );
}

function EdgeLine({ from, to, rel, props, isNew }) {
  const es = EDGE_STYLES[rel] || { color: "#666", dash: null, label: rel };
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const len = Math.sqrt(dx*dx + dy*dy);
  if (len === 0) return null;
  const nx = dx/len, ny = dy/len;
  const fw = (from.small ? 45 : Math.max(from.label.length * 7.2 + 28, 100)) / 2;
  const tw = (to.small ? 45 : Math.max(to.label.length * 7.2 + 28, 100)) / 2;
  const fh = from.small ? 11 : 15;
  const th = to.small ? 11 : 15;
  const sx = from.x + nx * fw * 0.9;
  const sy = from.y + ny * fh;
  const ex = to.x - nx * tw * 0.9;
  const ey = to.y - ny * th;
  const mx = (sx+ex)/2, my = (sy+ey)/2 - 10;

  return (
    <g>
      <path d={`M ${sx} ${sy} Q ${mx} ${my} ${ex} ${ey}`} fill="none"
        stroke={es.color} strokeWidth={1.2}
        strokeDasharray={es.dash || undefined} opacity={0.5}
        markerEnd={`url(#arrow-${rel})`} />
      <text x={mx} y={my - 5} textAnchor="middle" fill={es.color} opacity={0.7}
        style={{ fontSize: "7px", fontFamily: "monospace" }}>
        {es.label}
      </text>
    </g>
  );
}

function Sidebar({ data }) {
  if (!data) return null;
  const style = NODE_TYPE_STYLES[data.entityType] || NODE_TYPE_STYLES.ScaffoldNode;
  return (
    <div style={{
      background: "rgba(20,20,22,0.95)", border: "1px solid rgba(120,115,105,0.2)",
      borderRadius: "8px", padding: "14px 16px", fontSize: "11px",
      lineHeight: 1.55, color: "#C8C3B8", maxHeight: "100%", overflowY: "auto",
    }}>
      <div style={{ fontSize: "10px", color: style.stroke || "#7B68EE", fontFamily: "monospace",
        textTransform: "uppercase", letterSpacing: "1px", marginBottom: "6px" }}>
        {data.entityType}
      </div>
      <div style={{ fontSize: "13px", color: "#F0ECE0", fontWeight: 600, marginBottom: "8px",
        fontFamily: "'Georgia', serif" }}>
        {data.title}
      </div>
      <p style={{ margin: "0 0 10px", color: "#A09A8C" }}>{data.desc}</p>
      <div style={{ borderTop: "1px solid rgba(120,115,105,0.15)", paddingTop: "8px" }}>
        <div style={{ fontSize: "9px", color: "#6B6560", textTransform: "uppercase",
          letterSpacing: "1px", marginBottom: "4px" }}>Properties</div>
        {data.properties.map((p, i) => (
          <div key={i} style={{ fontFamily: "monospace", fontSize: "10px", color: "#8B8680",
            padding: "2px 0", borderLeft: `2px solid ${style.stroke || '#7B68EE'}22`,
            paddingLeft: "8px", marginBottom: "3px" }}>
            {p}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function DisciplineOntologyViz() {
  const [currentStep, setCurrentStep] = useState(0);
  const [prevStep, setPrevStep] = useState(-1);
  const step = STEPS[currentStep];
  const prev = prevStep >= 0 ? STEPS[prevStep] : { nodes: [], edges: [] };
  const prevIds = new Set(prev.nodes.map(n => n.id));
  const prevEdgeKeys = new Set(prev.edges.map(e => `${e.from}-${e.to}`));

  const goTo = useCallback((s) => { setPrevStep(currentStep); setCurrentStep(s); }, [currentStep]);

  const srcColors = {
    "Wikidata": "#7B68EE", "LCSH/FAST": "#FFB74D", "D10 Claim Promotion Pipeline": "#E57373",
    "Canonical Graph": "#4CAF50"
  };

  return (
    <div style={{
      width: "100%", minHeight: "100vh",
      background: "linear-gradient(160deg, #0F0F12 0%, #16161C 40%, #0F0F12 100%)",
      color: "#E8E3D8", fontFamily: "'Georgia', serif",
      display: "flex", flexDirection: "column",
    }}>
      {/* Header */}
      <div style={{ padding: "16px 24px 10px", borderBottom: "1px solid rgba(120,115,105,0.12)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "4px" }}>
          <span style={{ fontSize: "9px", color: "#5A5650", letterSpacing: "2px", textTransform: "uppercase" }}>
            Chrystallum · Ontology-Mapped Subgraph Construction
          </span>
          {step.activeSource && (
            <span style={{
              fontSize: "8px", padding: "2px 8px", borderRadius: "10px",
              background: (srcColors[step.activeSource] || "#666") + "22",
              color: srcColors[step.activeSource] || "#999",
              fontFamily: "monospace", fontWeight: 600,
            }}>
              ● {step.activeSource}
            </span>
          )}
        </div>
        <h1 style={{ fontSize: "20px", fontWeight: 700, color: "#F0ECE0", margin: "0 0 2px" }}>
          Step {step.id}: {step.title}
        </h1>
        <p style={{ fontSize: "12px", color: "#7A7568", margin: 0, fontStyle: "italic" }}>
          {step.subtitle}
        </p>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        {/* Graph */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <svg viewBox="0 0 800 520" style={{
            flex: 1, width: "100%",
            background: "radial-gradient(ellipse at center, rgba(40,38,50,0.25) 0%, transparent 70%)",
          }}>
            <defs>
              {Object.entries(EDGE_STYLES).map(([name, s]) => (
                <marker key={name} id={`arrow-${name}`} markerWidth="7" markerHeight="5" refX="6" refY="2.5" orient="auto">
                  <polygon points="0 0, 7 2.5, 0 5" fill={s.color} opacity="0.6" />
                </marker>
              ))}
            </defs>
            {step.edges.map((edge, i) => {
              const f = step.nodes.find(n => n.id === edge.from);
              const t = step.nodes.find(n => n.id === edge.to);
              if (!f || !t) return null;
              return <EdgeLine key={`${edge.from}-${edge.to}-${i}`} from={f} to={t}
                rel={edge.rel} props={edge.props} isNew={!prevEdgeKeys.has(`${edge.from}-${edge.to}`)} />;
            })}
            {step.nodes.map(node => (
              <NodeBox key={node.id} node={node} isNew={!prevIds.has(node.id)} />
            ))}
          </svg>

          {/* Description + query */}
          <div style={{ padding: "10px 24px 8px", background: "rgba(15,15,18,0.8)",
            borderTop: "1px solid rgba(120,115,105,0.1)" }}>
            <p style={{ fontSize: "11.5px", color: "#B0AAA0", lineHeight: 1.5, margin: "0 0 6px" }}>
              {step.description}
            </p>
            {step.query && (
              <div style={{ fontFamily: "monospace", fontSize: "9.5px", color: "#6B6560",
                background: "rgba(0,0,0,0.4)", padding: "5px 10px", borderRadius: "4px" }}>
                {step.query}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div style={{ width: 280, padding: "12px", borderLeft: "1px solid rgba(120,115,105,0.1)",
          background: "rgba(12,12,15,0.5)", overflowY: "auto" }}>
          <Sidebar data={step.sidebar} />

          {/* Legend */}
          <div style={{ marginTop: "14px", padding: "10px 12px", background: "rgba(20,20,22,0.8)",
            borderRadius: "8px", border: "1px solid rgba(120,115,105,0.1)" }}>
            <div style={{ fontSize: "9px", color: "#5A5650", textTransform: "uppercase",
              letterSpacing: "1px", marginBottom: "6px" }}>Node Types</div>
            {Object.entries(NODE_TYPE_STYLES).map(([name, s]) => (
              <div key={name} style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "3px" }}>
                <div style={{ width: 12, height: 12, borderRadius: 3, background: s.fill,
                  border: `1.5px solid ${s.stroke}` }} />
                <span style={{ fontSize: "9.5px", color: "#8B8680", fontFamily: "monospace" }}>{name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Step nav */}
      <div style={{ padding: "8px 24px 12px", display: "flex", gap: "5px", alignItems: "center",
        borderTop: "1px solid rgba(120,115,105,0.1)", background: "rgba(12,12,15,0.6)" }}>
        {STEPS.map((s, i) => (
          <button key={i} onClick={() => goTo(i)} style={{
            width: i === currentStep ? 38 : 30, height: 28, borderRadius: 5,
            border: i === currentStep ? "1.5px solid #7B68EE" : "1px solid rgba(120,115,105,0.2)",
            background: i === currentStep ? "rgba(123,104,238,0.15)" : "transparent",
            color: i === currentStep ? "#C8C0F0" : "#5A5650",
            fontSize: "11px", fontFamily: "monospace", fontWeight: i === currentStep ? 700 : 400,
            cursor: "pointer", transition: "all 0.2s ease",
          }}>
            {i}
          </button>
        ))}
        <span style={{ fontSize: "9px", color: "#5A5650", marginLeft: "8px", fontFamily: "monospace" }}>
          {currentStep + 1}/{STEPS.length}
        </span>
      </div>
    </div>
  );
}
