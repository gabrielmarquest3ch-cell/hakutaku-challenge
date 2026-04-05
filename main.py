import streamlit as st
import extrator 

#Configura pagina 
st.set_page_config(page_title="Hakutaku MVP", page_icon="", layout="wide")

#titulo da pagina
st.title("Hakutaku: Organizational Intelligence Layer")
st.markdown("---")

# ==========================================
# ZONA 1: A Torre de Controle (Barra Lateral)
# ==========================================
with st.sidebar:
    st.header("Data entry")
    st.write("Upload your meeting or text message")
    
    # O componente de upload
    file_up = st.file_uploader("Document (.txt)", type=["txt"])
    
    # O botão principal (ainda não faz nada, só mostra um aviso)
    if st.button("Extract knowledgment", type="primary", use_container_width=True):
        if file_up is not None:
            with st.spinner("Processing your file..."):
                fileText = file_up.getvalue().decode("utf-8")

                extractData = extrator.processData(fileText)

                st.session_state['data'] = extractData

                print(extractData)
            
            st.success("Sucesseful data extract")
        else:
            st.warning("Please, upload a .txt file")
        
        
    st.markdown("---")
    
    st.subheader("System X-ray")
    st.write("")
    
    # Componente visual para exibir métricas (números em destaque)
    col_a, col_b = st.columns(2)
    col_a.metric(label="Active Tasks", value="12", delta="+2 today")
    col_b.metric(label="Critical risks", value="3", delta="-1 solved", delta_color="inverse")


# ==========================================
# ZONA 2: Resumo Executivo (Proposals)
# ==========================================
st.header("Insights & Proposals")
st.write("Ai Sugestions :")

# Criamos 3 colunas para colocar os alertas lado a lado
col1, col2, col3 = st.columns(3)

with col1:
    st.error("**imminent risk:** \n\nCliente TechNova mencionou cancelamento. \n\n**Ação sugerida:** Agendar call de contenção com a diretoria.")
with col2:
    st.success("**New delegation:** \n\nMarina Costa assumiu o Mapeamento Salesforce. \n\n**Status:** Em andamento.")
with col3:
    st.warning("**Blocker Indenfied:** \n\nA tarefa 'Integração de API' está bloqueada e sem dono. \n\n**Ação sugerida:** Atribuir a um engenheiro sênior.")

st.markdown("---")

# ==========================================
# ZONA 3: O Cérebro da Empresa (O Grafo)
# ==========================================
st.header("Knowledge Graph (Actual State)")
st.write("Tecnical vision. (Showing pending only).")

# Criamos uma caixa com borda para demarcar onde o gráfico matemático vai entrar
caixa_grafo = st.container(border=True)
with caixa_grafo:
    st.html(
        "<div style='height: 400px; display: flex; align-items: center; justify-content: center; color: gray; font-size: 20px;'>"
        ""
        "</div>"
    )