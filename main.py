import streamlit as st
import extrator 
import graphEngine
from streamlit_agraph import agraph, Node, Edge, Config
import neoj4Client

# page config
st.set_page_config(page_title="Hakutaku MVP", page_icon="", layout="wide")

# Page title
st.title("Hakutaku: Organizational Intelligence Layer")
st.markdown("---")

# ==========================================
# (Side Bar)
# ==========================================
with st.sidebar:
    st.header("Data entry")
    st.write("Upload your meeting or text message")
    
    # file uploader
    file_up = st.file_uploader("Document (.txt)", type=["txt"])
    
    # O botão principal (ainda não faz nada, só mostra um aviso)
    if st.button("Extract knowledgment", type="primary", use_container_width=True):
        if file_up is not None:
            with st.spinner("Processing your file..."):


                fileText = file_up.getvalue().decode("utf-8")

                existing_context = graphEngine.get_active_context(graphEngine.meu_driver)
                extractData = extrator.processData(fileText, existing_context)

                neoj4Client.save_to_neo4j(extractData)

                st.success("Data save em database")


                st.session_state['data'] = extractData
                st.session_state['proposals'] = extractData.get('proposals', [])

                graph_networkx = graphEngine.load_graph_from_neo4j(graphEngine.meu_driver)

                st.session_state['graph'] = graph_networkx


            st.success("Sucesseful data extract")

            st.write(f"**Nodes** {graph_networkx.number_of_nodes()}")
            st.write(f"**Conections** {graph_networkx.number_of_edges()}")
            with st.expander("show JSON"):
                st.json(extractData)
        else:
            st.warning("Please, upload a .txt file")
        
        
    st.markdown("---")
    
    st.subheader("System X-ray")
    st.write("")
    
    # metrics 
    col_a, col_b = st.columns(2)
    col_a.metric(label="Active Tasks", value="12", delta="+2 today")
    col_b.metric(label="Critical risks", value="3", delta="-1 solved", delta_color="inverse")


# ==========================================
# Proposals
# ==========================================
st.header("Insights & Proposals")
st.write("Ai Sugestions :")

proposals = st.session_state.get('proposals', [])

if not proposals:
    st.info("No proposals yet. Upload a document to generate insights.")
else:
    type_labels = {"risk": "Risk", "task": "Task", "bottleneck": "Bottleneck"}

    for i in range(0, len(proposals), 3):
        cols = st.columns(3)
        for j, proposal in enumerate(proposals[i:i+3]):
            ptype = proposal.get('type', 'info')
            label = type_labels.get(ptype, ptype.capitalize())
            message = f"**{label}**\n\n{proposal.get('message', '')}"
            with cols[j]:
                if ptype == 'risk':
                    st.error(message)
                elif ptype in ('task', 'bottleneck'):
                    st.warning(message)
                else:
                    st.info(message)

st.markdown("---")

# ==========================================
# Graph
# ==========================================
st.header("Knowledge Graph (Actual State)")
st.write("Technical vision. (Showing pending only).")

# Carrega o grafo do Neo4j se ainda não estiver na sessão
if 'graph' not in st.session_state:
    st.session_state['graph'] = graphEngine.load_graph_from_neo4j(graphEngine.meu_driver)

# 1. Verifica se o grafo já foi extraído e está na memória
if 'graph' in st.session_state:
    # 2. Resgata o grafo da memória!
    grafo_atual = st.session_state['graph']
    
    nodes = []
    edges = []

    # 3. Usa o grafo resgatado para criar os nós COLORIDOS e LIMPÍSSIMOS
    for node_id, node_data in grafo_atual.nodes(data=True):
        tipo_no = node_data.get("type", "Unknown")
        label_no = node_data.get("name", node_id)
        
        # Define o visual baseado no TIPO da entidade (A Ontologia!)
        cor_no = "#82b1ff" # Azul padrão
        
        if tipo_no == "Person":
            cor_no = "#0d47a1" # Azul escuro
            formato_no = "dot"
        elif tipo_no == "Task":
            cor_no = "#ffb300" # Âmbar
            formato_no = "hexagon"
        elif tipo_no == "Risk":
            cor_no = "#d32f2f" # Vermelho
            formato_no = "triangle"
        elif tipo_no == "Client":
            cor_no = "#2e7d32" # Verde
            formato_no = "star"
        elif tipo_no == "Event":
            cor_no = "#ab47bc" # Roxo
            formato_no = "diamond"
        
        nodes.append(
            Node(
                id=node_id,
                label=label_no,
                size=20, # Tamanho mais equilibrado
                shape=formato_no,
                color=cor_no
            )
        )

    # 4. Usa o grafo resgatado para criar as arestas CLARAS e LIMPÍSSIMAS
    for source, target, edge_data in grafo_atual.edges(data=True):
        rel_type = edge_data.get("relationship_type", "")
        
        # Melhora o visual da aresta e remove o contorno do texto!
        edges.append(
            Edge(
                source=source,
                target=target,
                label=rel_type,
                type="CURVE_SMOOTH",
                color="#757575", # Cinza
                label_color="#bdbdbd" # Cinza claro para o texto
            )
        )

    config_dict = {
        "width": "100%",
        "height": 800,
        "directed": True,
        "hierarchical": True,
        "nodes": {
            "font": {"color": "#e0e0e0", "size": 13, "face": "Arial"},
            "borderWidthSelected": 2,
            "widthConstraint": {"maximum": 160}
        },
        "edges": {
            "font": {
                "color": "#757575",
                "size": 10,
                "align": "top",
                "strokeWidth": 0,
                "background": "transparent"
            },
            "smooth": {"type": "cubicBezier", "forceDirection": "vertical", "roundness": 0.4},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.4}}
        },
        "physics": {"enabled": False},
        "layout": {
            "hierarchical": {
                "enabled": True,
                "direction": "UD",
                "sortMethod": "directed",
                "nodeSpacing": 180,
                "levelSeparation": 160,
                "treeSpacing": 220
            }
        }
    }

    # Transforma o dicionário em um objeto Config
    config = Config(**config_dict)

    # Graph container
    caixa_grafo = st.container(border=True)
    with caixa_grafo:
        st.write("Ajustando a visualização interativa...")
        return_value = agraph(nodes=nodes, edges=edges, config=config)

else:
    st.info("Please upload a document and click 'Extract knowledgment' to generate the graph.")

# ==========================================
# Full History Graph
# ==========================================
st.markdown("---")
st.header("Full Knowledge Graph (Historical)")
st.write("Complete view including resolved and completed entities.")

full_graph = graphEngine.load_full_graph_from_neo4j(graphEngine.meu_driver)

if full_graph.number_of_nodes() == 0:
    st.info("No data in the knowledge base yet.")
else:
    status_opacity = {"Done": "#555555", "Resolved": "#555555", "Active": None, "Pending": None}

    full_nodes = []
    full_edges = []

    for node_id, node_data in full_graph.nodes(data=True):
        tipo_no = node_data.get("type", "Unknown")
        label_no = node_data.get("name", node_id)
        status_no = node_data.get("status", "Active")

        if status_no in ("Done", "Resolved"):
            cor_no = "#444444"
            formato_no = "dot"
        elif tipo_no == "Person":
            cor_no = "#0d47a1"
            formato_no = "dot"
        elif tipo_no == "Task":
            cor_no = "#ffb300"
            formato_no = "hexagon"
        elif tipo_no == "Risk":
            cor_no = "#d32f2f"
            formato_no = "triangle"
        elif tipo_no == "Client":
            cor_no = "#2e7d32"
            formato_no = "star"
        elif tipo_no == "Event":
            cor_no = "#ab47bc"
            formato_no = "diamond"
        else:
            cor_no = "#82b1ff"
            formato_no = "dot"

        full_nodes.append(Node(id=node_id, label=label_no, size=20, shape=formato_no, color=cor_no))

    for source, target, edge_data in full_graph.edges(data=True):
        rel_type = edge_data.get("relationship_type", "")
        full_edges.append(Edge(source=source, target=target, label=rel_type, type="CURVE_SMOOTH", color="#444444", label_color="#666666"))

    config_full_dict = {
        "width": "100%",
        "height": 800,
        "directed": True,
        "hierarchical": True,
        "nodes": {
            "font": {"color": "#e0e0e0", "size": 13, "face": "Arial"},
            "borderWidthSelected": 2,
            "widthConstraint": {"maximum": 160}
        },
        "edges": {
            "font": {
                "color": "#757575",
                "size": 10,
                "align": "top",
                "strokeWidth": 0,
                "background": "transparent"
            },
            "smooth": {"type": "cubicBezier", "forceDirection": "vertical", "roundness": 0.4},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.4}}
        },
        "physics": {"enabled": False},
        "layout": {
            "hierarchical": {
                "enabled": True,
                "direction": "UD",
                "sortMethod": "directed",
                "nodeSpacing": 180,
                "levelSeparation": 160,
                "treeSpacing": 220
            }
        }
    }

    config_full = Config(**config_full_dict)

    caixa_full = st.container(border=True)
    with caixa_full:
        agraph(nodes=full_nodes, edges=full_edges, config=config_full)