// Fix gen and praenomen labels (Ser. = Servius not Sergius; gens prefix -> full Latin)
// Run after: create_onomastic_nodes.py has created Gens/Praenomen nodes

// 1. Praenomen: Ser. -> Servius (was wrongly Sergius)
MATCH (p:Praenomen {praenomen_id: "Ser."})
WHERE p.label_latin = "Sergius"
SET p.label_latin = "Servius";

// 2. Gens: prefix -> full Latin gens name
UNWIND [
  {gens_id: "POMP", label_latin: "Pompeia"},
  {gens_id: "CORN", label_latin: "Cornelia"},
  {gens_id: "IVLI", label_latin: "Iulia"},
  {gens_id: "TULL", label_latin: "Tullia"},
  {gens_id: "CICER", label_latin: "Tullia"},
  {gens_id: "ANTO", label_latin: "Antonia"},
  {gens_id: "CASS", label_latin: "Cassia"},
  {gens_id: "CLAU", label_latin: "Claudia"},
  {gens_id: "FABI", label_latin: "Fabia"},
  {gens_id: "LICI", label_latin: "Licinia"},
  {gens_id: "LIVI", label_latin: "Livia"},
  {gens_id: "MARC", label_latin: "Marcia"},
  {gens_id: "SEMP", label_latin: "Sempronia"},
  {gens_id: "SERV", label_latin: "Servilia"},
  {gens_id: "SULP", label_latin: "Sulpicia"},
  {gens_id: "TERE", label_latin: "Terentia"},
  {gens_id: "VALE", label_latin: "Valeria"}
] AS row
MATCH (g:Gens {gens_id: row.gens_id})
SET g.label_latin = row.label_latin;
