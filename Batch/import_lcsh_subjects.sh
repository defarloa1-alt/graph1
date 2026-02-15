# Import LCSH Subjects Cypher into Neo4j
# Usage: bash import_lcsh_subjects.sh <NEO4J_USERNAME> <NEO4J_PASSWORD> <NEO4J_BOLT_URL>
# Example: bash import_lcsh_subjects.sh neo4j mypassword bolt://localhost:7687

NEO4J_USER=$1
NEO4J_PASS=$2
NEO4J_URL=$3
CYPHER_FILE="LCSH/skos subject/subjects_full.cypher"

if [ -z "$NEO4J_USER" ] || [ -z "$NEO4J_PASS" ] || [ -z "$NEO4J_URL" ]; then
  echo "Usage: bash import_lcsh_subjects.sh <NEO4J_USERNAME> <NEO4J_PASSWORD> <NEO4J_BOLT_URL>"
  exit 1
fi

# Import using cypher-shell (must be installed and on PATH)
cat "$CYPHER_FILE" | cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASS" -a "$NEO4J_URL"

echo "Import complete."
