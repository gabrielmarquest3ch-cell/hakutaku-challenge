import os
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

def save_to_neo4j(structured_data):
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    with driver.session() as session:
        delta = structured_data.get("graph_delta", {})

        for entity in delta.get("new_entities", []):
            query = (
                f"MERGE (n:{entity['type']} {{id: $id}}) "
                "SET n.name = $name"
            )
            session.run(query, id=entity['id'], name=entity['name'])

        for rel in delta.get("new_relationships", []):
            query = (
                "MATCH (a {id: $source_id}), (b {id: $target_id}) "
                f"MERGE (a)-[r:{rel['relationship_type']}]->(b)"
            )
            session.run(query, source_id=rel['source_id'], target_id=rel['target_id'])

    driver.close()