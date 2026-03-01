// LCSH BROADER_THAN edges for Discipline nodes
// Run after loading discipline_majors_mapped.csv
// (parent)-[:BROADER_THAN]->(child) means parent is broader than child

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2009006799' OR child.lcsh_id STARTS WITH 'sh2009006799|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2020000052' OR parent.lcsh_id STARTS WITH 'sh2020000052|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85004336' OR child.lcsh_id STARTS WITH 'sh85004336|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85140372' OR parent.lcsh_id STARTS WITH 'sh85140372|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006306' OR child.lcsh_id STARTS WITH 'sh85006306|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119961' OR parent.lcsh_id STARTS WITH 'sh85119961|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006314' OR child.lcsh_id STARTS WITH 'sh85006314|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh92005350' OR parent.lcsh_id STARTS WITH 'sh92005350|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006314' OR child.lcsh_id STARTS WITH 'sh85006314|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090516' OR parent.lcsh_id STARTS WITH 'sh85090516|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006314' OR child.lcsh_id STARTS WITH 'sh85006314|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh92006288' OR parent.lcsh_id STARTS WITH 'sh92006288|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006333' OR child.lcsh_id STARTS WITH 'sh85006333|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006314' OR parent.lcsh_id STARTS WITH 'sh85006314|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008742' OR child.lcsh_id STARTS WITH 'sh85008742|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065698' OR parent.lcsh_id STARTS WITH 'sh85065698|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008742' OR child.lcsh_id STARTS WITH 'sh85008742|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85011526' OR parent.lcsh_id STARTS WITH 'sh85011526|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008742' OR child.lcsh_id STARTS WITH 'sh85008742|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85013560' OR parent.lcsh_id STARTS WITH 'sh85013560|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008742' OR child.lcsh_id STARTS WITH 'sh85008742|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85064932' OR parent.lcsh_id STARTS WITH 'sh85064932|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85010772' OR child.lcsh_id STARTS WITH 'sh85010772|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85036481' OR parent.lcsh_id STARTS WITH 'sh85036481|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92005509' OR child.lcsh_id STARTS WITH 'sh92005509|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015918' OR parent.lcsh_id STARTS WITH 'sh85015918|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92005509' OR child.lcsh_id STARTS WITH 'sh92005509|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85030761' OR parent.lcsh_id STARTS WITH 'sh85030761|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92005509' OR child.lcsh_id STARTS WITH 'sh92005509|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85130598' OR parent.lcsh_id STARTS WITH 'sh85130598|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85017454' OR child.lcsh_id STARTS WITH 'sh85017454|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85112599' OR parent.lcsh_id STARTS WITH 'sh85112599|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85018133' OR child.lcsh_id STARTS WITH 'sh85018133|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85135233' OR parent.lcsh_id STARTS WITH 'sh85135233|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85022218' OR child.lcsh_id STARTS WITH 'sh85022218|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080259' OR parent.lcsh_id STARTS WITH 'sh85080259|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85024301' OR child.lcsh_id STARTS WITH 'sh85024301|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85122925' OR parent.lcsh_id STARTS WITH 'sh85122925|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85025009' OR child.lcsh_id STARTS WITH 'sh85025009|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005757' OR parent.lcsh_id STARTS WITH 'sh85005757|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85025009' OR child.lcsh_id STARTS WITH 'sh85025009|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85013580' OR parent.lcsh_id STARTS WITH 'sh85013580|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85134665' OR child.lcsh_id STARTS WITH 'sh85134665|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85025219' OR parent.lcsh_id STARTS WITH 'sh85025219|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035731' OR child.lcsh_id STARTS WITH 'sh85035731|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85117963' OR parent.lcsh_id STARTS WITH 'sh85117963|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040106' OR child.lcsh_id STARTS WITH 'sh85040106|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054438' OR parent.lcsh_id STARTS WITH 'sh85054438|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040468' OR child.lcsh_id STARTS WITH 'sh85040468|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh92004048' OR parent.lcsh_id STARTS WITH 'sh92004048|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040468' OR child.lcsh_id STARTS WITH 'sh85040468|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89005705' OR parent.lcsh_id STARTS WITH 'sh89005705|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040605' OR child.lcsh_id STARTS WITH 'sh85040605|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85025193' OR parent.lcsh_id STARTS WITH 'sh85025193|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041367' OR child.lcsh_id STARTS WITH 'sh85041367|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh98004353' OR parent.lcsh_id STARTS WITH 'sh98004353|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85043413' OR child.lcsh_id STARTS WITH 'sh85043413|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054438' OR parent.lcsh_id STARTS WITH 'sh85054438|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85043929' OR child.lcsh_id STARTS WITH 'sh85043929|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054442' OR parent.lcsh_id STARTS WITH 'sh85054442|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85043777' OR child.lcsh_id STARTS WITH 'sh85043777|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85016973' OR parent.lcsh_id STARTS WITH 'sh85016973|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85051829' OR child.lcsh_id STARTS WITH 'sh85051829|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85114953' OR parent.lcsh_id STARTS WITH 'sh85114953|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85051865' OR child.lcsh_id STARTS WITH 'sh85051865|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89004004' OR parent.lcsh_id STARTS WITH 'sh89004004|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054365' OR child.lcsh_id STARTS WITH 'sh85054365|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054438' OR parent.lcsh_id STARTS WITH 'sh85054438|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054411' OR child.lcsh_id STARTS WITH 'sh85054411|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054442' OR parent.lcsh_id STARTS WITH 'sh85054442|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054380' OR child.lcsh_id STARTS WITH 'sh85054380|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89006411' OR parent.lcsh_id STARTS WITH 'sh89006411|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054413' OR child.lcsh_id STARTS WITH 'sh85054413|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054380' OR parent.lcsh_id STARTS WITH 'sh85054380|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054723' OR child.lcsh_id STARTS WITH 'sh85054723|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85031235' OR parent.lcsh_id STARTS WITH 'sh85031235|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054723' OR child.lcsh_id STARTS WITH 'sh85054723|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85041430' OR parent.lcsh_id STARTS WITH 'sh85041430|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054723' OR child.lcsh_id STARTS WITH 'sh85054723|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85072732' OR parent.lcsh_id STARTS WITH 'sh85072732|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054723' OR child.lcsh_id STARTS WITH 'sh85054723|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85099708' OR parent.lcsh_id STARTS WITH 'sh85099708|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054723' OR child.lcsh_id STARTS WITH 'sh85054723|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054723' OR child.lcsh_id STARTS WITH 'sh85054723|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85120047' OR parent.lcsh_id STARTS WITH 'sh85120047|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85057151' OR child.lcsh_id STARTS WITH 'sh85057151|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026704' OR parent.lcsh_id STARTS WITH 'sh85026704|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85057151' OR child.lcsh_id STARTS WITH 'sh85057151|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065703' OR parent.lcsh_id STARTS WITH 'sh85065703|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85022551' OR child.lcsh_id STARTS WITH 'sh85022551|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85021130' OR parent.lcsh_id STARTS WITH 'sh85021130|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85022551' OR child.lcsh_id STARTS WITH 'sh85022551|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022543' OR parent.lcsh_id STARTS WITH 'sh85022543|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85059867' OR child.lcsh_id STARTS WITH 'sh85059867|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85013674' OR parent.lcsh_id STARTS WITH 'sh85013674|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85059867' OR child.lcsh_id STARTS WITH 'sh85059867|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85070422' OR parent.lcsh_id STARTS WITH 'sh85070422|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85059867' OR child.lcsh_id STARTS WITH 'sh85059867|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119966' OR parent.lcsh_id STARTS WITH 'sh85119966|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88000222' OR child.lcsh_id STARTS WITH 'sh88000222|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029534' OR parent.lcsh_id STARTS WITH 'sh85029534|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2013000266' OR child.lcsh_id STARTS WITH 'sh2013000266|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029513' OR parent.lcsh_id STARTS WITH 'sh85029513|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85068397' OR child.lcsh_id STARTS WITH 'sh85068397|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100934' OR child.lcsh_id STARTS WITH 'sh85100934|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100864' OR parent.lcsh_id STARTS WITH 'sh85100864|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85074944' OR child.lcsh_id STARTS WITH 'sh85074944|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026704' OR parent.lcsh_id STARTS WITH 'sh85026704|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85074944' OR child.lcsh_id STARTS WITH 'sh85074944|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85068863' OR parent.lcsh_id STARTS WITH 'sh85068863|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85080966' OR child.lcsh_id STARTS WITH 'sh85080966|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh95009606' OR parent.lcsh_id STARTS WITH 'sh95009606|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081990' OR child.lcsh_id STARTS WITH 'sh85081990|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85036481' OR parent.lcsh_id STARTS WITH 'sh85036481|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081991' OR child.lcsh_id STARTS WITH 'sh85081991|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85018279' OR parent.lcsh_id STARTS WITH 'sh85018279|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081991' OR child.lcsh_id STARTS WITH 'sh85081991|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85036481' OR parent.lcsh_id STARTS WITH 'sh85036481|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85090702' OR child.lcsh_id STARTS WITH 'sh85090702|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2011005559' OR parent.lcsh_id STARTS WITH 'sh2011005559|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85090702' OR child.lcsh_id STARTS WITH 'sh85090702|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85148550' OR parent.lcsh_id STARTS WITH 'sh85148550|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097195' OR child.lcsh_id STARTS WITH 'sh85097195|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065695' OR parent.lcsh_id STARTS WITH 'sh85065695|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097195' OR child.lcsh_id STARTS WITH 'sh85097195|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85064932' OR parent.lcsh_id STARTS WITH 'sh85064932|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100070' OR child.lcsh_id STARTS WITH 'sh85100070|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067921' OR parent.lcsh_id STARTS WITH 'sh85067921|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097451' OR child.lcsh_id STARTS WITH 'sh85097451|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85064932' OR parent.lcsh_id STARTS WITH 'sh85064932|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097451' OR child.lcsh_id STARTS WITH 'sh85097451|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065698' OR parent.lcsh_id STARTS WITH 'sh85065698|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097144' OR child.lcsh_id STARTS WITH 'sh85097144|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85097126' OR parent.lcsh_id STARTS WITH 'sh85097126|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85114953' OR child.lcsh_id STARTS WITH 'sh85114953|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85068863' OR parent.lcsh_id STARTS WITH 'sh85068863|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85115040' OR child.lcsh_id STARTS WITH 'sh85115040|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85011205' OR parent.lcsh_id STARTS WITH 'sh85011205|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85115040' OR child.lcsh_id STARTS WITH 'sh85115040|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2012000320' OR parent.lcsh_id STARTS WITH 'sh2012000320|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85115971' OR child.lcsh_id STARTS WITH 'sh85115971|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85123367' OR parent.lcsh_id STARTS WITH 'sh85123367|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85117331' OR child.lcsh_id STARTS WITH 'sh85117331|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065695' OR parent.lcsh_id STARTS WITH 'sh85065695|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2002000569' OR child.lcsh_id STARTS WITH 'sh2002000569|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2004000479' OR parent.lcsh_id STARTS WITH 'sh2004000479|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2002000569' OR child.lcsh_id STARTS WITH 'sh2002000569|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh92004914' OR parent.lcsh_id STARTS WITH 'sh92004914|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2002000569' OR child.lcsh_id STARTS WITH 'sh2002000569|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh95000541' OR parent.lcsh_id STARTS WITH 'sh95000541|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2004000479' OR child.lcsh_id STARTS WITH 'sh2004000479|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh88000222' OR parent.lcsh_id STARTS WITH 'sh88000222|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2004000479' OR child.lcsh_id STARTS WITH 'sh2004000479|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2009007899' OR parent.lcsh_id STARTS WITH 'sh2009007899|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119961' OR child.lcsh_id STARTS WITH 'sh85119961|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85002020' OR parent.lcsh_id STARTS WITH 'sh85002020|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85122803' OR child.lcsh_id STARTS WITH 'sh85122803|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065698' OR parent.lcsh_id STARTS WITH 'sh85065698|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85123361' OR child.lcsh_id STARTS WITH 'sh85123361|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065703' OR parent.lcsh_id STARTS WITH 'sh85065703|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126261' OR child.lcsh_id STARTS WITH 'sh85126261|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85114953' OR parent.lcsh_id STARTS WITH 'sh85114953|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126268' OR child.lcsh_id STARTS WITH 'sh85126268|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh92005334' OR parent.lcsh_id STARTS WITH 'sh92005334|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85139700' OR child.lcsh_id STARTS WITH 'sh85139700|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080966' OR parent.lcsh_id STARTS WITH 'sh85080966|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh97003561' OR child.lcsh_id STARTS WITH 'sh97003561|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029535' OR parent.lcsh_id STARTS WITH 'sh85029535|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh97003561' OR child.lcsh_id STARTS WITH 'sh97003561|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2012003486' OR parent.lcsh_id STARTS WITH 'sh2012003486|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh97003561' OR child.lcsh_id STARTS WITH 'sh97003561|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh96004653' OR parent.lcsh_id STARTS WITH 'sh96004653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95000541' OR child.lcsh_id STARTS WITH 'sh95000541|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh88002671' OR parent.lcsh_id STARTS WITH 'sh88002671|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95000541' OR child.lcsh_id STARTS WITH 'sh95000541|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh92002381' OR parent.lcsh_id STARTS WITH 'sh92002381|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85149236' OR child.lcsh_id STARTS WITH 'sh85149236|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85013182' OR parent.lcsh_id STARTS WITH 'sh85013182|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85149236' OR child.lcsh_id STARTS WITH 'sh85149236|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85073531' OR parent.lcsh_id STARTS WITH 'sh85073531|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85149236' OR child.lcsh_id STARTS WITH 'sh85149236|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85091879' OR parent.lcsh_id STARTS WITH 'sh85091879|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85036481' OR child.lcsh_id STARTS WITH 'sh85036481|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85135657' OR parent.lcsh_id STARTS WITH 'sh85135657|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85000405' OR child.lcsh_id STARTS WITH 'sh85000405|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85107253' OR parent.lcsh_id STARTS WITH 'sh85107253|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85000411' OR child.lcsh_id STARTS WITH 'sh85000411|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85018260' OR parent.lcsh_id STARTS WITH 'sh85018260|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125404' OR child.lcsh_id STARTS WITH 'sh85125404|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85143117' OR parent.lcsh_id STARTS WITH 'sh85143117|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125404' OR child.lcsh_id STARTS WITH 'sh85125404|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85145789' OR parent.lcsh_id STARTS WITH 'sh85145789|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85039329' OR child.lcsh_id STARTS WITH 'sh85039329|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85034149' OR parent.lcsh_id STARTS WITH 'sh85034149|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85000744' OR child.lcsh_id STARTS WITH 'sh85000744|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85008276' OR parent.lcsh_id STARTS WITH 'sh85008276|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85000744' OR child.lcsh_id STARTS WITH 'sh85000744|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85044098' OR parent.lcsh_id STARTS WITH 'sh85044098|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh00005896' OR child.lcsh_id STARTS WITH 'sh00005896|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh99005040' OR parent.lcsh_id STARTS WITH 'sh99005040|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85000913' OR child.lcsh_id STARTS WITH 'sh85000913|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108696' OR parent.lcsh_id STARTS WITH 'sh85108696|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85000969' OR child.lcsh_id STARTS WITH 'sh85000969|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001028' OR child.lcsh_id STARTS WITH 'sh85001028|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001086' OR child.lcsh_id STARTS WITH 'sh85001086|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85018260' OR parent.lcsh_id STARTS WITH 'sh85018260|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001086' OR child.lcsh_id STARTS WITH 'sh85001086|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029077' OR parent.lcsh_id STARTS WITH 'sh85029077|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001086' OR child.lcsh_id STARTS WITH 'sh85001086|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065926' OR parent.lcsh_id STARTS WITH 'sh85065926|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001086' OR child.lcsh_id STARTS WITH 'sh85001086|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85113295' OR parent.lcsh_id STARTS WITH 'sh85113295|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001295' OR child.lcsh_id STARTS WITH 'sh85001295|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040316' OR parent.lcsh_id STARTS WITH 'sh85040316|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001295' OR child.lcsh_id STARTS WITH 'sh85001295|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85049376' OR parent.lcsh_id STARTS WITH 'sh85049376|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001295' OR child.lcsh_id STARTS WITH 'sh85001295|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053291' OR parent.lcsh_id STARTS WITH 'sh85053291|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001295' OR child.lcsh_id STARTS WITH 'sh85001295|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85103619' OR parent.lcsh_id STARTS WITH 'sh85103619|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001319' OR child.lcsh_id STARTS WITH 'sh85001319|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029044' OR parent.lcsh_id STARTS WITH 'sh85029044|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95007821' OR child.lcsh_id STARTS WITH 'sh95007821|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85001319' OR parent.lcsh_id STARTS WITH 'sh85001319|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95007821' OR child.lcsh_id STARTS WITH 'sh95007821|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85008947' OR parent.lcsh_id STARTS WITH 'sh85008947|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95007821' OR child.lcsh_id STARTS WITH 'sh95007821|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001441' OR child.lcsh_id STARTS WITH 'sh85001441|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029049' OR child.lcsh_id STARTS WITH 'sh85029049|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85002415' OR parent.lcsh_id STARTS WITH 'sh85002415|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002427' OR child.lcsh_id STARTS WITH 'sh85002427|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074350' OR parent.lcsh_id STARTS WITH 'sh85074350|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002310' OR child.lcsh_id STARTS WITH 'sh85002310|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85133121' OR parent.lcsh_id STARTS WITH 'sh85133121|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002313' OR child.lcsh_id STARTS WITH 'sh85002313|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014134' OR parent.lcsh_id STARTS WITH 'sh85014134|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002313' OR child.lcsh_id STARTS WITH 'sh85002313|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002298' OR child.lcsh_id STARTS WITH 'sh85002298|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85031469' OR parent.lcsh_id STARTS WITH 'sh85031469|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002484' OR child.lcsh_id STARTS WITH 'sh85002484|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040837' OR parent.lcsh_id STARTS WITH 'sh85040837|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86001792' OR child.lcsh_id STARTS WITH 'sh86001792|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014263' OR parent.lcsh_id STARTS WITH 'sh85014263|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002415' OR child.lcsh_id STARTS WITH 'sh85002415|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065826' OR parent.lcsh_id STARTS WITH 'sh85065826|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002415' OR child.lcsh_id STARTS WITH 'sh85002415|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85076841' OR parent.lcsh_id STARTS WITH 'sh85076841|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002307' OR child.lcsh_id STARTS WITH 'sh85002307|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh90003962' OR parent.lcsh_id STARTS WITH 'sh90003962|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85002307' OR child.lcsh_id STARTS WITH 'sh85002307|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084356' OR child.lcsh_id STARTS WITH 'sh85084356|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014127' OR parent.lcsh_id STARTS WITH 'sh85014127|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91006254' OR child.lcsh_id STARTS WITH 'sh91006254|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85002415' OR parent.lcsh_id STARTS WITH 'sh85002415|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85003425' OR child.lcsh_id STARTS WITH 'sh85003425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082139' OR parent.lcsh_id STARTS WITH 'sh85082139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054140' OR child.lcsh_id STARTS WITH 'sh85054140|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054133' OR parent.lcsh_id STARTS WITH 'sh85054133|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85003487' OR child.lcsh_id STARTS WITH 'sh85003487|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85003425' OR parent.lcsh_id STARTS WITH 'sh85003425|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85003487' OR child.lcsh_id STARTS WITH 'sh85003487|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85007169' OR parent.lcsh_id STARTS WITH 'sh85007169|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85004972' OR child.lcsh_id STARTS WITH 'sh85004972|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85130766' OR parent.lcsh_id STARTS WITH 'sh85130766|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023011' OR child.lcsh_id STARTS WITH 'sh85023011|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85004835' OR child.lcsh_id STARTS WITH 'sh85004835|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005167' OR child.lcsh_id STARTS WITH 'sh85005167|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005162' OR parent.lcsh_id STARTS WITH 'sh85005162|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005172' OR child.lcsh_id STARTS WITH 'sh85005172|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91006269' OR child.lcsh_id STARTS WITH 'sh91006269|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005172' OR parent.lcsh_id STARTS WITH 'sh85005172|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91006269' OR child.lcsh_id STARTS WITH 'sh91006269|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh91006274' OR parent.lcsh_id STARTS WITH 'sh91006274|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91006269' OR child.lcsh_id STARTS WITH 'sh91006269|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101679' OR parent.lcsh_id STARTS WITH 'sh85101679|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005190' OR child.lcsh_id STARTS WITH 'sh85005190|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053877' OR parent.lcsh_id STARTS WITH 'sh85053877|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005169' OR child.lcsh_id STARTS WITH 'sh85005169|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85149996' OR parent.lcsh_id STARTS WITH 'sh85149996|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85087348' OR child.lcsh_id STARTS WITH 'sh85087348|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85087347' OR parent.lcsh_id STARTS WITH 'sh85087347|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005291' OR child.lcsh_id STARTS WITH 'sh85005291|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026014' OR parent.lcsh_id STARTS WITH 'sh85026014|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005579' OR child.lcsh_id STARTS WITH 'sh85005579|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118696' OR parent.lcsh_id STARTS WITH 'sh85118696|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005581' OR child.lcsh_id STARTS WITH 'sh85005581|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124003' OR parent.lcsh_id STARTS WITH 'sh85124003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2003004295' OR child.lcsh_id STARTS WITH 'sh2003004295|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh89003038' OR child.lcsh_id STARTS WITH 'sh89003038|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005588' OR child.lcsh_id STARTS WITH 'sh85005588|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101512' OR parent.lcsh_id STARTS WITH 'sh85101512|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh98004527' OR child.lcsh_id STARTS WITH 'sh98004527|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh90001980' OR parent.lcsh_id STARTS WITH 'sh90001980|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006167' OR child.lcsh_id STARTS WITH 'sh85006167|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96009482' OR child.lcsh_id STARTS WITH 'sh96009482|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006168' OR child.lcsh_id STARTS WITH 'sh85006168|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077222' OR parent.lcsh_id STARTS WITH 'sh85077222|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108472' OR child.lcsh_id STARTS WITH 'sh85108472|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006231' OR child.lcsh_id STARTS WITH 'sh85006231|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006246' OR parent.lcsh_id STARTS WITH 'sh85006246|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006231' OR child.lcsh_id STARTS WITH 'sh85006231|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006232' OR child.lcsh_id STARTS WITH 'sh85006232|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006231' OR parent.lcsh_id STARTS WITH 'sh85006231|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006232' OR child.lcsh_id STARTS WITH 'sh85006232|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006246' OR child.lcsh_id STARTS WITH 'sh85006246|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006517' OR child.lcsh_id STARTS WITH 'sh85006517|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006509' OR parent.lcsh_id STARTS WITH 'sh85006509|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006517' OR child.lcsh_id STARTS WITH 'sh85006517|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85007488' OR parent.lcsh_id STARTS WITH 'sh85007488|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006507' OR child.lcsh_id STARTS WITH 'sh85006507|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006507' OR child.lcsh_id STARTS WITH 'sh85006507|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85010480' OR parent.lcsh_id STARTS WITH 'sh85010480|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006507' OR child.lcsh_id STARTS WITH 'sh85006507|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061212' OR parent.lcsh_id STARTS WITH 'sh85061212|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006611' OR child.lcsh_id STARTS WITH 'sh85006611|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85007461' OR parent.lcsh_id STARTS WITH 'sh85007461|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006988' OR child.lcsh_id STARTS WITH 'sh85006988|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006988' OR child.lcsh_id STARTS WITH 'sh85006988|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85113021' OR parent.lcsh_id STARTS WITH 'sh85113021|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85007163' OR child.lcsh_id STARTS WITH 'sh85007163|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082139' OR parent.lcsh_id STARTS WITH 'sh85082139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85007163' OR child.lcsh_id STARTS WITH 'sh85007163|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85120387' OR parent.lcsh_id STARTS WITH 'sh85120387|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119004' OR child.lcsh_id STARTS WITH 'sh85119004|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85007461' OR parent.lcsh_id STARTS WITH 'sh85007461|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008180' OR child.lcsh_id STARTS WITH 'sh85008180|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014250' OR parent.lcsh_id STARTS WITH 'sh85014250|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008180' OR child.lcsh_id STARTS WITH 'sh85008180|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh88006179' OR parent.lcsh_id STARTS WITH 'sh88006179|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008180' OR child.lcsh_id STARTS WITH 'sh85008180|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85037973' OR parent.lcsh_id STARTS WITH 'sh85037973|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008180' OR child.lcsh_id STARTS WITH 'sh85008180|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042288' OR parent.lcsh_id STARTS WITH 'sh85042288|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008180' OR child.lcsh_id STARTS WITH 'sh85008180|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85078122' OR parent.lcsh_id STARTS WITH 'sh85078122|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008180' OR child.lcsh_id STARTS WITH 'sh85008180|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079341' OR parent.lcsh_id STARTS WITH 'sh85079341|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008180' OR child.lcsh_id STARTS WITH 'sh85008180|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119773' OR parent.lcsh_id STARTS WITH 'sh85119773|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008180' OR child.lcsh_id STARTS WITH 'sh85008180|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85122767' OR parent.lcsh_id STARTS WITH 'sh85122767|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033827' OR child.lcsh_id STARTS WITH 'sh85033827|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85007461' OR parent.lcsh_id STARTS WITH 'sh85007461|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033827' OR child.lcsh_id STARTS WITH 'sh85033827|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85064466' OR parent.lcsh_id STARTS WITH 'sh85064466|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033827' OR child.lcsh_id STARTS WITH 'sh85033827|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066719' OR parent.lcsh_id STARTS WITH 'sh85066719|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033827' OR child.lcsh_id STARTS WITH 'sh85033827|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077507' OR parent.lcsh_id STARTS WITH 'sh85077507|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008324' OR child.lcsh_id STARTS WITH 'sh85008324|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062913' OR parent.lcsh_id STARTS WITH 'sh85062913|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh90004216' OR child.lcsh_id STARTS WITH 'sh90004216|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033157' OR child.lcsh_id STARTS WITH 'sh85033157|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033157' OR child.lcsh_id STARTS WITH 'sh85033157|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85125953' OR parent.lcsh_id STARTS WITH 'sh85125953|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85008942' OR child.lcsh_id STARTS WITH 'sh85008942|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85009024' OR parent.lcsh_id STARTS WITH 'sh85009024|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009003' OR child.lcsh_id STARTS WITH 'sh85009003|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89005705' OR parent.lcsh_id STARTS WITH 'sh89005705|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009032' OR child.lcsh_id STARTS WITH 'sh85009032|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85009003' OR parent.lcsh_id STARTS WITH 'sh85009003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009032' OR child.lcsh_id STARTS WITH 'sh85009032|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85033150' OR parent.lcsh_id STARTS WITH 'sh85033150|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009032' OR child.lcsh_id STARTS WITH 'sh85009032|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009289' OR child.lcsh_id STARTS WITH 'sh85009289|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2018002590' OR parent.lcsh_id STARTS WITH 'sh2018002590|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2018002590' OR child.lcsh_id STARTS WITH 'sh2018002590|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040468' OR parent.lcsh_id STARTS WITH 'sh85040468|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009391' OR child.lcsh_id STARTS WITH 'sh85009391|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006096' OR parent.lcsh_id STARTS WITH 'sh85006096|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009391' OR child.lcsh_id STARTS WITH 'sh85009391|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85007409' OR parent.lcsh_id STARTS WITH 'sh85007409|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009391' OR child.lcsh_id STARTS WITH 'sh85009391|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85041141' OR parent.lcsh_id STARTS WITH 'sh85041141|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009391' OR child.lcsh_id STARTS WITH 'sh85009391|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083497' OR parent.lcsh_id STARTS WITH 'sh85083497|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009391' OR child.lcsh_id STARTS WITH 'sh85009391|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009391' OR child.lcsh_id STARTS WITH 'sh85009391|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85134988' OR parent.lcsh_id STARTS WITH 'sh85134988|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85010164' OR child.lcsh_id STARTS WITH 'sh85010164|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85010157' OR parent.lcsh_id STARTS WITH 'sh85010157|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85010164' OR child.lcsh_id STARTS WITH 'sh85010164|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082771' OR parent.lcsh_id STARTS WITH 'sh85082771|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh90002778' OR child.lcsh_id STARTS WITH 'sh90002778|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85137072' OR parent.lcsh_id STARTS WITH 'sh85137072|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85010864' OR child.lcsh_id STARTS WITH 'sh85010864|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084783' OR parent.lcsh_id STARTS WITH 'sh85084783|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85011312' OR child.lcsh_id STARTS WITH 'sh85011312|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85013838' OR child.lcsh_id STARTS WITH 'sh85013838|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85038731' OR parent.lcsh_id STARTS WITH 'sh85038731|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85013838' OR child.lcsh_id STARTS WITH 'sh85013838|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh96008049' OR parent.lcsh_id STARTS WITH 'sh96008049|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85013873' OR child.lcsh_id STARTS WITH 'sh85013873|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85013838' OR parent.lcsh_id STARTS WITH 'sh85013838|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2012003227' OR child.lcsh_id STARTS WITH 'sh2012003227|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2018002256' OR parent.lcsh_id STARTS WITH 'sh2018002256|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014119' OR child.lcsh_id STARTS WITH 'sh85014119|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85125363' OR parent.lcsh_id STARTS WITH 'sh85125363|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014171' OR child.lcsh_id STARTS WITH 'sh85014171|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014171' OR child.lcsh_id STARTS WITH 'sh85014171|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014171' OR child.lcsh_id STARTS WITH 'sh85014171|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083022' OR parent.lcsh_id STARTS WITH 'sh85083022|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014127' OR child.lcsh_id STARTS WITH 'sh85014127|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85027044' OR parent.lcsh_id STARTS WITH 'sh85027044|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014127' OR child.lcsh_id STARTS WITH 'sh85014127|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014134' OR child.lcsh_id STARTS WITH 'sh85014134|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014134' OR child.lcsh_id STARTS WITH 'sh85014134|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014136' OR child.lcsh_id STARTS WITH 'sh85014136|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118616' OR parent.lcsh_id STARTS WITH 'sh85118616|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014147' OR child.lcsh_id STARTS WITH 'sh85014147|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014147' OR child.lcsh_id STARTS WITH 'sh85014147|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053986' OR parent.lcsh_id STARTS WITH 'sh85053986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh00003585' OR child.lcsh_id STARTS WITH 'sh00003585|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014206' OR parent.lcsh_id STARTS WITH 'sh85014206|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh00003585' OR child.lcsh_id STARTS WITH 'sh00003585|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066150' OR parent.lcsh_id STARTS WITH 'sh85066150|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101512' OR child.lcsh_id STARTS WITH 'sh85101512|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014203' OR child.lcsh_id STARTS WITH 'sh85014203|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85076841' OR parent.lcsh_id STARTS WITH 'sh85076841|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014236' OR child.lcsh_id STARTS WITH 'sh85014236|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014253' OR parent.lcsh_id STARTS WITH 'sh85014253|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014236' OR child.lcsh_id STARTS WITH 'sh85014236|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082767' OR parent.lcsh_id STARTS WITH 'sh85082767|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014237' OR child.lcsh_id STARTS WITH 'sh85014237|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014134' OR parent.lcsh_id STARTS WITH 'sh85014134|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014237' OR child.lcsh_id STARTS WITH 'sh85014237|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014253' OR parent.lcsh_id STARTS WITH 'sh85014253|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014237' OR child.lcsh_id STARTS WITH 'sh85014237|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014237' OR child.lcsh_id STARTS WITH 'sh85014237|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2010013493' OR child.lcsh_id STARTS WITH 'sh2010013493|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006509' OR parent.lcsh_id STARTS WITH 'sh85006509|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2010013493' OR child.lcsh_id STARTS WITH 'sh2010013493|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014171' OR parent.lcsh_id STARTS WITH 'sh85014171|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014253' OR child.lcsh_id STARTS WITH 'sh85014253|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014253' OR child.lcsh_id STARTS WITH 'sh85014253|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083022' OR parent.lcsh_id STARTS WITH 'sh85083022|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014253' OR child.lcsh_id STARTS WITH 'sh85014253|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097152' OR child.lcsh_id STARTS WITH 'sh85097152|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85097123' OR parent.lcsh_id STARTS WITH 'sh85097123|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014263' OR child.lcsh_id STARTS WITH 'sh85014263|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022900' OR parent.lcsh_id STARTS WITH 'sh85022900|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh99002613' OR child.lcsh_id STARTS WITH 'sh99002613|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101206' OR parent.lcsh_id STARTS WITH 'sh85101206|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2016002790' OR child.lcsh_id STARTS WITH 'sh2016002790|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh90005677' OR parent.lcsh_id STARTS WITH 'sh90005677|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2016002790' OR child.lcsh_id STARTS WITH 'sh2016002790|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh88000865' OR parent.lcsh_id STARTS WITH 'sh88000865|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015976' OR child.lcsh_id STARTS WITH 'sh85015976|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015976' OR child.lcsh_id STARTS WITH 'sh85015976|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090222' OR parent.lcsh_id STARTS WITH 'sh85090222|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2009007945' OR child.lcsh_id STARTS WITH 'sh2009007945|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85128566' OR parent.lcsh_id STARTS WITH 'sh85128566|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85017004' OR child.lcsh_id STARTS WITH 'sh85017004|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029044' OR parent.lcsh_id STARTS WITH 'sh85029044|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85017004' OR child.lcsh_id STARTS WITH 'sh85017004|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh99004266' OR parent.lcsh_id STARTS WITH 'sh99004266|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85017004' OR child.lcsh_id STARTS WITH 'sh85017004|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85133270' OR parent.lcsh_id STARTS WITH 'sh85133270|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85018260' OR child.lcsh_id STARTS WITH 'sh85018260|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85018260' OR child.lcsh_id STARTS WITH 'sh85018260|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080336' OR parent.lcsh_id STARTS WITH 'sh85080336|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85018802' OR child.lcsh_id STARTS WITH 'sh85018802|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082116' OR parent.lcsh_id STARTS WITH 'sh85082116|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85018809' OR child.lcsh_id STARTS WITH 'sh85018809|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082365' OR parent.lcsh_id STARTS WITH 'sh85082365|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85019430' OR child.lcsh_id STARTS WITH 'sh85019430|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87002642' OR child.lcsh_id STARTS WITH 'sh87002642|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85019512' OR parent.lcsh_id STARTS WITH 'sh85019512|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87002642' OR child.lcsh_id STARTS WITH 'sh87002642|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85019547' OR parent.lcsh_id STARTS WITH 'sh85019547|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85019646' OR child.lcsh_id STARTS WITH 'sh85019646|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85075119' OR parent.lcsh_id STARTS WITH 'sh85075119|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85020211' OR child.lcsh_id STARTS WITH 'sh85020211|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083023' OR parent.lcsh_id STARTS WITH 'sh85083023|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85020211' OR child.lcsh_id STARTS WITH 'sh85020211|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101610' OR parent.lcsh_id STARTS WITH 'sh85101610|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85020435' OR child.lcsh_id STARTS WITH 'sh85020435|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85017693' OR parent.lcsh_id STARTS WITH 'sh85017693|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85020435' OR child.lcsh_id STARTS WITH 'sh85020435|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080653' OR parent.lcsh_id STARTS WITH 'sh85080653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91002611' OR child.lcsh_id STARTS WITH 'sh91002611|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85022900' OR child.lcsh_id STARTS WITH 'sh85022900|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023029' OR child.lcsh_id STARTS WITH 'sh85023029|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023029' OR child.lcsh_id STARTS WITH 'sh85023029|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85133147' OR parent.lcsh_id STARTS WITH 'sh85133147|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2003001403' OR child.lcsh_id STARTS WITH 'sh2003001403|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2003006495' OR parent.lcsh_id STARTS WITH 'sh2003006495|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2003001403' OR child.lcsh_id STARTS WITH 'sh2003001403|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066150' OR parent.lcsh_id STARTS WITH 'sh85066150|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85022986' OR child.lcsh_id STARTS WITH 'sh85022986|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89005705' OR parent.lcsh_id STARTS WITH 'sh89005705|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2005000482' OR child.lcsh_id STARTS WITH 'sh2005000482|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023011' OR parent.lcsh_id STARTS WITH 'sh85023011|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2005000482' OR child.lcsh_id STARTS WITH 'sh2005000482|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2005000963' OR parent.lcsh_id STARTS WITH 'sh2005000963|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2005000482' OR child.lcsh_id STARTS WITH 'sh2005000482|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2005000964' OR parent.lcsh_id STARTS WITH 'sh2005000964|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2001002085' OR child.lcsh_id STARTS WITH 'sh2001002085|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023357' OR parent.lcsh_id STARTS WITH 'sh85023357|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023396' OR child.lcsh_id STARTS WITH 'sh85023396|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85047060' OR parent.lcsh_id STARTS WITH 'sh85047060|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023396' OR child.lcsh_id STARTS WITH 'sh85023396|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108846' OR parent.lcsh_id STARTS WITH 'sh85108846|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023396' OR child.lcsh_id STARTS WITH 'sh85023396|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124089' OR parent.lcsh_id STARTS WITH 'sh85124089|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023396' OR child.lcsh_id STARTS WITH 'sh85023396|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124112' OR parent.lcsh_id STARTS WITH 'sh85124112|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023380' OR child.lcsh_id STARTS WITH 'sh85023380|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023357' OR parent.lcsh_id STARTS WITH 'sh85023357|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023380' OR child.lcsh_id STARTS WITH 'sh85023380|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85037359' OR parent.lcsh_id STARTS WITH 'sh85037359|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85025406' OR child.lcsh_id STARTS WITH 'sh85025406|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85010480' OR parent.lcsh_id STARTS WITH 'sh85010480|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85025619' OR child.lcsh_id STARTS WITH 'sh85025619|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061212' OR parent.lcsh_id STARTS WITH 'sh85061212|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85025650' OR child.lcsh_id STARTS WITH 'sh85025650|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85037397' OR parent.lcsh_id STARTS WITH 'sh85037397|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85025650' OR child.lcsh_id STARTS WITH 'sh85025650|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077732' OR parent.lcsh_id STARTS WITH 'sh85077732|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85025650' OR child.lcsh_id STARTS WITH 'sh85025650|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85088819' OR parent.lcsh_id STARTS WITH 'sh85088819|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85026014' OR child.lcsh_id STARTS WITH 'sh85026014|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101302' OR parent.lcsh_id STARTS WITH 'sh85101302|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85026014' OR child.lcsh_id STARTS WITH 'sh85026014|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101206' OR parent.lcsh_id STARTS WITH 'sh85101206|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85026371' OR child.lcsh_id STARTS WITH 'sh85026371|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85031329' OR parent.lcsh_id STARTS WITH 'sh85031329|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85026371' OR child.lcsh_id STARTS WITH 'sh85026371|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026379' OR parent.lcsh_id STARTS WITH 'sh85026379|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85026338' OR child.lcsh_id STARTS WITH 'sh85026338|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043249' OR parent.lcsh_id STARTS WITH 'sh85043249|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85026331' OR child.lcsh_id STARTS WITH 'sh85026331|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh99000303' OR child.lcsh_id STARTS WITH 'sh99000303|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85027044' OR child.lcsh_id STARTS WITH 'sh85027044|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2018002590' OR parent.lcsh_id STARTS WITH 'sh2018002590|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85027063' OR child.lcsh_id STARTS WITH 'sh85027063|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023380' OR parent.lcsh_id STARTS WITH 'sh85023380|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85027063' OR child.lcsh_id STARTS WITH 'sh85027063|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85027067' OR parent.lcsh_id STARTS WITH 'sh85027067|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037496' OR child.lcsh_id STARTS WITH 'sh85037496|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85037489' OR parent.lcsh_id STARTS WITH 'sh85037489|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037496' OR child.lcsh_id STARTS WITH 'sh85037496|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85098685' OR parent.lcsh_id STARTS WITH 'sh85098685|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85027067' OR child.lcsh_id STARTS WITH 'sh85027067|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108381' OR parent.lcsh_id STARTS WITH 'sh85108381|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85027067' OR child.lcsh_id STARTS WITH 'sh85027067|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108472' OR parent.lcsh_id STARTS WITH 'sh85108472|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2008004883' OR child.lcsh_id STARTS WITH 'sh2008004883|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042293' OR parent.lcsh_id STARTS WITH 'sh85042293|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85027299' OR child.lcsh_id STARTS WITH 'sh85027299|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101517' OR parent.lcsh_id STARTS WITH 'sh85101517|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85027742' OR child.lcsh_id STARTS WITH 'sh85027742|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87007652' OR child.lcsh_id STARTS WITH 'sh87007652|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh88006179' OR parent.lcsh_id STARTS WITH 'sh88006179|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87007652' OR child.lcsh_id STARTS WITH 'sh87007652|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88006179' OR child.lcsh_id STARTS WITH 'sh88006179|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85028802' OR child.lcsh_id STARTS WITH 'sh85028802|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85003425' OR parent.lcsh_id STARTS WITH 'sh85003425|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85028802' OR child.lcsh_id STARTS WITH 'sh85028802|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082116' OR parent.lcsh_id STARTS WITH 'sh85082116|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85028940' OR child.lcsh_id STARTS WITH 'sh85028940|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85075119' OR parent.lcsh_id STARTS WITH 'sh85075119|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029027' OR child.lcsh_id STARTS WITH 'sh85029027|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029301' OR child.lcsh_id STARTS WITH 'sh85029301|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061192' OR parent.lcsh_id STARTS WITH 'sh85061192|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077534' OR child.lcsh_id STARTS WITH 'sh85077534|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100821' OR parent.lcsh_id STARTS WITH 'sh85100821|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85112599' OR child.lcsh_id STARTS WITH 'sh85112599|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026423' OR parent.lcsh_id STARTS WITH 'sh85026423|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2020006312' OR child.lcsh_id STARTS WITH 'sh2020006312|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077224' OR child.lcsh_id STARTS WITH 'sh85077224|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006168' OR parent.lcsh_id STARTS WITH 'sh85006168|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029552' OR child.lcsh_id STARTS WITH 'sh85029552|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh98003200' OR parent.lcsh_id STARTS WITH 'sh98003200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029552' OR child.lcsh_id STARTS WITH 'sh85029552|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85035046' OR parent.lcsh_id STARTS WITH 'sh85035046|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029552' OR child.lcsh_id STARTS WITH 'sh85029552|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079341' OR parent.lcsh_id STARTS WITH 'sh85079341|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029511' OR child.lcsh_id STARTS WITH 'sh85029511|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85088762' OR parent.lcsh_id STARTS WITH 'sh85088762|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029512' OR child.lcsh_id STARTS WITH 'sh85029512|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029513' OR parent.lcsh_id STARTS WITH 'sh85029513|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029524' OR child.lcsh_id STARTS WITH 'sh85029524|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079331' OR parent.lcsh_id STARTS WITH 'sh85079331|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029524' OR child.lcsh_id STARTS WITH 'sh85029524|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029534' OR parent.lcsh_id STARTS WITH 'sh85029534|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107310' OR child.lcsh_id STARTS WITH 'sh85107310|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042288' OR parent.lcsh_id STARTS WITH 'sh85042288|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh89003285' OR child.lcsh_id STARTS WITH 'sh89003285|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029497' OR child.lcsh_id STARTS WITH 'sh85029497|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043249' OR parent.lcsh_id STARTS WITH 'sh85043249|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029623' OR child.lcsh_id STARTS WITH 'sh85029623|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85000258' OR parent.lcsh_id STARTS WITH 'sh85000258|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029623' OR child.lcsh_id STARTS WITH 'sh85029623|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85072732' OR parent.lcsh_id STARTS WITH 'sh85072732|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029623' OR child.lcsh_id STARTS WITH 'sh85029623|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85099708' OR parent.lcsh_id STARTS WITH 'sh85099708|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029623' OR child.lcsh_id STARTS WITH 'sh85029623|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85030765' OR child.lcsh_id STARTS WITH 'sh85030765|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077404' OR parent.lcsh_id STARTS WITH 'sh85077404|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85030765' OR child.lcsh_id STARTS WITH 'sh85030765|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082246' OR parent.lcsh_id STARTS WITH 'sh85082246|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85030765' OR child.lcsh_id STARTS WITH 'sh85030765|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124647' OR parent.lcsh_id STARTS WITH 'sh85124647|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88001138' OR child.lcsh_id STARTS WITH 'sh88001138|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85027742' OR parent.lcsh_id STARTS WITH 'sh85027742|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95000524' OR child.lcsh_id STARTS WITH 'sh95000524|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85031326' OR child.lcsh_id STARTS WITH 'sh85031326|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061212' OR parent.lcsh_id STARTS WITH 'sh85061212|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85031329' OR child.lcsh_id STARTS WITH 'sh85031329|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108696' OR parent.lcsh_id STARTS WITH 'sh85108696|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85031496' OR child.lcsh_id STARTS WITH 'sh85031496|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh87006429' OR parent.lcsh_id STARTS WITH 'sh87006429|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85031576' OR child.lcsh_id STARTS WITH 'sh85031576|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85041516' OR parent.lcsh_id STARTS WITH 'sh85041516|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85031576' OR child.lcsh_id STARTS WITH 'sh85031576|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082768' OR parent.lcsh_id STARTS WITH 'sh85082768|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85031684' OR child.lcsh_id STARTS WITH 'sh85031684|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85032203' OR child.lcsh_id STARTS WITH 'sh85032203|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85032912' OR child.lcsh_id STARTS WITH 'sh85032912|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85028940' OR parent.lcsh_id STARTS WITH 'sh85028940|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033150' OR child.lcsh_id STARTS WITH 'sh85033150|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033150' OR child.lcsh_id STARTS WITH 'sh85033150|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85125953' OR parent.lcsh_id STARTS WITH 'sh85125953|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033167' OR child.lcsh_id STARTS WITH 'sh85033167|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85033169' OR parent.lcsh_id STARTS WITH 'sh85033169|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033169' OR child.lcsh_id STARTS WITH 'sh85033169|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85009003' OR parent.lcsh_id STARTS WITH 'sh85009003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033169' OR child.lcsh_id STARTS WITH 'sh85033169|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85036505' OR parent.lcsh_id STARTS WITH 'sh85036505|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033169' OR child.lcsh_id STARTS WITH 'sh85033169|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084286' OR parent.lcsh_id STARTS WITH 'sh85084286|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033421' OR child.lcsh_id STARTS WITH 'sh85033421|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85060103' OR parent.lcsh_id STARTS WITH 'sh85060103|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033421' OR child.lcsh_id STARTS WITH 'sh85033421|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108472' OR parent.lcsh_id STARTS WITH 'sh85108472|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033847' OR child.lcsh_id STARTS WITH 'sh85033847|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85010030' OR parent.lcsh_id STARTS WITH 'sh85010030|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85033847' OR child.lcsh_id STARTS WITH 'sh85033847|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85033827' OR parent.lcsh_id STARTS WITH 'sh85033827|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034032' OR child.lcsh_id STARTS WITH 'sh85034032|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005588' OR parent.lcsh_id STARTS WITH 'sh85005588|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034049' OR child.lcsh_id STARTS WITH 'sh85034049|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85071120' OR parent.lcsh_id STARTS WITH 'sh85071120|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034058' OR child.lcsh_id STARTS WITH 'sh85034058|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85103429' OR parent.lcsh_id STARTS WITH 'sh85103429|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034058' OR child.lcsh_id STARTS WITH 'sh85034058|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108696' OR parent.lcsh_id STARTS WITH 'sh85108696|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh89002994' OR child.lcsh_id STARTS WITH 'sh89002994|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124003' OR parent.lcsh_id STARTS WITH 'sh85124003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034122' OR child.lcsh_id STARTS WITH 'sh85034122|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080336' OR parent.lcsh_id STARTS WITH 'sh85080336|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034122' OR child.lcsh_id STARTS WITH 'sh85034122|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85107109' OR parent.lcsh_id STARTS WITH 'sh85107109|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034498' OR child.lcsh_id STARTS WITH 'sh85034498|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89005705' OR parent.lcsh_id STARTS WITH 'sh89005705|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034748' OR child.lcsh_id STARTS WITH 'sh85034748|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85034755' OR parent.lcsh_id STARTS WITH 'sh85034755|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034748' OR child.lcsh_id STARTS WITH 'sh85034748|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067165' OR parent.lcsh_id STARTS WITH 'sh85067165|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034748' OR child.lcsh_id STARTS WITH 'sh85034748|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85104904' OR parent.lcsh_id STARTS WITH 'sh85104904|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034969' OR child.lcsh_id STARTS WITH 'sh85034969|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85048270' OR parent.lcsh_id STARTS WITH 'sh85048270|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035046' OR child.lcsh_id STARTS WITH 'sh85035046|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85031658' OR parent.lcsh_id STARTS WITH 'sh85031658|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035046' OR child.lcsh_id STARTS WITH 'sh85035046|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042383' OR parent.lcsh_id STARTS WITH 'sh85042383|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035046' OR child.lcsh_id STARTS WITH 'sh85035046|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85131743' OR parent.lcsh_id STARTS WITH 'sh85131743|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035170' OR child.lcsh_id STARTS WITH 'sh85035170|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85130976' OR parent.lcsh_id STARTS WITH 'sh85130976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035240' OR child.lcsh_id STARTS WITH 'sh85035240|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035659' OR child.lcsh_id STARTS WITH 'sh85035659|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85004709' OR parent.lcsh_id STARTS WITH 'sh85004709|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035659' OR child.lcsh_id STARTS WITH 'sh85035659|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85099818' OR parent.lcsh_id STARTS WITH 'sh85099818|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035852' OR child.lcsh_id STARTS WITH 'sh85035852|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85035848' OR parent.lcsh_id STARTS WITH 'sh85035848|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh97002073' OR child.lcsh_id STARTS WITH 'sh97002073|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh86007858' OR parent.lcsh_id STARTS WITH 'sh86007858|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035859' OR child.lcsh_id STARTS WITH 'sh85035859|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042288' OR parent.lcsh_id STARTS WITH 'sh85042288|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2018002256' OR child.lcsh_id STARTS WITH 'sh2018002256|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079331' OR parent.lcsh_id STARTS WITH 'sh85079331|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2018002256' OR child.lcsh_id STARTS WITH 'sh2018002256|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh97001717' OR parent.lcsh_id STARTS WITH 'sh97001717|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035862' OR child.lcsh_id STARTS WITH 'sh85035862|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042288' OR parent.lcsh_id STARTS WITH 'sh85042288|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85035862' OR child.lcsh_id STARTS WITH 'sh85035862|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85048195' OR parent.lcsh_id STARTS WITH 'sh85048195|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037972' OR child.lcsh_id STARTS WITH 'sh85037972|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85037976' OR parent.lcsh_id STARTS WITH 'sh85037976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037972' OR child.lcsh_id STARTS WITH 'sh85037972|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85109042' OR parent.lcsh_id STARTS WITH 'sh85109042|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037972' OR child.lcsh_id STARTS WITH 'sh85037972|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85133270' OR parent.lcsh_id STARTS WITH 'sh85133270|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86007767' OR child.lcsh_id STARTS WITH 'sh86007767|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079331' OR parent.lcsh_id STARTS WITH 'sh85079331|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86007767' OR child.lcsh_id STARTS WITH 'sh86007767|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh97001717' OR parent.lcsh_id STARTS WITH 'sh97001717|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86006549' OR child.lcsh_id STARTS WITH 'sh86006549|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080359' OR parent.lcsh_id STARTS WITH 'sh85080359|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86006549' OR child.lcsh_id STARTS WITH 'sh86006549|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89005491' OR parent.lcsh_id STARTS WITH 'sh89005491|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2008009697' OR child.lcsh_id STARTS WITH 'sh2008009697|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh95000541' OR parent.lcsh_id STARTS WITH 'sh95000541|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85036659' OR child.lcsh_id STARTS WITH 'sh85036659|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124003' OR parent.lcsh_id STARTS WITH 'sh85124003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85036862' OR child.lcsh_id STARTS WITH 'sh85036862|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85036863' OR parent.lcsh_id STARTS WITH 'sh85036863|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85036953' OR child.lcsh_id STARTS WITH 'sh85036953|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037000' OR child.lcsh_id STARTS WITH 'sh85037000|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040146' OR parent.lcsh_id STARTS WITH 'sh85040146|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037000' OR child.lcsh_id STARTS WITH 'sh85037000|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85086410' OR parent.lcsh_id STARTS WITH 'sh85086410|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037197' OR child.lcsh_id STARTS WITH 'sh85037197|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85033827' OR parent.lcsh_id STARTS WITH 'sh85033827|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037352' OR child.lcsh_id STARTS WITH 'sh85037352|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037359' OR child.lcsh_id STARTS WITH 'sh85037359|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85037358' OR parent.lcsh_id STARTS WITH 'sh85037358|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037359' OR child.lcsh_id STARTS WITH 'sh85037359|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037878' OR child.lcsh_id STARTS WITH 'sh85037878|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2004000803' OR child.lcsh_id STARTS WITH 'sh2004000803|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85070736' OR parent.lcsh_id STARTS WITH 'sh85070736|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh98006600' OR child.lcsh_id STARTS WITH 'sh98006600|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85081863' OR parent.lcsh_id STARTS WITH 'sh85081863|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95004496' OR child.lcsh_id STARTS WITH 'sh95004496|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85106451' OR parent.lcsh_id STARTS WITH 'sh85106451|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93003312' OR child.lcsh_id STARTS WITH 'sh93003312|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85033841' OR parent.lcsh_id STARTS WITH 'sh85033841|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93003312' OR child.lcsh_id STARTS WITH 'sh93003312|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85113021' OR parent.lcsh_id STARTS WITH 'sh85113021|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88004324' OR child.lcsh_id STARTS WITH 'sh88004324|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85008180' OR parent.lcsh_id STARTS WITH 'sh85008180|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101277' OR child.lcsh_id STARTS WITH 'sh85101277|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101206' OR parent.lcsh_id STARTS WITH 'sh85101206|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85039316' OR child.lcsh_id STARTS WITH 'sh85039316|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077507' OR parent.lcsh_id STARTS WITH 'sh85077507|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85039408' OR child.lcsh_id STARTS WITH 'sh85039408|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85007461' OR parent.lcsh_id STARTS WITH 'sh85007461|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85039408' OR child.lcsh_id STARTS WITH 'sh85039408|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85056474' OR parent.lcsh_id STARTS WITH 'sh85056474|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85039408' OR child.lcsh_id STARTS WITH 'sh85039408|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85064408' OR parent.lcsh_id STARTS WITH 'sh85064408|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85039408' OR child.lcsh_id STARTS WITH 'sh85039408|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080653' OR parent.lcsh_id STARTS WITH 'sh85080653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053976' OR child.lcsh_id STARTS WITH 'sh85053976|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054185' OR parent.lcsh_id STARTS WITH 'sh85054185|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040311' OR child.lcsh_id STARTS WITH 'sh85040311|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084334' OR parent.lcsh_id STARTS WITH 'sh85084334|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87007854' OR child.lcsh_id STARTS WITH 'sh87007854|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040490' OR child.lcsh_id STARTS WITH 'sh85040490|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026331' OR parent.lcsh_id STARTS WITH 'sh85026331|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040490' OR child.lcsh_id STARTS WITH 'sh85040490|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040490' OR child.lcsh_id STARTS WITH 'sh85040490|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043221' OR parent.lcsh_id STARTS WITH 'sh85043221|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040680' OR child.lcsh_id STARTS WITH 'sh85040680|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85025728' OR parent.lcsh_id STARTS WITH 'sh85025728|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040680' OR child.lcsh_id STARTS WITH 'sh85040680|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85112661' OR parent.lcsh_id STARTS WITH 'sh85112661|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040680' OR child.lcsh_id STARTS WITH 'sh85040680|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85134705' OR parent.lcsh_id STARTS WITH 'sh85134705|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040752' OR child.lcsh_id STARTS WITH 'sh85040752|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040752' OR child.lcsh_id STARTS WITH 'sh85040752|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh92004048' OR parent.lcsh_id STARTS WITH 'sh92004048|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040766' OR child.lcsh_id STARTS WITH 'sh85040766|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040766' OR child.lcsh_id STARTS WITH 'sh85040766|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85045198' OR parent.lcsh_id STARTS WITH 'sh85045198|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054016' OR child.lcsh_id STARTS WITH 'sh85054016|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053986' OR parent.lcsh_id STARTS WITH 'sh85053986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054085' OR child.lcsh_id STARTS WITH 'sh85054085|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101560' OR parent.lcsh_id STARTS WITH 'sh85101560|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040817' OR child.lcsh_id STARTS WITH 'sh85040817|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040837' OR child.lcsh_id STARTS WITH 'sh85040837|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040837' OR child.lcsh_id STARTS WITH 'sh85040837|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85102696' OR parent.lcsh_id STARTS WITH 'sh85102696|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107209' OR child.lcsh_id STARTS WITH 'sh85107209|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084819' OR parent.lcsh_id STARTS WITH 'sh85084819|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107209' OR child.lcsh_id STARTS WITH 'sh85107209|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85130690' OR parent.lcsh_id STARTS WITH 'sh85130690|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040850' OR child.lcsh_id STARTS WITH 'sh85040850|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124003' OR parent.lcsh_id STARTS WITH 'sh85124003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85011609' OR child.lcsh_id STARTS WITH 'sh85011609|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85048256' OR parent.lcsh_id STARTS WITH 'sh85048256|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85011609' OR child.lcsh_id STARTS WITH 'sh85011609|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85048306' OR parent.lcsh_id STARTS WITH 'sh85048306|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91006274' OR child.lcsh_id STARTS WITH 'sh91006274|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91006274' OR child.lcsh_id STARTS WITH 'sh91006274|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101679' OR parent.lcsh_id STARTS WITH 'sh85101679|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93001294' OR child.lcsh_id STARTS WITH 'sh93001294|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh96009482' OR parent.lcsh_id STARTS WITH 'sh96009482|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93001294' OR child.lcsh_id STARTS WITH 'sh93001294|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh95010683' OR parent.lcsh_id STARTS WITH 'sh95010683|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93001294' OR child.lcsh_id STARTS WITH 'sh93001294|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090284' OR parent.lcsh_id STARTS WITH 'sh85090284|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85040989' OR child.lcsh_id STARTS WITH 'sh85040989|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026423' OR parent.lcsh_id STARTS WITH 'sh85026423|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041108' OR child.lcsh_id STARTS WITH 'sh85041108|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041108' OR child.lcsh_id STARTS WITH 'sh85041108|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85034755' OR parent.lcsh_id STARTS WITH 'sh85034755|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041108' OR child.lcsh_id STARTS WITH 'sh85041108|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85041014' OR parent.lcsh_id STARTS WITH 'sh85041014|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041141' OR child.lcsh_id STARTS WITH 'sh85041141|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041254' OR child.lcsh_id STARTS WITH 'sh85041254|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100113' OR parent.lcsh_id STARTS WITH 'sh85100113|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041254' OR child.lcsh_id STARTS WITH 'sh85041254|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108411' OR parent.lcsh_id STARTS WITH 'sh85108411|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041254' OR child.lcsh_id STARTS WITH 'sh85041254|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041254' OR child.lcsh_id STARTS WITH 'sh85041254|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119708' OR parent.lcsh_id STARTS WITH 'sh85119708|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041666' OR child.lcsh_id STARTS WITH 'sh85041666|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85042383' OR child.lcsh_id STARTS WITH 'sh85042383|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85041666' OR parent.lcsh_id STARTS WITH 'sh85041666|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85042383' OR child.lcsh_id STARTS WITH 'sh85042383|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89005705' OR parent.lcsh_id STARTS WITH 'sh89005705|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85043147' OR child.lcsh_id STARTS WITH 'sh85043147|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065977' OR parent.lcsh_id STARTS WITH 'sh85065977|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85043249' OR child.lcsh_id STARTS WITH 'sh85043249|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2007000310' OR parent.lcsh_id STARTS WITH 'sh2007000310|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85043176' OR child.lcsh_id STARTS WITH 'sh85043176|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065826' OR parent.lcsh_id STARTS WITH 'sh85065826|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85043176' OR child.lcsh_id STARTS WITH 'sh85043176|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85133147' OR parent.lcsh_id STARTS WITH 'sh85133147|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044125' OR child.lcsh_id STARTS WITH 'sh85044125|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85149983' OR parent.lcsh_id STARTS WITH 'sh85149983|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044168' OR child.lcsh_id STARTS WITH 'sh85044168|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044168' OR child.lcsh_id STARTS WITH 'sh85044168|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93004763' OR child.lcsh_id STARTS WITH 'sh93004763|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044169' OR child.lcsh_id STARTS WITH 'sh85044169|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044170' OR child.lcsh_id STARTS WITH 'sh85044170|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95010683' OR child.lcsh_id STARTS WITH 'sh95010683|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh92004048' OR parent.lcsh_id STARTS WITH 'sh92004048|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95010683' OR child.lcsh_id STARTS WITH 'sh95010683|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080336' OR parent.lcsh_id STARTS WITH 'sh85080336|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92004048' OR child.lcsh_id STARTS WITH 'sh92004048|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96003462' OR child.lcsh_id STARTS WITH 'sh96003462|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85044173' OR parent.lcsh_id STARTS WITH 'sh85044173|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96003462' OR child.lcsh_id STARTS WITH 'sh96003462|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85136331' OR parent.lcsh_id STARTS WITH 'sh85136331|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96010093' OR child.lcsh_id STARTS WITH 'sh96010093|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014171' OR parent.lcsh_id STARTS WITH 'sh85014171|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044373' OR child.lcsh_id STARTS WITH 'sh85044373|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108638' OR parent.lcsh_id STARTS WITH 'sh85108638|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85072732' OR child.lcsh_id STARTS WITH 'sh85072732|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85072732' OR child.lcsh_id STARTS WITH 'sh85072732|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044600' OR child.lcsh_id STARTS WITH 'sh85044600|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85057508' OR parent.lcsh_id STARTS WITH 'sh85057508|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044600' OR child.lcsh_id STARTS WITH 'sh85044600|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082129' OR parent.lcsh_id STARTS WITH 'sh85082129|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044600' OR child.lcsh_id STARTS WITH 'sh85044600|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082702' OR parent.lcsh_id STARTS WITH 'sh85082702|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85044600' OR child.lcsh_id STARTS WITH 'sh85044600|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85136920' OR parent.lcsh_id STARTS WITH 'sh85136920|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85045096' OR child.lcsh_id STARTS WITH 'sh85045096|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85045198' OR child.lcsh_id STARTS WITH 'sh85045198|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85045198' OR child.lcsh_id STARTS WITH 'sh85045198|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080292' OR parent.lcsh_id STARTS WITH 'sh85080292|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85045425' OR child.lcsh_id STARTS WITH 'sh85045425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85045421' OR child.lcsh_id STARTS WITH 'sh85045421|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85045198' OR parent.lcsh_id STARTS WITH 'sh85045198|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85045421' OR child.lcsh_id STARTS WITH 'sh85045421|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85089048' OR parent.lcsh_id STARTS WITH 'sh85089048|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85045926' OR child.lcsh_id STARTS WITH 'sh85045926|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85113021' OR parent.lcsh_id STARTS WITH 'sh85113021|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046029' OR child.lcsh_id STARTS WITH 'sh85046029|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh90004042' OR child.lcsh_id STARTS WITH 'sh90004042|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh90004042' OR child.lcsh_id STARTS WITH 'sh90004042|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85046029' OR parent.lcsh_id STARTS WITH 'sh85046029|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046244' OR child.lcsh_id STARTS WITH 'sh85046244|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023027' OR parent.lcsh_id STARTS WITH 'sh85023027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126898' OR child.lcsh_id STARTS WITH 'sh85126898|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh86000064' OR parent.lcsh_id STARTS WITH 'sh86000064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046374' OR child.lcsh_id STARTS WITH 'sh85046374|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85046376' OR parent.lcsh_id STARTS WITH 'sh85046376|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046374' OR child.lcsh_id STARTS WITH 'sh85046374|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100683' OR parent.lcsh_id STARTS WITH 'sh85100683|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046374' OR child.lcsh_id STARTS WITH 'sh85046374|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108411' OR parent.lcsh_id STARTS WITH 'sh85108411|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046433' OR child.lcsh_id STARTS WITH 'sh85046433|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85072732' OR parent.lcsh_id STARTS WITH 'sh85072732|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046433' OR child.lcsh_id STARTS WITH 'sh85046433|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046433' OR child.lcsh_id STARTS WITH 'sh85046433|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046433' OR child.lcsh_id STARTS WITH 'sh85046433|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85111773' OR parent.lcsh_id STARTS WITH 'sh85111773|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108474' OR child.lcsh_id STARTS WITH 'sh85108474|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108467' OR parent.lcsh_id STARTS WITH 'sh85108467|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046453' OR child.lcsh_id STARTS WITH 'sh85046453|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85072732' OR parent.lcsh_id STARTS WITH 'sh85072732|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046823' OR child.lcsh_id STARTS WITH 'sh85046823|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85046856' OR parent.lcsh_id STARTS WITH 'sh85046856|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046823' OR child.lcsh_id STARTS WITH 'sh85046823|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065835' OR parent.lcsh_id STARTS WITH 'sh85065835|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85047057' OR child.lcsh_id STARTS WITH 'sh85047057|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85047061' OR child.lcsh_id STARTS WITH 'sh85047061|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85047013' OR parent.lcsh_id STARTS WITH 'sh85047013|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85047061' OR child.lcsh_id STARTS WITH 'sh85047061|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85057493' OR parent.lcsh_id STARTS WITH 'sh85057493|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85047061' OR child.lcsh_id STARTS WITH 'sh85047061|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85081466' OR parent.lcsh_id STARTS WITH 'sh85081466|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93006951' OR child.lcsh_id STARTS WITH 'sh93006951|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85047760' OR child.lcsh_id STARTS WITH 'sh85047760|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85047741' OR parent.lcsh_id STARTS WITH 'sh85047741|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85047760' OR child.lcsh_id STARTS WITH 'sh85047760|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108516' OR parent.lcsh_id STARTS WITH 'sh85108516|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85047932' OR child.lcsh_id STARTS WITH 'sh85047932|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85035979' OR parent.lcsh_id STARTS WITH 'sh85035979|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85047932' OR child.lcsh_id STARTS WITH 'sh85047932|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080593' OR parent.lcsh_id STARTS WITH 'sh85080593|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85048050' OR child.lcsh_id STARTS WITH 'sh85048050|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077507' OR parent.lcsh_id STARTS WITH 'sh85077507|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85048256' OR child.lcsh_id STARTS WITH 'sh85048256|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101269' OR child.lcsh_id STARTS WITH 'sh85101269|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85007461' OR parent.lcsh_id STARTS WITH 'sh85007461|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85048479' OR child.lcsh_id STARTS WITH 'sh85048479|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85048800' OR child.lcsh_id STARTS WITH 'sh85048800|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85048793' OR parent.lcsh_id STARTS WITH 'sh85048793|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2005020061' OR child.lcsh_id STARTS WITH 'sh2005020061|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006246' OR parent.lcsh_id STARTS WITH 'sh85006246|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85048666' OR child.lcsh_id STARTS WITH 'sh85048666|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006210' OR parent.lcsh_id STARTS WITH 'sh85006210|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85048666' OR child.lcsh_id STARTS WITH 'sh85048666|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh96005610' OR parent.lcsh_id STARTS WITH 'sh96005610|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85049342' OR child.lcsh_id STARTS WITH 'sh85049342|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015992' OR parent.lcsh_id STARTS WITH 'sh85015992|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85049383' OR child.lcsh_id STARTS WITH 'sh85049383|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85031576' OR parent.lcsh_id STARTS WITH 'sh85031576|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050104' OR child.lcsh_id STARTS WITH 'sh85050104|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85045198' OR parent.lcsh_id STARTS WITH 'sh85045198|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050104' OR child.lcsh_id STARTS WITH 'sh85050104|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080593' OR parent.lcsh_id STARTS WITH 'sh85080593|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050150' OR child.lcsh_id STARTS WITH 'sh85050150|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85050104' OR parent.lcsh_id STARTS WITH 'sh85050104|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2018000786' OR child.lcsh_id STARTS WITH 'sh2018000786|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022900' OR parent.lcsh_id STARTS WITH 'sh85022900|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050537' OR child.lcsh_id STARTS WITH 'sh85050537|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh90001487' OR parent.lcsh_id STARTS WITH 'sh90001487|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050537' OR child.lcsh_id STARTS WITH 'sh85050537|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2021003625' OR child.lcsh_id STARTS WITH 'sh2021003625|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh90001487' OR parent.lcsh_id STARTS WITH 'sh90001487|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2021003625' OR child.lcsh_id STARTS WITH 'sh2021003625|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85050707' OR parent.lcsh_id STARTS WITH 'sh85050707|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh90001487' OR child.lcsh_id STARTS WITH 'sh90001487|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050567' OR child.lcsh_id STARTS WITH 'sh85050567|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090284' OR parent.lcsh_id STARTS WITH 'sh85090284|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050575' OR child.lcsh_id STARTS WITH 'sh85050575|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85063461' OR child.lcsh_id STARTS WITH 'sh85063461|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85063458' OR parent.lcsh_id STARTS WITH 'sh85063458|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050707' OR child.lcsh_id STARTS WITH 'sh85050707|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85002415' OR parent.lcsh_id STARTS WITH 'sh85002415|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050707' OR child.lcsh_id STARTS WITH 'sh85050707|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090254' OR parent.lcsh_id STARTS WITH 'sh85090254|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050802' OR child.lcsh_id STARTS WITH 'sh85050802|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85050812' OR parent.lcsh_id STARTS WITH 'sh85050812|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050802' OR child.lcsh_id STARTS WITH 'sh85050802|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074518' OR parent.lcsh_id STARTS WITH 'sh85074518|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85050802' OR child.lcsh_id STARTS WITH 'sh85050802|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079341' OR parent.lcsh_id STARTS WITH 'sh85079341|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85051943' OR child.lcsh_id STARTS WITH 'sh85051943|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006231' OR parent.lcsh_id STARTS WITH 'sh85006231|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85051944' OR child.lcsh_id STARTS WITH 'sh85051944|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006232' OR parent.lcsh_id STARTS WITH 'sh85006232|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85052162' OR child.lcsh_id STARTS WITH 'sh85052162|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053089' OR parent.lcsh_id STARTS WITH 'sh85053089|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85052162' OR child.lcsh_id STARTS WITH 'sh85052162|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062204' OR parent.lcsh_id STARTS WITH 'sh85062204|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85052312' OR child.lcsh_id STARTS WITH 'sh85052312|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85018809' OR parent.lcsh_id STARTS WITH 'sh85018809|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006028' OR child.lcsh_id STARTS WITH 'sh85006028|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85112735' OR parent.lcsh_id STARTS WITH 'sh85112735|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85006028' OR child.lcsh_id STARTS WITH 'sh85006028|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85134665' OR parent.lcsh_id STARTS WITH 'sh85134665|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053291' OR child.lcsh_id STARTS WITH 'sh85053291|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85049376' OR parent.lcsh_id STARTS WITH 'sh85049376|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053291' OR child.lcsh_id STARTS WITH 'sh85053291|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85134783' OR parent.lcsh_id STARTS WITH 'sh85134783|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053479' OR child.lcsh_id STARTS WITH 'sh85053479|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067347' OR parent.lcsh_id STARTS WITH 'sh85067347|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053712' OR child.lcsh_id STARTS WITH 'sh85053712|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85036229' OR parent.lcsh_id STARTS WITH 'sh85036229|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053853' OR child.lcsh_id STARTS WITH 'sh85053853|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85059536' OR parent.lcsh_id STARTS WITH 'sh85059536|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053877' OR child.lcsh_id STARTS WITH 'sh85053877|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053877' OR child.lcsh_id STARTS WITH 'sh85053877|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042722' OR parent.lcsh_id STARTS WITH 'sh85042722|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053877' OR child.lcsh_id STARTS WITH 'sh85053877|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083538' OR parent.lcsh_id STARTS WITH 'sh85083538|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2002000809' OR child.lcsh_id STARTS WITH 'sh2002000809|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85086586' OR parent.lcsh_id STARTS WITH 'sh85086586|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053960' OR child.lcsh_id STARTS WITH 'sh85053960|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053960' OR child.lcsh_id STARTS WITH 'sh85053960|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040468' OR parent.lcsh_id STARTS WITH 'sh85040468|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85053969' OR child.lcsh_id STARTS WITH 'sh85053969|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054185' OR parent.lcsh_id STARTS WITH 'sh85054185|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2015002292' OR child.lcsh_id STARTS WITH 'sh2015002292|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89003285' OR parent.lcsh_id STARTS WITH 'sh89003285|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2015002292' OR child.lcsh_id STARTS WITH 'sh2015002292|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2015003033' OR parent.lcsh_id STARTS WITH 'sh2015003033|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054037' OR child.lcsh_id STARTS WITH 'sh85054037|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040468' OR parent.lcsh_id STARTS WITH 'sh85040468|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054037' OR child.lcsh_id STARTS WITH 'sh85054037|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090222' OR parent.lcsh_id STARTS WITH 'sh85090222|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85078856' OR child.lcsh_id STARTS WITH 'sh85078856|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh88000316' OR parent.lcsh_id STARTS WITH 'sh88000316|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054133' OR child.lcsh_id STARTS WITH 'sh85054133|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082139' OR parent.lcsh_id STARTS WITH 'sh85082139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054165' OR child.lcsh_id STARTS WITH 'sh85054165|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101552' OR parent.lcsh_id STARTS WITH 'sh85101552|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054185' OR child.lcsh_id STARTS WITH 'sh85054185|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040468' OR parent.lcsh_id STARTS WITH 'sh85040468|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054185' OR child.lcsh_id STARTS WITH 'sh85054185|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2013000289' OR child.lcsh_id STARTS WITH 'sh2013000289|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043221' OR parent.lcsh_id STARTS WITH 'sh85043221|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054271' OR child.lcsh_id STARTS WITH 'sh85054271|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090254' OR parent.lcsh_id STARTS WITH 'sh85090254|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054271' OR child.lcsh_id STARTS WITH 'sh85054271|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85105992' OR parent.lcsh_id STARTS WITH 'sh85105992|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054724' OR child.lcsh_id STARTS WITH 'sh85054724|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108516' OR parent.lcsh_id STARTS WITH 'sh85108516|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85055077' OR child.lcsh_id STARTS WITH 'sh85055077|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054037' OR parent.lcsh_id STARTS WITH 'sh85054037|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85055077' OR child.lcsh_id STARTS WITH 'sh85055077|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85063458' OR parent.lcsh_id STARTS WITH 'sh85063458|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85055284' OR child.lcsh_id STARTS WITH 'sh85055284|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85037923' OR parent.lcsh_id STARTS WITH 'sh85037923|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85055284' OR child.lcsh_id STARTS WITH 'sh85055284|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85052356' OR parent.lcsh_id STARTS WITH 'sh85052356|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85055284' OR child.lcsh_id STARTS WITH 'sh85055284|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054140' OR parent.lcsh_id STARTS WITH 'sh85054140|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85148199' OR child.lcsh_id STARTS WITH 'sh85148199|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108638' OR parent.lcsh_id STARTS WITH 'sh85108638|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh99010179' OR child.lcsh_id STARTS WITH 'sh99010179|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067435' OR parent.lcsh_id STARTS WITH 'sh85067435|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85055892' OR child.lcsh_id STARTS WITH 'sh85055892|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85018260' OR parent.lcsh_id STARTS WITH 'sh85018260|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85055892' OR child.lcsh_id STARTS WITH 'sh85055892|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067082' OR parent.lcsh_id STARTS WITH 'sh85067082|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85056099' OR child.lcsh_id STARTS WITH 'sh85056099|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85109163' OR parent.lcsh_id STARTS WITH 'sh85109163|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85056471' OR child.lcsh_id STARTS WITH 'sh85056471|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85028802' OR parent.lcsh_id STARTS WITH 'sh85028802|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85056471' OR child.lcsh_id STARTS WITH 'sh85056471|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85136089' OR parent.lcsh_id STARTS WITH 'sh85136089|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85056474' OR child.lcsh_id STARTS WITH 'sh85056474|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85007461' OR parent.lcsh_id STARTS WITH 'sh85007461|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85056474' OR child.lcsh_id STARTS WITH 'sh85056474|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85143917' OR parent.lcsh_id STARTS WITH 'sh85143917|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85057493' OR child.lcsh_id STARTS WITH 'sh85057493|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108516' OR parent.lcsh_id STARTS WITH 'sh85108516|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85058092' OR child.lcsh_id STARTS WITH 'sh85058092|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91001894' OR child.lcsh_id STARTS WITH 'sh91001894|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090284' OR parent.lcsh_id STARTS WITH 'sh85090284|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85058192' OR child.lcsh_id STARTS WITH 'sh85058192|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85068457' OR parent.lcsh_id STARTS WITH 'sh85068457|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85058192' OR child.lcsh_id STARTS WITH 'sh85058192|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85068461' OR parent.lcsh_id STARTS WITH 'sh85068461|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85058939' OR child.lcsh_id STARTS WITH 'sh85058939|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85011437' OR parent.lcsh_id STARTS WITH 'sh85011437|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85058939' OR child.lcsh_id STARTS WITH 'sh85058939|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85018802' OR parent.lcsh_id STARTS WITH 'sh85018802|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85058939' OR child.lcsh_id STARTS WITH 'sh85058939|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082116' OR parent.lcsh_id STARTS WITH 'sh85082116|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85058939' OR child.lcsh_id STARTS WITH 'sh85058939|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082139' OR parent.lcsh_id STARTS WITH 'sh85082139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85059518' OR child.lcsh_id STARTS WITH 'sh85059518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85059518' OR child.lcsh_id STARTS WITH 'sh85059518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101679' OR parent.lcsh_id STARTS WITH 'sh85101679|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh00005607' OR child.lcsh_id STARTS WITH 'sh00005607|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2001008792' OR parent.lcsh_id STARTS WITH 'sh2001008792|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh89005069' OR child.lcsh_id STARTS WITH 'sh89005069|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066150' OR parent.lcsh_id STARTS WITH 'sh85066150|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh89005069' OR child.lcsh_id STARTS WITH 'sh89005069|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083074' OR parent.lcsh_id STARTS WITH 'sh85083074|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85083002' OR child.lcsh_id STARTS WITH 'sh85083002|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118622' OR parent.lcsh_id STARTS WITH 'sh85118622|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85083002' OR child.lcsh_id STARTS WITH 'sh85083002|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85123985' OR parent.lcsh_id STARTS WITH 'sh85123985|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86007745' OR child.lcsh_id STARTS WITH 'sh86007745|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85027067' OR parent.lcsh_id STARTS WITH 'sh85027067|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86007745' OR child.lcsh_id STARTS WITH 'sh86007745|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083185' OR parent.lcsh_id STARTS WITH 'sh85083185|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009496' OR child.lcsh_id STARTS WITH 'sh85009496|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85059612' OR parent.lcsh_id STARTS WITH 'sh85059612|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85009496' OR child.lcsh_id STARTS WITH 'sh85009496|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85099708' OR parent.lcsh_id STARTS WITH 'sh85099708|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85060075' OR child.lcsh_id STARTS WITH 'sh85060075|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85149983' OR parent.lcsh_id STARTS WITH 'sh85149983|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85060103' OR child.lcsh_id STARTS WITH 'sh85060103|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062839' OR parent.lcsh_id STARTS WITH 'sh85062839|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85060103' OR child.lcsh_id STARTS WITH 'sh85060103|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067484' OR parent.lcsh_id STARTS WITH 'sh85067484|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85060130' OR child.lcsh_id STARTS WITH 'sh85060130|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067347' OR parent.lcsh_id STARTS WITH 'sh85067347|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88007874' OR child.lcsh_id STARTS WITH 'sh88007874|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85060196' OR parent.lcsh_id STARTS WITH 'sh85060196|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88007874' OR child.lcsh_id STARTS WITH 'sh88007874|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85113620' OR parent.lcsh_id STARTS WITH 'sh85113620|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85060464' OR child.lcsh_id STARTS WITH 'sh85060464|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85149983' OR parent.lcsh_id STARTS WITH 'sh85149983|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061084' OR child.lcsh_id STARTS WITH 'sh85061084|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85004835' OR parent.lcsh_id STARTS WITH 'sh85004835|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061091' OR child.lcsh_id STARTS WITH 'sh85061091|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118236' OR parent.lcsh_id STARTS WITH 'sh85118236|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2020008754' OR child.lcsh_id STARTS WITH 'sh2020008754|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89003980' OR parent.lcsh_id STARTS WITH 'sh89003980|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061211' OR child.lcsh_id STARTS WITH 'sh85061211|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85010030' OR parent.lcsh_id STARTS WITH 'sh85010030|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077519' OR child.lcsh_id STARTS WITH 'sh85077519|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85034149' OR parent.lcsh_id STARTS WITH 'sh85034149|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077519' OR child.lcsh_id STARTS WITH 'sh85077519|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85129379' OR parent.lcsh_id STARTS WITH 'sh85129379|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061308' OR child.lcsh_id STARTS WITH 'sh85061308|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85004709' OR parent.lcsh_id STARTS WITH 'sh85004709|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061308' OR child.lcsh_id STARTS WITH 'sh85061308|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85028263' OR parent.lcsh_id STARTS WITH 'sh85028263|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061308' OR child.lcsh_id STARTS WITH 'sh85061308|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85075925' OR parent.lcsh_id STARTS WITH 'sh85075925|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061308' OR child.lcsh_id STARTS WITH 'sh85061308|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85103365' OR parent.lcsh_id STARTS WITH 'sh85103365|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061308' OR child.lcsh_id STARTS WITH 'sh85061308|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85111945' OR parent.lcsh_id STARTS WITH 'sh85111945|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061673' OR child.lcsh_id STARTS WITH 'sh85061673|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85047054' OR parent.lcsh_id STARTS WITH 'sh85047054|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061673' OR child.lcsh_id STARTS WITH 'sh85061673|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061657' OR parent.lcsh_id STARTS WITH 'sh85061657|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062868' OR child.lcsh_id STARTS WITH 'sh85062868|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh90004042' OR parent.lcsh_id STARTS WITH 'sh90004042|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062868' OR child.lcsh_id STARTS WITH 'sh85062868|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101512' OR parent.lcsh_id STARTS WITH 'sh85101512|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88006552' OR child.lcsh_id STARTS WITH 'sh88006552|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85038376' OR parent.lcsh_id STARTS WITH 'sh85038376|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88006552' OR child.lcsh_id STARTS WITH 'sh88006552|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101017' OR parent.lcsh_id STARTS WITH 'sh85101017|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062204' OR child.lcsh_id STARTS WITH 'sh85062204|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85002415' OR parent.lcsh_id STARTS WITH 'sh85002415|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062839' OR child.lcsh_id STARTS WITH 'sh85062839|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062843' OR parent.lcsh_id STARTS WITH 'sh85062843|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062839' OR child.lcsh_id STARTS WITH 'sh85062839|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101512' OR parent.lcsh_id STARTS WITH 'sh85101512|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062839' OR child.lcsh_id STARTS WITH 'sh85062839|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062839' OR child.lcsh_id STARTS WITH 'sh85062839|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124003' OR parent.lcsh_id STARTS WITH 'sh85124003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062843' OR child.lcsh_id STARTS WITH 'sh85062843|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062856' OR child.lcsh_id STARTS WITH 'sh85062856|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005570' OR child.lcsh_id STARTS WITH 'sh85005570|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005570' OR child.lcsh_id STARTS WITH 'sh85005570|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053986' OR parent.lcsh_id STARTS WITH 'sh85053986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062884' OR child.lcsh_id STARTS WITH 'sh85062884|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062843' OR parent.lcsh_id STARTS WITH 'sh85062843|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062884' OR child.lcsh_id STARTS WITH 'sh85062884|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083022' OR parent.lcsh_id STARTS WITH 'sh85083022|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062884' OR child.lcsh_id STARTS WITH 'sh85062884|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101679' OR parent.lcsh_id STARTS WITH 'sh85101679|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100143' OR child.lcsh_id STARTS WITH 'sh85100143|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080336' OR parent.lcsh_id STARTS WITH 'sh85080336|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100143' OR child.lcsh_id STARTS WITH 'sh85100143|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108611' OR parent.lcsh_id STARTS WITH 'sh85108611|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062913' OR child.lcsh_id STARTS WITH 'sh85062913|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85075529' OR parent.lcsh_id STARTS WITH 'sh85075529|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88003229' OR child.lcsh_id STARTS WITH 'sh88003229|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062867' OR parent.lcsh_id STARTS WITH 'sh85062867|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85063305' OR child.lcsh_id STARTS WITH 'sh85063305|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85063305' OR child.lcsh_id STARTS WITH 'sh85063305|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85049383' OR parent.lcsh_id STARTS WITH 'sh85049383|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85145539' OR child.lcsh_id STARTS WITH 'sh85145539|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053960' OR parent.lcsh_id STARTS WITH 'sh85053960|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85145539' OR child.lcsh_id STARTS WITH 'sh85145539|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85063458' OR parent.lcsh_id STARTS WITH 'sh85063458|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85063439' OR child.lcsh_id STARTS WITH 'sh85063439|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054037' OR parent.lcsh_id STARTS WITH 'sh85054037|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85063439' OR child.lcsh_id STARTS WITH 'sh85063439|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85063458' OR parent.lcsh_id STARTS WITH 'sh85063458|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85063443' OR child.lcsh_id STARTS WITH 'sh85063443|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006246' OR parent.lcsh_id STARTS WITH 'sh85006246|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85063443' OR child.lcsh_id STARTS WITH 'sh85063443|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090425' OR parent.lcsh_id STARTS WITH 'sh85090425|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85063326' OR child.lcsh_id STARTS WITH 'sh85063326|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101564' OR parent.lcsh_id STARTS WITH 'sh85101564|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85064050' OR child.lcsh_id STARTS WITH 'sh85064050|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85149983' OR parent.lcsh_id STARTS WITH 'sh85149983|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85064120' OR child.lcsh_id STARTS WITH 'sh85064120|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85072732' OR parent.lcsh_id STARTS WITH 'sh85072732|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85064120' OR child.lcsh_id STARTS WITH 'sh85064120|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh99001255' OR child.lcsh_id STARTS WITH 'sh99001255|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh99001272' OR parent.lcsh_id STARTS WITH 'sh99001272|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86002614' OR child.lcsh_id STARTS WITH 'sh86002614|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85064579' OR parent.lcsh_id STARTS WITH 'sh85064579|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108476' OR child.lcsh_id STARTS WITH 'sh85108476|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065864' OR parent.lcsh_id STARTS WITH 'sh85065864|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108476' OR child.lcsh_id STARTS WITH 'sh85108476|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100143' OR parent.lcsh_id STARTS WITH 'sh85100143|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108476' OR child.lcsh_id STARTS WITH 'sh85108476|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108472' OR parent.lcsh_id STARTS WITH 'sh85108472|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037199' OR child.lcsh_id STARTS WITH 'sh85037199|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85037197' OR parent.lcsh_id STARTS WITH 'sh85037197|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85065864' OR child.lcsh_id STARTS WITH 'sh85065864|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh97001369' OR child.lcsh_id STARTS WITH 'sh97001369|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065960' OR parent.lcsh_id STARTS WITH 'sh85065960|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85065909' OR child.lcsh_id STARTS WITH 'sh85065909|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084819' OR parent.lcsh_id STARTS WITH 'sh85084819|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87002293' OR child.lcsh_id STARTS WITH 'sh87002293|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85133147' OR parent.lcsh_id STARTS WITH 'sh85133147|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87002293' OR child.lcsh_id STARTS WITH 'sh87002293|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89005491' OR parent.lcsh_id STARTS WITH 'sh89005491|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85066147' OR child.lcsh_id STARTS WITH 'sh85066147|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080336' OR parent.lcsh_id STARTS WITH 'sh85080336|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2021005721' OR child.lcsh_id STARTS WITH 'sh2021005721|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066147' OR parent.lcsh_id STARTS WITH 'sh85066147|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2021005721' OR child.lcsh_id STARTS WITH 'sh2021005721|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85107027' OR parent.lcsh_id STARTS WITH 'sh85107027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85066148' OR child.lcsh_id STARTS WITH 'sh85066148|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85038731' OR parent.lcsh_id STARTS WITH 'sh85038731|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85066148' OR child.lcsh_id STARTS WITH 'sh85066148|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066150' OR parent.lcsh_id STARTS WITH 'sh85066150|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85066150' OR child.lcsh_id STARTS WITH 'sh85066150|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85066163' OR child.lcsh_id STARTS WITH 'sh85066163|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh98003200' OR parent.lcsh_id STARTS WITH 'sh98003200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85066163' OR child.lcsh_id STARTS WITH 'sh85066163|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh97001717' OR parent.lcsh_id STARTS WITH 'sh97001717|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023017' OR child.lcsh_id STARTS WITH 'sh85023017|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85066745' OR child.lcsh_id STARTS WITH 'sh85066745|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85067088' OR child.lcsh_id STARTS WITH 'sh85067088|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85052317' OR parent.lcsh_id STARTS WITH 'sh85052317|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85067167' OR child.lcsh_id STARTS WITH 'sh85067167|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067082' OR parent.lcsh_id STARTS WITH 'sh85067082|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85062836' OR child.lcsh_id STARTS WITH 'sh85062836|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85025083' OR parent.lcsh_id STARTS WITH 'sh85025083|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85067222' OR child.lcsh_id STARTS WITH 'sh85067222|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85067222' OR child.lcsh_id STARTS WITH 'sh85067222|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85034755' OR parent.lcsh_id STARTS WITH 'sh85034755|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85067347' OR child.lcsh_id STARTS WITH 'sh85067347|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029042' OR child.lcsh_id STARTS WITH 'sh85029042|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85067395' OR child.lcsh_id STARTS WITH 'sh85067395|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040837' OR parent.lcsh_id STARTS WITH 'sh85040837|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85067395' OR child.lcsh_id STARTS WITH 'sh85067395|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067435' OR parent.lcsh_id STARTS WITH 'sh85067435|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85067417' OR child.lcsh_id STARTS WITH 'sh85067417|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85075119' OR parent.lcsh_id STARTS WITH 'sh85075119|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119471' OR child.lcsh_id STARTS WITH 'sh85119471|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067435' OR parent.lcsh_id STARTS WITH 'sh85067435|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87004890' OR child.lcsh_id STARTS WITH 'sh87004890|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85028901' OR parent.lcsh_id STARTS WITH 'sh85028901|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87004890' OR child.lcsh_id STARTS WITH 'sh87004890|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067395' OR parent.lcsh_id STARTS WITH 'sh85067395|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh94007902' OR child.lcsh_id STARTS WITH 'sh94007902|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029513' OR parent.lcsh_id STARTS WITH 'sh85029513|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85068296' OR child.lcsh_id STARTS WITH 'sh85068296|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85002313' OR parent.lcsh_id STARTS WITH 'sh85002313|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85068296' OR child.lcsh_id STARTS WITH 'sh85068296|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85063305' OR parent.lcsh_id STARTS WITH 'sh85063305|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85069833' OR child.lcsh_id STARTS WITH 'sh85069833|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85001968' OR parent.lcsh_id STARTS WITH 'sh85001968|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85069833' OR child.lcsh_id STARTS WITH 'sh85069833|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85088762' OR parent.lcsh_id STARTS WITH 'sh85088762|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85070643' OR child.lcsh_id STARTS WITH 'sh85070643|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85020430' OR parent.lcsh_id STARTS WITH 'sh85020430|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85070643' OR child.lcsh_id STARTS WITH 'sh85070643|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85148029' OR parent.lcsh_id STARTS WITH 'sh85148029|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85070736' OR child.lcsh_id STARTS WITH 'sh85070736|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077507' OR parent.lcsh_id STARTS WITH 'sh85077507|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85070736' OR child.lcsh_id STARTS WITH 'sh85070736|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108869' OR parent.lcsh_id STARTS WITH 'sh85108869|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85070788' OR child.lcsh_id STARTS WITH 'sh85070788|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85009793' OR parent.lcsh_id STARTS WITH 'sh85009793|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85071077' OR child.lcsh_id STARTS WITH 'sh85071077|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029335' OR parent.lcsh_id STARTS WITH 'sh85029335|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85071077' OR child.lcsh_id STARTS WITH 'sh85071077|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85075119' OR parent.lcsh_id STARTS WITH 'sh85075119|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85071895' OR child.lcsh_id STARTS WITH 'sh85071895|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85081156' OR parent.lcsh_id STARTS WITH 'sh85081156|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85073687' OR child.lcsh_id STARTS WITH 'sh85073687|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95006396' OR child.lcsh_id STARTS WITH 'sh95006396|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090284' OR parent.lcsh_id STARTS WITH 'sh85090284|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95006396' OR child.lcsh_id STARTS WITH 'sh95006396|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85145542' OR parent.lcsh_id STARTS WITH 'sh85145542|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh90002545' OR child.lcsh_id STARTS WITH 'sh90002545|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85074518' OR child.lcsh_id STARTS WITH 'sh85074518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85074518' OR child.lcsh_id STARTS WITH 'sh85074518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85074518' OR child.lcsh_id STARTS WITH 'sh85074518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85045198' OR parent.lcsh_id STARTS WITH 'sh85045198|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85074518' OR child.lcsh_id STARTS WITH 'sh85074518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066289' OR parent.lcsh_id STARTS WITH 'sh85066289|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85074518' OR child.lcsh_id STARTS WITH 'sh85074518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082693' OR parent.lcsh_id STARTS WITH 'sh85082693|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85074518' OR child.lcsh_id STARTS WITH 'sh85074518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100821' OR parent.lcsh_id STARTS WITH 'sh85100821|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95009376' OR child.lcsh_id STARTS WITH 'sh95009376|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95009376' OR child.lcsh_id STARTS WITH 'sh95009376|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85071088' OR parent.lcsh_id STARTS WITH 'sh85071088|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85075351' OR child.lcsh_id STARTS WITH 'sh85075351|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100163' OR parent.lcsh_id STARTS WITH 'sh85100163|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85075480' OR child.lcsh_id STARTS WITH 'sh85075480|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85000155' OR parent.lcsh_id STARTS WITH 'sh85000155|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85075520' OR child.lcsh_id STARTS WITH 'sh85075520|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029421' OR parent.lcsh_id STARTS WITH 'sh85029421|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85075520' OR child.lcsh_id STARTS WITH 'sh85075520|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85075292' OR child.lcsh_id STARTS WITH 'sh85075292|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85075292' OR child.lcsh_id STARTS WITH 'sh85075292|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85045195' OR parent.lcsh_id STARTS WITH 'sh85045195|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85075141' OR child.lcsh_id STARTS WITH 'sh85075141|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108472' OR parent.lcsh_id STARTS WITH 'sh85108472|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85076841' OR child.lcsh_id STARTS WITH 'sh85076841|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85076844' OR child.lcsh_id STARTS WITH 'sh85076844|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85000155' OR parent.lcsh_id STARTS WITH 'sh85000155|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85076844' OR child.lcsh_id STARTS WITH 'sh85076844|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85123970' OR parent.lcsh_id STARTS WITH 'sh85123970|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077053' OR child.lcsh_id STARTS WITH 'sh85077053|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006246' OR parent.lcsh_id STARTS WITH 'sh85006246|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2013002090' OR child.lcsh_id STARTS WITH 'sh2013002090|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh96000740' OR parent.lcsh_id STARTS WITH 'sh96000740|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2013002090' OR child.lcsh_id STARTS WITH 'sh2013002090|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2002000569' OR parent.lcsh_id STARTS WITH 'sh2002000569|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077455' OR child.lcsh_id STARTS WITH 'sh85077455|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042288' OR parent.lcsh_id STARTS WITH 'sh85042288|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077455' OR child.lcsh_id STARTS WITH 'sh85077455|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85048195' OR parent.lcsh_id STARTS WITH 'sh85048195|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077455' OR child.lcsh_id STARTS WITH 'sh85077455|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85125332' OR parent.lcsh_id STARTS WITH 'sh85125332|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029406' OR child.lcsh_id STARTS WITH 'sh85029406|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074546' OR parent.lcsh_id STARTS WITH 'sh85074546|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034149' OR child.lcsh_id STARTS WITH 'sh85034149|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077507' OR parent.lcsh_id STARTS WITH 'sh85077507|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034149' OR child.lcsh_id STARTS WITH 'sh85034149|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85113628' OR parent.lcsh_id STARTS WITH 'sh85113628|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077509' OR child.lcsh_id STARTS WITH 'sh85077509|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85001441' OR parent.lcsh_id STARTS WITH 'sh85001441|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85077507' OR child.lcsh_id STARTS WITH 'sh85077507|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100821' OR parent.lcsh_id STARTS WITH 'sh85100821|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2011000728' OR child.lcsh_id STARTS WITH 'sh2011000728|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040430' OR parent.lcsh_id STARTS WITH 'sh85040430|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2011000728' OR child.lcsh_id STARTS WITH 'sh2011000728|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040438' OR parent.lcsh_id STARTS WITH 'sh85040438|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85078106' OR child.lcsh_id STARTS WITH 'sh85078106|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067157' OR parent.lcsh_id STARTS WITH 'sh85067157|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85078106' OR child.lcsh_id STARTS WITH 'sh85078106|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85078106' OR child.lcsh_id STARTS WITH 'sh85078106|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85078106' OR child.lcsh_id STARTS WITH 'sh85078106|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118577' OR parent.lcsh_id STARTS WITH 'sh85118577|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85078128' OR child.lcsh_id STARTS WITH 'sh85078128|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85085132' OR parent.lcsh_id STARTS WITH 'sh85085132|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85079324' OR child.lcsh_id STARTS WITH 'sh85079324|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85008180' OR parent.lcsh_id STARTS WITH 'sh85008180|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85079324' OR child.lcsh_id STARTS WITH 'sh85079324|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079341' OR parent.lcsh_id STARTS WITH 'sh85079341|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85079443' OR child.lcsh_id STARTS WITH 'sh85079443|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85079784' OR child.lcsh_id STARTS WITH 'sh85079784|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85049376' OR parent.lcsh_id STARTS WITH 'sh85049376|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85079931' OR child.lcsh_id STARTS WITH 'sh85079931|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079930' OR parent.lcsh_id STARTS WITH 'sh85079930|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96010388' OR child.lcsh_id STARTS WITH 'sh96010388|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85149983' OR parent.lcsh_id STARTS WITH 'sh85149983|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85080363' OR child.lcsh_id STARTS WITH 'sh85080363|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080336' OR parent.lcsh_id STARTS WITH 'sh85080336|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85080363' OR child.lcsh_id STARTS WITH 'sh85080363|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85107109' OR parent.lcsh_id STARTS WITH 'sh85107109|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081138' OR child.lcsh_id STARTS WITH 'sh85081138|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006231' OR parent.lcsh_id STARTS WITH 'sh85006231|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081138' OR child.lcsh_id STARTS WITH 'sh85081138|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85081263' OR parent.lcsh_id STARTS WITH 'sh85081263|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91005227' OR child.lcsh_id STARTS WITH 'sh91005227|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh91002611' OR parent.lcsh_id STARTS WITH 'sh91002611|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91005227' OR child.lcsh_id STARTS WITH 'sh91005227|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85081156' OR parent.lcsh_id STARTS WITH 'sh85081156|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081156' OR child.lcsh_id STARTS WITH 'sh85081156|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006232' OR parent.lcsh_id STARTS WITH 'sh85006232|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081193' OR child.lcsh_id STARTS WITH 'sh85081193|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054185' OR parent.lcsh_id STARTS WITH 'sh85054185|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081193' OR child.lcsh_id STARTS WITH 'sh85081193|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85093880' OR parent.lcsh_id STARTS WITH 'sh85093880|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081193' OR child.lcsh_id STARTS WITH 'sh85081193|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85129495' OR parent.lcsh_id STARTS WITH 'sh85129495|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh98000806' OR child.lcsh_id STARTS WITH 'sh98000806|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh96010388' OR parent.lcsh_id STARTS WITH 'sh96010388|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh98000806' OR child.lcsh_id STARTS WITH 'sh98000806|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85081138' OR parent.lcsh_id STARTS WITH 'sh85081138|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081307' OR child.lcsh_id STARTS WITH 'sh85081307|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081307' OR child.lcsh_id STARTS WITH 'sh85081307|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85045198' OR parent.lcsh_id STARTS WITH 'sh85045198|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081333' OR child.lcsh_id STARTS WITH 'sh85081333|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065889' OR parent.lcsh_id STARTS WITH 'sh85065889|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081339' OR child.lcsh_id STARTS WITH 'sh85081339|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85018306' OR parent.lcsh_id STARTS WITH 'sh85018306|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2006007647' OR child.lcsh_id STARTS WITH 'sh2006007647|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080664' OR parent.lcsh_id STARTS WITH 'sh85080664|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2006007647' OR child.lcsh_id STARTS WITH 'sh2006007647|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85107212' OR parent.lcsh_id STARTS WITH 'sh85107212|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85081863' OR child.lcsh_id STARTS WITH 'sh85081863|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082094' OR child.lcsh_id STARTS WITH 'sh85082094|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89005705' OR parent.lcsh_id STARTS WITH 'sh89005705|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082119' OR child.lcsh_id STARTS WITH 'sh85082119|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082119' OR child.lcsh_id STARTS WITH 'sh85082119|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005583' OR parent.lcsh_id STARTS WITH 'sh85005583|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014235' OR child.lcsh_id STARTS WITH 'sh85014235|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85014235' OR child.lcsh_id STARTS WITH 'sh85014235|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082139' OR parent.lcsh_id STARTS WITH 'sh85082139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082122' OR child.lcsh_id STARTS WITH 'sh85082122|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006168' OR parent.lcsh_id STARTS WITH 'sh85006168|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082122' OR child.lcsh_id STARTS WITH 'sh85082122|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066289' OR parent.lcsh_id STARTS WITH 'sh85066289|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082122' OR child.lcsh_id STARTS WITH 'sh85082122|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077222' OR parent.lcsh_id STARTS WITH 'sh85077222|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85003435' OR child.lcsh_id STARTS WITH 'sh85003435|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85078115' OR parent.lcsh_id STARTS WITH 'sh85078115|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082139' OR child.lcsh_id STARTS WITH 'sh85082139|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082757' OR child.lcsh_id STARTS WITH 'sh85082757|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082767' OR child.lcsh_id STARTS WITH 'sh85082767|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93001518' OR child.lcsh_id STARTS WITH 'sh93001518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082757' OR parent.lcsh_id STARTS WITH 'sh85082757|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93001518' OR child.lcsh_id STARTS WITH 'sh93001518|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084822' OR parent.lcsh_id STARTS WITH 'sh85084822|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96010160' OR child.lcsh_id STARTS WITH 'sh96010160|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh00007046' OR parent.lcsh_id STARTS WITH 'sh00007046|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082846' OR child.lcsh_id STARTS WITH 'sh85082846|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85030958' OR parent.lcsh_id STARTS WITH 'sh85030958|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082859' OR child.lcsh_id STARTS WITH 'sh85082859|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037489' OR child.lcsh_id STARTS WITH 'sh85037489|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083129' OR parent.lcsh_id STARTS WITH 'sh85083129|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037507' OR child.lcsh_id STARTS WITH 'sh85037507|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85037498' OR parent.lcsh_id STARTS WITH 'sh85037498|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85037507' OR child.lcsh_id STARTS WITH 'sh85037507|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85064474' OR parent.lcsh_id STARTS WITH 'sh85064474|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082955' OR child.lcsh_id STARTS WITH 'sh85082955|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh90001487' OR parent.lcsh_id STARTS WITH 'sh90001487|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082955' OR child.lcsh_id STARTS WITH 'sh85082955|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082974' OR child.lcsh_id STARTS WITH 'sh85082974|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083022' OR parent.lcsh_id STARTS WITH 'sh85083022|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082974' OR child.lcsh_id STARTS WITH 'sh85082974|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084783' OR parent.lcsh_id STARTS WITH 'sh85084783|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85083001' OR child.lcsh_id STARTS WITH 'sh85083001|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014253' OR parent.lcsh_id STARTS WITH 'sh85014253|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85083001' OR child.lcsh_id STARTS WITH 'sh85083001|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85083022' OR child.lcsh_id STARTS WITH 'sh85083022|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85076841' OR parent.lcsh_id STARTS WITH 'sh85076841|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85134723' OR child.lcsh_id STARTS WITH 'sh85134723|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083129' OR parent.lcsh_id STARTS WITH 'sh85083129|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85083064' OR child.lcsh_id STARTS WITH 'sh85083064|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062843' OR parent.lcsh_id STARTS WITH 'sh85062843|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85083064' OR child.lcsh_id STARTS WITH 'sh85083064|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85076841' OR parent.lcsh_id STARTS WITH 'sh85076841|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96000740' OR child.lcsh_id STARTS WITH 'sh96000740|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh99001059' OR parent.lcsh_id STARTS WITH 'sh99001059|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084158' OR child.lcsh_id STARTS WITH 'sh85084158|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85096330' OR parent.lcsh_id STARTS WITH 'sh85096330|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084286' OR child.lcsh_id STARTS WITH 'sh85084286|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084334' OR child.lcsh_id STARTS WITH 'sh85084334|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2018002590' OR parent.lcsh_id STARTS WITH 'sh2018002590|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2001008470' OR child.lcsh_id STARTS WITH 'sh2001008470|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084783' OR child.lcsh_id STARTS WITH 'sh85084783|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084819' OR child.lcsh_id STARTS WITH 'sh85084819|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084822' OR child.lcsh_id STARTS WITH 'sh85084822|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042383' OR parent.lcsh_id STARTS WITH 'sh85042383|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084822' OR child.lcsh_id STARTS WITH 'sh85084822|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2001012575' OR parent.lcsh_id STARTS WITH 'sh2001012575|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084822' OR child.lcsh_id STARTS WITH 'sh85084822|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119903' OR parent.lcsh_id STARTS WITH 'sh85119903|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85084862' OR child.lcsh_id STARTS WITH 'sh85084862|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084334' OR parent.lcsh_id STARTS WITH 'sh85084334|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001371' OR child.lcsh_id STARTS WITH 'sh85001371|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85085132' OR parent.lcsh_id STARTS WITH 'sh85085132|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85085207' OR child.lcsh_id STARTS WITH 'sh85085207|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061211' OR parent.lcsh_id STARTS WITH 'sh85061211|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85085207' OR child.lcsh_id STARTS WITH 'sh85085207|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061212' OR parent.lcsh_id STARTS WITH 'sh85061212|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85085264' OR child.lcsh_id STARTS WITH 'sh85085264|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85085207' OR parent.lcsh_id STARTS WITH 'sh85085207|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85085264' OR child.lcsh_id STARTS WITH 'sh85085264|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124228' OR parent.lcsh_id STARTS WITH 'sh85124228|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85085264' OR child.lcsh_id STARTS WITH 'sh85085264|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85145114' OR parent.lcsh_id STARTS WITH 'sh85145114|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85128514' OR child.lcsh_id STARTS WITH 'sh85128514|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85085132' OR parent.lcsh_id STARTS WITH 'sh85085132|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85085589' OR child.lcsh_id STARTS WITH 'sh85085589|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101560' OR parent.lcsh_id STARTS WITH 'sh85101560|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85085712' OR child.lcsh_id STARTS WITH 'sh85085712|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85086422' OR child.lcsh_id STARTS WITH 'sh85086422|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026864' OR parent.lcsh_id STARTS WITH 'sh85026864|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85086422' OR child.lcsh_id STARTS WITH 'sh85086422|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119004' OR parent.lcsh_id STARTS WITH 'sh85119004|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85061236' OR child.lcsh_id STARTS WITH 'sh85061236|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85148201' OR parent.lcsh_id STARTS WITH 'sh85148201|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85086577' OR child.lcsh_id STARTS WITH 'sh85086577|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014171' OR parent.lcsh_id STARTS WITH 'sh85014171|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85086577' OR child.lcsh_id STARTS WITH 'sh85086577|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014253' OR parent.lcsh_id STARTS WITH 'sh85014253|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2003004725' OR child.lcsh_id STARTS WITH 'sh2003004725|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85086577' OR parent.lcsh_id STARTS WITH 'sh85086577|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85087347' OR child.lcsh_id STARTS WITH 'sh85087347|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85004837' OR parent.lcsh_id STARTS WITH 'sh85004837|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85087350' OR child.lcsh_id STARTS WITH 'sh85087350|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85087341' OR parent.lcsh_id STARTS WITH 'sh85087341|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85087350' OR child.lcsh_id STARTS WITH 'sh85087350|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101049' OR parent.lcsh_id STARTS WITH 'sh85101049|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85088079' OR child.lcsh_id STARTS WITH 'sh85088079|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85134578' OR parent.lcsh_id STARTS WITH 'sh85134578|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85088722' OR child.lcsh_id STARTS WITH 'sh85088722|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2021008605' OR parent.lcsh_id STARTS WITH 'sh2021008605|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097089' OR child.lcsh_id STARTS WITH 'sh85097089|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85088762' OR parent.lcsh_id STARTS WITH 'sh85088762|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85064678' OR child.lcsh_id STARTS WITH 'sh85064678|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85088806' OR parent.lcsh_id STARTS WITH 'sh85088806|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85089188' OR child.lcsh_id STARTS WITH 'sh85089188|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015976' OR parent.lcsh_id STARTS WITH 'sh85015976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85089188' OR child.lcsh_id STARTS WITH 'sh85089188|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084783' OR parent.lcsh_id STARTS WITH 'sh85084783|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2002000242' OR child.lcsh_id STARTS WITH 'sh2002000242|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2017004703' OR child.lcsh_id STARTS WITH 'sh2017004703|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2009116228' OR parent.lcsh_id STARTS WITH 'sh2009116228|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2017004703' OR child.lcsh_id STARTS WITH 'sh2017004703|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077224' OR parent.lcsh_id STARTS WITH 'sh85077224|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88002425' OR child.lcsh_id STARTS WITH 'sh88002425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85008180' OR parent.lcsh_id STARTS WITH 'sh85008180|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88002425' OR child.lcsh_id STARTS WITH 'sh88002425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042288' OR parent.lcsh_id STARTS WITH 'sh85042288|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88002425' OR child.lcsh_id STARTS WITH 'sh88002425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh88003229' OR parent.lcsh_id STARTS WITH 'sh88003229|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88002425' OR child.lcsh_id STARTS WITH 'sh88002425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2009007899' OR parent.lcsh_id STARTS WITH 'sh2009007899|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85090284' OR child.lcsh_id STARTS WITH 'sh85090284|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85031255' OR parent.lcsh_id STARTS WITH 'sh85031255|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85090425' OR child.lcsh_id STARTS WITH 'sh85090425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077989' OR parent.lcsh_id STARTS WITH 'sh85077989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85090425' OR child.lcsh_id STARTS WITH 'sh85090425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85095629' OR parent.lcsh_id STARTS WITH 'sh85095629|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091113' OR child.lcsh_id STARTS WITH 'sh85091113|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85004835' OR parent.lcsh_id STARTS WITH 'sh85004835|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091113' OR child.lcsh_id STARTS WITH 'sh85091113|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85091114' OR parent.lcsh_id STARTS WITH 'sh85091114|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091114' OR child.lcsh_id STARTS WITH 'sh85091114|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh91006099' OR parent.lcsh_id STARTS WITH 'sh91006099|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2005008805' OR child.lcsh_id STARTS WITH 'sh2005008805|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh91005166' OR parent.lcsh_id STARTS WITH 'sh91005166|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2005008805' OR child.lcsh_id STARTS WITH 'sh2005008805|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091118' OR child.lcsh_id STARTS WITH 'sh85091118|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043068' OR parent.lcsh_id STARTS WITH 'sh85043068|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091118' OR child.lcsh_id STARTS WITH 'sh85091118|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85091139' OR parent.lcsh_id STARTS WITH 'sh85091139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2021003848' OR child.lcsh_id STARTS WITH 'sh2021003848|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005162' OR parent.lcsh_id STARTS WITH 'sh85005162|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2021003848' OR child.lcsh_id STARTS WITH 'sh2021003848|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85091114' OR parent.lcsh_id STARTS WITH 'sh85091114|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091139' OR child.lcsh_id STARTS WITH 'sh85091139|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091159' OR child.lcsh_id STARTS WITH 'sh85091159|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85091114' OR parent.lcsh_id STARTS WITH 'sh85091114|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091159' OR child.lcsh_id STARTS WITH 'sh85091159|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101679' OR parent.lcsh_id STARTS WITH 'sh85101679|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091163' OR child.lcsh_id STARTS WITH 'sh85091163|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85091159' OR parent.lcsh_id STARTS WITH 'sh85091159|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85091163' OR child.lcsh_id STARTS WITH 'sh85091163|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108484' OR parent.lcsh_id STARTS WITH 'sh85108484|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91006099' OR child.lcsh_id STARTS WITH 'sh91006099|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083022' OR parent.lcsh_id STARTS WITH 'sh85083022|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85092349' OR child.lcsh_id STARTS WITH 'sh85092349|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082133' OR parent.lcsh_id STARTS WITH 'sh85082133|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85082118' OR child.lcsh_id STARTS WITH 'sh85082118|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85086421' OR parent.lcsh_id STARTS WITH 'sh85086421|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85092368' OR child.lcsh_id STARTS WITH 'sh85092368|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85092968' OR child.lcsh_id STARTS WITH 'sh85092968|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85092968' OR child.lcsh_id STARTS WITH 'sh85092968|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85093024' OR parent.lcsh_id STARTS WITH 'sh85093024|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093024' OR child.lcsh_id STARTS WITH 'sh85093024|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093222' OR child.lcsh_id STARTS WITH 'sh85093222|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85003425' OR parent.lcsh_id STARTS WITH 'sh85003425|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093349' OR child.lcsh_id STARTS WITH 'sh85093349|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082982' OR parent.lcsh_id STARTS WITH 'sh85082982|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093362' OR child.lcsh_id STARTS WITH 'sh85093362|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85020252' OR parent.lcsh_id STARTS WITH 'sh85020252|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093362' OR child.lcsh_id STARTS WITH 'sh85093362|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093654' OR child.lcsh_id STARTS WITH 'sh85093654|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093768' OR child.lcsh_id STARTS WITH 'sh85093768|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093850' OR child.lcsh_id STARTS WITH 'sh85093850|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh91000759' OR parent.lcsh_id STARTS WITH 'sh91000759|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093850' OR child.lcsh_id STARTS WITH 'sh85093850|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101568' OR parent.lcsh_id STARTS WITH 'sh85101568|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093850' OR child.lcsh_id STARTS WITH 'sh85093850|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108516' OR parent.lcsh_id STARTS WITH 'sh85108516|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093850' OR child.lcsh_id STARTS WITH 'sh85093850|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85134729' OR parent.lcsh_id STARTS WITH 'sh85134729|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093882' OR child.lcsh_id STARTS WITH 'sh85093882|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2021001476' OR parent.lcsh_id STARTS WITH 'sh2021001476|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093937' OR child.lcsh_id STARTS WITH 'sh85093937|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040468' OR parent.lcsh_id STARTS WITH 'sh85040468|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85093937' OR child.lcsh_id STARTS WITH 'sh85093937|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85081263' OR parent.lcsh_id STARTS WITH 'sh85081263|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85094813' OR child.lcsh_id STARTS WITH 'sh85094813|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074523' OR parent.lcsh_id STARTS WITH 'sh85074523|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85094813' OR child.lcsh_id STARTS WITH 'sh85094813|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85094812' OR parent.lcsh_id STARTS WITH 'sh85094812|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85094833' OR child.lcsh_id STARTS WITH 'sh85094833|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095071' OR child.lcsh_id STARTS WITH 'sh85095071|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095181' OR child.lcsh_id STARTS WITH 'sh85095181|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85087992' OR child.lcsh_id STARTS WITH 'sh85087992|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85063519' OR parent.lcsh_id STARTS WITH 'sh85063519|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85128280' OR child.lcsh_id STARTS WITH 'sh85128280|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126460' OR child.lcsh_id STARTS WITH 'sh85126460|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85047940' OR parent.lcsh_id STARTS WITH 'sh85047940|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095299' OR child.lcsh_id STARTS WITH 'sh85095299|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074518' OR parent.lcsh_id STARTS WITH 'sh85074518|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095299' OR child.lcsh_id STARTS WITH 'sh85095299|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85113628' OR parent.lcsh_id STARTS WITH 'sh85113628|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095299' OR child.lcsh_id STARTS WITH 'sh85095299|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85126460' OR parent.lcsh_id STARTS WITH 'sh85126460|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023022' OR child.lcsh_id STARTS WITH 'sh85023022|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095524' OR child.lcsh_id STARTS WITH 'sh85095524|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080336' OR parent.lcsh_id STARTS WITH 'sh85080336|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095524' OR child.lcsh_id STARTS WITH 'sh85095524|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85095521' OR parent.lcsh_id STARTS WITH 'sh85095521|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095524' OR child.lcsh_id STARTS WITH 'sh85095524|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108476' OR parent.lcsh_id STARTS WITH 'sh85108476|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095524' OR child.lcsh_id STARTS WITH 'sh85095524|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85123994' OR parent.lcsh_id STARTS WITH 'sh85123994|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91002392' OR child.lcsh_id STARTS WITH 'sh91002392|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86004134' OR child.lcsh_id STARTS WITH 'sh86004134|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023022' OR parent.lcsh_id STARTS WITH 'sh85023022|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095726' OR child.lcsh_id STARTS WITH 'sh85095726|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85149983' OR parent.lcsh_id STARTS WITH 'sh85149983|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095770' OR child.lcsh_id STARTS WITH 'sh85095770|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85036953' OR parent.lcsh_id STARTS WITH 'sh85036953|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85095770' OR child.lcsh_id STARTS WITH 'sh85095770|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85095799' OR parent.lcsh_id STARTS WITH 'sh85095799|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85096050' OR child.lcsh_id STARTS WITH 'sh85096050|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097061' OR child.lcsh_id STARTS WITH 'sh85097061|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101552' OR parent.lcsh_id STARTS WITH 'sh85101552|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2001004516' OR child.lcsh_id STARTS WITH 'sh2001004516|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005586' OR parent.lcsh_id STARTS WITH 'sh85005586|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2001004516' OR child.lcsh_id STARTS WITH 'sh2001004516|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85097123' OR parent.lcsh_id STARTS WITH 'sh85097123|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2001004516' OR child.lcsh_id STARTS WITH 'sh2001004516|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101512' OR parent.lcsh_id STARTS WITH 'sh85101512|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097024' OR child.lcsh_id STARTS WITH 'sh85097024|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097024' OR child.lcsh_id STARTS WITH 'sh85097024|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85097123' OR parent.lcsh_id STARTS WITH 'sh85097123|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097026' OR child.lcsh_id STARTS WITH 'sh85097026|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015976' OR parent.lcsh_id STARTS WITH 'sh85015976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097026' OR child.lcsh_id STARTS WITH 'sh85097026|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85097123' OR parent.lcsh_id STARTS WITH 'sh85097123|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097123' OR child.lcsh_id STARTS WITH 'sh85097123|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061190' OR parent.lcsh_id STARTS WITH 'sh85061190|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097123' OR child.lcsh_id STARTS WITH 'sh85097123|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85149983' OR parent.lcsh_id STARTS WITH 'sh85149983|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097270' OR child.lcsh_id STARTS WITH 'sh85097270|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015976' OR parent.lcsh_id STARTS WITH 'sh85015976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097270' OR child.lcsh_id STARTS WITH 'sh85097270|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85097026' OR parent.lcsh_id STARTS WITH 'sh85097026|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097826' OR child.lcsh_id STARTS WITH 'sh85097826|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh95008935' OR parent.lcsh_id STARTS WITH 'sh95008935|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85097922' OR child.lcsh_id STARTS WITH 'sh85097922|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85025778' OR child.lcsh_id STARTS WITH 'sh85025778|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85134705' OR parent.lcsh_id STARTS WITH 'sh85134705|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85098604' OR child.lcsh_id STARTS WITH 'sh85098604|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85025778' OR parent.lcsh_id STARTS WITH 'sh85025778|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85098685' OR child.lcsh_id STARTS WITH 'sh85098685|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083022' OR parent.lcsh_id STARTS WITH 'sh85083022|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85099163' OR child.lcsh_id STARTS WITH 'sh85099163|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85093362' OR parent.lcsh_id STARTS WITH 'sh85093362|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023483' OR child.lcsh_id STARTS WITH 'sh85023483|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023443' OR parent.lcsh_id STARTS WITH 'sh85023443|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85099185' OR child.lcsh_id STARTS WITH 'sh85099185|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85099708' OR child.lcsh_id STARTS WITH 'sh85099708|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85027742' OR parent.lcsh_id STARTS WITH 'sh85027742|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85099818' OR child.lcsh_id STARTS WITH 'sh85099818|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85008324' OR parent.lcsh_id STARTS WITH 'sh85008324|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85099922' OR child.lcsh_id STARTS WITH 'sh85099922|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85036953' OR parent.lcsh_id STARTS WITH 'sh85036953|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100427' OR child.lcsh_id STARTS WITH 'sh85100427|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85085712' OR parent.lcsh_id STARTS WITH 'sh85085712|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100472' OR child.lcsh_id STARTS WITH 'sh85100472|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101560' OR parent.lcsh_id STARTS WITH 'sh85101560|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100596' OR child.lcsh_id STARTS WITH 'sh85100596|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85039719' OR parent.lcsh_id STARTS WITH 'sh85039719|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100596' OR child.lcsh_id STARTS WITH 'sh85100596|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082055' OR parent.lcsh_id STARTS WITH 'sh85082055|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100596' OR child.lcsh_id STARTS WITH 'sh85100596|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100603' OR parent.lcsh_id STARTS WITH 'sh85100603|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100599' OR child.lcsh_id STARTS WITH 'sh85100599|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083022' OR parent.lcsh_id STARTS WITH 'sh85083022|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100603' OR child.lcsh_id STARTS WITH 'sh85100603|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100603' OR child.lcsh_id STARTS WITH 'sh85100603|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100623' OR child.lcsh_id STARTS WITH 'sh85100623|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014241' OR parent.lcsh_id STARTS WITH 'sh85014241|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102793' OR child.lcsh_id STARTS WITH 'sh85102793|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014189' OR parent.lcsh_id STARTS WITH 'sh85014189|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102793' OR child.lcsh_id STARTS WITH 'sh85102793|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100673' OR parent.lcsh_id STARTS WITH 'sh85100673|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102793' OR child.lcsh_id STARTS WITH 'sh85102793|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85142524' OR parent.lcsh_id STARTS WITH 'sh85142524|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100845' OR child.lcsh_id STARTS WITH 'sh85100845|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026429' OR parent.lcsh_id STARTS WITH 'sh85026429|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100845' OR child.lcsh_id STARTS WITH 'sh85100845|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85076807' OR parent.lcsh_id STARTS WITH 'sh85076807|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100845' OR child.lcsh_id STARTS WITH 'sh85100845|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85094833' OR parent.lcsh_id STARTS WITH 'sh85094833|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85100849' OR child.lcsh_id STARTS WITH 'sh85100849|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062913' OR parent.lcsh_id STARTS WITH 'sh85062913|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2002006356' OR child.lcsh_id STARTS WITH 'sh2002006356|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh99005065' OR parent.lcsh_id STARTS WITH 'sh99005065|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh89004340' OR child.lcsh_id STARTS WITH 'sh89004340|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101053' OR child.lcsh_id STARTS WITH 'sh85101053|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077222' OR parent.lcsh_id STARTS WITH 'sh85077222|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85001264' OR child.lcsh_id STARTS WITH 'sh85001264|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054037' OR parent.lcsh_id STARTS WITH 'sh85054037|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101288' OR child.lcsh_id STARTS WITH 'sh85101288|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101274' OR parent.lcsh_id STARTS WITH 'sh85101274|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101288' OR child.lcsh_id STARTS WITH 'sh85101288|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85070736' OR parent.lcsh_id STARTS WITH 'sh85070736|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85003477' OR child.lcsh_id STARTS WITH 'sh85003477|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015976' OR parent.lcsh_id STARTS WITH 'sh85015976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85023027' OR child.lcsh_id STARTS WITH 'sh85023027|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85022986' OR parent.lcsh_id STARTS WITH 'sh85022986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101517' OR child.lcsh_id STARTS WITH 'sh85101517|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101552' OR child.lcsh_id STARTS WITH 'sh85101552|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053986' OR parent.lcsh_id STARTS WITH 'sh85053986|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101560' OR child.lcsh_id STARTS WITH 'sh85101560|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054037' OR parent.lcsh_id STARTS WITH 'sh85054037|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh91000759' OR child.lcsh_id STARTS WITH 'sh91000759|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85112401' OR parent.lcsh_id STARTS WITH 'sh85112401|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2021001476' OR child.lcsh_id STARTS WITH 'sh2021001476|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85093937' OR parent.lcsh_id STARTS WITH 'sh85093937|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh89005705' OR child.lcsh_id STARTS WITH 'sh89005705|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101653' OR child.lcsh_id STARTS WITH 'sh85101653|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89005705' OR parent.lcsh_id STARTS WITH 'sh89005705|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101679' OR child.lcsh_id STARTS WITH 'sh85101679|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101568' OR child.lcsh_id STARTS WITH 'sh85101568|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083159' OR parent.lcsh_id STARTS WITH 'sh85083159|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101568' OR child.lcsh_id STARTS WITH 'sh85101568|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85134729' OR parent.lcsh_id STARTS WITH 'sh85134729|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015961' OR child.lcsh_id STARTS WITH 'sh85015961|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014171' OR parent.lcsh_id STARTS WITH 'sh85014171|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015961' OR child.lcsh_id STARTS WITH 'sh85015961|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015976' OR parent.lcsh_id STARTS WITH 'sh85015976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101689' OR child.lcsh_id STARTS WITH 'sh85101689|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014147' OR parent.lcsh_id STARTS WITH 'sh85014147|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101689' OR child.lcsh_id STARTS WITH 'sh85101689|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015976' OR parent.lcsh_id STARTS WITH 'sh85015976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101720' OR child.lcsh_id STARTS WITH 'sh85101720|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2003004721' OR parent.lcsh_id STARTS WITH 'sh2003004721|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101722' OR child.lcsh_id STARTS WITH 'sh85101722|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85072117' OR parent.lcsh_id STARTS WITH 'sh85072117|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85101747' OR child.lcsh_id STARTS WITH 'sh85101747|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101788' OR parent.lcsh_id STARTS WITH 'sh85101788|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88000316' OR child.lcsh_id STARTS WITH 'sh88000316|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85009003' OR parent.lcsh_id STARTS WITH 'sh85009003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88000316' OR child.lcsh_id STARTS WITH 'sh88000316|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054037' OR parent.lcsh_id STARTS WITH 'sh85054037|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102652' OR child.lcsh_id STARTS WITH 'sh85102652|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124544' OR parent.lcsh_id STARTS WITH 'sh85124544|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102696' OR child.lcsh_id STARTS WITH 'sh85102696|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85033827' OR parent.lcsh_id STARTS WITH 'sh85033827|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102696' OR child.lcsh_id STARTS WITH 'sh85102696|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85046278' OR parent.lcsh_id STARTS WITH 'sh85046278|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102696' OR child.lcsh_id STARTS WITH 'sh85102696|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080336' OR parent.lcsh_id STARTS WITH 'sh85080336|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102696' OR child.lcsh_id STARTS WITH 'sh85102696|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85095521' OR parent.lcsh_id STARTS WITH 'sh85095521|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015978' OR child.lcsh_id STARTS WITH 'sh85015978|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85004835' OR parent.lcsh_id STARTS WITH 'sh85004835|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015978' OR child.lcsh_id STARTS WITH 'sh85015978|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015976' OR parent.lcsh_id STARTS WITH 'sh85015976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102720' OR child.lcsh_id STARTS WITH 'sh85102720|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090284' OR parent.lcsh_id STARTS WITH 'sh85090284|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102720' OR child.lcsh_id STARTS WITH 'sh85102720|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85103025' OR parent.lcsh_id STARTS WITH 'sh85103025|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015985' OR child.lcsh_id STARTS WITH 'sh85015985|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015976' OR parent.lcsh_id STARTS WITH 'sh85015976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015985' OR child.lcsh_id STARTS WITH 'sh85015985|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88005635' OR child.lcsh_id STARTS WITH 'sh88005635|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh91006274' OR parent.lcsh_id STARTS WITH 'sh91006274|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88005635' OR child.lcsh_id STARTS WITH 'sh88005635|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015985' OR parent.lcsh_id STARTS WITH 'sh85015985|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88005635' OR child.lcsh_id STARTS WITH 'sh88005635|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85102796' OR parent.lcsh_id STARTS WITH 'sh85102796|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102745' OR child.lcsh_id STARTS WITH 'sh85102745|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053877' OR parent.lcsh_id STARTS WITH 'sh85053877|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015992' OR child.lcsh_id STARTS WITH 'sh85015992|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015976' OR parent.lcsh_id STARTS WITH 'sh85015976|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85015992' OR child.lcsh_id STARTS WITH 'sh85015992|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85087347' OR parent.lcsh_id STARTS WITH 'sh85087347|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102732' OR child.lcsh_id STARTS WITH 'sh85102732|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85002385' OR parent.lcsh_id STARTS WITH 'sh85002385|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85102796' OR child.lcsh_id STARTS WITH 'sh85102796|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101679' OR parent.lcsh_id STARTS WITH 'sh85101679|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85103704' OR child.lcsh_id STARTS WITH 'sh85103704|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077507' OR parent.lcsh_id STARTS WITH 'sh85077507|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104345' OR child.lcsh_id STARTS WITH 'sh85104345|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85045198' OR parent.lcsh_id STARTS WITH 'sh85045198|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104345' OR child.lcsh_id STARTS WITH 'sh85104345|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85104440' OR parent.lcsh_id STARTS WITH 'sh85104440|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054025' OR child.lcsh_id STARTS WITH 'sh85054025|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005570' OR parent.lcsh_id STARTS WITH 'sh85005570|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104425' OR child.lcsh_id STARTS WITH 'sh85104425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85104440' OR parent.lcsh_id STARTS WITH 'sh85104440|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104425' OR child.lcsh_id STARTS WITH 'sh85104425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104425' OR child.lcsh_id STARTS WITH 'sh85104425|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85123994' OR parent.lcsh_id STARTS WITH 'sh85123994|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104440' OR child.lcsh_id STARTS WITH 'sh85104440|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124003' OR parent.lcsh_id STARTS WITH 'sh85124003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104457' OR child.lcsh_id STARTS WITH 'sh85104457|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85104440' OR parent.lcsh_id STARTS WITH 'sh85104440|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104457' OR child.lcsh_id STARTS WITH 'sh85104457|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104920' OR child.lcsh_id STARTS WITH 'sh85104920|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053877' OR parent.lcsh_id STARTS WITH 'sh85053877|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85104920' OR child.lcsh_id STARTS WITH 'sh85104920|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85060367' OR parent.lcsh_id STARTS WITH 'sh85060367|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85106058' OR child.lcsh_id STARTS WITH 'sh85106058|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053766' OR parent.lcsh_id STARTS WITH 'sh85053766|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85106058' OR child.lcsh_id STARTS WITH 'sh85106058|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074574' OR parent.lcsh_id STARTS WITH 'sh85074574|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85106058' OR child.lcsh_id STARTS WITH 'sh85106058|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85078115' OR parent.lcsh_id STARTS WITH 'sh85078115|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85106058' OR child.lcsh_id STARTS WITH 'sh85106058|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119877' OR parent.lcsh_id STARTS WITH 'sh85119877|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041077' OR child.lcsh_id STARTS WITH 'sh85041077|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh87007854' OR parent.lcsh_id STARTS WITH 'sh87007854|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85030965' OR child.lcsh_id STARTS WITH 'sh85030965|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85075119' OR parent.lcsh_id STARTS WITH 'sh85075119|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107212' OR child.lcsh_id STARTS WITH 'sh85107212|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065864' OR parent.lcsh_id STARTS WITH 'sh85065864|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107212' OR child.lcsh_id STARTS WITH 'sh85107212|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082757' OR parent.lcsh_id STARTS WITH 'sh85082757|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85123160' OR child.lcsh_id STARTS WITH 'sh85123160|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh90004091' OR parent.lcsh_id STARTS WITH 'sh90004091|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85028378' OR child.lcsh_id STARTS WITH 'sh85028378|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85132964' OR parent.lcsh_id STARTS WITH 'sh85132964|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107313' OR child.lcsh_id STARTS WITH 'sh85107313|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042288' OR parent.lcsh_id STARTS WITH 'sh85042288|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107313' OR child.lcsh_id STARTS WITH 'sh85107313|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074581' OR parent.lcsh_id STARTS WITH 'sh85074581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107319' OR child.lcsh_id STARTS WITH 'sh85107319|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107319' OR child.lcsh_id STARTS WITH 'sh85107319|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85041014' OR parent.lcsh_id STARTS WITH 'sh85041014|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85065919' OR child.lcsh_id STARTS WITH 'sh85065919|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080336' OR parent.lcsh_id STARTS WITH 'sh85080336|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107437' OR child.lcsh_id STARTS WITH 'sh85107437|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85078115' OR parent.lcsh_id STARTS WITH 'sh85078115|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107496' OR child.lcsh_id STARTS WITH 'sh85107496|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107552' OR child.lcsh_id STARTS WITH 'sh85107552|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074545' OR parent.lcsh_id STARTS WITH 'sh85074545|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85107552' OR child.lcsh_id STARTS WITH 'sh85107552|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85078106' OR parent.lcsh_id STARTS WITH 'sh85078106|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86007375' OR child.lcsh_id STARTS WITH 'sh86007375|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014120' OR parent.lcsh_id STARTS WITH 'sh85014120|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86007375' OR child.lcsh_id STARTS WITH 'sh86007375|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85053855' OR parent.lcsh_id STARTS WITH 'sh85053855|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108376' OR child.lcsh_id STARTS WITH 'sh85108376|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124049' OR parent.lcsh_id STARTS WITH 'sh85124049|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108381' OR child.lcsh_id STARTS WITH 'sh85108381|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083185' OR parent.lcsh_id STARTS WITH 'sh85083185|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108410' OR child.lcsh_id STARTS WITH 'sh85108410|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108501' OR parent.lcsh_id STARTS WITH 'sh85108501|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108410' OR child.lcsh_id STARTS WITH 'sh85108410|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85125363' OR parent.lcsh_id STARTS WITH 'sh85125363|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108411' OR child.lcsh_id STARTS WITH 'sh85108411|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108427' OR child.lcsh_id STARTS WITH 'sh85108427|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85027067' OR parent.lcsh_id STARTS WITH 'sh85027067|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108427' OR child.lcsh_id STARTS WITH 'sh85108427|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090925' OR parent.lcsh_id STARTS WITH 'sh85090925|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108427' OR child.lcsh_id STARTS WITH 'sh85108427|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108448' OR parent.lcsh_id STARTS WITH 'sh85108448|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108432' OR child.lcsh_id STARTS WITH 'sh85108432|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077222' OR parent.lcsh_id STARTS WITH 'sh85077222|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108432' OR child.lcsh_id STARTS WITH 'sh85108432|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108459' OR child.lcsh_id STARTS WITH 'sh85108459|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062843' OR parent.lcsh_id STARTS WITH 'sh85062843|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108459' OR child.lcsh_id STARTS WITH 'sh85108459|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100849' OR parent.lcsh_id STARTS WITH 'sh85100849|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108459' OR child.lcsh_id STARTS WITH 'sh85108459|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85125350' OR parent.lcsh_id STARTS WITH 'sh85125350|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108485' OR child.lcsh_id STARTS WITH 'sh85108485|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108487' OR parent.lcsh_id STARTS WITH 'sh85108487|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108485' OR child.lcsh_id STARTS WITH 'sh85108485|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85112549' OR parent.lcsh_id STARTS WITH 'sh85112549|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108490' OR child.lcsh_id STARTS WITH 'sh85108490|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108448' OR parent.lcsh_id STARTS WITH 'sh85108448|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108490' OR child.lcsh_id STARTS WITH 'sh85108490|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108464' OR parent.lcsh_id STARTS WITH 'sh85108464|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108490' OR child.lcsh_id STARTS WITH 'sh85108490|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85117919' OR parent.lcsh_id STARTS WITH 'sh85117919|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86001417' OR child.lcsh_id STARTS WITH 'sh86001417|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85091127' OR parent.lcsh_id STARTS WITH 'sh85091127|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108479' OR child.lcsh_id STARTS WITH 'sh85108479|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85091139' OR parent.lcsh_id STARTS WITH 'sh85091139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108498' OR child.lcsh_id STARTS WITH 'sh85108498|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023041' OR parent.lcsh_id STARTS WITH 'sh85023041|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108498' OR child.lcsh_id STARTS WITH 'sh85108498|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100599' OR parent.lcsh_id STARTS WITH 'sh85100599|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108484' OR child.lcsh_id STARTS WITH 'sh85108484|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101679' OR parent.lcsh_id STARTS WITH 'sh85101679|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108484' OR child.lcsh_id STARTS WITH 'sh85108484|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108425' OR parent.lcsh_id STARTS WITH 'sh85108425|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108516' OR child.lcsh_id STARTS WITH 'sh85108516|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083651' OR parent.lcsh_id STARTS WITH 'sh85083651|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108611' OR child.lcsh_id STARTS WITH 'sh85108611|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85104440' OR parent.lcsh_id STARTS WITH 'sh85104440|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108638' OR child.lcsh_id STARTS WITH 'sh85108638|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85059518' OR parent.lcsh_id STARTS WITH 'sh85059518|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108638' OR child.lcsh_id STARTS WITH 'sh85108638|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh87006649' OR parent.lcsh_id STARTS WITH 'sh87006649|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108696' OR child.lcsh_id STARTS WITH 'sh85108696|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85075119' OR parent.lcsh_id STARTS WITH 'sh85075119|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2004003366' OR child.lcsh_id STARTS WITH 'sh2004003366|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85108871' OR child.lcsh_id STARTS WITH 'sh85108871|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015617' OR parent.lcsh_id STARTS WITH 'sh85015617|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh98001235' OR child.lcsh_id STARTS WITH 'sh98001235|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85072732' OR parent.lcsh_id STARTS WITH 'sh85072732|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh98001235' OR child.lcsh_id STARTS WITH 'sh98001235|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89004340' OR parent.lcsh_id STARTS WITH 'sh89004340|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2021005718' OR child.lcsh_id STARTS WITH 'sh2021005718|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85089048' OR parent.lcsh_id STARTS WITH 'sh85089048|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh95001341' OR child.lcsh_id STARTS WITH 'sh95001341|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040999' OR parent.lcsh_id STARTS WITH 'sh85040999|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85110385' OR child.lcsh_id STARTS WITH 'sh85110385|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029044' OR parent.lcsh_id STARTS WITH 'sh85029044|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85110385' OR child.lcsh_id STARTS WITH 'sh85110385|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85133270' OR parent.lcsh_id STARTS WITH 'sh85133270|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85110774' OR child.lcsh_id STARTS WITH 'sh85110774|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85110872' OR child.lcsh_id STARTS WITH 'sh85110872|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85137069' OR parent.lcsh_id STARTS WITH 'sh85137069|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85111355' OR child.lcsh_id STARTS WITH 'sh85111355|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85107090' OR parent.lcsh_id STARTS WITH 'sh85107090|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85111355' OR child.lcsh_id STARTS WITH 'sh85111355|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85142090' OR parent.lcsh_id STARTS WITH 'sh85142090|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85111357' OR child.lcsh_id STARTS WITH 'sh85111357|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85128181' OR parent.lcsh_id STARTS WITH 'sh85128181|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85111362' OR child.lcsh_id STARTS WITH 'sh85111362|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh93001294' OR parent.lcsh_id STARTS WITH 'sh93001294|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85111362' OR child.lcsh_id STARTS WITH 'sh85111362|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2001000588' OR parent.lcsh_id STARTS WITH 'sh2001000588|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2001000752' OR child.lcsh_id STARTS WITH 'sh2001000752|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2020000052' OR parent.lcsh_id STARTS WITH 'sh2020000052|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2001000752' OR child.lcsh_id STARTS WITH 'sh2001000752|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85107813' OR parent.lcsh_id STARTS WITH 'sh85107813|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85111662' OR child.lcsh_id STARTS WITH 'sh85111662|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074546' OR parent.lcsh_id STARTS WITH 'sh85074546|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85111945' OR child.lcsh_id STARTS WITH 'sh85111945|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080593' OR parent.lcsh_id STARTS WITH 'sh85080593|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92000704' OR child.lcsh_id STARTS WITH 'sh92000704|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079324' OR parent.lcsh_id STARTS WITH 'sh85079324|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92000704' OR child.lcsh_id STARTS WITH 'sh92000704|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85112459' OR parent.lcsh_id STARTS WITH 'sh85112459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh94003448' OR child.lcsh_id STARTS WITH 'sh94003448|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85046441' OR parent.lcsh_id STARTS WITH 'sh85046441|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85112953' OR child.lcsh_id STARTS WITH 'sh85112953|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85112953' OR child.lcsh_id STARTS WITH 'sh85112953|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85076810' OR parent.lcsh_id STARTS WITH 'sh85076810|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85112953' OR child.lcsh_id STARTS WITH 'sh85112953|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101679' OR parent.lcsh_id STARTS WITH 'sh85101679|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85112953' OR child.lcsh_id STARTS WITH 'sh85112953|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85120560' OR parent.lcsh_id STARTS WITH 'sh85120560|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85113628' OR child.lcsh_id STARTS WITH 'sh85113628|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85010030' OR parent.lcsh_id STARTS WITH 'sh85010030|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh88000877' OR child.lcsh_id STARTS WITH 'sh88000877|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067347' OR parent.lcsh_id STARTS WITH 'sh85067347|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85115899' OR child.lcsh_id STARTS WITH 'sh85115899|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85002484' OR parent.lcsh_id STARTS WITH 'sh85002484|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85115899' OR child.lcsh_id STARTS WITH 'sh85115899|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029215' OR parent.lcsh_id STARTS WITH 'sh85029215|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85115899' OR child.lcsh_id STARTS WITH 'sh85115899|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040804' OR parent.lcsh_id STARTS WITH 'sh85040804|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85115899' OR child.lcsh_id STARTS WITH 'sh85115899|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85112367' OR parent.lcsh_id STARTS WITH 'sh85112367|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85118622' OR child.lcsh_id STARTS WITH 'sh85118622|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85127474' OR parent.lcsh_id STARTS WITH 'sh85127474|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85088064' OR child.lcsh_id STARTS WITH 'sh85088064|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85039316' OR parent.lcsh_id STARTS WITH 'sh85039316|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041082' OR child.lcsh_id STARTS WITH 'sh85041082|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119634' OR child.lcsh_id STARTS WITH 'sh85119634|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054185' OR parent.lcsh_id STARTS WITH 'sh85054185|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2009007899' OR child.lcsh_id STARTS WITH 'sh2009007899|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh89003285' OR parent.lcsh_id STARTS WITH 'sh89003285|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2009007899' OR child.lcsh_id STARTS WITH 'sh2009007899|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042288' OR parent.lcsh_id STARTS WITH 'sh85042288|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2009007899' OR child.lcsh_id STARTS WITH 'sh2009007899|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119870' OR parent.lcsh_id STARTS WITH 'sh85119870|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92004914' OR child.lcsh_id STARTS WITH 'sh92004914|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85008180' OR parent.lcsh_id STARTS WITH 'sh85008180|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92004914' OR child.lcsh_id STARTS WITH 'sh92004914|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066289' OR parent.lcsh_id STARTS WITH 'sh85066289|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92004914' OR child.lcsh_id STARTS WITH 'sh92004914|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2009007899' OR parent.lcsh_id STARTS WITH 'sh2009007899|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119870' OR child.lcsh_id STARTS WITH 'sh85119870|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029301' OR parent.lcsh_id STARTS WITH 'sh85029301|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119870' OR child.lcsh_id STARTS WITH 'sh85119870|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066289' OR parent.lcsh_id STARTS WITH 'sh85066289|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119870' OR child.lcsh_id STARTS WITH 'sh85119870|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074518' OR parent.lcsh_id STARTS WITH 'sh85074518|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119870' OR child.lcsh_id STARTS WITH 'sh85119870|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85076359' OR parent.lcsh_id STARTS WITH 'sh85076359|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119870' OR child.lcsh_id STARTS WITH 'sh85119870|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082693' OR parent.lcsh_id STARTS WITH 'sh85082693|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85119950' OR child.lcsh_id STARTS WITH 'sh85119950|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119870' OR parent.lcsh_id STARTS WITH 'sh85119870|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85120145' OR child.lcsh_id STARTS WITH 'sh85120145|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85003425' OR parent.lcsh_id STARTS WITH 'sh85003425|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85120145' OR child.lcsh_id STARTS WITH 'sh85120145|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082139' OR parent.lcsh_id STARTS WITH 'sh85082139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2001004460' OR child.lcsh_id STARTS WITH 'sh2001004460|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054086' OR parent.lcsh_id STARTS WITH 'sh85054086|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85120300' OR child.lcsh_id STARTS WITH 'sh85120300|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85060130' OR parent.lcsh_id STARTS WITH 'sh85060130|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85120387' OR child.lcsh_id STARTS WITH 'sh85120387|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082139' OR parent.lcsh_id STARTS WITH 'sh85082139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85120542' OR child.lcsh_id STARTS WITH 'sh85120542|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061673' OR parent.lcsh_id STARTS WITH 'sh85061673|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh90004841' OR child.lcsh_id STARTS WITH 'sh90004841|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh90004841' OR child.lcsh_id STARTS WITH 'sh90004841|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124003' OR parent.lcsh_id STARTS WITH 'sh85124003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85052948' OR child.lcsh_id STARTS WITH 'sh85052948|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85044107' OR parent.lcsh_id STARTS WITH 'sh85044107|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85052948' OR child.lcsh_id STARTS WITH 'sh85052948|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101517' OR parent.lcsh_id STARTS WITH 'sh85101517|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85122827' OR child.lcsh_id STARTS WITH 'sh85122827|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85088806' OR parent.lcsh_id STARTS WITH 'sh85088806|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85123948' OR child.lcsh_id STARTS WITH 'sh85123948|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061212' OR parent.lcsh_id STARTS WITH 'sh85061212|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85123948' OR child.lcsh_id STARTS WITH 'sh85123948|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2006006990' OR child.lcsh_id STARTS WITH 'sh2006006990|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2006007023' OR parent.lcsh_id STARTS WITH 'sh2006007023|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2006006990' OR child.lcsh_id STARTS WITH 'sh2006006990|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh87002172' OR parent.lcsh_id STARTS WITH 'sh87002172|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2006006990' OR child.lcsh_id STARTS WITH 'sh2006006990|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh2015002635' OR parent.lcsh_id STARTS WITH 'sh2015002635|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2006006990' OR child.lcsh_id STARTS WITH 'sh2006006990|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh96008680' OR parent.lcsh_id STARTS WITH 'sh96008680|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85123985' OR child.lcsh_id STARTS WITH 'sh85123985|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85123948' OR parent.lcsh_id STARTS WITH 'sh85123948|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85123994' OR child.lcsh_id STARTS WITH 'sh85123994|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85062856' OR parent.lcsh_id STARTS WITH 'sh85062856|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85123994' OR child.lcsh_id STARTS WITH 'sh85123994|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85123994' OR child.lcsh_id STARTS WITH 'sh85123994|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85123946' OR parent.lcsh_id STARTS WITH 'sh85123946|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85123994' OR child.lcsh_id STARTS WITH 'sh85123994|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124003' OR child.lcsh_id STARTS WITH 'sh85124003|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026423' OR parent.lcsh_id STARTS WITH 'sh85026423|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124049' OR child.lcsh_id STARTS WITH 'sh85124049|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh87006649' OR parent.lcsh_id STARTS WITH 'sh87006649|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124195' OR child.lcsh_id STARTS WITH 'sh85124195|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074514' OR parent.lcsh_id STARTS WITH 'sh85074514|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124195' OR child.lcsh_id STARTS WITH 'sh85124195|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077222' OR parent.lcsh_id STARTS WITH 'sh85077222|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124195' OR child.lcsh_id STARTS WITH 'sh85124195|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124200' OR child.lcsh_id STARTS WITH 'sh85124200|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124003' OR parent.lcsh_id STARTS WITH 'sh85124003|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85041146' OR child.lcsh_id STARTS WITH 'sh85041146|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85072731' OR child.lcsh_id STARTS WITH 'sh85072731|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85072731' OR child.lcsh_id STARTS WITH 'sh85072731|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85072732' OR parent.lcsh_id STARTS WITH 'sh85072732|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85072731' OR child.lcsh_id STARTS WITH 'sh85072731|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108736' OR parent.lcsh_id STARTS WITH 'sh85108736|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85072731' OR child.lcsh_id STARTS WITH 'sh85072731|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124198' OR child.lcsh_id STARTS WITH 'sh85124198|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85071088' OR parent.lcsh_id STARTS WITH 'sh85071088|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124198' OR child.lcsh_id STARTS WITH 'sh85124198|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85112587' OR child.lcsh_id STARTS WITH 'sh85112587|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85124200' OR parent.lcsh_id STARTS WITH 'sh85124200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2015002635' OR child.lcsh_id STARTS WITH 'sh2015002635|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080326' OR parent.lcsh_id STARTS WITH 'sh85080326|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2015002635' OR child.lcsh_id STARTS WITH 'sh2015002635|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85133169' OR parent.lcsh_id STARTS WITH 'sh85133169|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029534' OR child.lcsh_id STARTS WITH 'sh85029534|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh98003200' OR parent.lcsh_id STARTS WITH 'sh98003200|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87007398' OR child.lcsh_id STARTS WITH 'sh87007398|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85029538' OR child.lcsh_id STARTS WITH 'sh85029538|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029532' OR parent.lcsh_id STARTS WITH 'sh85029532|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124299' OR child.lcsh_id STARTS WITH 'sh85124299|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85107310' OR parent.lcsh_id STARTS WITH 'sh85107310|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124376' OR child.lcsh_id STARTS WITH 'sh85124376|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85002415' OR parent.lcsh_id STARTS WITH 'sh85002415|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124376' OR child.lcsh_id STARTS WITH 'sh85124376|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040468' OR parent.lcsh_id STARTS WITH 'sh85040468|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85124636' OR child.lcsh_id STARTS WITH 'sh85124636|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023027' OR parent.lcsh_id STARTS WITH 'sh85023027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125363' OR child.lcsh_id STARTS WITH 'sh85125363|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85031576' OR parent.lcsh_id STARTS WITH 'sh85031576|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125363' OR child.lcsh_id STARTS WITH 'sh85125363|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082129' OR parent.lcsh_id STARTS WITH 'sh85082129|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125363' OR child.lcsh_id STARTS WITH 'sh85125363|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101653' OR parent.lcsh_id STARTS WITH 'sh85101653|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125363' OR child.lcsh_id STARTS WITH 'sh85125363|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85103619' OR parent.lcsh_id STARTS WITH 'sh85103619|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125363' OR child.lcsh_id STARTS WITH 'sh85125363|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85110340' OR parent.lcsh_id STARTS WITH 'sh85110340|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125363' OR child.lcsh_id STARTS WITH 'sh85125363|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85145785' OR parent.lcsh_id STARTS WITH 'sh85145785|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85096159' OR child.lcsh_id STARTS WITH 'sh85096159|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85008947' OR parent.lcsh_id STARTS WITH 'sh85008947|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85096159' OR child.lcsh_id STARTS WITH 'sh85096159|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85067491' OR parent.lcsh_id STARTS WITH 'sh85067491|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85096159' OR child.lcsh_id STARTS WITH 'sh85096159|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080584' OR parent.lcsh_id STARTS WITH 'sh85080584|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125953' OR child.lcsh_id STARTS WITH 'sh85125953|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85033169' OR parent.lcsh_id STARTS WITH 'sh85033169|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85125953' OR child.lcsh_id STARTS WITH 'sh85125953|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85046212' OR child.lcsh_id STARTS WITH 'sh85046212|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040989' OR parent.lcsh_id STARTS WITH 'sh85040989|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126434' OR child.lcsh_id STARTS WITH 'sh85126434|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074518' OR parent.lcsh_id STARTS WITH 'sh85074518|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126441' OR child.lcsh_id STARTS WITH 'sh85126441|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074574' OR parent.lcsh_id STARTS WITH 'sh85074574|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126441' OR child.lcsh_id STARTS WITH 'sh85126441|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85077222' OR parent.lcsh_id STARTS WITH 'sh85077222|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126441' OR child.lcsh_id STARTS WITH 'sh85126441|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85126434' OR parent.lcsh_id STARTS WITH 'sh85126434|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126887' OR child.lcsh_id STARTS WITH 'sh85126887|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85111945' OR parent.lcsh_id STARTS WITH 'sh85111945|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126948' OR child.lcsh_id STARTS WITH 'sh85126948|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85126948' OR child.lcsh_id STARTS WITH 'sh85126948|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh86000064' OR parent.lcsh_id STARTS WITH 'sh86000064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86000064' OR child.lcsh_id STARTS WITH 'sh86000064|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101517' OR parent.lcsh_id STARTS WITH 'sh85101517|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh86000064' OR child.lcsh_id STARTS WITH 'sh86000064|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85127580' OR child.lcsh_id STARTS WITH 'sh85127580|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85082139' OR parent.lcsh_id STARTS WITH 'sh85082139|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85128181' OR child.lcsh_id STARTS WITH 'sh85128181|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85107090' OR parent.lcsh_id STARTS WITH 'sh85107090|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85054086' OR child.lcsh_id STARTS WITH 'sh85054086|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85101560' OR parent.lcsh_id STARTS WITH 'sh85101560|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85128566' OR child.lcsh_id STARTS WITH 'sh85128566|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85051944' OR parent.lcsh_id STARTS WITH 'sh85051944|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85129198' OR child.lcsh_id STARTS WITH 'sh85129198|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006611' OR parent.lcsh_id STARTS WITH 'sh85006611|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85129198' OR child.lcsh_id STARTS WITH 'sh85129198|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh94008290' OR child.lcsh_id STARTS WITH 'sh94008290|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85079324' OR parent.lcsh_id STARTS WITH 'sh85079324|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85018306' OR child.lcsh_id STARTS WITH 'sh85018306|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065889' OR parent.lcsh_id STARTS WITH 'sh85065889|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85018306' OR child.lcsh_id STARTS WITH 'sh85018306|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85078128' OR parent.lcsh_id STARTS WITH 'sh85078128|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh00000385' OR child.lcsh_id STARTS WITH 'sh00000385|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85023027' OR parent.lcsh_id STARTS WITH 'sh85023027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85130766' OR child.lcsh_id STARTS WITH 'sh85130766|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85130857' OR child.lcsh_id STARTS WITH 'sh85130857|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85130976' OR child.lcsh_id STARTS WITH 'sh85130976|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85146326' OR parent.lcsh_id STARTS WITH 'sh85146326|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85131750' OR child.lcsh_id STARTS WITH 'sh85131750|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85131750' OR child.lcsh_id STARTS WITH 'sh85131750|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85065864' OR parent.lcsh_id STARTS WITH 'sh85065864|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85131750' OR child.lcsh_id STARTS WITH 'sh85131750|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85131733' OR parent.lcsh_id STARTS WITH 'sh85131733|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85132964' OR child.lcsh_id STARTS WITH 'sh85132964|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118321' OR parent.lcsh_id STARTS WITH 'sh85118321|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85133147' OR child.lcsh_id STARTS WITH 'sh85133147|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118553' OR parent.lcsh_id STARTS WITH 'sh85118553|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85133184' OR child.lcsh_id STARTS WITH 'sh85133184|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043106' OR parent.lcsh_id STARTS WITH 'sh85043106|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85133184' OR child.lcsh_id STARTS WITH 'sh85133184|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85118622' OR parent.lcsh_id STARTS WITH 'sh85118622|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85133270' OR child.lcsh_id STARTS WITH 'sh85133270|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85133270' OR child.lcsh_id STARTS WITH 'sh85133270|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85066289' OR parent.lcsh_id STARTS WITH 'sh85066289|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh94009175' OR child.lcsh_id STARTS WITH 'sh94009175|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85042722' OR parent.lcsh_id STARTS WITH 'sh85042722|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh94009175' OR child.lcsh_id STARTS WITH 'sh94009175|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85098685' OR parent.lcsh_id STARTS WITH 'sh85098685|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85034152' OR child.lcsh_id STARTS WITH 'sh85034152|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040970' OR parent.lcsh_id STARTS WITH 'sh85040970|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh99001177' OR child.lcsh_id STARTS WITH 'sh99001177|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85005581' OR parent.lcsh_id STARTS WITH 'sh85005581|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85134522' OR child.lcsh_id STARTS WITH 'sh85134522|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85099818' OR parent.lcsh_id STARTS WITH 'sh85099818|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85039340' OR child.lcsh_id STARTS WITH 'sh85039340|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85034149' OR parent.lcsh_id STARTS WITH 'sh85034149|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85134614' OR child.lcsh_id STARTS WITH 'sh85134614|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85100163' OR parent.lcsh_id STARTS WITH 'sh85100163|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85134776' OR child.lcsh_id STARTS WITH 'sh85134776|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85136077' OR child.lcsh_id STARTS WITH 'sh85136077|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85085194' OR parent.lcsh_id STARTS WITH 'sh85085194|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85136077' OR child.lcsh_id STARTS WITH 'sh85136077|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85130857' OR parent.lcsh_id STARTS WITH 'sh85130857|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85136089' OR child.lcsh_id STARTS WITH 'sh85136089|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85054133' OR parent.lcsh_id STARTS WITH 'sh85054133|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85136089' OR child.lcsh_id STARTS WITH 'sh85136089|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85104647' OR parent.lcsh_id STARTS WITH 'sh85104647|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85136089' OR child.lcsh_id STARTS WITH 'sh85136089|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85120387' OR parent.lcsh_id STARTS WITH 'sh85120387|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85136092' OR child.lcsh_id STARTS WITH 'sh85136092|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85076357' OR parent.lcsh_id STARTS WITH 'sh85076357|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85028901' OR child.lcsh_id STARTS WITH 'sh85028901|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85136742' OR child.lcsh_id STARTS WITH 'sh85136742|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85136505' OR parent.lcsh_id STARTS WITH 'sh85136505|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85136958' OR child.lcsh_id STARTS WITH 'sh85136958|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074518' OR parent.lcsh_id STARTS WITH 'sh85074518|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85136958' OR child.lcsh_id STARTS WITH 'sh85136958|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85136974' OR parent.lcsh_id STARTS WITH 'sh85136974|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85137069' OR child.lcsh_id STARTS WITH 'sh85137069|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85026331' OR parent.lcsh_id STARTS WITH 'sh85026331|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85137069' OR child.lcsh_id STARTS WITH 'sh85137069|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85043176' OR parent.lcsh_id STARTS WITH 'sh85043176|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2002008688' OR child.lcsh_id STARTS WITH 'sh2002008688|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85146326' OR parent.lcsh_id STARTS WITH 'sh85146326|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85138061' OR child.lcsh_id STARTS WITH 'sh85138061|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85027048' OR parent.lcsh_id STARTS WITH 'sh85027048|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85138061' OR child.lcsh_id STARTS WITH 'sh85138061|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85139563' OR child.lcsh_id STARTS WITH 'sh85139563|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85111790' OR parent.lcsh_id STARTS WITH 'sh85111790|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85141310' OR child.lcsh_id STARTS WITH 'sh85141310|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040850' OR parent.lcsh_id STARTS WITH 'sh85040850|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85026282' OR child.lcsh_id STARTS WITH 'sh85026282|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85074348' OR parent.lcsh_id STARTS WITH 'sh85074348|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85026282' OR child.lcsh_id STARTS WITH 'sh85026282|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85102696' OR parent.lcsh_id STARTS WITH 'sh85102696|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85141451' OR child.lcsh_id STARTS WITH 'sh85141451|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85141939' OR child.lcsh_id STARTS WITH 'sh85141939|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85001441' OR parent.lcsh_id STARTS WITH 'sh85001441|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85141939' OR child.lcsh_id STARTS WITH 'sh85141939|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85072732' OR parent.lcsh_id STARTS WITH 'sh85072732|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85141939' OR child.lcsh_id STARTS WITH 'sh85141939|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084286' OR parent.lcsh_id STARTS WITH 'sh85084286|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85141939' OR child.lcsh_id STARTS WITH 'sh85141939|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85108459' OR parent.lcsh_id STARTS WITH 'sh85108459|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh87003044' OR child.lcsh_id STARTS WITH 'sh87003044|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006232' OR parent.lcsh_id STARTS WITH 'sh85006232|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85143046' OR child.lcsh_id STARTS WITH 'sh85143046|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85083064' OR parent.lcsh_id STARTS WITH 'sh85083064|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85143544' OR child.lcsh_id STARTS WITH 'sh85143544|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85129122' OR parent.lcsh_id STARTS WITH 'sh85129122|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85143555' OR child.lcsh_id STARTS WITH 'sh85143555|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85143613' OR parent.lcsh_id STARTS WITH 'sh85143613|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85143799' OR child.lcsh_id STARTS WITH 'sh85143799|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084783' OR parent.lcsh_id STARTS WITH 'sh85084783|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh93005976' OR child.lcsh_id STARTS WITH 'sh93005976|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85045198' OR parent.lcsh_id STARTS WITH 'sh85045198|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85007461' OR child.lcsh_id STARTS WITH 'sh85007461|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85008324' OR parent.lcsh_id STARTS WITH 'sh85008324|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85143917' OR child.lcsh_id STARTS WITH 'sh85143917|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85029027' OR parent.lcsh_id STARTS WITH 'sh85029027|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85144017' OR child.lcsh_id STARTS WITH 'sh85144017|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85052162' OR parent.lcsh_id STARTS WITH 'sh85052162|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85144279' OR child.lcsh_id STARTS WITH 'sh85144279|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85113021' OR parent.lcsh_id STARTS WITH 'sh85113021|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh2005004309' OR child.lcsh_id STARTS WITH 'sh2005004309|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85063458' OR parent.lcsh_id STARTS WITH 'sh85063458|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85145748' OR child.lcsh_id STARTS WITH 'sh85145748|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh93001294' OR parent.lcsh_id STARTS WITH 'sh93001294|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh98004795' OR child.lcsh_id STARTS WITH 'sh98004795|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh96009904' OR parent.lcsh_id STARTS WITH 'sh96009904|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96008680' OR child.lcsh_id STARTS WITH 'sh96008680|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh95000713' OR parent.lcsh_id STARTS WITH 'sh95000713|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85146011' OR child.lcsh_id STARTS WITH 'sh85146011|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084098' OR parent.lcsh_id STARTS WITH 'sh85084098|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85146012' OR child.lcsh_id STARTS WITH 'sh85146012|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85050766' OR parent.lcsh_id STARTS WITH 'sh85050766|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85146012' OR child.lcsh_id STARTS WITH 'sh85146012|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080664' OR parent.lcsh_id STARTS WITH 'sh85080664|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85146012' OR child.lcsh_id STARTS WITH 'sh85146012|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85084093' OR parent.lcsh_id STARTS WITH 'sh85084093|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85146012' OR child.lcsh_id STARTS WITH 'sh85146012|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85119312' OR parent.lcsh_id STARTS WITH 'sh85119312|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85146325' OR child.lcsh_id STARTS WITH 'sh85146325|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090284' OR parent.lcsh_id STARTS WITH 'sh85090284|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85146326' OR child.lcsh_id STARTS WITH 'sh85146326|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85040752' OR parent.lcsh_id STARTS WITH 'sh85040752|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85146731' OR child.lcsh_id STARTS WITH 'sh85146731|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85031255' OR parent.lcsh_id STARTS WITH 'sh85031255|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85146731' OR child.lcsh_id STARTS WITH 'sh85146731|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090284' OR parent.lcsh_id STARTS WITH 'sh85090284|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96005596' OR child.lcsh_id STARTS WITH 'sh96005596|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090254' OR parent.lcsh_id STARTS WITH 'sh85090254|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh96005596' OR child.lcsh_id STARTS WITH 'sh96005596|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85149996' OR parent.lcsh_id STARTS WITH 'sh85149996|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh92006740' OR child.lcsh_id STARTS WITH 'sh92006740|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85133301' OR parent.lcsh_id STARTS WITH 'sh85133301|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh90004091' OR child.lcsh_id STARTS WITH 'sh90004091|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85080623' OR parent.lcsh_id STARTS WITH 'sh85080623|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85148201' OR child.lcsh_id STARTS WITH 'sh85148201|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85061212' OR parent.lcsh_id STARTS WITH 'sh85061212|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005230' OR child.lcsh_id STARTS WITH 'sh85005230|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85006509' OR parent.lcsh_id STARTS WITH 'sh85006509|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85005230' OR child.lcsh_id STARTS WITH 'sh85005230|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85015539' OR parent.lcsh_id STARTS WITH 'sh85015539|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85149983' OR child.lcsh_id STARTS WITH 'sh85149983|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85014203' OR parent.lcsh_id STARTS WITH 'sh85014203|'
MERGE (parent)-[:BROADER_THAN]->(child);

MATCH (child:Discipline) WHERE child.lcsh_id = 'sh85149983' OR child.lcsh_id STARTS WITH 'sh85149983|'
MATCH (parent:Discipline) WHERE parent.lcsh_id = 'sh85090222' OR parent.lcsh_id STARTS WITH 'sh85090222|'
MERGE (parent)-[:BROADER_THAN]->(child);
