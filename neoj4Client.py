import os
import hashlib
from datetime import datetime
from neo4j import GraphDatabase

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

def save_to_neo4j(structured_data):
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    with driver.session() as session:
        delta = structured_data.get("graph_delta", {})

        now = datetime.utcnow().isoformat()

        for entity in delta.get("new_entities", []):
            query = (
                f"MERGE (n:{entity['type']} {{id: $id}}) "
                "SET n.name = $name, n.status = $status, "
                "n.created_at = coalesce(n.created_at, $now)"
            )
            session.run(query, id=entity['id'], name=entity['name'], status=entity.get('status', 'Active'), now=now)

        for rel in delta.get("new_relationships", []):
            query = (
                "MATCH (a {id: $source_id}), (b {id: $target_id}) "
                f"MERGE (a)-[r:{rel['relationship_type']}]->(b)"
            )
            session.run(query, source_id=rel['source_id'], target_id=rel['target_id'])

        for update in delta.get("status_updates", []):
            if update['new_status'] in ('Done', 'Resolved'):
                completed_at = update.get('completed_at') or now[:10]
                query = "MATCH (n {id: $id}) SET n.status = $status, n.completed_at = coalesce(n.completed_at, $completed_at)"
                session.run(query, id=update['entity_id'], status=update['new_status'], completed_at=completed_at)
            else:
                query = "MATCH (n {id: $id}) SET n.status = $status"
                session.run(query, id=update['entity_id'], status=update['new_status'])

        for proposal in structured_data.get("proposals", []):
            pid = "proposal_" + hashlib.md5(proposal["message"].encode()).hexdigest()[:12]
            query = (
                "MERGE (p:Proposal {id: $id}) "
                "SET p.type = $type, p.message = $message, p.status = coalesce(p.status, 'Open')"
            )
            session.run(query, id=pid, type=proposal.get("type", "info"), message=proposal["message"])

    driver.close()


def load_active_tasks_from_neo4j():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    tasks = []
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Task)
            WHERE t.status IN ['Active', 'Pending']
            OPTIONAL MATCH (p:Person)-[:PERFORMED]->(t)
            RETURN t.id as id, t.name as name, t.status as status, collect(p.name) as owners
        """)
        for record in result:
            tasks.append({
                "id": record["id"],
                "name": record["name"],
                "status": record["status"],
                "owners": record["owners"]
            })
    driver.close()
    return tasks


def load_completed_tasks_from_neo4j():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    tasks = []
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Task)
            WHERE t.status = 'Done'
            OPTIONAL MATCH (p:Person)-[:PERFORMED]->(t)
            RETURN t.id as id, t.name as name, collect(p.name) as owners
        """)
        for record in result:
            tasks.append({
                "id": record["id"],
                "name": record["name"],
                "owners": record["owners"]
            })
    driver.close()
    return tasks


def load_resolved_risks_from_neo4j():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    risks = []
    with driver.session() as session:
        result = session.run("""
            MATCH (r:Risk)
            WHERE r.status = 'Resolved'
            OPTIONAL MATCH (src)-[:RAISED]->(r)
            RETURN r.id as id, r.name as name, collect(src.name) as raised_by
        """)
        for record in result:
            risks.append({
                "id": record["id"],
                "name": record["name"],
                "raised_by": record["raised_by"]
            })
    driver.close()
    return risks


def load_active_risks_from_neo4j():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    risks = []
    with driver.session() as session:
        result = session.run("""
            MATCH (r:Risk)
            WHERE r.status IN ['Active', 'Pending']
            OPTIONAL MATCH (src)-[:RAISED]->(r)
            RETURN r.id as id, r.name as name, r.status as status, collect(src.name) as raised_by
        """)
        for record in result:
            risks.append({
                "id": record["id"],
                "name": record["name"],
                "status": record["status"],
                "raised_by": record["raised_by"]
            })
    driver.close()
    return risks


def load_completion_chart_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    tasks, risks = [], []
    with driver.session() as session:
        result = session.run(
            "MATCH (t:Task) WHERE t.completed_at IS NOT NULL RETURN t.completed_at as date ORDER BY date"
        )
        for record in result:
            tasks.append(record["date"][:10])

        result = session.run(
            "MATCH (r:Risk) WHERE r.completed_at IS NOT NULL RETURN r.completed_at as date ORDER BY date"
        )
        for record in result:
            risks.append(record["date"][:10])
    driver.close()
    return tasks, risks


def load_metrics_from_neo4j():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    metrics = {"active_tasks": 0, "critical_risks": 0}
    with driver.session() as session:
        result = session.run(
            "MATCH (t:Task) WHERE t.status IN ['Active', 'Pending'] RETURN count(t) as total"
        )
        metrics["active_tasks"] = result.single()["total"]

        result = session.run(
            "MATCH (r:Risk) WHERE r.status IN ['Active', 'Pending'] RETURN count(r) as total"
        )
        metrics["critical_risks"] = result.single()["total"]
    driver.close()
    return metrics


def load_proposals_from_neo4j():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    proposals = []
    with driver.session() as session:
        result = session.run(
            "MATCH (p:Proposal) WHERE p.status = 'Open' RETURN p.type as type, p.message as message"
        )
        for record in result:
            proposals.append({"type": record["type"], "message": record["message"]})
    driver.close()
    return proposals