## Infrastructure
n8n = orchestration when needed - not currently used
python = import to neo4j functions, plus as a tool for langchain agents
neo4j = the knowledge graph
Langchain / Langgraph = orchestration and running agents
ui = tbd

## agents

the graph in neo 4j has two types of nodes - data, and as a shell for running llm agents who  learn a subject and perform operations and use tools

## Subgraphs

thing of this system  as a wiki for subgraphs. the agent (a node) calls lllm to learn and uncover facts, where the agent will persist the knowledge in the graph. 

To me, the main subgraphs explain the who, what, when, where, why and how of an event. all nodes are tethered to a subject backbone - lcc-fast-marc, and many to a temporal backbone,  and a geo backbone. so a "fact" tying to that backbone would be people, geo, temporal, events. each subgraph, which i call a cluster, also has citation nodes - for recording quotes from the sources and perhaps obseration nodes,  where responses are kept to validate and sometimes debate the claim. for people in events - the llm must capture their goal, their ations and the results. GAR. could be many to many relationship between people and events.



