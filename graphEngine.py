
import networkx as nx
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

print(f"testando URI: {URI}")


meu_driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def buildGraph (structuredData):

    graph = nx.DiGraph()

    if "graph_delta" not in structuredData:
        return graph
    

    deltaInfo = structuredData["graph_delta"]

    for entity in deltaInfo.get("new_entities", []):
        graph.add_node(
            entity["id"],
            type=entity["type"],
            name=entity["name"]
        )

    for relation in deltaInfo.get("new_relationships", []):
        graph.add_edge(
            relation["source_id"],
            relation["target_id"],
            relationship_type=relation["relationship_type"]
        )
    return graph

def get_active_context(driver):
    context_data = {"entities": [], "relationships": []}

    with driver.session() as session:
        query = """
        MATCH (n)
        WHERE n.status IS NULL OR (n.status <> 'Done' AND n.status <> 'Resolved')
        RETURN n.id as id, n.name as name, labels(n)[0] as type, n.status as status
        """
        result = session.run(query)
        for record in result:
            context_data["entities"].append({
                "id": record["id"],
                "name": record["name"],
                "type": record["type"],
                "status": record["status"] or "Active"
            })

    return context_data


def load_graph_from_neo4j(driver):
    graph = nx.DiGraph()

    with driver.session() as session:
        nodes_query = """
        MATCH (n)
        WHERE n.status IS NULL OR (n.status <> 'Done' AND n.status <> 'Resolved')
        RETURN n.id as id, n.name as name, labels(n)[0] as type, n.status as status
        """
        for record in session.run(nodes_query):
            graph.add_node(
                record["id"],
                type=record["type"],
                name=record["name"],
                status=record["status"] or "Active"
            )

        edges_query = """
        MATCH (a)-[r]->(b)
        WHERE (a.status IS NULL OR (a.status <> 'Done' AND a.status <> 'Resolved'))
          AND (b.status IS NULL OR (b.status <> 'Done' AND b.status <> 'Resolved'))
        RETURN a.id as source, b.id as target, type(r) as relationship_type
        """
        for record in session.run(edges_query):
            graph.add_edge(
                record["source"],
                record["target"],
                relationship_type=record["relationship_type"]
            )

    isolados = [n for n, grau in graph.degree() if grau == 0]
    graph.remove_nodes_from(isolados)

    return graph



def load_full_graph_from_neo4j(driver):
    graph = nx.DiGraph()

    with driver.session() as session:
        nodes_query = "MATCH (n) RETURN n.id as id, n.name as name, labels(n)[0] as type, n.status as status"
        for record in session.run(nodes_query):
            graph.add_node(
                record["id"],
                type=record["type"],
                name=record["name"],
                status=record["status"] or "Active"
            )

        edges_query = "MATCH (a)-[r]->(b) RETURN a.id as source, b.id as target, type(r) as relationship_type"
        for record in session.run(edges_query):
            graph.add_edge(
                record["source"],
                record["target"],
                relationship_type=record["relationship_type"]
            )

    return graph


if __name__ == "__main__":
    json_teste = {
        'graph_delta': {
            'new_entities': [{'id': 'vanessa', 'type': 'Person', 'name': 'Vanessa'}, {'id': 'server_connection', 'type': 'SystemComponent', 'name': 'Conexão do Servidor'}, {'id': 'fix_server_connection_task', 'type': 'Task', 'name': 'Consertar Conexão do Servidor'}], 
            'new_relationships': [{'source_id': 'vanessa', 'target_id': 'fix_server_connection_task', 'relationship_type': 'PERFORMED'}, {'source_id': 'fix_server_connection_task', 'target_id': 'server_connection', 'relationship_type': 'AFFECTS'}]
        }
    }

    grafo = get_active_context(meu_driver)
    print(grafo)