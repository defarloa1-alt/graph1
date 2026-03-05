import { useState, useMemo, useEffect, useRef } from "react";
import * as d3 from "d3";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — DISCIPLINE UNIVERSE & REPOSITORY INDEX                      ║
// ║  Stack: Neo4j ──► Cytoscape.js ──► React                                   ║
// ║                                                                             ║
// ║  This file is the React application layer.                                 ║
// ║  Data flows: Neo4j (Cypher) → JSON → Cytoscape elements → React render    ║
// ║  Graph topology views use d3-force (same layout engine as Cytoscape fcose) ║
// ║  Production swap: replace d3 renderer with cytoscape({container, elements})║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  ink:"#0D1117", paper:"#F7F4EF", dim:"#8B8680", rule:"#D4CEC6",
  teal:"#1A7A6E", amber:"#B5860D", crimson:"#8B1A1A", navy:"#1A3A5C",
  green:"#1E6B3C", purple:"#5B2D8E", gold:"#C9A227", slate:"#4A5568",
  orange:"#B45309", rose:"#9B2335", cyan:"#0E7490", lime:"#3D6B21",
  bg2:"#EDEAE3",
};

// ── FACET COLORS ──────────────────────────────────────────────────────────────
const FACET_COLOR = {
  Political:C.navy, Military:C.crimson, Economic:C.amber, Social:C.teal,
  Cultural:C.purple, Biographic:C.rose, Diplomatic:C.cyan, Geographic:C.lime,
  Archaeological:C.orange, Religious:C.gold, Intellectual:C.navy,
  Linguistic:C.teal, Artistic:C.purple, Demographic:C.green,
  Environmental:C.lime, Communication:C.orange, Scientific:C.cyan,
  Technological:C.slate,
};

// ══════════════════════════════════════════════════════════════════════════════
// STACK ARCHITECTURE DATA CONTRACT
// ══════════════════════════════════════════════════════════════════════════════
const STACK = {
  layers: [
    {
      name:"Neo4j", role:"Graph Data Store", color:C.teal,
      desc:"All entities, relationships, federation sources, and system nodes. Queries return JSON via Bolt or HTTP API.",
      node_types:["Entity","Discipline","Facet","SYS_FederationSource","LCSH_Heading",
        "LCC_Class","WorldCat_Work","BibliographySource","RetrievalContext","SYS_RelationshipType"],
      query_interface:"Cypher over Bolt (neo4j://localhost:7687) or HTTP (localhost:7474/db/neo4j/tx)",
      example_query:`// Discipline subgraph for Cytoscape
MATCH (d:Entity {entity_type:'CONCEPT'})
WHERE d.qid IN ['Q36442','Q179805','Q32492','Q166542']
OPTIONAL MATCH (d)-[r:DISCIPLINE_HAS_PART|DISCIPLINE_PART_OF]->(d2)
RETURN d, r, d2`,
    },
    {
      name:"Cytoscape.js", role:"Graph Visualization", color:C.purple,
      desc:"Renders graph topology. Receives elements in Cytoscape JSON format. Layout: fcose (force-directed) for discipline graphs, breadthfirst for hierarchy views.",
      elements_format:`// Cytoscape elements contract
{
  nodes: [
    { data: { id:"Q36442", label:"political science",
        type:"discipline", lcc:"J-JZ", dewey:"320",
        facets:["Political","Diplomatic"],
        in_graph: true, primary_for:["Political"] } },
    ...
  ],
  edges: [
    { data: { id:"e_Q36442_Q32492", source:"Q36442",
        target:"Q32492", type:"DISCIPLINE_HAS_PART" } },
    ...
  ]
}`,
      layouts:["fcose — force-directed, best for discipline/facet graphs",
        "breadthfirst — hierarchy view for LCC call number tree",
        "cose — fast force layout for large subgraphs",
        "circle — facet ring view"],
      style_hooks:["type === 'discipline' → circle node, color by primary_for[0]",
        "type === 'facet' → diamond node, facet color",
        "in_graph: false → dashed border (needs harvest)",
        "edge type === 'DISCIPLINE_HAS_PART' → directed solid",
        "edge type === 'TEACHES_VIA' → dashed to federation source"],
      mount:`// Production mount (swap d3 renderer for this)
import cytoscape from 'cytoscape';
import fcose from 'cytoscape-fcose';
cytoscape.use(fcose);

const cy = cytoscape({
  container: document.getElementById('cy'),
  elements: buildElements(neo4jResult),
  style: CYTOSCAPE_STYLE,
  layout: { name:'fcose', animate:true, randomize:false,
    idealEdgeLength: 80, nodeRepulsion: 4500 }
});`,
    },
    {
      name:"React", role:"Application Shell", color:C.navy,
      desc:"This file. Tabbed interface for human and agent consumption. Components receive props from Neo4j query results. Cytoscape container is a ref-mounted div inside a React component.",
      data_flow:[
        "1. Agent or human selects facet / entity / discipline",
        "2. React dispatches Cypher query to Neo4j via Bolt/HTTP",
        "3. Result JSON normalized to Cytoscape elements format",
        "4. Cytoscape re-renders in mounted container ref",
        "5. React sidebar shows selected node detail panel",
      ],
      neo4j_to_elements:`// Adapter: Neo4j result → Cytoscape elements
function buildElements(records) {
  const nodes = [], edges = [], seen = new Set();
  for (const r of records) {
    if (r.d && !seen.has(r.d.properties.qid)) {
      seen.add(r.d.properties.qid);
      nodes.push({ data: {
        id: r.d.properties.qid,
        label: r.d.properties.label,
        type: 'discipline',
        ...r.d.properties
      }});
    }
    if (r.r && r.d2) {
      edges.push({ data: {
        id: r.d.properties.qid+'_'+r.d2.properties.qid,
        source: r.d.properties.qid,
        target: r.d2.properties.qid,
        type: r.r.type
      }});
    }
  }
  return { nodes, edges };
}`,
    },
  ],
  cypher_queries: [
    { id:"CQ-01", name:"Full discipline graph",
      desc:"All discipline nodes + DISCIPLINE_HAS_PART edges → Cytoscape nodes/edges",
      query:`MATCH (d:Entity)
WHERE d.entity_type='CONCEPT'
  AND d.qid IN $discipline_qids
OPTIONAL MATCH (d)-[r:DISCIPLINE_HAS_PART]->(d2)
RETURN d, r, d2` },
    { id:"CQ-02", name:"Facet → discipline map",
      desc:"For a given facet, all disciplines that serve it → two-tier graph",
      query:`MATCH (f:Facet {label:$facet_label})
MATCH (d:Entity {entity_type:'CONCEPT'})
WHERE $facet_label IN d.facets
RETURN f, d, d.primary_for` },
    { id:"CQ-03", name:"Discipline → federation sources",
      desc:"Which sources can enrich a discipline → TEACHES_VIA edges",
      query:`MATCH (d:Entity {qid:$qid})
MATCH (fs:SYS_FederationSource)
WHERE fs.scoping_role IN ['subject_classification','literature','curriculum']
RETURN d, fs` },
    { id:"CQ-04", name:"Discipline → bibliography",
      desc:"Books/works indexed under a discipline's LCSH heading",
      query:`MATCH (d:Entity {qid:$qid})
MATCH (h:LCSH_Heading {lcsh_id:d.lcsh})
MATCH (h)-[:INDEXES]->(w:WorldCat_Work)
RETURN d, h, w ORDER BY w.citation_count DESC LIMIT 25` },
    { id:"CQ-05", name:"Harvest gap query",
      desc:"Disciplines with needs_harvest=true — for pipeline prioritisation",
      query:`MATCH (d:Entity {entity_type:'CONCEPT'})
WHERE d.needs_harvest = true
RETURN d.qid, d.label, d.facet_count
ORDER BY d.facet_count DESC` },
  ],
};

// ══════════════════════════════════════════════════════════════════════════════
// REPOSITORY TEMPLATES
// ══════════════════════════════════════════════════════════════════════════════
const REPOS = {
  OPENALEX_WORKS:    { name:"OpenAlex Works",   color:C.teal,
    url:"https://api.openalex.org/works?filter=concepts.id:{oa_id}&sort=cited_by_count:desc&per_page=25" },
  OPENALEX_CONCEPT:  { name:"OpenAlex Concept", color:C.teal,
    url:"https://api.openalex.org/concepts/{oa_id}" },
  OPEN_LIBRARY:      { name:"Open Library",     color:C.navy,
    url:"https://openlibrary.org/subjects/{slug}.json?limit=50" },
  OPEN_SYLLABUS:     { name:"Open Syllabus",    color:C.navy,
    url:"https://api.opensyllabus.org/v1/fields?q={slug}" },
  LCSH_HEADING:      { name:"LCSH Authority",   color:C.purple,
    url:"https://id.loc.gov/authorities/subjects/{lcsh}.html" },
  WORLDCAT:          { name:"WorldCat",          color:C.purple,
    url:"https://www.worldcat.org/search?q=su%3A{label}" },
  INTERNET_ARCHIVE:  { name:"Internet Archive", color:C.amber,
    url:"https://archive.org/search?query=subject%3A%22{label}%22&mediatype=texts" },
  DOAJ:              { name:"DOAJ",              color:C.amber,
    url:"https://doaj.org/search/articles?ref=hp&q={label}" },
  PERSEUS:           { name:"Perseus",           color:C.crimson,
    url:"https://catalog.perseus.org/catalog?utf8=&search[query]={label}" },
  JSTOR_SEARCH:      { name:"JSTOR",             color:C.slate,
    url:"https://www.jstor.org/action/doBasicSearch?Query={label}&acc=on&wc=on" },
  HATHI_TRUST:       { name:"HathiTrust",        color:C.orange,
    url:"https://catalog.hathitrust.org/Search/Home?lookfor={label}&type=subject" },
  EUROPEANA:         { name:"Europeana",         color:C.orange,
    url:"https://www.europeana.eu/en/search?query={label}" },
  ZENODO:            { name:"Zenodo",            color:C.lime,
    url:"https://zenodo.org/search?q={label}&type=publication" },
  CORE_AC:           { name:"CORE",              color:C.lime,
    url:"https://core.ac.uk/search?q={label}" },
};

// ══════════════════════════════════════════════════════════════════════════════
// FEDERATION SOURCES — updated with PIR, SNAP:DRGN, APR
// ══════════════════════════════════════════════════════════════════════════════
const FEDERATION_SOURCES = [
  { name:"Wikidata",    status:"operational", weight:1.00, role:"discovery_hub",
    entity_types:["ALL"], prop:"", access:"api", format:"SPARQL/JSON",
    endpoint:"https://query.wikidata.org/sparql",
    url_template:"https://www.wikidata.org/wiki/{qid}",
    node_type:null, prop_name:"qid" },
  { name:"Trismegistos",status:"operational", weight:0.95, role:"persons/inscriptions",
    entity_types:["PERSON","INSCRIPTION"], prop:"P1696", access:"api", format:"JSON",
    endpoint:"https://www.trismegistos.org/dataservices/per/index.php",
    url_template:"https://www.trismegistos.org/person/{id}",
    node_type:"BibliographySource", prop_name:"trismeg_id" },
  { name:"LGPN",        status:"operational", weight:0.93, role:"persons",
    entity_types:["PERSON"], prop:"P1047", access:"via_wikidata", format:"SPARQL/JSON",
    endpoint:"https://query.wikidata.org/sparql",
    url_template:"https://www.lgpn.ox.ac.uk/id/{id}",
    node_type:null, prop_name:"lgpn_id" },
  { name:"Pleiades",    status:"operational", weight:0.92, role:"places",
    entity_types:["PLACE"], prop:"P1584", access:"local", format:"CSV/GeoJSON",
    endpoint:"https://atlantides.org/downloads/pleiades/dumps/",
    url_template:"https://pleiades.stoa.org/places/{id}",
    node_type:"Pleiades_Place", prop_name:"pleiades_id" },
  { name:"LCSH/FAST/LCC",status:"operational",weight:0.90, role:"subject_classification",
    entity_types:["SUBJECTCONCEPT","Discipline"], prop:"P244", access:"local", format:"SKOS/CSV",
    endpoint:"https://id.loc.gov/",
    url_template:"https://id.loc.gov/authorities/subjects/{id}.html",
    node_type:"LCSH_Heading", prop_name:"lcsh_id" },
  { name:"Getty AAT",   status:"partial",     weight:0.90, role:"concepts",
    entity_types:["SUBJECTCONCEPT"], prop:"P1014", access:"via_wikidata", format:"SPARQL/JSON",
    endpoint:"https://query.wikidata.org/sparql",
    url_template:"https://vocab.getty.edu/aat/{id}",
    node_type:"LCSH_Heading", prop_name:"getty_aat_id" },
  { name:"DPRR",        status:"blocked",     weight:0.85, role:"persons",
    entity_types:["PERSON"], prop:"P6863", access:"sparql", format:"SPARQL/JSON",
    endpoint:"http://romanrepublic.ac.uk/rdf/endpoint/",
    url_template:"http://romanrepublic.ac.uk/person/{id}",
    node_type:null, prop_name:"dprr_id",
    notes:"Blocked — endpoint intermittent. Full RDF dump available as fallback." },
  { name:"PIR",         status:"planned",     weight:0.83, role:"persons",
    entity_types:["PERSON"], prop:"P4384", access:"api", format:"JSON",
    endpoint:"https://pir.bbaw.de/api/",
    url_template:"https://pir.bbaw.de/person/{id}",
    node_type:null, prop_name:"pir_id",
    notes:"Prosopographia Imperii Romani — Augustus to Diocletian. Laravel/PHP JSON API (GitHub: telota/PIR). Covers post-DPRR persons. Add P4384 as wikidata_property." },
  { name:"SNAP:DRGN",   status:"planned",     weight:0.80, role:"persons",
    entity_types:["PERSON"], prop:"", access:"api", format:"RDF/JSON-LD",
    endpoint:"http://snap.dighum.kcl.ac.uk/",
    url_template:"http://snap.dighum.kcl.ac.uk/id/{id}",
    node_type:null, prop_name:"snap_id",
    notes:"Standards for Networking Ancient Prosopographies. Cross-links DPRR, PIR, LGPN, Trismegistos. Add snap_id property to :Person nodes as the universal crosswalk key." },
  { name:"APR",         status:"planned",     weight:0.75, role:"persons",
    entity_types:["PERSON"], prop:"", access:"web_only", format:"HTML",
    endpoint:"https://www.aarome.org/prosopographical-databases",
    url_template:null,
    node_type:null, prop_name:null,
    notes:"Amici populi Romani — foreign allies & client rulers 3rd BCE–4th CE. Web search only, no public API. Manual harvest required." },
  { name:"PeriodO",     status:"operational", weight:0.85, role:"temporal",
    entity_types:["SUBJECTCONCEPT","POLITY"], prop:"", access:"local", format:"JSON-LD",
    endpoint:"https://data.perio.do/",
    url_template:"https://client.perio.do/?page=period-view&backendID=web-{id}",
    node_type:"Periodo_Period", prop_name:"periodo_id" },
  { name:"VIAF",        status:"partial",     weight:0.85, role:"persons",
    entity_types:["PERSON","ORGANIZATION"], prop:"P214", access:"via_wikidata", format:"SPARQL/JSON",
    endpoint:"https://query.wikidata.org/sparql",
    url_template:"https://viaf.org/viaf/{id}/",
    node_type:null, prop_name:"viaf_id" },
  { name:"OpenAlex",    status:"planned",     weight:0.80, role:"literature",
    entity_types:["Discipline","SUBJECTCONCEPT"], prop:null, access:"api", format:"JSON",
    endpoint:"https://api.openalex.org/works",
    url_template:"https://api.openalex.org/works?filter=concepts.id:{id}&sort=cited_by_count:desc&per_page=25",
    node_type:"BibliographySource", prop_name:"oa_id" },
  { name:"Open Library",status:"planned",     weight:0.75, role:"books",
    entity_types:["Discipline","SUBJECTCONCEPT"], prop:null, access:"api", format:"JSON",
    endpoint:"https://openlibrary.org/api/books",
    url_template:"https://openlibrary.org/subjects/{slug}.json",
    node_type:"WorldCat_Work", prop_name:null },
  { name:"Open Syllabus",status:"planned",    weight:0.75, role:"curriculum",
    entity_types:["Discipline"], prop:null, access:"api", format:"JSON",
    endpoint:"https://api.opensyllabus.org/",
    url_template:"https://api.opensyllabus.org/v1/fields?q={slug}",
    node_type:"BibliographySource", prop_name:null,
    notes:"Galaxy UI: https://galaxy.opensyllabus.org — export CSV of syllabus-ranked works per discipline cluster." },
  { name:"Perseus",     status:"planned",     weight:0.85, role:"primary_texts",
    entity_types:["SUBJECTCONCEPT","PERSON"], prop:null, access:"api", format:"XML/TEI",
    endpoint:"https://catalog.perseus.org/",
    url_template:"https://catalog.perseus.org/catalog/{id}",
    node_type:"BibliographySource", prop_name:"perseus_id" },
  { name:"OCD",         status:"planned",     weight:0.88, role:"taxonomy/grounding",
    entity_types:["SUBJECTCONCEPT","PERSON","PLACE"], prop:"P9106", access:"planned", format:null,
    endpoint:null, url_template:"https://oxfordre.com/classics/display/{id}",
    node_type:"BibliographySource", prop_name:"ocd_id" },
  { name:"EDH",         status:"planned",     weight:0.82, role:"inscriptions",
    entity_types:["PERSON","PLACE"], prop:"P2192", access:"planned", format:null,
    endpoint:null, url_template:"https://edh.ub.uni-heidelberg.de/edh/inschrift/{id}",
    node_type:"BibliographySource", prop_name:"edh_id" },
  { name:"CHRR",        status:"planned",     weight:null, role:"material_evidence",
    entity_types:["COIN"], prop:"", access:"planned", format:null,
    endpoint:null, url_template:null, node_type:"BibliographySource", prop_name:null },
  { name:"CRRO",        status:"planned",     weight:null, role:"material_evidence",
    entity_types:["COIN"], prop:"", access:"planned", format:null,
    endpoint:null, url_template:null, node_type:"BibliographySource", prop_name:null },
];

// ══════════════════════════════════════════════════════════════════════════════
// DISCIPLINES — with dewey field added, 3 political science patches added
// ══════════════════════════════════════════════════════════════════════════════
const DISCIPLINES = [
  // ── HISTORY ───────────────────────────────────────────────────────────────
  { qid:"Q309",     label:"history",                   dewey:"900", in_graph:true,
    oa_id:"C116676364", lcsh:"sh85061212", lcc:"D-DX",
    facets:["Political","Military","Cultural","Economic","Social","Biographic","Diplomatic","Religious","Intellectual","Demographic","Environmental","Geographic","Linguistic","Artistic","Archaeological","Scientific","Technological","Communication"],
    primary_for:[], repos:["OPENALEX_WORKS","OPEN_LIBRARY","WORLDCAT","HATHI_TRUST","JSTOR_SEARCH","OPEN_SYLLABUS"] },
  { qid:"Q435608",  label:"ancient history",           dewey:"930", in_graph:true,
    oa_id:"C2780762961", lcsh:"sh85004880", lcc:"D51-90",
    facets:["Political","Military","Cultural","Economic","Social","Biographic","Diplomatic","Religious","Geographic","Archaeological","Linguistic","Artistic"],
    primary_for:["Political","Military","Biographic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","HATHI_TRUST"] },
  { qid:"Q830852",  label:"history of ancient Rome",   dewey:"937", in_graph:true,
    oa_id:"C2779756987", lcsh:"sh85115007", lcc:"DG200-365",
    facets:["Political","Military","Cultural","Economic","Social","Biographic","Diplomatic","Religious","Geographic","Archaeological","Linguistic","Artistic","Demographic"],
    primary_for:["Political","Biographic","Military"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","INTERNET_ARCHIVE","HATHI_TRUST"] },
  { qid:"Q180536",  label:"economic history",          dewey:"330.09", in_graph:false,
    oa_id:"C2776944186", lcsh:"sh85040830", lcc:"HC-HD",
    facets:["Economic","Social","Political","Demographic","Technological"],
    primary_for:["Economic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","OPEN_SYLLABUS","DOAJ"] },
  { qid:"Q50423863",label:"social history",            dewey:"309", in_graph:false,
    oa_id:"C2780780767", lcsh:"sh85123992", lcc:"HN",
    facets:["Social","Demographic","Cultural","Economic","Biographic"],
    primary_for:["Social","Demographic"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ"] },
  { qid:"Q17524420",label:"cultural history",          dewey:"306.09", in_graph:false,
    oa_id:"C2778969723", lcsh:"sh85034583", lcc:"CB",
    facets:["Cultural","Artistic","Intellectual","Religious","Linguistic"],
    primary_for:["Cultural"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ","EUROPEANA"] },
  { qid:"Q503551",  label:"historical geography",      dewey:"911", in_graph:false,
    oa_id:"C2776823584", lcsh:"sh85061350", lcc:"G70-71",
    facets:["Geographic","Environmental","Military","Political","Demographic"],
    primary_for:["Geographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","DOAJ"] },
  { qid:"Q34739",   label:"history of science",        dewey:"509", in_graph:false,
    oa_id:"C558239735",  lcsh:"sh85061380", lcc:"Q125-127",
    facets:["Scientific","Intellectual","Technological"],
    primary_for:["Scientific"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ"] },
  { qid:"Q1535670", label:"history of technology",     dewey:"609", in_graph:false,
    oa_id:"C2779555317", lcsh:"sh85061370", lcc:"T15-19",
    facets:["Technological","Scientific","Economic"],
    primary_for:["Technological"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ"] },
  { qid:"Q3015699", label:"environmental history",     dewey:"304.2", in_graph:false,
    oa_id:"C2776957218", lcsh:"sh92000311", lcc:"GF13",
    facets:["Environmental","Geographic","Demographic","Economic"],
    primary_for:["Environmental"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ","ZENODO"] },
  { qid:"Q1194524", label:"history of religion",       dewey:"200.9", in_graph:false,
    oa_id:"C2779028977", lcsh:"sh85061377", lcc:"BL",
    facets:["Religious","Cultural","Intellectual","Social"],
    primary_for:["Religious"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","HATHI_TRUST"] },
  { qid:"Q1066186", label:"study of history",          dewey:"907", in_graph:true,
    oa_id:"C116676364", lcsh:"sh85061212", lcc:"D",
    facets:["Intellectual"],  primary_for:["Intellectual"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH"] },

  // ── POLITICAL / LEGAL ────────────────────────────────────────────────────
  { qid:"Q36442",   label:"political science",         dewey:"320", in_graph:true,
    oa_id:"C17744445",  lcsh:"sh85104440", lcc:"J-JZ",
    facets:["Political","Diplomatic","Social","Intellectual"],
    primary_for:["Political"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","WORLDCAT","DOAJ"] },
  { qid:"Q179805",  label:"political philosophy",      dewey:"320.01", in_graph:false,
    oa_id:"C2780660205", lcsh:"sh85104452", lcc:"JC",
    facets:["Political","Intellectual","Social"],  primary_for:["Intellectual"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST","PERSEUS"] },
  { qid:"Q32492",   label:"comparative politics",      dewey:"320.3", in_graph:true,
    oa_id:"C2779576573", lcsh:"sh85029476", lcc:"JF51",
    facets:["Political","Diplomatic"],  primary_for:["Diplomatic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ"] },
  { qid:"Q166542",  label:"international relations",   dewey:"327", in_graph:false,
    oa_id:"C2779091846", lcsh:"sh85067435", lcc:"JZ",
    facets:["Diplomatic","Political"],  primary_for:["Diplomatic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","OPEN_SYLLABUS"] },
  { qid:"Q7748",    label:"law",                       dewey:"340", in_graph:false,
    oa_id:"C199539241",  lcsh:"sh85075119", lcc:"K",
    facets:["Political","Social","Economic"],  primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","HATHI_TRUST"] },
  { qid:"Q4932206", label:"jurisprudence",             dewey:"340.1", in_graph:false,
    oa_id:"C2779524025", lcsh:"sh85071797", lcc:"K201-487",
    facets:["Political","Intellectual"],  primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST","PERSEUS"] },
  { qid:"Q31728",   label:"public administration",     dewey:"351", in_graph:true,
    oa_id:"C2779007467", lcsh:"sh85108432", lcc:"JK-JS",
    facets:["Political","Social"],  primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ"] },
  // ── NEW: political science patches (from Perplexity chat) ─────────────────
  { qid:"Q211141",  label:"political methodology",     dewey:"320.01", in_graph:false,
    oa_id:"C2779576500", lcsh:"sh2008006787", lcc:"JA71",
    facets:["Political","Intellectual","Scientific"],  primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ","WORLDCAT"],
    notes:"Formal methods, causal inference, game theory, computational social science." },
  { qid:"Q281947",  label:"formal political theory",   dewey:"320.1", in_graph:false,
    oa_id:"C2779576510", lcsh:"sh2007001234", lcc:"JA74.5",
    facets:["Political","Intellectual"],  primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ"],
    notes:"Normative theory, rational choice, republicanism as ideal, Polybius/Cicero canon." },
  { qid:"Q717037",  label:"political behaviour",       dewey:"324", in_graph:false,
    oa_id:"C2779576520", lcsh:"sh85104427", lcc:"JA74.5",
    facets:["Political","Social","Communication"],  primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","DOAJ","WORLDCAT"],
    notes:"Elections, crowds, contiones, popular assemblies, political participation. SCA signals: VOTED_IN, PARTICIPATED_IN→assembly, CLIENT_OF, crowd event." },

  // ── ECONOMICS ─────────────────────────────────────────────────────────────
  { qid:"Q8134",    label:"economics",                 dewey:"330", in_graph:false,
    oa_id:"C162324750",  lcsh:"sh85040850", lcc:"HB-HJ",
    facets:["Economic","Social","Political","Demographic"],  primary_for:["Economic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","WORLDCAT","DOAJ"] },
  { qid:"Q43501",   label:"trade",                     dewey:"382", in_graph:false,
    oa_id:"C139719470",  lcsh:"sh85136136", lcc:"HF",
    facets:["Economic","Diplomatic","Geographic","Military"],  primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT"] },
  { qid:"Q185357",  label:"numismatics",               dewey:"737", in_graph:false,
    oa_id:"C2780861543", lcsh:"sh85092769", lcc:"CJ",
    facets:["Economic","Archaeological","Artistic","Political"],
    primary_for:["Economic","Archaeological"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","INTERNET_ARCHIVE"] },

  // ── SOCIAL SCIENCES ───────────────────────────────────────────────────────
  { qid:"Q21201",   label:"sociology",                 dewey:"301", in_graph:false,
    oa_id:"C144024400",  lcsh:"sh85124098", lcc:"HM-HX",
    facets:["Social","Cultural","Demographic","Communication","Biographic"],
    primary_for:["Social"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","WORLDCAT","DOAJ"] },
  { qid:"Q37732",   label:"demography",                dewey:"304.6", in_graph:false,
    oa_id:"C2779316295", lcsh:"sh85036609", lcc:"HB851-3697",
    facets:["Demographic","Social","Economic","Environmental","Geographic"],
    primary_for:["Demographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","DOAJ","ZENODO"] },
  { qid:"Q23404",   label:"anthropology",              dewey:"301", in_graph:true,
    oa_id:"C142362112",  lcsh:"sh85005681", lcc:"GN",
    facets:["Cultural","Social","Demographic","Archaeological","Biographic","Linguistic"],
    primary_for:["Cultural"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","OPEN_SYLLABUS"] },
  { qid:"Q1071",    label:"geography",                 dewey:"910", in_graph:false,
    oa_id:"C205007833",  lcsh:"sh85053986", lcc:"G",
    facets:["Geographic","Environmental","Military","Demographic"],
    primary_for:["Geographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","DOAJ"] },
  { qid:"Q188605",  label:"environmental science",     dewey:"363.7", in_graph:false,
    oa_id:"C39432304",   lcsh:"sh85044203", lcc:"GE",
    facets:["Environmental","Scientific","Geographic"],  primary_for:["Environmental"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ","ZENODO","CORE_AC"] },
  { qid:"Q1069",    label:"geology",                   dewey:"551", in_graph:true,
    oa_id:"C185592680",  lcsh:"sh85054043", lcc:"QE",
    facets:["Environmental","Archaeological","Geographic"],  primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","ZENODO"] },
  { qid:"Q720858",  label:"human ecology",             dewey:"304.2", in_graph:true,
    oa_id:"C2776942939", lcsh:"sh85061962", lcc:"GF",
    facets:["Environmental","Demographic","Social","Geographic"],
    primary_for:["Environmental"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","DOAJ"] },

  // ── COMMUNICATION ─────────────────────────────────────────────────────────
  { qid:"Q517702",  label:"mass communication",        dewey:"302.23", in_graph:false,
    oa_id:"C2776929534", lcsh:"sh85081498", lcc:"P87-96",
    facets:["Communication","Social","Cultural","Political"],
    primary_for:["Communication"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","DOAJ","WORLDCAT"] },
  { qid:"Q3332985", label:"media studies",             dewey:"302.23", in_graph:false,
    oa_id:"C2779576384", lcsh:"sh85082874", lcc:"P87-96",
    facets:["Communication","Cultural","Social","Intellectual"],
    primary_for:["Communication"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ","OPEN_SYLLABUS"] },
  { qid:"Q81009",   label:"rhetoric",                  dewey:"808", in_graph:false,
    oa_id:"C2779576940", lcsh:"sh85113255", lcc:"PN175-239",
    facets:["Communication","Linguistic","Intellectual","Political"],
    primary_for:["Communication","Linguistic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST"] },
  { qid:"Q131436",  label:"propaganda",                dewey:"303.375", in_graph:false,
    oa_id:"C2779018621", lcsh:"sh85107335", lcc:"P301",
    facets:["Communication","Political","Military","Cultural"],  primary_for:[],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT"] },

  // ── LINGUISTICS ───────────────────────────────────────────────────────────
  { qid:"Q8162",    label:"linguistics",               dewey:"410", in_graph:false,
    oa_id:"C41008148",   lcsh:"sh85077556", lcc:"P",
    facets:["Linguistic","Cultural","Intellectual","Communication"],
    primary_for:["Linguistic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","WORLDCAT","DOAJ"] },
  { qid:"Q40634",   label:"philology",                 dewey:"410", in_graph:true,
    oa_id:"C2779130124", lcsh:"sh85101443", lcc:"PA-PZ",
    facets:["Linguistic","Intellectual","Cultural","Archaeological"],
    primary_for:["Linguistic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST"] },
  { qid:"Q131476",  label:"epigraphy",                 dewey:"411.7", in_graph:false,
    oa_id:"C2779517890", lcsh:"sh85044160", lcc:"CN",
    facets:["Linguistic","Archaeological","Biographic","Political","Religious"],
    primary_for:["Linguistic","Archaeological"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","INTERNET_ARCHIVE"] },
  { qid:"Q182622",  label:"onomastics",                dewey:"929.4", in_graph:false,
    oa_id:"C2779031578", lcsh:"sh85095146", lcc:"P321",
    facets:["Linguistic","Biographic","Cultural","Geographic"],  primary_for:["Linguistic"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT"] },
  { qid:"Q12060559",label:"paleography",               dewey:"091", in_graph:false,
    oa_id:"C2779559891", lcsh:"sh85096768", lcc:"Z105-115",
    facets:["Linguistic","Archaeological","Intellectual","Communication"],  primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","INTERNET_ARCHIVE","HATHI_TRUST"] },
  { qid:"Q495527",  label:"classical philology",       dewey:"480", in_graph:true,
    oa_id:"C2779130124", lcsh:"sh85026706", lcc:"PA",
    facets:["Linguistic","Intellectual","Cultural"],  primary_for:["Linguistic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST"] },

  // ── ARCHAEOLOGY ───────────────────────────────────────────────────────────
  { qid:"Q23498",   label:"archaeology",               dewey:"930.1", in_graph:false,
    oa_id:"C105702510",  lcsh:"sh85006507", lcc:"CC-CN",
    facets:["Archaeological","Geographic","Environmental","Artistic","Technological"],
    primary_for:["Archaeological"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","DOAJ","ZENODO"] },
  { qid:"Q815250",  label:"classical archaeology",     dewey:"938", in_graph:false,
    oa_id:"C2779527048", lcsh:"sh85026679", lcc:"DE-DF",
    facets:["Archaeological","Artistic","Cultural","Geographic","Religious"],
    primary_for:["Archaeological","Artistic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","EUROPEANA","WORLDCAT","INTERNET_ARCHIVE"] },
  { qid:"Q757248",  label:"papyrology",                dewey:"091", in_graph:true,
    oa_id:"C2779543875", lcsh:"sh85097637", lcc:"CN",
    facets:["Archaeological","Linguistic","Biographic","Economic","Social"],
    primary_for:["Archaeological","Linguistic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","INTERNET_ARCHIVE","HATHI_TRUST"] },
  { qid:"Q1371704", label:"etruscology",               dewey:"937.5", in_graph:true,
    oa_id:"C2781042234", lcsh:"sh85045093", lcc:"DG223",
    facets:["Archaeological","Cultural","Linguistic","Religious","Artistic"],
    primary_for:["Archaeological"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","EUROPEANA"] },

  // ── ARTS ─────────────────────────────────────────────────────────────────
  { qid:"Q50637",   label:"art history",               dewey:"709", in_graph:true,
    oa_id:"C138885621",  lcsh:"sh85007697", lcc:"N",
    facets:["Artistic","Cultural","Archaeological","Intellectual","Religious"],
    primary_for:["Artistic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","EUROPEANA","WORLDCAT","OPEN_SYLLABUS"] },
  { qid:"Q11826511",label:"iconography",               dewey:"704.94", in_graph:false,
    oa_id:"C2779096476", lcsh:"sh85064117", lcc:"N7560",
    facets:["Artistic","Religious","Cultural","Archaeological"],  primary_for:["Artistic"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","EUROPEANA","WORLDCAT"] },

  // ── BIOGRAPHY / PROSOPOGRAPHY ────────────────────────────────────────────
  { qid:"Q1774192", label:"prosopography",             dewey:"929.2", in_graph:false,
    oa_id:"C2779756988", lcsh:"sh85108043", lcc:"CS",
    facets:["Biographic","Social","Political","Military","Demographic"],
    primary_for:["Biographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","HATHI_TRUST"] },
  { qid:"Q595045",  label:"genealogy",                 dewey:"929.1", in_graph:false,
    oa_id:"C2779130125", lcsh:"sh85053695", lcc:"CS",
    facets:["Biographic","Social","Demographic"],  primary_for:["Biographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","INTERNET_ARCHIVE"] },

  // ── RELIGIOUS STUDIES ────────────────────────────────────────────────────
  { qid:"Q34187",   label:"religious studies",         dewey:"200", in_graph:false,
    oa_id:"C63528460",   lcsh:"sh85112549", lcc:"BL-BX",
    facets:["Religious","Cultural","Social","Intellectual","Archaeological"],
    primary_for:["Religious"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","OPEN_SYLLABUS","DOAJ"] },
  { qid:"Q170382",  label:"mythology",                 dewey:"291.13", in_graph:false,
    oa_id:"C2779005614", lcsh:"sh85089374", lcc:"BL303-325",
    facets:["Religious","Cultural","Linguistic","Artistic","Intellectual"],
    primary_for:["Religious"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST","PERSEUS"] },

  // ── MILITARY ─────────────────────────────────────────────────────────────
  { qid:"Q192781",  label:"military history",          dewey:"355.009", in_graph:true,
    oa_id:"C192780198",  lcsh:"sh85085207", lcc:"U-UH",
    facets:["Military","Political","Geographic","Technological","Diplomatic"],
    primary_for:["Military"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","INTERNET_ARCHIVE","HATHI_TRUST"] },
  { qid:"Q46196",   label:"military science",          dewey:"355", in_graph:false,
    oa_id:"C192780199",  lcsh:"sh85085217", lcc:"U",
    facets:["Military","Technological","Political"],  primary_for:["Military"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","PERSEUS"] },

  // ── SCIENCE ───────────────────────────────────────────────────────────────
  { qid:"Q420",     label:"biology",                   dewey:"570", in_graph:true,
    oa_id:"C86803240",   lcsh:"sh85014253", lcc:"QH-QR",
    facets:["Scientific","Environmental","Demographic"],  primary_for:["Scientific"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ","ZENODO"] },
  { qid:"Q11190",   label:"medicine",                  dewey:"610", in_graph:false,
    oa_id:"C71924100",   lcsh:"sh85083064", lcc:"R",
    facets:["Scientific","Social","Demographic","Environmental"],  primary_for:["Scientific"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ","ZENODO"] },

  // ── CLASSICS ─────────────────────────────────────────────────────────────
  { qid:"Q841090",  label:"classics",                  dewey:"480", in_graph:true,
    oa_id:"C27548473",   lcsh:"sh85026706", lcc:"PA",
    facets:["Linguistic","Cultural","Intellectual","Artistic","Religious"],
    primary_for:["Intellectual","Linguistic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST","INTERNET_ARCHIVE"] },
  { qid:"Q112939719",label:"Classical Greek and Roman history", dewey:"938", in_graph:true,
    oa_id:"C2779756989", lcsh:"sh85026705", lcc:"DG",
    facets:["Political","Military","Cultural","Archaeological","Biographic","Demographic","Religious","Artistic","Economic","Social","Geographic","Diplomatic"],
    primary_for:["Biographic","Archaeological"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","EUROPEANA","INTERNET_ARCHIVE","HATHI_TRUST"] },
];

// ── FACETS (18) ──────────────────────────────────────────────────────────────
const FACETS = [
  { label:"Political",     color:C.navy,    icon:"⚖",
    desc:"Power, governance, magistracies, legislation, statecraft.",
    sca_signals:["P31=Q3024240","P31=Q1307214","POSITION_HELD","CITIZEN_OF","legislation event"],
    primary:["political science","history of ancient Rome","ancient history","jurisprudence",
      "political philosophy","political methodology","formal political theory","political behaviour"] },
  { label:"Military",      color:C.crimson, icon:"⚔",
    desc:"Warfare, armies, battles, sieges, strategy, logistics.",
    sca_signals:["FOUGHT_IN","BATTLE_PARTICIPANT","DEFEATED","CONQUERED","BESIEGED"],
    primary:["military history","military science","history of ancient Rome","ancient history"] },
  { label:"Economic",      color:C.amber,   icon:"💰",
    desc:"Trade, currency, taxation, agriculture, labour, commerce.",
    sca_signals:["P31=Q4917→coin","PRODUCED","numismatic entity","trade route"],
    primary:["economics","economic history","numismatics","trade"] },
  { label:"Social",        color:C.teal,    icon:"👥",
    desc:"Class, slavery, family, gender, daily life, customs, patronage.",
    sca_signals:["MEMBER_OF→class","SLAVE/FREEDMAN","PATRON_OF","family edges"],
    primary:["sociology","social history","anthropology","prosopography","demography"] },
  { label:"Cultural",      color:C.purple,  icon:"🎭",
    desc:"Values, festivals, entertainment, identity, acculturation.",
    sca_signals:["cultural entity in corpus","festival","LIVED_IN→region","P31=cultural practice"],
    primary:["cultural history","anthropology","classics","art history"] },
  { label:"Biographic",    color:C.rose,    icon:"📜",
    desc:"Individual life histories, careers, prosopography, onomastics.",
    sca_signals:["entity_type=PERSON","FATHER_OF","POSITION_HELD","BORN_IN_YEAR","DIED_IN_YEAR"],
    primary:["prosopography","genealogy","onomastics","ancient history","classical philology"] },
  { label:"Diplomatic",    color:C.cyan,    icon:"🤝",
    desc:"Treaties, alliances, embassies, foreign relations, client kingdoms.",
    sca_signals:["ALLIED_WITH","TREATY","DECLARED_FOR","client kingdom"],
    primary:["international relations","comparative politics","ancient history"] },
  { label:"Geographic",    color:C.lime,    icon:"🗺",
    desc:"Territories, provinces, roads, topography, spatial analysis.",
    sca_signals:["entity_type=PLACE","pleiades_id","LOCATED_IN","HAD_CAPITAL"],
    primary:["historical geography","geography","classical archaeology"] },
  { label:"Archaeological",color:C.orange,  icon:"⛏",
    desc:"Material evidence, excavations, artefacts, epigraphy, numismatics.",
    sca_signals:["pleiades_id","getty_aat_id","inscriptions","coin entity","EVIDENCED_BY"],
    primary:["archaeology","classical archaeology","etruscology","papyrology","epigraphy","numismatics"] },
  { label:"Religious",     color:C.gold,    icon:"🏛",
    desc:"Cults, temples, priesthoods, divination, ritual, theology.",
    sca_signals:["ADHERES_TO→religion","temple entity","PRIEST role","ritual event"],
    primary:["religious studies","history of religion","mythology"] },
  { label:"Intellectual",  color:C.navy,    icon:"📚",
    desc:"Philosophy, literature, scholarship, rhetoric, ideas.",
    sca_signals:["AUTHOR","WROTE","WORK_OF","philosophical text"],
    primary:["classics","classical philology","political philosophy","history of science","formal political theory"] },
  { label:"Linguistic",    color:C.teal,    icon:"📝",
    desc:"Latin language, inscriptions, manuscripts, papyri, script.",
    sca_signals:["inscribed entity","lcsh heading for language","text corpus node"],
    primary:["linguistics","philology","epigraphy","classical philology","onomastics","rhetoric"] },
  { label:"Artistic",      color:C.purple,  icon:"🎨",
    desc:"Visual arts, sculpture, painting, architecture, coins, gems.",
    sca_signals:["getty_aat_id","P31=Q3305213→painting","P31=Q860861→sculpture"],
    primary:["art history","classical archaeology","iconography","numismatics"] },
  { label:"Demographic",   color:C.green,   icon:"👤",
    desc:"Population, migration, mortality, fertility, urbanisation.",
    sca_signals:["census data","MIGRATED_FROM","MIGRATED_TO","population estimate"],
    primary:["demography","social history","historical geography","anthropology"] },
  { label:"Environmental", color:C.lime,    icon:"🌿",
    desc:"Climate, agriculture, land use, resources, disease, ecology.",
    sca_signals:["climate entity","agricultural entity","disaster event"],
    primary:["environmental history","environmental science","geology","human ecology"] },
  { label:"Communication", color:C.orange,  icon:"📡",
    desc:"Oratory, propaganda, public records, information networks.",
    sca_signals:["AUTHOR→speech/letter","P31=Q49848→letter","rhetorical text"],
    primary:["mass communication","rhetoric","media studies","propaganda","political behaviour"] },
  { label:"Scientific",    color:C.cyan,    icon:"🔬",
    desc:"Natural philosophy, medicine, mathematics, astronomy.",
    sca_signals:["scientific text in corpus","mathematical entity","medical text"],
    primary:["history of science","medicine","biology","political methodology"] },
  { label:"Technological", color:C.slate,   icon:"⚙",
    desc:"Engineering, infrastructure, construction, hydraulics, roads.",
    sca_signals:["aqueduct entity","P31=Q811979→structure","road node"],
    primary:["history of technology","military science","classical archaeology"] },
];

// ══════════════════════════════════════════════════════════════════════════════
// UI HELPERS
// ══════════════════════════════════════════════════════════════════════════════
function Mono({ children, col=C.teal, s=9 }) {
  return <code style={{fontFamily:"'Courier New',monospace",color:col,fontSize:s,
    background:col+"12",padding:"1px 5px",borderRadius:3}}>{children}</code>;
}
function Tag({ label, fill, s=8 }) {
  return <span style={{background:fill+"18",border:`1px solid ${fill}`,borderRadius:10,
    padding:"1px 7px",fontSize:s,color:fill,fontWeight:"bold",
    display:"inline-block",margin:1}}>{label}</span>;
}
function CopyBtn({ text }) {
  const [ok,setOk]=useState(false);
  return <button onClick={()=>{navigator.clipboard?.writeText(text);setOk(true);setTimeout(()=>setOk(false),1400);}}
    style={{background:ok?C.green:C.slate,color:"white",border:"none",borderRadius:3,
      padding:"1px 8px",fontSize:8,cursor:"pointer",fontWeight:"bold"}}>{ok?"✓":"copy"}</button>;
}
const STATUS_COL={operational:C.green,partial:C.amber,planned:C.slate,blocked:C.crimson,web_only:C.dim};

// ══════════════════════════════════════════════════════════════════════════════
// D3 GRAPH VIEW — Cytoscape.js elements format, d3-force renderer
// Swap cytoscape({container,elements,...}) for production
// ══════════════════════════════════════════════════════════════════════════════
function GraphView({ facetFilter }) {
  const svgRef = useRef(null);
  const [hovNode, setHovNode] = useState(null);
  const [mode, setMode] = useState("discipline-facet"); // discipline-facet | hierarchy | federation

  // Build Cytoscape-format elements from DISCIPLINES + FACETS
  const elements = useMemo(()=>{
    const nodes = [], edges = [];

    if (mode === "discipline-facet") {
      // Facet nodes
      FACETS.forEach(f=>{
        nodes.push({ data:{ id:`f_${f.label}`, label:f.label,
          type:"facet", color:f.color, icon:f.icon } });
      });
      // Discipline nodes
      const shown = facetFilter==="ALL"
        ? DISCIPLINES
        : DISCIPLINES.filter(d=>d.facets.includes(facetFilter)||d.primary_for.includes(facetFilter));
      shown.slice(0,40).forEach(d=>{
        nodes.push({ data:{ id:d.qid, label:d.label, type:"discipline",
          in_graph:d.in_graph, lcc:d.lcc, dewey:d.dewey,
          color:d.primary_for[0]?FACET_COLOR[d.primary_for[0]]:C.dim } });
        d.primary_for.forEach(f=>{
          edges.push({ data:{ id:`pe_${d.qid}_${f}`, source:d.qid,
            target:`f_${f}`, type:"PRIMARY_FOR" } });
        });
        const secondaryFacets = d.facets.filter(f=>!d.primary_for.includes(f));
        secondaryFacets.slice(0,2).forEach(f=>{
          edges.push({ data:{ id:`se_${d.qid}_${f}`, source:d.qid,
            target:`f_${f}`, type:"SUPPORTS" } });
        });
      });
    } else if (mode === "hierarchy") {
      // LCC call-number hierarchy
      const groups = {};
      DISCIPLINES.forEach(d=>{
        const top = d.lcc.split(/[-\d]/)[0].replace(/\s/,"").slice(0,2)||"?";
        if(!groups[top]) groups[top]=[];
        groups[top].push(d);
      });
      Object.entries(groups).forEach(([g,discs])=>{
        nodes.push({data:{id:`lcc_${g}`,label:`LCC ${g}`,type:"lcc",color:C.amber}});
        discs.forEach(d=>{
          nodes.push({data:{id:d.qid,label:d.label,type:"discipline",
            in_graph:d.in_graph,color:d.in_graph?C.green:C.amber}});
          edges.push({data:{id:`h_${d.qid}`,source:`lcc_${g}`,target:d.qid,type:"CLASSIFIES"}});
        });
      });
    } else {
      // Federation sources → disciplines
      const shown = FEDERATION_SOURCES.filter(fs=>
        fs.entity_types.some(t=>["Discipline","SUBJECTCONCEPT","ALL"].includes(t)));
      shown.forEach(fs=>{
        nodes.push({data:{id:`fs_${fs.name}`,label:fs.name,type:"federation",
          color:STATUS_COL[fs.status]||C.dim}});
      });
      DISCIPLINES.slice(0,20).forEach(d=>{
        nodes.push({data:{id:d.qid,label:d.label,type:"discipline",
          in_graph:d.in_graph,color:C.slate}});
        const usable = d.repos.filter(rk=>
          ["OPENALEX_WORKS","OPEN_SYLLABUS","LCSH_HEADING"].includes(rk));
        usable.forEach(rk=>{
          const fsName = rk==="OPENALEX_WORKS"?"OpenAlex":rk==="OPEN_SYLLABUS"?"Open Syllabus":"LCSH/FAST/LCC";
          edges.push({data:{id:`f_${d.qid}_${rk}`,source:`fs_${fsName}`,
            target:d.qid,type:"TEACHES_VIA"}});
        });
      });
    }
    return { nodes, edges };
  },[mode, facetFilter]);

  useEffect(()=>{
    if(!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const W = svgRef.current.clientWidth||700, H=480;
    svg.attr("width",W).attr("height",H);

    const typeR = { facet:22, lcc:18, federation:20, discipline:12 };
    const typeCol = n => n.data.color || (n.data.type==="facet"?C.navy:n.data.in_graph?C.green:C.amber);

    const g = svg.append("g");
    svg.call(d3.zoom().scaleExtent([0.3,3])
      .on("zoom",e=>g.attr("transform",e.transform)));

    const sim = d3.forceSimulation(elements.nodes)
      .force("link", d3.forceLink(elements.edges)
        .id(d=>d.data.id).distance(d=>d.data.type==="PRIMARY_FOR"?70:120).strength(0.4))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(W/2,H/2))
      .force("collide", d3.forceCollide().radius(d=>typeR[d.data.type]||14+4));

    const link = g.append("g").selectAll("line").data(elements.edges).join("line")
      .attr("stroke",d=>d.data.type==="PRIMARY_FOR"?C.crimson:d.data.type==="TEACHES_VIA"?C.teal:C.rule)
      .attr("stroke-width",d=>d.data.type==="PRIMARY_FOR"?2:1)
      .attr("stroke-opacity",0.7)
      .attr("stroke-dasharray",d=>d.data.type==="SUPPORTS"?"4,3":"none");

    const node = g.append("g").selectAll("g").data(elements.nodes).join("g")
      .attr("cursor","pointer")
      .call(d3.drag()
        .on("start",(e,d)=>{if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;})
        .on("drag",(e,d)=>{d.fx=e.x;d.fy=e.y;})
        .on("end",(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}))
      .on("mouseenter",(e,d)=>setHovNode(d.data))
      .on("mouseleave",()=>setHovNode(null));

    node.append("circle")
      .attr("r",d=>typeR[d.data.type]||12)
      .attr("fill",d=>typeCol(d)+"22")
      .attr("stroke",d=>typeCol(d))
      .attr("stroke-width",d=>d.data.in_graph===false?1.5:2)
      .attr("stroke-dasharray",d=>d.data.in_graph===false?"4,2":"none");

    node.append("text")
      .attr("text-anchor","middle").attr("dy","0.35em")
      .attr("font-size",d=>d.data.type==="facet"?10:d.data.type==="lcc"?9:7.5)
      .attr("font-family","Arial,sans-serif")
      .attr("font-weight",d=>d.data.type==="facet"?"bold":"normal")
      .attr("fill",d=>typeCol(d))
      .attr("pointer-events","none")
      .text(d=>d.data.type==="facet"?d.data.icon+" "+d.data.label:
        d.data.label.length>16?d.data.label.slice(0,14)+"…":d.data.label);

    sim.on("tick",()=>{
      link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y)
          .attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
      node.attr("transform",d=>`translate(${d.x},${d.y})`);
    });
    return ()=>sim.stop();
  },[elements]);

  return (
    <div>
      <div style={{display:"flex",gap:8,marginBottom:8,alignItems:"center",flexWrap:"wrap"}}>
        {[["discipline-facet","Discipline → Facet"],["hierarchy","LCC Hierarchy"],["federation","Federation Sources"]].map(([k,l])=>(
          <button key={k} onClick={()=>setMode(k)}
            style={{border:`1.5px solid ${mode===k?C.navy:C.rule}`,background:mode===k?C.navy:"white",
              color:mode===k?"white":C.slate,borderRadius:12,padding:"3px 12px",fontSize:9,cursor:"pointer",fontWeight:"bold"}}>
            {l}
          </button>
        ))}
        <span style={{fontSize:9,color:C.dim,marginLeft:4}}>
          Scroll: zoom · Drag: pan · Node drag: reposition ·{" "}
          <span style={{color:C.green}}>●</span> in-graph{" "}
          <span style={{color:C.amber,borderBottom:`1px dashed ${C.amber}`}}>- -</span> needs harvest
        </span>
      </div>
      <div style={{position:"relative",border:`1px solid ${C.rule}`,borderRadius:8,
        background:C.ink,overflow:"hidden"}}>
        <svg ref={svgRef} style={{display:"block",width:"100%",height:480}}/>
        {hovNode && (
          <div style={{position:"absolute",top:10,right:10,background:"rgba(13,17,23,.92)",
            border:`1px solid ${FACET_COLOR[hovNode.label]||C.rule}`,borderRadius:6,
            padding:"8px 12px",color:"white",maxWidth:220,pointerEvents:"none"}}>
            <div style={{fontWeight:"bold",fontSize:11,color:FACET_COLOR[hovNode.label]||C.teal,marginBottom:4}}>
              {hovNode.icon&&hovNode.icon+" "}{hovNode.label}
            </div>
            {hovNode.type==="discipline"&&<>
              <div style={{fontSize:9,color:"#aaa",marginBottom:2}}>Dewey {hovNode.dewey} · LCC {hovNode.lcc}</div>
              <div style={{fontSize:9,color:hovNode.in_graph?C.green:C.amber}}>
                {hovNode.in_graph?"✓ in graph":"○ needs harvest"}
              </div>
            </>}
            {hovNode.type==="facet"&&<div style={{fontSize:9,color:"#aaa"}}>{hovNode.desc}</div>}
            {hovNode.type==="federation"&&<div style={{fontSize:9,color:"#aaa"}}>{hovNode.status}</div>}
          </div>
        )}
      </div>
      <div style={{marginTop:6,fontSize:8.5,color:C.dim,fontFamily:"Arial,sans-serif"}}>
        Production: replace d3 renderer with{" "}
        <Mono col={C.purple} s={8}>cytoscape({"{"} container: ref.current, elements, layout:{"{"} name:'fcose' {"}"} {"}"})</Mono>
        {" "}· Layout algo: <Mono s={8} col={C.slate}>fcose</Mono> for discipline graphs,{" "}
        <Mono s={8} col={C.slate}>breadthfirst</Mono> for LCC hierarchy
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// STACK ARCHITECTURE TAB
// ══════════════════════════════════════════════════════════════════════════════
function StackView() {
  const [openQ, setOpenQ] = useState("CQ-01");
  const [openLayer, setOpenLayer] = useState("Neo4j");
  return (
    <div>
      {/* three-layer diagram */}
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:0,
        marginBottom:16,border:`1px solid ${C.rule}`,borderRadius:8,overflow:"hidden"}}>
        {STACK.layers.map((l,i)=>(
          <div key={l.name} onClick={()=>setOpenLayer(l.name)}
            style={{borderRight:i<2?`1px solid ${C.rule}`:"none",
              background:openLayer===l.name?l.color+"18":"white",cursor:"pointer",
              borderBottom:openLayer===l.name?`3px solid ${l.color}`:"3px solid transparent"}}>
            <div style={{padding:"10px 14px"}}>
              <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:4}}>
                <span style={{fontSize:14,fontWeight:"bold",color:l.color}}>{l.name}</span>
                {i<2&&<span style={{color:C.dim,fontSize:14}}>──►</span>}
              </div>
              <div style={{fontSize:9,color:C.slate}}>{l.role}</div>
              <div style={{fontSize:8.5,color:C.dim,marginTop:4}}>{l.desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* layer detail */}
      {STACK.layers.filter(l=>l.label===openLayer||l.name===openLayer).map(l=>(
        <div key={l.name} style={{background:"white",border:`1.5px solid ${l.color}`,
          borderRadius:8,padding:14,marginBottom:16}}>
          <div style={{fontWeight:"bold",color:l.color,fontSize:12,marginBottom:10}}>{l.name}</div>
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
            <div>
              {l.node_types&&<>
                <div style={{fontSize:8,color:C.dim,fontWeight:"bold",marginBottom:4}}>NODE TYPES</div>
                <div style={{display:"flex",flexWrap:"wrap",gap:3,marginBottom:8}}>
                  {l.node_types.map(n=><Mono key={n} col={l.color} s={8}>:{n}</Mono>)}
                </div>
              </>}
              {l.layouts&&<>
                <div style={{fontSize:8,color:C.dim,fontWeight:"bold",marginBottom:4}}>LAYOUTS</div>
                {l.layouts.map(lyt=><div key={lyt} style={{fontSize:8.5,color:C.slate,marginBottom:2}}>• {lyt}</div>)}
              </>}
              {l.data_flow&&<>
                <div style={{fontSize:8,color:C.dim,fontWeight:"bold",marginBottom:4}}>DATA FLOW</div>
                {l.data_flow.map(s=><div key={s} style={{fontSize:8.5,color:C.slate,marginBottom:2}}>{s}</div>)}
              </>}
            </div>
            <div>
              {(l.example_query||l.elements_format||l.mount||l.neo4j_to_elements)&&<>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:4}}>
                  <div style={{fontSize:8,color:C.dim,fontWeight:"bold"}}>
                    {l.example_query?"EXAMPLE CYPHER":l.mount?"PRODUCTION MOUNT":l.neo4j_to_elements?"ADAPTER":"ELEMENTS FORMAT"}
                  </div>
                  <CopyBtn text={l.example_query||l.elements_format||l.mount||l.neo4j_to_elements}/>
                </div>
                <pre style={{fontFamily:"'Courier New',monospace",fontSize:8,color:l.color,
                  background:l.color+"08",borderRadius:4,padding:8,margin:0,
                  overflow:"auto",maxHeight:200,whiteSpace:"pre-wrap"}}>{l.example_query||l.elements_format||l.mount||l.neo4j_to_elements}</pre>
              </>}
            </div>
          </div>
        </div>
      ))}

      {/* Cypher query library */}
      <div style={{fontWeight:"bold",color:C.ink,fontSize:11,marginBottom:8}}>
        Neo4j → Cytoscape Cypher Queries
      </div>
      {STACK.cypher_queries.map(q=>(
        <div key={q.id} style={{border:`1px solid ${C.rule}`,borderRadius:6,marginBottom:6,overflow:"hidden"}}>
          <div onClick={()=>setOpenQ(openQ===q.id?null:q.id)}
            style={{padding:"7px 12px",cursor:"pointer",background:openQ===q.id?"#F0EDE8":"white",
              display:"flex",gap:10,alignItems:"center"}}>
            <Mono col={C.navy}>{q.id}</Mono>
            <span style={{fontWeight:"bold",fontSize:10,color:C.ink}}>{q.name}</span>
            <span style={{fontSize:9,color:C.dim,flex:1}}>{q.desc}</span>
            <span style={{color:C.dim}}>{openQ===q.id?"▲":"▼"}</span>
          </div>
          {openQ===q.id&&(
            <div style={{padding:"8px 12px",borderTop:`1px solid ${C.rule}`,background:"white"}}>
              <div style={{display:"flex",justifyContent:"space-between",marginBottom:4}}>
                <Mono col={C.dim} s={8}>Cypher</Mono>
                <CopyBtn text={q.query}/>
              </div>
              <pre style={{fontFamily:"'Courier New',monospace",fontSize:9,color:C.teal,
                background:C.teal+"08",borderRadius:4,padding:8,margin:0,
                overflow:"auto",maxHeight:150}}>{q.query}</pre>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// DISCIPLINE TABLE TAB
// ══════════════════════════════════════════════════════════════════════════════
function DisciplineTable() {
  const [search,setSearch]=useState("");
  const [ff,setFf]=useState("ALL");
  const [fs,setFs]=useState("ALL");
  const [open,setOpen]=useState(null);

  const rows = useMemo(()=>DISCIPLINES.filter(d=>{
    const ms = !search||d.label.toLowerCase().includes(search.toLowerCase());
    const mf = ff==="ALL"||d.facets.includes(ff)||d.primary_for.includes(ff);
    const ms2= fs==="ALL"||(fs==="in_graph"&&d.in_graph)||(fs==="harvest"&&!d.in_graph);
    return ms&&mf&&ms2;
  }),[search,ff,fs]);

  return (
    <div>
      <div style={{display:"flex",gap:8,marginBottom:10,flexWrap:"wrap",alignItems:"center"}}>
        <input value={search} onChange={e=>setSearch(e.target.value)}
          placeholder="Search…" style={{border:`1px solid ${C.rule}`,borderRadius:6,
            padding:"4px 10px",fontSize:10,flex:"0 0 150px"}}/>
        <select value={ff} onChange={e=>setFf(e.target.value)}
          style={{border:`1px solid ${C.rule}`,borderRadius:6,padding:"4px 8px",fontSize:10}}>
          <option value="ALL">All Facets</option>
          {FACETS.map(f=><option key={f.label} value={f.label}>{f.icon} {f.label}</option>)}
        </select>
        {["ALL","in_graph","harvest"].map(s=>(
          <button key={s} onClick={()=>setFs(s)}
            style={{border:`1.5px solid ${fs===s?C.navy:C.rule}`,background:fs===s?C.navy:"white",
              color:fs===s?"white":C.slate,borderRadius:12,padding:"3px 10px",fontSize:9,cursor:"pointer"}}>
            {s==="ALL"?"All":s==="in_graph"?"In Graph":"Needs Harvest"}
            {" "}({s==="ALL"?DISCIPLINES.length:DISCIPLINES.filter(d=>s==="in_graph"?d.in_graph:!d.in_graph).length})
          </button>
        ))}
      </div>
      <div style={{fontSize:9.5,color:C.dim,marginBottom:8}}>{rows.length} disciplines</div>
      {rows.map(d=>(
        <div key={d.qid} style={{border:`1px solid ${C.rule}`,borderRadius:5,marginBottom:5,
          borderLeft:`3px solid ${d.in_graph?C.green:C.amber}`}}>
          <div onClick={()=>setOpen(open===d.qid?null:d.qid)}
            style={{padding:"6px 10px",cursor:"pointer",background:"white",
              display:"flex",gap:8,alignItems:"center",flexWrap:"wrap"}}>
            <span style={{background:(d.in_graph?C.green:C.amber)+"18",border:`1px solid ${d.in_graph?C.green:C.amber}`,
              borderRadius:8,padding:"1px 7px",fontSize:7.5,color:d.in_graph?C.green:C.amber,fontWeight:"bold"}}>
              {d.in_graph?"IN GRAPH":"HARVEST"}
            </span>
            <Mono col={C.slate}>{d.qid}</Mono>
            <span style={{fontWeight:"bold",fontSize:10.5,color:C.ink}}>{d.label}</span>
            <Mono col={C.amber} s={8}>{d.dewey}</Mono>
            <Mono col={C.navy} s={8}>{d.lcc}</Mono>
            {d.primary_for.map(f=><Tag key={f} label={`★${f}`} fill={FACET_COLOR[f]||C.navy}/>)}
            <span style={{marginLeft:"auto",fontSize:9,color:C.dim}}>{d.facets.length}F · {d.repos.length}R · {open===d.qid?"▲":"▼"}</span>
          </div>
          {open===d.qid&&(
            <div style={{borderTop:`1px solid ${C.rule}`,background:"#FAFAF8",
              padding:"8px 10px",display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
              <div>
                <div style={{fontSize:8,color:C.dim,fontWeight:"bold",marginBottom:4}}>FACETS SERVED</div>
                <div style={{display:"flex",flexWrap:"wrap",gap:2,marginBottom:8}}>
                  {d.facets.map(f=><Tag key={f} label={d.primary_for.includes(f)?`★${f}`:f}
                    fill={FACET_COLOR[f]||C.slate} s={8}/>)}
                </div>
                <div style={{display:"flex",gap:12,marginBottom:6,flexWrap:"wrap"}}>
                  <div><div style={{fontSize:8,color:C.dim}}>Dewey</div><Mono col={C.orange}>{d.dewey}</Mono></div>
                  <div><div style={{fontSize:8,color:C.dim}}>LCC</div><Mono col={C.amber}>{d.lcc}</Mono></div>
                  {d.lcsh&&<div><div style={{fontSize:8,color:C.dim}}>LCSH</div><Mono col={C.purple}>{d.lcsh}</Mono></div>}
                  {d.oa_id&&<div><div style={{fontSize:8,color:C.dim}}>OpenAlex</div><Mono col={C.teal}>{d.oa_id}</Mono></div>}
                </div>
                {d.notes&&<div style={{background:C.navy+"08",border:`1px solid ${C.navy}33`,
                  borderRadius:4,padding:"4px 8px",fontSize:8.5,color:C.navy,fontStyle:"italic"}}>{d.notes}</div>}
              </div>
              <div>
                <div style={{fontSize:8,color:C.dim,fontWeight:"bold",marginBottom:4}}>REPOS ({d.repos.length})</div>
                {d.repos.map(rk=>{
                  const r=REPOS[rk];
                  const url=r.url.replace("{oa_id}",d.oa_id||"").replace("{lcsh}",d.lcsh||"")
                    .replace("{slug}",d.label.toLowerCase().replace(/\s+/g,"-"))
                    .replace("{label}",encodeURIComponent(d.label));
                  return (
                    <div key={rk} style={{marginBottom:4,borderLeft:`2px solid ${r.color}`,paddingLeft:5}}>
                      <div style={{display:"flex",gap:4,alignItems:"center"}}>
                        <span style={{fontSize:8.5,fontWeight:"bold",color:r.color}}>{r.name}</span>
                        <CopyBtn text={url}/>
                      </div>
                      <div style={{fontFamily:"monospace",fontSize:7,color:C.dim,wordBreak:"break-all"}}>{url}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// FEDERATION TAB
// ══════════════════════════════════════════════════════════════════════════════
function FedView() {
  const [open,setOpen]=useState(null);
  const [filter,setFilter]=useState("ALL");
  const shown=filter==="ALL"?FEDERATION_SOURCES:FEDERATION_SOURCES.filter(s=>s.status===filter);
  return (
    <div>
      <div style={{fontSize:9,color:C.slate,background:"white",border:`1px solid ${C.rule}`,
        borderRadius:6,padding:"6px 10px",marginBottom:10}}>
        Updated: PIR (Q4384), SNAP:DRGN (crosswalk key), APR (web-only), Open Syllabus Galaxy noted.
        <strong style={{color:C.amber}}> snap_id</strong> to be added as universal crosswalk property on :Person nodes.
      </div>
      <div style={{display:"flex",gap:6,marginBottom:10,flexWrap:"wrap"}}>
        {["ALL","operational","partial","planned","blocked","web_only"].map(s=>{
          const col=s==="ALL"?C.navy:(STATUS_COL[s]||C.slate);
          return <button key={s} onClick={()=>setFilter(s)}
            style={{border:`1.5px solid ${col}`,background:filter===s?col:"white",
              color:filter===s?"white":col,borderRadius:12,padding:"2px 10px",fontSize:9,cursor:"pointer",fontWeight:"bold"}}>
            {s}({s==="ALL"?FEDERATION_SOURCES.length:FEDERATION_SOURCES.filter(x=>x.status===s).length})
          </button>;
        })}
      </div>
      {shown.map(src=>{
        const col=STATUS_COL[src.status]||C.dim;
        return (
          <div key={src.name} style={{border:`1.5px solid ${col}33`,borderLeft:`4px solid ${col}`,
            borderRadius:5,marginBottom:5,opacity:src.status==="blocked"?.7:1}}>
            <div onClick={()=>setOpen(open===src.name?null:src.name)}
              style={{padding:"6px 10px",cursor:"pointer",background:"white",
                display:"flex",gap:8,alignItems:"center",flexWrap:"wrap"}}>
              <Tag label={src.status} fill={col}/>
              <span style={{fontWeight:"bold",fontSize:11,color:C.ink,minWidth:110}}>{src.name}</span>
              {src.weight&&<Mono col={C.amber} s={8}>w={src.weight}</Mono>}
              <span style={{fontSize:9,color:C.dim,flex:1}}>{src.role}</span>
              <div style={{display:"flex",gap:2}}>{src.entity_types.map(e=><Tag key={e} label={e} fill={C.slate}/>)}</div>
              <span style={{color:C.dim,fontSize:9}}>{open===src.name?"▲":"▼"}</span>
            </div>
            {open===src.name&&(
              <div style={{padding:"8px 10px",background:"#FAFAF8",borderTop:`1px solid ${C.rule}`,
                display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
                <div>
                  {src.endpoint&&<div style={{marginBottom:6}}><div style={{fontSize:8,color:C.dim}}>ENDPOINT</div>
                    <Mono col={C.navy}>{src.endpoint}</Mono></div>}
                  {src.url_template&&<div style={{marginBottom:6}}><div style={{fontSize:8,color:C.dim}}>URL TEMPLATE</div>
                    <div style={{display:"flex",gap:4}}><Mono col={C.teal} s={8}>{src.url_template}</Mono><CopyBtn text={src.url_template}/></div>
                  </div>}
                  {src.prop&&<div style={{marginBottom:4}}><div style={{fontSize:8,color:C.dim}}>WIKIDATA PROP</div>
                    <Mono col={C.purple}>{src.prop}</Mono>{" → "}
                    <Mono col={C.slate} s={8}>n.{src.prop_name||"?"}</Mono></div>}
                  {src.node_type&&<div><div style={{fontSize:8,color:C.dim}}>RESOURCE NODE</div>
                    <Mono col={C.amber}>:{src.node_type}</Mono></div>}
                </div>
                <div>
                  {src.notes&&<div style={{background:C.amber+"10",border:`1px solid ${C.amber}`,
                    borderRadius:4,padding:"5px 8px",fontSize:8.5,color:C.ink,marginBottom:6}}>
                    <strong style={{color:C.amber}}>Note: </strong>{src.notes}</div>}
                  <div style={{fontSize:8,color:C.dim,marginBottom:3}}>ACCESS</div>
                  <div style={{display:"flex",gap:4}}><Mono col={C.navy}>{src.access}</Mono>
                    <Mono col={C.slate}>{src.format||"TBD"}</Mono></div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// ROOT
// ══════════════════════════════════════════════════════════════════════════════
export default function App() {
  const [view,setView]=useState("graph");
  const [facetFilter,setFacetFilter]=useState("ALL");
  const VIEWS=[
    ["graph",`Graph View`],
    ["disciplines",`Disciplines (${DISCIPLINES.length})`],
    ["federation",`Federation (${FEDERATION_SOURCES.length})`],
    ["stack","Stack Architecture"],
  ];
  return (
    <div style={{fontFamily:"Georgia,serif",background:C.paper,minHeight:"100vh",padding:16}}>
      {/* header */}
      <div style={{borderBottom:`2px solid ${C.ink}`,paddingBottom:10,marginBottom:12}}>
        <div style={{display:"flex",alignItems:"baseline",gap:10,flexWrap:"wrap"}}>
          <span style={{fontSize:10,fontWeight:"bold",color:C.dim,letterSpacing:3,
            textTransform:"uppercase",fontFamily:"Arial,sans-serif"}}>CHRYSTALLUM</span>
          <span style={{fontSize:15,fontWeight:"bold",color:C.ink}}>Discipline Universe & Repository Index</span>
          <div style={{display:"flex",gap:6,marginLeft:4}}>
            {[["Neo4j",C.teal],["Cytoscape.js",C.purple],["React",C.navy]].map(([n,c])=>(
              <span key={n} style={{background:c,color:"white",borderRadius:4,
                padding:"1px 8px",fontSize:8.5,fontWeight:"bold"}}>{n}</span>
            ))}
          </div>
          <span style={{color:C.dim,fontSize:9,marginLeft:"auto",fontFamily:"Arial,sans-serif"}}>
            {DISCIPLINES.length} disciplines · 18 facets · {FEDERATION_SOURCES.length} sources
          </span>
        </div>
        <div style={{fontSize:9,color:C.slate,marginTop:3,fontFamily:"Arial,sans-serif"}}>
          All 18 facet agents invoked per entity. SCA assigns primary. Dewey + LCC + LCSH = three-axis discipline address.
          Cytoscape.js handles graph topology; React handles application shell; Neo4j is source of truth.
        </div>
      </div>

      {/* nav */}
      <div style={{display:"flex",gap:0,marginBottom:12,borderBottom:`2px solid ${C.ink}`,
        fontFamily:"Arial,sans-serif"}}>
        {VIEWS.map(([k,l])=>(
          <button key={k} onClick={()=>setView(k)}
            style={{border:"none",padding:"6px 14px",fontSize:10,cursor:"pointer",
              background:"transparent",fontWeight:view===k?"bold":"normal",
              color:view===k?C.ink:C.dim,
              borderBottom:view===k?`3px solid ${C.ink}`:"3px solid transparent"}}>
            {l}
          </button>
        ))}
        {view==="graph"&&(
          <div style={{marginLeft:"auto",display:"flex",alignItems:"center",gap:6}}>
            <span style={{fontSize:9,color:C.dim}}>Facet filter:</span>
            <select value={facetFilter} onChange={e=>setFacetFilter(e.target.value)}
              style={{border:`1px solid ${C.rule}`,borderRadius:6,padding:"2px 6px",fontSize:9}}>
              <option value="ALL">All</option>
              {FACETS.map(f=><option key={f.label} value={f.label}>{f.icon} {f.label}</option>)}
            </select>
          </div>
        )}
      </div>

      {view==="graph"       && <GraphView facetFilter={facetFilter}/>}
      {view==="disciplines" && <DisciplineTable/>}
      {view==="federation"  && <FedView/>}
      {view==="stack"       && <StackView/>}
    </div>
  );
}
