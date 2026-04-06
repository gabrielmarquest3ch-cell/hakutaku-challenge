import networkx as nx

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

if __name__ == "__main__":
    json_teste = {
        'graph_delta': {
            'new_entities': [{'id': 'vanessa', 'type': 'Person', 'name': 'Vanessa'}, {'id': 'server_connection', 'type': 'SystemComponent', 'name': 'Conexão do Servidor'}, {'id': 'fix_server_connection_task', 'type': 'Task', 'name': 'Consertar Conexão do Servidor'}], 
            'new_relationships': [{'source_id': 'vanessa', 'target_id': 'fix_server_connection_task', 'relationship_type': 'PERFORMED'}, {'source_id': 'fix_server_connection_task', 'target_id': 'server_connection', 'relationship_type': 'AFFECTS'}]
        }
    }

    grafo = buildGraph(json_teste)
    print(f" Nós: {grafo.number_of_nodes()} | Arestas: {grafo.number_of_edges()}")