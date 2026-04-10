import os
import networkx as nx
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

# Keep meu_driver as alias for backwards compatibility with main.py references
meu_driver = driver


def get_active_context(neo4j_driver):
    context = {"entities": [], "relationships": []}

    with neo4j_driver.session() as session:
        result = session.run("""
            MATCH (n)
            WHERE NOT n:Proposal
              AND (n.status IS NULL OR (n.status <> 'Done' AND n.status <> 'Resolved'))
            RETURN n.id as id, n.name as name, labels(n)[0] as type, n.status as status
        """)
        for record in result:
            context["entities"].append({
                "id": record["id"],
                "name": record["name"],
                "type": record["type"],
                "status": record["status"] or "Active"
            })

    return context


def load_graph_from_neo4j(neo4j_driver):
    graph = nx.DiGraph()

    with neo4j_driver.session() as session:
        nodes = session.run("""
            MATCH (n)
            WHERE NOT n:Proposal
              AND (n.status IS NULL OR (n.status <> 'Done' AND n.status <> 'Resolved'))
            RETURN n.id as id, n.name as name, labels(n)[0] as type, n.status as status
        """)
        for record in nodes:
            graph.add_node(
                record["id"],
                type=record["type"],
                name=record["name"],
                status=record["status"] or "Active"
            )

        edges = session.run("""
            MATCH (a)-[r]->(b)
            WHERE (a.status IS NULL OR (a.status <> 'Done' AND a.status <> 'Resolved'))
              AND (b.status IS NULL OR (b.status <> 'Done' AND b.status <> 'Resolved'))
            RETURN a.id as source, b.id as target, type(r) as relationship_type
        """)
        for record in edges:
            graph.add_edge(record["source"], record["target"], relationship_type=record["relationship_type"])

    isolated = [n for n, degree in graph.degree() if degree == 0]
    graph.remove_nodes_from(isolated)

    return graph


def load_full_graph_from_neo4j(neo4j_driver):
    graph = nx.DiGraph()

    with neo4j_driver.session() as session:
        nodes = session.run(
            "MATCH (n) WHERE NOT n:Proposal RETURN n.id as id, n.name as name, labels(n)[0] as type, n.status as status"
        )
        for record in nodes:
            graph.add_node(
                record["id"],
                type=record["type"],
                name=record["name"],
                status=record["status"] or "Active"
            )

        edges = session.run(
            "MATCH (a)-[r]->(b) RETURN a.id as source, b.id as target, type(r) as relationship_type"
        )
        for record in edges:
            graph.add_edge(record["source"], record["target"], relationship_type=record["relationship_type"])

    return graph
