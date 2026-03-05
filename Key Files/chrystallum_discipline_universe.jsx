import { useState, useMemo } from "react";

// ╔══════════════════════════════════════════════════════════════════════════════╗
// ║  CHRYSTALLUM — COMPLETE DISCIPLINE UNIVERSE & REPOSITORY INDEX             ║
// ║  All 18 Facet Agents · Every Academic Discipline · All Addressable Repos   ║
// ║                                                                             ║
// ║  AGENT MODEL:                                                               ║
// ║  ALL 18 facet agents are invoked for every entity. Each scores its own     ║
// ║  facet relevance. SCA reads all scores and assigns PRIMARY facet.          ║
// ║  Secondary facets above threshold remain active as co-assignments.         ║
// ║  The capability_cipher encodes primary + all secondary facets.             ║
// ╚══════════════════════════════════════════════════════════════════════════════╝

const C = {
  ink:"#0D1117", paper:"#F7F4EF", dim:"#8B8680", rule:"#D4CEC6",
  teal:"#1A7A6E", amber:"#B5860D", crimson:"#8B1A1A", navy:"#1A3A5C",
  green:"#1E6B3C", purple:"#5B2D8E", gold:"#C9A227", slate:"#4A5568",
  orange:"#B45309", rose:"#9B2335", cyan:"#0E7490", lime:"#3D6B21",
};

// ── REPOSITORY TEMPLATES ───────────────────────────────────────────────────────
// Every addressable source an agent can call to retrieve training material.
// {slug}   = normalized discipline label (lowercase, hyphens)
// {lcsh}   = LCSH heading ID
// {oa_id}  = OpenAlex concept ID (C + number)
// {label}  = raw discipline label for free-text search
// {viaf}   = VIAF ID
const REPOS = {
  OPENALEX_CONCEPT:  { name:"OpenAlex Concept",    color:C.teal,
    url:"https://api.openalex.org/concepts/{oa_id}",
    desc:"Concept metadata, related concepts, works count" },
  OPENALEX_WORKS:    { name:"OpenAlex Top Works",   color:C.teal,
    url:"https://api.openalex.org/works?filter=concepts.id:{oa_id}&sort=cited_by_count:desc&per_page=25",
    desc:"Top 25 cited works in this discipline — open-access links included" },
  OPENALEX_JOURNALS: { name:"OpenAlex Journals",   color:C.teal,
    url:"https://api.openalex.org/sources?filter=topics.subfield.display_name:{label}&sort=cited_by_count:desc",
    desc:"Top journals publishing in this discipline" },
  OPEN_LIBRARY:      { name:"Open Library Subject",color:C.navy,
    url:"https://openlibrary.org/subjects/{slug}.json?limit=50",
    desc:"50 books classified under this subject — many with read-online links" },
  OPEN_SYLLABUS:     { name:"Open Syllabus",       color:C.navy,
    url:"https://api.opensyllabus.org/v1/fields?q={slug}",
    desc:"Most-assigned textbooks in university syllabi globally" },
  LCSH_HEADING:      { name:"LCSH Authority",      color:C.purple,
    url:"https://id.loc.gov/authorities/subjects/{lcsh}.html",
    desc:"Subject heading authority: scope note, broader/narrower terms, LCC range" },
  WORLDCAT:          { name:"WorldCat Subject",    color:C.purple,
    url:"https://www.worldcat.org/search?q=su%3A{label}",
    desc:"Library catalogue search — all editions, formats, holding libraries" },
  INTERNET_ARCHIVE:  { name:"Internet Archive",    color:C.amber,
    url:"https://archive.org/search?query=subject%3A%22{label}%22&mediatype=texts",
    desc:"Full-text books and periodicals — many in public domain" },
  DOAJ:              { name:"DOAJ Open Journals",  color:C.amber,
    url:"https://doaj.org/search/articles?ref=hp&q={label}",
    desc:"Directory of Open Access Journals — peer-reviewed articles, no paywall" },
  PERSEUS:           { name:"Perseus Library",     color:C.crimson,
    url:"https://catalog.perseus.org/catalog?utf8=&search[query]={label}",
    desc:"Classical primary texts — Latin and Greek with translations and commentary" },
  JSTOR_SEARCH:      { name:"JSTOR Full-Text",     color:C.slate,
    url:"https://www.jstor.org/action/doBasicSearch?Query={label}&acc=on&wc=on",
    desc:"Academic journal archive — includes open access content" },
  GOOGLE_SCHOLAR:    { name:"Google Scholar",      color:C.slate,
    url:"https://scholar.google.com/scholar?q={label}&as_sdt=0%2C5",
    desc:"Broad academic literature — preprints, theses, conference papers" },
  EUROPEANA:         { name:"Europeana",            color:C.orange,
    url:"https://www.europeana.eu/en/search?query={label}&media=true",
    desc:"European cultural heritage — digitised artworks, manuscripts, artefacts" },
  HATHI_TRUST:       { name:"HathiTrust Digital",  color:C.orange,
    url:"https://catalog.hathitrust.org/Search/Home?lookfor={label}&type=subject",
    desc:"Digitised books from major research libraries — full text for PD works" },
  ZENODO:            { name:"Zenodo Research",      color:C.lime,
    url:"https://zenodo.org/search?q={label}&type=publication",
    desc:"Open research outputs — data, preprints, datasets, grey literature" },
  CORE_AC:           { name:"CORE Open Access",    color:C.lime,
    url:"https://core.ac.uk/search?q={label}",
    desc:"Aggregator of open-access research papers from repositories worldwide" },
};

// ── COMPLETE DISCIPLINE UNIVERSE ───────────────────────────────────────────────
// in_graph: true = already a node in Chrystallum
// needs_harvest: true = QID known, must be added via harvest pipeline
// oa_id: OpenAlex concept ID (C-prefixed number)
// lcsh: LCSH heading ID (sh + number)
// lcc: Library of Congress Classification range
// facets: ALL facets this discipline informs (many-to-many)
// repos: which REPO keys apply (ordered by priority)
// primary_for: which facet(s) this discipline is the PRIMARY academic home of
const DISCIPLINES = [

  // ══ HISTORY CLUSTER ═══════════════════════════════════════════════════════
  { qid:"Q309",    label:"history",
    in_graph:true, needs_harvest:false,
    oa_id:"C116676364", lcsh:"sh85061212", lcc:"D-DX",
    facets:["Political","Military","Cultural","Economic","Social","Biographic","Diplomatic","Religious","Intellectual","Demographic","Environmental","Geographic","Linguistic","Artistic","Archaeological","Scientific","Technological","Communication"],
    primary_for:[], // all facets draw on history — no single primary
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","WORLDCAT","HATHI_TRUST","JSTOR_SEARCH","OPEN_SYLLABUS"] },

  { qid:"Q435608", label:"ancient history",
    in_graph:true, needs_harvest:false,
    oa_id:"C2780762961", lcsh:"sh85004880", lcc:"D51-90",
    facets:["Political","Military","Cultural","Economic","Social","Biographic","Diplomatic","Religious","Geographic","Archaeological","Linguistic","Artistic"],
    primary_for:["Political","Military","Biographic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","HATHI_TRUST"] },

  { qid:"Q830852", label:"history of ancient Rome",
    in_graph:true, needs_harvest:false,
    oa_id:"C2779756987", lcsh:"sh85115007", lcc:"DG200-DG365",
    facets:["Political","Military","Cultural","Economic","Social","Biographic","Diplomatic","Religious","Geographic","Archaeological","Linguistic","Artistic","Demographic"],
    primary_for:["Political","Biographic","Military"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","INTERNET_ARCHIVE","HATHI_TRUST"] },

  { qid:"Q180536", label:"economic history",
    in_graph:false, needs_harvest:true,
    oa_id:"C2776944186", lcsh:"sh85040830", lcc:"HC-HD",
    facets:["Economic","Social","Political","Demographic","Technological"],
    primary_for:["Economic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","OPEN_SYLLABUS","DOAJ"] },

  { qid:"Q50423863",label:"social history",
    in_graph:false, needs_harvest:true,
    oa_id:"C2780780767", lcsh:"sh85123992", lcc:"HN",
    facets:["Social","Demographic","Cultural","Economic","Biographic"],
    primary_for:["Social","Demographic"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ"] },

  { qid:"Q17524420", label:"cultural history",
    in_graph:false, needs_harvest:true,
    oa_id:"C2778969723", lcsh:"sh85034583", lcc:"CB",
    facets:["Cultural","Artistic","Intellectual","Religious","Linguistic"],
    primary_for:["Cultural"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ","EUROPEANA"] },

  { qid:"Q503551",  label:"historical geography",
    in_graph:false, needs_harvest:true,
    oa_id:"C2776823584", lcsh:"sh85061350", lcc:"G70-G71",
    facets:["Geographic","Environmental","Military","Political","Demographic"],
    primary_for:["Geographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","DOAJ"] },

  { qid:"Q34739",   label:"history of science",
    in_graph:false, needs_harvest:true,
    oa_id:"C558239735",  lcsh:"sh85061380", lcc:"Q125-Q127",
    facets:["Scientific","Intellectual","Technological"],
    primary_for:["Scientific"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ"] },

  { qid:"Q1535670", label:"history of technology",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779555317", lcsh:"sh85061370", lcc:"T15-T19",
    facets:["Technological","Scientific","Economic"],
    primary_for:["Technological"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ"] },

  { qid:"Q3015699", label:"environmental history",
    in_graph:false, needs_harvest:true,
    oa_id:"C2776957218", lcsh:"sh92000311", lcc:"GF13",
    facets:["Environmental","Geographic","Demographic","Economic"],
    primary_for:["Environmental"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","DOAJ","ZENODO"] },

  { qid:"Q1194524", label:"history of religion",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779028977", lcsh:"sh85061377", lcc:"BL",
    facets:["Religious","Cultural","Intellectual","Social"],
    primary_for:["Religious"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","HATHI_TRUST"] },

  { qid:"Q1066186", label:"study of history",
    in_graph:true, needs_harvest:false,
    oa_id:"C116676364", lcsh:"sh85061212", lcc:"D",
    facets:["Intellectual"],
    primary_for:["Intellectual"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH"] },

  // ══ POLITICAL / LEGAL CLUSTER ═════════════════════════════════════════════
  { qid:"Q36442",   label:"political science",
    in_graph:true, needs_harvest:false,
    oa_id:"C17744445",  lcsh:"sh85104440", lcc:"J-JZ",
    facets:["Political","Diplomatic","Social","Intellectual"],
    primary_for:["Political"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","WORLDCAT","DOAJ"] },

  { qid:"Q179805",  label:"political philosophy",
    in_graph:false, needs_harvest:true,
    oa_id:"C2780660205", lcsh:"sh85104452", lcc:"JC",
    facets:["Political","Intellectual","Social"],
    primary_for:["Intellectual"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST","PERSEUS"] },

  { qid:"Q32492",   label:"comparative politics",
    in_graph:true, needs_harvest:false,
    oa_id:"C2779576573", lcsh:"sh85029476", lcc:"JF51",
    facets:["Political","Diplomatic"],
    primary_for:["Diplomatic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ"] },

  { qid:"Q166542",  label:"international relations",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779091846", lcsh:"sh85067435", lcc:"JZ",
    facets:["Diplomatic","Political"],
    primary_for:["Diplomatic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","OPEN_SYLLABUS"] },

  { qid:"Q7748",    label:"law",
    in_graph:false, needs_harvest:true,
    oa_id:"C199539241",  lcsh:"sh85075119", lcc:"K",
    facets:["Political","Social","Economic"],
    primary_for:[], // Roman law is cross-cutting
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","HATHI_TRUST"] },

  { qid:"Q4932206", label:"jurisprudence",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779524025", lcsh:"sh85071797", lcc:"K201-K487",
    facets:["Political","Intellectual"],
    primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST","PERSEUS"] },

  { qid:"Q31728",   label:"public administration",
    in_graph:true, needs_harvest:false,
    oa_id:"C2779007467", lcsh:"sh85108432", lcc:"JK-JS",
    facets:["Political","Social"],
    primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ"] },

  // ══ ECONOMICS CLUSTER ═════════════════════════════════════════════════════
  { qid:"Q8134",    label:"economics",
    in_graph:false, needs_harvest:true,
    oa_id:"C162324750",  lcsh:"sh85040850", lcc:"HB-HJ",
    facets:["Economic","Social","Political","Demographic"],
    primary_for:["Economic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","WORLDCAT","DOAJ"] },

  { qid:"Q43501",   label:"trade",
    in_graph:false, needs_harvest:true,
    oa_id:"C139719470",  lcsh:"sh85136136", lcc:"HF",
    facets:["Economic","Diplomatic","Geographic","Military"],
    primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT"] },

  { qid:"Q185357",  label:"numismatics",
    in_graph:false, needs_harvest:true,
    oa_id:"C2780861543", lcsh:"sh85092769", lcc:"CJ",
    facets:["Economic","Archaeological","Artistic","Political"],
    primary_for:["Economic","Archaeological"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","INTERNET_ARCHIVE"] },

  // ══ SOCIOLOGY / SOCIAL SCIENCES ═══════════════════════════════════════════
  { qid:"Q21201",   label:"sociology",
    in_graph:false, needs_harvest:true,
    oa_id:"C144024400",  lcsh:"sh85124098", lcc:"HM-HX",
    facets:["Social","Cultural","Demographic","Communication","Biographic"],
    primary_for:["Social"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","WORLDCAT","DOAJ"] },

  { qid:"Q37732",   label:"demography",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779316295", lcsh:"sh85036609", lcc:"HB851-HB3697",
    facets:["Demographic","Social","Economic","Environmental","Geographic"],
    primary_for:["Demographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","DOAJ","ZENODO"] },

  { qid:"Q23404",   label:"anthropology",
    in_graph:true, needs_harvest:false,
    oa_id:"C142362112",  lcsh:"sh85005681", lcc:"GN",
    facets:["Cultural","Social","Demographic","Archaeological","Biographic","Linguistic"],
    primary_for:["Cultural"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","OPEN_SYLLABUS"] },

  { qid:"Q1071",    label:"geography",
    in_graph:false, needs_harvest:true,
    oa_id:"C205007833",  lcsh:"sh85053986", lcc:"G",
    facets:["Geographic","Environmental","Military","Demographic"],
    primary_for:["Geographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","DOAJ"] },

  { qid:"Q188605",  label:"environmental science",
    in_graph:false, needs_harvest:true,
    oa_id:"C39432304",   lcsh:"sh85044203", lcc:"GE",
    facets:["Environmental","Scientific","Geographic"],
    primary_for:["Environmental"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ","ZENODO","CORE_AC"] },

  { qid:"Q1069",    label:"geology",
    in_graph:true, needs_harvest:false,
    oa_id:"C185592680",  lcsh:"sh85054043", lcc:"QE",
    facets:["Environmental","Archaeological","Geographic"],
    primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","ZENODO"] },

  { qid:"Q720858",  label:"human ecology",
    in_graph:true, needs_harvest:false,
    oa_id:"C2776942939", lcsh:"sh85061962", lcc:"GF",
    facets:["Environmental","Demographic","Social","Geographic"],
    primary_for:["Environmental"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","DOAJ"] },

  // ══ COMMUNICATION CLUSTER ═════════════════════════════════════════════════
  { qid:"Q517702",  label:"mass communication",
    in_graph:false, needs_harvest:true,
    oa_id:"C2776929534", lcsh:"sh85081498", lcc:"P87-P96",
    facets:["Communication","Social","Cultural","Political"],
    primary_for:["Communication"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","DOAJ","WORLDCAT"] },

  { qid:"Q3332985", label:"media studies",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779576384", lcsh:"sh85082874", lcc:"P87-P96",
    facets:["Communication","Cultural","Social","Intellectual"],
    primary_for:["Communication"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ","OPEN_SYLLABUS"] },

  { qid:"Q81009",   label:"rhetoric",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779576940", lcsh:"sh85113255", lcc:"PN175-PN239",
    facets:["Communication","Linguistic","Intellectual","Political"],
    primary_for:["Communication","Linguistic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST"] },

  { qid:"Q131436",  label:"propaganda",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779018621", lcsh:"sh85107335", lcc:"P301",
    facets:["Communication","Political","Military","Cultural"],
    primary_for:[],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT"] },

  // ══ LINGUISTICS CLUSTER ═══════════════════════════════════════════════════
  { qid:"Q8162",    label:"linguistics",
    in_graph:false, needs_harvest:true,
    oa_id:"C41008148",   lcsh:"sh85077556", lcc:"P",
    facets:["Linguistic","Cultural","Intellectual","Communication"],
    primary_for:["Linguistic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","OPEN_SYLLABUS","JSTOR_SEARCH","WORLDCAT","DOAJ"] },

  { qid:"Q40634",   label:"philology",
    in_graph:true, needs_harvest:false,
    oa_id:"C2779130124", lcsh:"sh85101443", lcc:"PA-PZ",
    facets:["Linguistic","Intellectual","Cultural","Archaeological"],
    primary_for:["Linguistic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST"] },

  { qid:"Q131476",  label:"epigraphy",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779517890", lcsh:"sh85044160", lcc:"CN",
    facets:["Linguistic","Archaeological","Biographic","Political","Religious"],
    primary_for:["Linguistic","Archaeological"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","INTERNET_ARCHIVE"] },

  { qid:"Q182622",  label:"onomastics",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779031578", lcsh:"sh85095146", lcc:"P321",
    facets:["Linguistic","Biographic","Cultural","Geographic"],
    primary_for:["Linguistic"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT"] },

  { qid:"Q12060559",label:"paleography",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779559891", lcsh:"sh85096768", lcc:"Z105-Z115",
    facets:["Linguistic","Archaeological","Intellectual","Communication"],
    primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","INTERNET_ARCHIVE","HATHI_TRUST"] },

  { qid:"Q495527",  label:"classical philology",
    in_graph:true, needs_harvest:false,
    oa_id:"C2779130124", lcsh:"sh85026706", lcc:"PA",
    facets:["Linguistic","Intellectual","Cultural","Literary"],
    primary_for:["Linguistic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST"] },

  // ══ ARCHAEOLOGY / MATERIAL CULTURE ════════════════════════════════════════
  { qid:"Q23498",   label:"archaeology",
    in_graph:false, needs_harvest:true,
    oa_id:"C105702510",  lcsh:"sh85006507", lcc:"CC-CN",
    facets:["Archaeological","Geographic","Environmental","Artistic","Technological"],
    primary_for:["Archaeological"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","DOAJ","ZENODO"] },

  { qid:"Q815250",  label:"classical archaeology",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779527048", lcsh:"sh85026679", lcc:"DE-DF",
    facets:["Archaeological","Artistic","Cultural","Geographic","Religious"],
    primary_for:["Archaeological","Artistic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","EUROPEANA","WORLDCAT","INTERNET_ARCHIVE"] },

  { qid:"Q757248",  label:"papyrology",
    in_graph:true, needs_harvest:false,
    oa_id:"C2779543875", lcsh:"sh85097637", lcc:"CN",
    facets:["Archaeological","Linguistic","Biographic","Economic","Social"],
    primary_for:["Archaeological","Linguistic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","INTERNET_ARCHIVE","HATHI_TRUST"] },

  { qid:"Q1371704", label:"etruscology",
    in_graph:true, needs_harvest:false,
    oa_id:"C2781042234", lcsh:"sh85045093", lcc:"DG223",
    facets:["Archaeological","Cultural","Linguistic","Religious","Artistic"],
    primary_for:["Archaeological"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT","EUROPEANA"] },

  // ══ ARTS / AESTHETICS ═════════════════════════════════════════════════════
  { qid:"Q50637",   label:"art history",
    in_graph:true, needs_harvest:false,
    oa_id:"C138885621",  lcsh:"sh85007697", lcc:"N",
    facets:["Artistic","Cultural","Archaeological","Intellectual","Religious"],
    primary_for:["Artistic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","EUROPEANA","WORLDCAT","OPEN_SYLLABUS"] },

  { qid:"Q35986",   label:"aesthetics",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779756987", lcsh:"sh85001441", lcc:"BH",
    facets:["Artistic","Intellectual","Cultural"],
    primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST"] },

  { qid:"Q11826511",label:"iconography",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779096476", lcsh:"sh85064117", lcc:"N7560",
    facets:["Artistic","Religious","Cultural","Archaeological"],
    primary_for:["Artistic"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","EUROPEANA","WORLDCAT"] },

  // ══ BIOGRAPHY / PROSOPOGRAPHY ═════════════════════════════════════════════
  { qid:"Q1774192", label:"prosopography",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779756988", lcsh:"sh85108043", lcc:"CS",
    facets:["Biographic","Social","Political","Military","Demographic"],
    primary_for:["Biographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","HATHI_TRUST"] },

  { qid:"Q595045",  label:"genealogy",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779130125", lcsh:"sh85053695", lcc:"CS",
    facets:["Biographic","Social","Demographic"],
    primary_for:["Biographic"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","INTERNET_ARCHIVE"] },

  // ══ RELIGIOUS STUDIES ═════════════════════════════════════════════════════
  { qid:"Q34187",   label:"religious studies",
    in_graph:false, needs_harvest:true,
    oa_id:"C63528460",   lcsh:"sh85112549", lcc:"BL-BX",
    facets:["Religious","Cultural","Social","Intellectual","Archaeological"],
    primary_for:["Religious"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","OPEN_SYLLABUS","DOAJ"] },

  { qid:"Q9174",    label:"religion",
    in_graph:true, needs_harvest:false,
    oa_id:"C63528460",   lcsh:"sh85112549", lcc:"BL",
    facets:["Religious","Cultural","Social","Political"],
    primary_for:["Religious"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST","WORLDCAT"] },

  { qid:"Q170382",  label:"mythology",
    in_graph:false, needs_harvest:true,
    oa_id:"C2779005614", lcsh:"sh85089374", lcc:"BL303-BL325",
    facets:["Religious","Cultural","Linguistic","Artistic","Intellectual"],
    primary_for:["Religious"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST","PERSEUS"] },

  // ══ MILITARY CLUSTER ══════════════════════════════════════════════════════
  { qid:"Q192781",  label:"military history",
    in_graph:true, needs_harvest:false,
    oa_id:"C192780198",  lcsh:"sh85085207", lcc:"U-UH",
    facets:["Military","Political","Geographic","Technological","Diplomatic"],
    primary_for:["Military"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","INTERNET_ARCHIVE","HATHI_TRUST"] },

  { qid:"Q46196",   label:"military science",
    in_graph:false, needs_harvest:true,
    oa_id:"C192780199",  lcsh:"sh85085217", lcc:"U",
    facets:["Military","Technological","Political"],
    primary_for:["Military"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","PERSEUS"] },

  // ══ SCIENCE / TECHNOLOGY ══════════════════════════════════════════════════
  { qid:"Q420",     label:"biology",
    in_graph:true, needs_harvest:false,
    oa_id:"C86803240",   lcsh:"sh85014253", lcc:"QH-QR",
    facets:["Scientific","Environmental","Demographic"],
    primary_for:["Scientific"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ","ZENODO"] },

  { qid:"Q413",     label:"physics",
    in_graph:false, needs_harvest:true,
    oa_id:"C121332964",  lcsh:"sh85101653", lcc:"QC",
    facets:["Scientific","Technological"],
    primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","ZENODO","CORE_AC"] },

  { qid:"Q11190",   label:"medicine",
    in_graph:false, needs_harvest:true,
    oa_id:"C71924100",   lcsh:"sh85083064", lcc:"R",
    facets:["Scientific","Social","Demographic","Environmental"],
    primary_for:["Scientific"],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","DOAJ","ZENODO"] },

  // ══ CLASSICS SPECIFIC ═════════════════════════════════════════════════════
  { qid:"Q841090",  label:"classics",
    in_graph:true, needs_harvest:false,
    oa_id:"C27548473",   lcsh:"sh85026706", lcc:"PA",
    facets:["Linguistic","Cultural","Intellectual","Artistic","Religious"],
    primary_for:["Intellectual","Linguistic"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","HATHI_TRUST","INTERNET_ARCHIVE"] },

  { qid:"Q112939719",label:"Classical Greek and Roman history",
    in_graph:true, needs_harvest:false,
    oa_id:"C2779756989", lcsh:"sh85026705", lcc:"DG",
    facets:["Political","Military","Cultural","Archaeological","Biographic","Demographic","Religious","Artistic","Economic","Social","Geographic","Diplomatic"],
    primary_for:["Biographic","Archaeological"],
    repos:["OPENALEX_WORKS","PERSEUS","OPEN_LIBRARY","JSTOR_SEARCH","EUROPEANA","INTERNET_ARCHIVE","HATHI_TRUST"] },

  { qid:"Q476294",  label:"oriental studies",
    in_graph:true, needs_harvest:false,
    oa_id:"C2779756990", lcsh:"sh85095636", lcc:"DS",
    facets:["Diplomatic","Cultural","Linguistic","Geographic"],
    primary_for:[],
    repos:["OPENALEX_WORKS","OPEN_LIBRARY","JSTOR_SEARCH","WORLDCAT","HATHI_TRUST"] },

  { qid:"Q26425130",label:"mycenology",
    in_graph:true, needs_harvest:false,
    oa_id:"C2781042235", lcsh:"sh85088892", lcc:"DF220",
    facets:["Archaeological","Linguistic","Cultural"],
    primary_for:["Archaeological"],
    repos:["OPENALEX_WORKS","JSTOR_SEARCH","OPEN_LIBRARY","WORLDCAT"] },
];

// ── FACET DEFINITIONS — 18 agents, every discipline mapped ────────────────────
const FACETS = [
  { label:"Political",     color:C.navy,    icon:"⚖",
    description:"Power structures, governance, constitutional forms, elections, magistracies, legislation, statecraft.",
    primary_disciplines:["political science","history of ancient Rome","ancient history","jurisprudence","public administration","comparative politics","political philosophy"],
    supporting_disciplines:["sociology","rhetoric","military history","international relations","history of religion","mass communication","economics"],
    sca_signals:["P31=Q3024240","P31=Q1307214","POSITION_HELD","CITIZEN_OF","HAS_SIGNIFICANT_EVENT→legislation"] },

  { label:"Military",      color:C.crimson, icon:"⚔",
    description:"Warfare, armies, generals, sieges, battles, fortifications, strategy, logistics, weapons.",
    primary_disciplines:["military history","military science","history of ancient Rome","ancient history","history of technology"],
    supporting_disciplines:["political science","geography","archaeology","history of science","environmental history"],
    sca_signals:["FOUGHT_IN","BATTLE_PARTICIPANT","DEFEATED","CONQUERED","BESIEGED","entity_type=EVENT+battle"] },

  { label:"Economic",      color:C.amber,   icon:"⚖",
    description:"Trade, currency, taxation, agriculture, labour, commerce, property, wealth distribution.",
    primary_disciplines:["economics","economic history","numismatics","trade","history of ancient Rome"],
    supporting_disciplines:["social history","demography","geography","archaeology","environmental history","political science"],
    sca_signals:["P31=Q4917→coin","PRODUCED","numismatic entity","trade route","economic text in corpus"] },

  { label:"Social",        color:C.teal,    icon:"👥",
    description:"Class structure, slavery, family, gender, daily life, customs, social mobility, patronage.",
    primary_disciplines:["sociology","social history","anthropology","prosopography","demography","history of ancient Rome"],
    supporting_disciplines:["cultural history","religious studies","economics","archaeology","linguistics"],
    sca_signals:["MEMBER_OF→social class","SLAVE/FREEDMAN status","PATRON_OF","family structure edges"] },

  { label:"Cultural",      color:C.purple,  icon:"🎭",
    description:"Values, customs, festivals, entertainment, spectacle, identity, acculturation, cultural exchange.",
    primary_disciplines:["cultural history","anthropology","classical studies","art history","history of ancient Rome"],
    supporting_disciplines:["religious studies","linguistics","mass communication","social history","archaeology"],
    sca_signals:["cultural entity in corpus","festival","LIVED_IN→cultural region","P31=cultural practice"] },

  { label:"Biographic",    color:C.rose,    icon:"📜",
    description:"Individual life histories, careers, prosopography, onomastics, family relationships.",
    primary_disciplines:["prosopography","biography","genealogy","onomastics","ancient history","classical philology"],
    supporting_disciplines:["political science","military history","archaeology","linguistics","social history"],
    sca_signals:["entity_type=PERSON","FATHER_OF","MOTHER_OF","POSITION_HELD","BORN_IN_YEAR","DIED_IN_YEAR"] },

  { label:"Diplomatic",    color:C.cyan,    icon:"🤝",
    description:"Treaties, alliances, embassies, foreign relations, negotiation, client kingdoms.",
    primary_disciplines:["international relations","comparative politics","history of ancient Rome","ancient history"],
    supporting_disciplines:["political science","military history","economics","rhetoric","geography"],
    sca_signals:["ALLIED_WITH","TREATY edge","DECLARED_FOR","diplomatic entity in corpus","client kingdom"] },

  { label:"Geographic",    color:C.lime,    icon:"🗺",
    description:"Territories, regions, provinces, roads, rivers, topography, cartography, spatial analysis.",
    primary_disciplines:["historical geography","geography","environmental history","classical archaeology"],
    supporting_disciplines:["military history","demography","economics","environmental science","ancient history"],
    sca_signals:["entity_type=PLACE","pleiades_id","LOCATED_IN","HAD_CAPITAL","P31=Q3024240","geographic text"] },

  { label:"Archaeological", color:C.orange, icon:"⛏",
    description:"Material evidence, excavations, artefacts, stratigraphy, archaeometry, numismatics, epigraphy.",
    primary_disciplines:["archaeology","classical archaeology","etruscology","papyrology","numismatics","epigraphy"],
    supporting_disciplines:["art history","environmental science","historical geography","geology","ancient history"],
    sca_signals:["pleiades_id","getty_aat_id","inscriptions","coin entity","EVIDENCED_BY","archaeological site"] },

  { label:"Religious",     color:C.gold,    icon:"🏛",
    description:"Cults, temples, priesthoods, divination, ritual, theology, religious law, syncretism.",
    primary_disciplines:["religious studies","history of religion","mythology","classical studies","anthropology"],
    supporting_disciplines:["art history","archaeology","linguistics","political science","social history"],
    sca_signals:["ADHERES_TO→religion","temple entity","PRIEST role","ritual event","P31=Q207694→temple"] },

  { label:"Intellectual",  color:C.navy,    icon:"📚",
    description:"Philosophy, science, literature, scholarship, education, rhetoric, ideas, knowledge transmission.",
    primary_disciplines:["classics","classical philology","political philosophy","history of science","study of history"],
    supporting_disciplines:["linguistics","religious studies","art history","rhetoric","mass communication"],
    sca_signals:["AUTHOR","WROTE","WORK_OF","philosophical text","DESCRIBES→intellectual concept"] },

  { label:"Linguistic",    color:C.teal,    icon:"📝",
    description:"Latin language, inscriptions, manuscripts, texts, vocabulary, grammar, script, papyri.",
    primary_disciplines:["linguistics","philology","epigraphy","classical philology","onomastics","paleography"],
    supporting_disciplines:["classics","archaeology","cultural history","mass communication","rhetoric"],
    sca_signals:["inscribed entity","lcsh heading for language","text corpus node","P31=Q1490→manuscript"] },

  { label:"Artistic",      color:C.purple,  icon:"🎨",
    description:"Visual arts, sculpture, painting, architecture, coins, gems, decorative arts, aesthetics.",
    primary_disciplines:["art history","classical archaeology","iconography","aesthetics","numismatics"],
    supporting_disciplines:["cultural history","religious studies","etruscology","archaeology","history of technology"],
    sca_signals:["getty_aat_id","EUROPEANA entity","P31=Q3305213→painting","P31=Q860861→sculpture"] },

  { label:"Demographic",   color:C.green,   icon:"👤",
    description:"Population size, migration, mortality, fertility, census, ethnicity, urbanisation.",
    primary_disciplines:["demography","social history","historical geography","sociology","ancient history"],
    supporting_disciplines:["economics","environmental history","medical history","anthropology","cultural history"],
    sca_signals:["census data node","MIGRATED_FROM","MIGRATED_TO","population estimate","demographic text"] },

  { label:"Environmental", color:C.lime,    icon:"🌿",
    description:"Climate, agriculture, land use, resources, disease, natural disaster, ecology.",
    primary_disciplines:["environmental history","environmental science","geology","human ecology","historical geography"],
    supporting_disciplines:["demography","economics","military history","archaeology","biology"],
    sca_signals:["climate entity","agricultural entity","disaster event","LOCATED_IN→geographic region","geology node"] },

  { label:"Communication", color:C.orange,  icon:"📡",
    description:"Oratory, written communication, propaganda, public records, law publication, information networks.",
    primary_disciplines:["mass communication","rhetoric","media studies","propaganda","classical philology"],
    supporting_disciplines:["linguistics","political science","cultural history","social history","archaeology"],
    sca_signals:["AUTHOR→speech/letter","P31=Q49848→letter","rhetorical text","public record entity"] },

  { label:"Scientific",    color:C.cyan,    icon:"🔬",
    description:"Natural philosophy, medicine, mathematics, astronomy, engineering knowledge.",
    primary_disciplines:["history of science","medicine","biology","physics","study of history"],
    supporting_disciplines:["history of technology","environmental science","philosophy","ancient history","classics"],
    sca_signals:["scientific text in corpus","mathematical entity","medical text","DESCRIBED_BY→scientific work"] },

  { label:"Technological", color:C.slate,   icon:"⚙",
    description:"Engineering, infrastructure, construction, weapons technology, hydraulics, road systems.",
    primary_disciplines:["history of technology","military science","classical archaeology","history of science"],
    supporting_disciplines:["environmental science","economics","military history","geography","engineering"],
    sca_signals:["aqueduct entity","P31=Q811979→architectural structure","road node","engineering text"] },
];

// SCA SELECTION RULE (declarative)
const SCA_RULE = {
  invocation:"ALL 18 facet agents are invoked for every entity entering the graph.",
  scoring:"Each agent scores its facet relevance 0.0–1.0 based on: P31 types match, relationship types present, authority IDs held, discipline connections, corpus temporal/geographic fit.",
  primary_selection:"SCA assigns PRIMARY facet = argmax(agent_scores). Ties broken by: (1) most specific P31 type match, (2) highest authority ID coverage, (3) strongest relationship density.",
  secondary_assignment:"All facets with score ≥ SYS_Threshold:secondary_facet_confidence remain active as co-assignments. Encoded in capability_cipher.",
  threshold_key:"SYS_Threshold:secondary_facet_confidence",
  example:{
    entity:"Roman Republic (Q17167)",
    all_scores:{ Political:0.97, Military:0.85, Geographic:0.72, Economic:0.61, Diplomatic:0.78, Social:0.55 },
    primary:"Political (0.97)",
    secondary:["Military","Diplomatic","Geographic","Economic"],
    below_threshold:["Social","Cultural","Biographic","Religious","Artistic","Archaeological","Intellectual","Linguistic","Demographic","Environmental","Communication","Scientific","Technological"],
  }
};

// ══════════════════════════════════════════════════════════════════════════════
// UI
// ══════════════════════════════════════════════════════════════════════════════

function Tag({ label, fill, s=8 }) {
  return <span style={{background:fill+"18",border:`1px solid ${fill}`,borderRadius:10,
    padding:"1px 8px",fontSize:s,color:fill,fontWeight:"bold",whiteSpace:"nowrap",
    display:"inline-block",margin:1}}>{label}</span>;
}
function Mono({ children, col=C.teal }) {
  return <code style={{fontFamily:"monospace",color:col,fontSize:9.5,background:col+"12",
    padding:"1px 5px",borderRadius:3}}>{children}</code>;
}
function CopyBtn({ text }) {
  const [ok, setOk] = useState(false);
  return <button onClick={()=>{navigator.clipboard?.writeText(text);setOk(true);setTimeout(()=>setOk(false),1400);}}
    style={{background:ok?C.green:C.slate,color:"white",border:"none",borderRadius:3,
      padding:"1px 8px",fontSize:8,cursor:"pointer",fontWeight:"bold"}}>{ok?"✓":"copy"}</button>;
}
function PillStatus({ s }) {
  const col = s?"#1E6B3C":"#B45309";
  return <span style={{background:col+"18",border:`1px solid ${col}`,borderRadius:8,
    padding:"1px 7px",fontSize:7.5,color:col,fontWeight:"bold",letterSpacing:.5}}>
    {s?"IN GRAPH":"NEEDS HARVEST"}
  </span>;
}

// ── OVERVIEW ─────────────────────────────────────────────────────────────────
function Overview() {
  const inGraph = DISCIPLINES.filter(d=>d.in_graph).length;
  const needs   = DISCIPLINES.filter(d=>d.needs_harvest).length;
  return (
    <div>
      {/* counts */}
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:10,marginBottom:16}}>
        {[
          ["18","Facet Agents",C.navy,"all invoked per entity"],
          [DISCIPLINES.length,"Disciplines",C.purple,"mapped to facets"],
          [inGraph,"In Graph",C.green,"already harvested"],
          [needs,"Need Harvest",C.amber,"QID known, not yet in graph"],
        ].map(([n,l,col,sub])=>(
          <div key={l} style={{background:"white",border:`2px solid ${col}`,borderRadius:8,padding:12,textAlign:"center"}}>
            <div style={{fontSize:28,fontWeight:"bold",color:col}}>{n}</div>
            <div style={{fontSize:11,fontWeight:"bold",color:C.ink}}>{l}</div>
            <div style={{fontSize:9,color:C.dim}}>{sub}</div>
          </div>
        ))}
      </div>

      {/* SCA model */}
      <div style={{background:"white",border:`1.5px solid ${C.navy}`,borderRadius:8,padding:14,marginBottom:16}}>
        <div style={{fontWeight:"bold",color:C.navy,fontSize:12,marginBottom:10}}>
          Multi-Agent Invocation Model
        </div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:14}}>
          <div>
            {[["Invocation",SCA_RULE.invocation],
              ["Scoring",SCA_RULE.scoring],
              ["Primary Selection",SCA_RULE.primary_selection],
              ["Secondary Assignment",SCA_RULE.secondary_assignment],
            ].map(([k,v])=>(
              <div key={k} style={{marginBottom:8}}>
                <div style={{fontSize:8.5,fontWeight:"bold",color:C.dim,marginBottom:2}}>{k.toUpperCase()}</div>
                <div style={{fontSize:9.5,color:C.ink}}>{v}</div>
              </div>
            ))}
          </div>
          <div style={{background:"#F7F4EF",borderRadius:6,padding:10}}>
            <div style={{fontSize:9,fontWeight:"bold",color:C.dim,marginBottom:8}}>
              WORKED EXAMPLE — {SCA_RULE.example.entity}
            </div>
            <div style={{marginBottom:6}}>
              {Object.entries(SCA_RULE.example.all_scores)
                .sort((a,b)=>b[1]-a[1])
                .map(([f,sc])=>{
                  const isPrimary = f===SCA_RULE.example.primary.split(" ")[0];
                  const isSecondary = SCA_RULE.example.secondary.includes(f);
                  const barW = Math.round(sc*100);
                  return (
                    <div key={f} style={{display:"flex",alignItems:"center",gap:6,marginBottom:3}}>
                      <span style={{fontSize:9,width:70,color:isPrimary?C.navy:isSecondary?C.teal:C.dim,
                        fontWeight:isPrimary?"bold":"normal"}}>{f}</span>
                      <div style={{flex:1,height:8,background:"#E5E7EB",borderRadius:4,overflow:"hidden"}}>
                        <div style={{width:`${barW}%`,height:"100%",
                          background:isPrimary?C.navy:isSecondary?C.teal:C.dim,
                          borderRadius:4,opacity:isPrimary?1:isSecondary?.7:.3}}/>
                      </div>
                      <span style={{fontSize:9,fontFamily:"monospace",color:C.dim,width:28}}>{sc.toFixed(2)}</span>
                      {isPrimary&&<Tag label="PRIMARY" fill={C.navy}/>}
                      {isSecondary&&<Tag label="2°" fill={C.teal}/>}
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
      </div>

      {/* repo index summary */}
      <div style={{background:"white",border:`1.5px solid ${C.purple}`,borderRadius:8,padding:14}}>
        <div style={{fontWeight:"bold",color:C.purple,fontSize:12,marginBottom:10}}>
          Repository Endpoints ({Object.keys(REPOS).length} sources)
        </div>
        <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8}}>
          {Object.entries(REPOS).map(([k,r])=>(
            <div key={k} style={{borderLeft:`3px solid ${r.color}`,paddingLeft:8}}>
              <div style={{fontSize:10,fontWeight:"bold",color:r.color}}>{r.name}</div>
              <div style={{fontSize:8.5,color:C.slate,marginBottom:3}}>{r.desc}</div>
              <Mono col={C.dim}>{r.url.replace("https://","").split("/")[0]}</Mono>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── DISCIPLINE UNIVERSE ───────────────────────────────────────────────────────
function DisciplineUniverse() {
  const [search, setSearch] = useState("");
  const [filterFacet, setFilterFacet] = useState("ALL");
  const [filterStatus, setFilterStatus] = useState("ALL");
  const [open, setOpen] = useState(null);

  const filtered = useMemo(()=>
    DISCIPLINES.filter(d=>{
      const matchSearch = !search || d.label.toLowerCase().includes(search.toLowerCase());
      const matchFacet  = filterFacet==="ALL" || d.facets.includes(filterFacet) || d.primary_for.includes(filterFacet);
      const matchStatus = filterStatus==="ALL"
        || (filterStatus==="in_graph" && d.in_graph)
        || (filterStatus==="needs_harvest" && d.needs_harvest);
      return matchSearch && matchFacet && matchStatus;
    }),[search,filterFacet,filterStatus]);

  return (
    <div>
      {/* controls */}
      <div style={{display:"flex",gap:8,marginBottom:12,flexWrap:"wrap",alignItems:"center"}}>
        <input value={search} onChange={e=>setSearch(e.target.value)}
          placeholder="Search disciplines…"
          style={{border:`1px solid ${C.rule}`,borderRadius:6,padding:"4px 10px",
            fontSize:10,fontFamily:"inherit",flex:"0 0 160px"}}/>
        <select value={filterFacet} onChange={e=>setFilterFacet(e.target.value)}
          style={{border:`1px solid ${C.rule}`,borderRadius:6,padding:"4px 8px",fontSize:10,fontFamily:"inherit"}}>
          <option value="ALL">All Facets</option>
          {FACETS.map(f=><option key={f.label} value={f.label}>{f.icon} {f.label}</option>)}
        </select>
        {["ALL","in_graph","needs_harvest"].map(s=>(
          <button key={s} onClick={()=>setFilterStatus(s)}
            style={{border:`1px solid ${filterStatus===s?C.navy:C.rule}`,
              background:filterStatus===s?C.navy:"white",
              color:filterStatus===s?"white":C.slate,
              borderRadius:12,padding:"3px 12px",fontSize:9,cursor:"pointer",fontWeight:"bold"}}>
            {s==="ALL"?"All":s==="in_graph"?"In Graph":"Needs Harvest"}
            {" "}({s==="ALL"?DISCIPLINES.length:DISCIPLINES.filter(d=>d[s]).length})
          </button>
        ))}
      </div>
      <div style={{fontSize:10,color:C.dim,marginBottom:8}}>{filtered.length} disciplines shown</div>

      {filtered.map(d=>(
        <div key={d.qid} style={{border:`1px solid ${C.rule}`,borderRadius:6,marginBottom:6,overflow:"hidden",
          borderLeft:`3px solid ${d.in_graph?C.green:C.amber}`}}>
          <div onClick={()=>setOpen(open===d.qid?null:d.qid)}
            style={{padding:"7px 12px",cursor:"pointer",background:"white",
              display:"flex",alignItems:"center",gap:10,flexWrap:"wrap"}}>
            <PillStatus s={d.in_graph}/>
            <Mono col={C.slate}>{d.qid}</Mono>
            <span style={{fontWeight:"bold",color:C.ink,fontSize:11}}>{d.label}</span>
            <Mono col={C.amber}>{d.lcc}</Mono>
            <div style={{display:"flex",gap:2,flexWrap:"wrap",flex:1}}>
              {d.primary_for.map(f=>{
                const fc = FACETS.find(x=>x.label===f);
                return <Tag key={f} label={`★ ${f}`} fill={fc?.color||C.navy}/>;
              })}
            </div>
            <span style={{fontSize:9,color:C.dim}}>{d.facets.length} facets · {d.repos.length} repos · {open===d.qid?"▲":"▼"}</span>
          </div>
          {open===d.qid && (
            <div style={{borderTop:`1px solid ${C.rule}`,background:"#FAFAF8",
              padding:"10px 12px",display:"grid",gridTemplateColumns:"1fr 1fr",gap:14}}>
              <div>
                <div style={{fontSize:8.5,fontWeight:"bold",color:C.dim,marginBottom:6}}>FACETS SERVED</div>
                <div style={{display:"flex",flexWrap:"wrap",gap:3,marginBottom:10}}>
                  {d.facets.map(f=>{
                    const fc = FACETS.find(x=>x.label===f);
                    const isPrimary = d.primary_for.includes(f);
                    return <Tag key={f} label={isPrimary?`★ ${f}`:f} fill={fc?.color||C.slate} s={8}/>;
                  })}
                </div>
                <div style={{display:"flex",gap:16,marginBottom:10}}>
                  {d.lcsh&&<div>
                    <div style={{fontSize:8,color:C.dim,marginBottom:2}}>LCSH</div>
                    <Mono col={C.purple}>{d.lcsh}</Mono>
                  </div>}
                  {d.oa_id&&<div>
                    <div style={{fontSize:8,color:C.dim,marginBottom:2}}>OpenAlex</div>
                    <Mono col={C.teal}>{d.oa_id}</Mono>
                  </div>}
                </div>
                {!d.in_graph&&<div style={{background:C.amber+"12",border:`1px solid ${C.amber}`,
                  borderRadius:4,padding:"5px 8px",fontSize:9}}>
                  <strong style={{color:C.amber}}>Harvest needed: </strong>
                  QID {d.qid} — add via P31=Q11862829 discipline harvest pipeline
                </div>}
              </div>
              <div>
                <div style={{fontSize:8.5,fontWeight:"bold",color:C.dim,marginBottom:6}}>
                  REPOSITORY ENDPOINTS ({d.repos.length})
                </div>
                {d.repos.map(rk=>{
                  const r = REPOS[rk];
                  const url = r.url
                    .replace("{oa_id}",d.oa_id||"")
                    .replace("{lcsh}",d.lcsh||"")
                    .replace("{slug}",d.label.toLowerCase().replace(/\s+/g,"-"))
                    .replace("{label}",encodeURIComponent(d.label));
                  return (
                    <div key={rk} style={{marginBottom:5,borderLeft:`2px solid ${r.color}`,paddingLeft:6}}>
                      <div style={{display:"flex",alignItems:"center",gap:5,marginBottom:1}}>
                        <span style={{fontSize:9,fontWeight:"bold",color:r.color}}>{r.name}</span>
                        <CopyBtn text={url}/>
                      </div>
                      <div style={{fontFamily:"monospace",fontSize:7.5,color:C.dim,wordBreak:"break-all"}}>{url}</div>
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

// ── BY FACET ─────────────────────────────────────────────────────────────────
function ByFacet() {
  const [sel, setSel] = useState("Political");
  const facet = FACETS.find(f=>f.label===sel);
  const primaryDiscs  = DISCIPLINES.filter(d=>d.primary_for.includes(sel));
  const supportDiscs  = DISCIPLINES.filter(d=>d.facets.includes(sel)&&!d.primary_for.includes(sel));

  // collect all unique repos across all disciplines for this facet
  const allRepos = [...new Set([
    ...primaryDiscs.flatMap(d=>d.repos),
    ...supportDiscs.flatMap(d=>d.repos),
  ])];

  return (
    <div style={{display:"grid",gridTemplateColumns:"180px 1fr",gap:12}}>
      {/* sidebar */}
      <div>
        {FACETS.map(f=>(
          <div key={f.label} onClick={()=>setSel(f.label)}
            style={{padding:"6px 10px",cursor:"pointer",borderRadius:5,marginBottom:3,
              background:sel===f.label?f.color:"white",
              border:`1.5px solid ${sel===f.label?f.color:C.rule}`,
              color:sel===f.label?"white":C.ink,fontSize:10,fontWeight:sel===f.label?"bold":"normal",
              display:"flex",alignItems:"center",gap:6}}>
            <span>{f.icon}</span>
            <span>{f.label}</span>
          </div>
        ))}
      </div>

      {/* content */}
      <div>
        <div style={{background:facet.color,borderRadius:8,padding:12,marginBottom:12,color:"white"}}>
          <div style={{fontSize:18,fontWeight:"bold",marginBottom:4}}>
            {facet.icon} {facet.label} Facet Agent
          </div>
          <div style={{fontSize:10,opacity:.85}}>{facet.description}</div>
        </div>

        {/* SCA signals */}
        <div style={{background:"white",border:`1px solid ${C.rule}`,borderRadius:6,
          padding:10,marginBottom:12}}>
          <div style={{fontSize:9,fontWeight:"bold",color:C.dim,marginBottom:5}}>SCA RELEVANCE SIGNALS</div>
          <div style={{display:"flex",flexWrap:"wrap",gap:4}}>
            {facet.sca_signals.map(s=><Mono key={s} col={facet.color}>{s}</Mono>)}
          </div>
        </div>

        {/* primary disciplines */}
        <div style={{marginBottom:12}}>
          <div style={{fontSize:10,fontWeight:"bold",color:C.ink,marginBottom:6}}>
            PRIMARY disciplines ({primaryDiscs.length}) — this facet is the academic home
          </div>
          {primaryDiscs.length===0
            ? <div style={{fontSize:9.5,color:C.dim,fontStyle:"italic"}}>
                This facet draws equally from history and cross-cutting disciplines.
              </div>
            : primaryDiscs.map(d=>(
              <div key={d.qid} style={{borderLeft:`4px solid ${facet.color}`,paddingLeft:10,
                marginBottom:8,background:"white",padding:"8px 10px",borderRadius:"0 6px 6px 0"}}>
                <div style={{display:"flex",gap:8,alignItems:"center",flexWrap:"wrap",marginBottom:4}}>
                  <PillStatus s={d.in_graph}/>
                  <Mono col={C.slate}>{d.qid}</Mono>
                  <span style={{fontWeight:"bold",color:C.ink,fontSize:11}}>{d.label}</span>
                  <Mono col={C.amber}>{d.lcc}</Mono>
                </div>
                <div style={{display:"flex",flexWrap:"wrap",gap:3}}>
                  {d.repos.map(rk=>(
                    <span key={rk} style={{fontSize:8,background:REPOS[rk].color+"15",
                      border:`1px solid ${REPOS[rk].color}`,borderRadius:10,
                      padding:"1px 7px",color:REPOS[rk].color}}>{REPOS[rk].name}</span>
                  ))}
                </div>
              </div>
            ))
          }
        </div>

        {/* supporting */}
        <div style={{marginBottom:12}}>
          <div style={{fontSize:10,fontWeight:"bold",color:C.ink,marginBottom:6}}>
            SUPPORTING disciplines ({supportDiscs.length}) — contextual coverage
          </div>
          <div style={{display:"flex",flexWrap:"wrap",gap:6}}>
            {supportDiscs.map(d=>(
              <div key={d.qid} style={{background:"white",border:`1px solid ${C.rule}`,
                borderRadius:5,padding:"4px 8px",fontSize:9}}>
                <PillStatus s={d.in_graph}/>{" "}
                <span style={{fontWeight:"bold"}}>{d.label}</span>
                {" "}<Mono col={C.amber}>{d.lcc}</Mono>
              </div>
            ))}
          </div>
        </div>

        {/* consolidated repo list for this facet */}
        <div style={{background:"white",border:`1px solid ${C.rule}`,borderRadius:6,padding:10}}>
          <div style={{fontSize:10,fontWeight:"bold",color:C.ink,marginBottom:8}}>
            ALL REPOSITORY ENDPOINTS for {facet.label} agent ({allRepos.length} sources)
          </div>
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:6}}>
            {allRepos.map(rk=>{
              const r = REPOS[rk];
              return (
                <div key={rk} style={{borderLeft:`2px solid ${r.color}`,paddingLeft:6}}>
                  <span style={{fontSize:9,fontWeight:"bold",color:r.color}}>{r.name}</span>
                  <div style={{fontSize:8,color:C.slate}}>{r.desc}</div>
                  <div style={{fontFamily:"monospace",fontSize:7.5,color:C.dim,wordBreak:"break-all"}}>{r.url}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── REPOSITORY INDEX ──────────────────────────────────────────────────────────
function RepoIndex() {
  return (
    <div>
      <div style={{fontSize:10,color:C.slate,marginBottom:12,background:"white",
        border:`1px solid ${C.rule}`,borderRadius:6,padding:10}}>
        Every discipline repository endpoint. URL templates use{" "}
        <Mono>{"{oa_id}"}</Mono>, <Mono>{"{lcsh}"}</Mono>, <Mono>{"{slug}"}</Mono>,{" "}
        <Mono>{"{label}"}</Mono> as substitution parameters.
        Agents resolve these from the discipline node's stored properties before calling.
        All fetches must be logged as <Mono col={C.amber}>:RetrievalContext</Mono> nodes.
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
        {Object.entries(REPOS).map(([k,r])=>(
          <div key={k} style={{background:"white",border:`1.5px solid ${r.color}33`,
            borderLeft:`4px solid ${r.color}`,borderRadius:5,padding:12}}>
            <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:6}}>
              <span style={{fontWeight:"bold",color:r.color,fontSize:12}}>{r.name}</span>
              <CopyBtn text={r.url}/>
            </div>
            <div style={{fontSize:9,color:C.slate,marginBottom:6}}>{r.desc}</div>
            <div style={{fontFamily:"monospace",fontSize:8.5,color:C.dim,
              background:"#F5F5F0",borderRadius:3,padding:"4px 8px",wordBreak:"break-all"}}>
              {r.url}
            </div>
            <div style={{marginTop:6,fontSize:8.5,color:C.dim}}>
              Used by: {DISCIPLINES.filter(d=>d.repos.includes(k)).length} disciplines
            </div>
          </div>
        ))}
      </div>

      {/* harvest priority queue */}
      <div style={{marginTop:16,background:"white",border:`1.5px solid ${C.amber}`,
        borderRadius:8,padding:12}}>
        <div style={{fontWeight:"bold",color:C.amber,fontSize:12,marginBottom:10}}>
          Harvest Priority Queue — {DISCIPLINES.filter(d=>d.needs_harvest).length} disciplines not yet in graph
        </div>
        <div style={{fontSize:9,color:C.slate,marginBottom:8}}>
          These disciplines have known Wikidata QIDs and must be added via the discipline harvest pipeline
          (P31=Q11862829). Order by facet coverage count descending — disciplines serving more facets first.
        </div>
        <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:6}}>
          {DISCIPLINES
            .filter(d=>d.needs_harvest)
            .sort((a,b)=>b.facets.length-a.facets.length)
            .map(d=>(
              <div key={d.qid} style={{border:`1px solid ${C.rule}`,borderRadius:4,
                padding:"5px 8px",fontSize:9}}>
                <div style={{display:"flex",gap:5,alignItems:"center",marginBottom:2}}>
                  <Mono col={C.amber}>{d.qid}</Mono>
                  <span style={{fontWeight:"bold",color:C.ink}}>{d.label}</span>
                </div>
                <div style={{color:C.dim}}>
                  {d.facets.length} facets · LCC {d.lcc}
                  {d.primary_for.length>0&&<span style={{color:C.crimson}}> · PRIMARY for {d.primary_for.join(", ")}</span>}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

// ── ROOT ─────────────────────────────────────────────────────────────────────
export default function DisciplineUniverse_Root() {
  const [view, setView] = useState("overview");
  const VIEWS = [
    ["overview",    "Overview"],
    ["disciplines", `All Disciplines (${DISCIPLINES.length})`],
    ["by_facet",    "By Facet"],
    ["repos",       `Repository Index (${Object.keys(REPOS).length})`],
  ];
  return (
    <div style={{fontFamily:"Georgia,'Times New Roman',serif",background:"#F7F4EF",minHeight:"100vh",padding:16}}>
      <div style={{borderBottom:`2px solid ${C.ink}`,paddingBottom:10,marginBottom:14}}>
        <div style={{display:"flex",alignItems:"baseline",gap:12,flexWrap:"wrap"}}>
          <span style={{fontSize:11,fontWeight:"bold",color:C.dim,letterSpacing:3,
            textTransform:"uppercase",fontFamily:"Arial,sans-serif"}}>CHRYSTALLUM</span>
          <span style={{fontSize:16,fontWeight:"bold",color:C.ink}}>
            Complete Discipline Universe & Repository Index
          </span>
          <span style={{color:C.dim,fontSize:9,marginLeft:"auto",fontFamily:"Arial,sans-serif"}}>
            18 Facet Agents · {DISCIPLINES.length} Disciplines · {Object.keys(REPOS).length} Repository Sources
          </span>
        </div>
        <div style={{fontSize:10,color:C.slate,marginTop:4,fontStyle:"italic",fontFamily:"Arial,sans-serif"}}>
          All facet agents invoked per entity. SCA assigns primary. Every discipline has an addressable
          repository chain for agent training material.
        </div>
      </div>

      <div style={{display:"flex",gap:0,marginBottom:14,borderBottom:`2px solid ${C.ink}`,
        fontFamily:"Arial,sans-serif"}}>
        {VIEWS.map(([k,l])=>(
          <button key={k} onClick={()=>setView(k)} style={{
            border:"none",padding:"7px 16px",fontSize:10,cursor:"pointer",background:"transparent",
            fontWeight:view===k?"bold":"normal",color:view===k?C.ink:C.dim,
            borderBottom:view===k?`3px solid ${C.ink}`:"3px solid transparent",letterSpacing:.4,
          }}>{l}</button>
        ))}
      </div>

      {view==="overview"    && <Overview/>}
      {view==="disciplines" && <DisciplineUniverse/>}
      {view==="by_facet"    && <ByFacet/>}
      {view==="repos"       && <RepoIndex/>}
    </div>
  );
}
