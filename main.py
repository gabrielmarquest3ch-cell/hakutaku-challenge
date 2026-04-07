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

                extractData = extrator.processData(fileText)

                neoj4Client.save_to_neo4j(extractData)

                st.success("Data save em database")


                st.session_state['data'] = extractData

                graph_networkx = graphEngine.buildGraph(extractData)

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

# Alerts 
col1, col2, col3 = st.columns(3)

with col1:  
    st.error("**imminent risk:** \n\nCliente TechNova mencionou cancelamento. \n\n**Ação sugerida:** Agendar call de contenção com a diretoria.")
with col2:
    st.success("**New delegation:** \n\nMarina Costa assumiu o Mapeamento Salesforce. \n\n**Status:** Em andamento.")
with col3:
    st.warning("**Blocker Indenfied:** \n\nA tarefa 'Integração de API' está bloqueada e sem dono. \n\n**Ação sugerida:** Atribuir a um engenheiro sênior.")

st.markdown("---")

# ==========================================
# Graph
# ==========================================
st.header("Knowledge Graph (Actual State)")
st.write("Technical vision. (Showing pending only).")

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

    # 5. Configurando o visual e a FÍSICA para dar espaço
    config_dict = {
        "width": 800,
        "height": 500,
        "directed": True,
        "nodes": {
            "font": {"color": "#616161", "size": 14, "face": "Arial", "multi": True}, # Arial limpa, cor cinza, tamanho menor
            "borderWidthSelected": 2
        },
        "edges": {
            "font": {
                "color": "#bdbdbd", 
                "size": 12, 
                "align": "top", 
                "strokeWidth": 0, # <--- ESSA É A MÁGICA QUE TIRA A BORDA!
                "background": "transparent"
            },
            "smooth": {"type": "curvedCW", "roundness": 0.2},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}}
        },
        "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -35000, # Aumentei MUITO a repulsão (era -10000)
                "centralGravity": 0.003,         # Diminuí o puxão pro centro (era 0.01)
                "springLength": 300,             # Deixei as setas bem mais longas (era 180)
                "springConstant": 0.005,         # Deixei as setas mais flexíveis
                "damping": 0.09,
                "avoidOverlap": 1
            },
            "stabilization": {"enabled": True, "iterations": 1000}
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
    # O que mostrar quando a página abre pela primeira vez
    st.info("Please upload a document and click 'Extract knowledgment' to generate the graph.")