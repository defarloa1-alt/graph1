// DPRR Bibliography Source Nodes
// Run before dprr_import.py so provenance properties can reference these nodes.
// See docs/IMPORT_DECISIONS.md

MERGE (dprr:BibliographySource {
  id: "DPRR",
  label: "Digital Prosopography of the Roman Republic",
  uri: "http://romanrepublic.ac.uk",
  institution: "King's College London",
  date: 2017,
  license: "MIT",
  editor: "Mouritsen, Henrik",
  backbone_source: "Broughton_MRR"
})

MERGE (zmeskal:BibliographySource {
  id: "Zmeskal_Adfinitas",
  label: "Adfinitas: Die Verwandtschaftsbeziehungen der Nobilität",
  editor: "Zmeskal, Klaus"
})

MERGE (broughton:BibliographySource {
  id: "Broughton_MRR",
  label: "The Magistrates of the Roman Republic",
  editor: "Broughton, T.R.S."
})

RETURN dprr, zmeskal, broughton;
