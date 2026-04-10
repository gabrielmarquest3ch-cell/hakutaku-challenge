import streamlit as st
import extrator
import graphEngine
import neoj4Client
import pandas as pd
from collections import Counter
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="Hakutaku MVP", layout="wide")

if 'proposals' not in st.session_state:
    st.session_state['proposals'] = neoj4Client.load_proposals_from_neo4j()
if 'graph' not in st.session_state:
    st.session_state['graph'] = graphEngine.load_graph_from_neo4j(graphEngine.driver)

st.title("Hakutaku: Organizational Intelligence Layer")
st.markdown("---")

with st.sidebar:
    st.header("Data Entry")
    st.write("Upload a meeting transcript or chat thread.")

    file_up = st.file_uploader("Document (.txt)", type=["txt"])

    if st.button("Extract Knowledge", type="primary", use_container_width=True):
        if file_up is not None:
            with st.spinner("Processing your file..."):
                text = file_up.getvalue().decode("utf-8")
                context = graphEngine.get_active_context(graphEngine.driver)
                extracted = extrator.processData(text, context)

                neoj4Client.save_to_neo4j(extracted)
                st.session_state['data'] = extracted
                st.session_state['proposals'] = neoj4Client.load_proposals_from_neo4j()
                st.session_state['graph'] = graphEngine.load_graph_from_neo4j(graphEngine.driver)

            graph = st.session_state['graph']
            st.success("Knowledge extracted successfully.")
            st.write(f"**Nodes:** {graph.number_of_nodes()}")
            st.write(f"**Connections:** {graph.number_of_edges()}")
            with st.expander("Show JSON"):
                st.json(extracted)
        else:
            st.warning("Please upload a .txt file.")

    st.markdown("---")
    st.subheader("System X-ray")

    metrics = neoj4Client.load_metrics_from_neo4j()
    col_a, col_b = st.columns(2)
    col_a.metric("Active Tasks", metrics["active_tasks"])
    col_b.metric("Critical Risks", metrics["critical_risks"])


# Insights & Proposals
st.header("Insights & Proposals")
st.write("AI-generated suggestions based on extracted knowledge:")

proposals = st.session_state.get('proposals', [])

if not proposals:
    st.info("No proposals yet. Upload a document to generate insights.")
else:
    TYPE_LABELS = {"risk": "Risk", "task": "Suggested Task", "bottleneck": "Bottleneck"}
    type_key = {v: k for k, v in TYPE_LABELS.items()}

    col_filter, col_toggle = st.columns([3, 1])
    with col_filter:
        selected = st.segmented_control("Filter", ["All"] + list(TYPE_LABELS.values()), default="All", label_visibility="collapsed")
    with col_toggle:
        group_by = st.toggle("Group by type", value=False)

    filtered = proposals if selected == "All" else [p for p in proposals if p.get("type") == type_key.get(selected)]

    def render_proposals(items):
        for i in range(0, len(items), 3):
            cols = st.columns(3)
            for j, proposal in enumerate(items[i:i+3]):
                ptype = proposal.get('type', 'info')
                label = TYPE_LABELS.get(ptype, ptype.capitalize())
                msg = f"**{label}**\n\n{proposal.get('message', '')}"
                with cols[j]:
                    if ptype == 'risk':
                        st.error(msg)
                    elif ptype == 'bottleneck':
                        st.warning(msg)
                    else:
                        st.info(msg)

    if group_by:
        for ptype, label in TYPE_LABELS.items():
            group = [p for p in filtered if p.get("type") == ptype]
            if group:
                st.markdown(f"**{label}s**")
                render_proposals(group)
    else:
        render_proposals(filtered[:3])
        if len(filtered) > 3:
            with st.expander(f"See more ({len(filtered) - 3} more)"):
                render_proposals(filtered[3:])

st.markdown("---")

# Tasks & Risks
st.header("Tasks & Risks")

tab_active, tab_history, tab_risks = st.tabs(["Active Tasks", "Completed Tasks", "Risk Mitigation"])

with tab_active:
    active_tasks = neoj4Client.load_active_tasks_from_neo4j()
    if not active_tasks:
        st.info("No active tasks found.")
    else:
        for task in active_tasks:
            owners = ", ".join(task["owners"]) if task["owners"] else "Unassigned"
            indicator = "🟡" if task["status"] == "Pending" else "🔵"
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 3, 1])
                c1.markdown(f"**{task['name']}**")
                c2.markdown(f"👤 {owners}")
                c3.markdown(f"{indicator} {task['status']}")

with tab_history:
    completed_tasks = neoj4Client.load_completed_tasks_from_neo4j()
    if not completed_tasks:
        st.info("No completed tasks yet.")
    else:
        for task in completed_tasks:
            owners = ", ".join(task["owners"]) if task["owners"] else "Unassigned"
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 3, 1])
                c1.markdown(f"**{task['name']}**")
                c2.markdown(f"👤 {owners}")
                c3.markdown("✅ Done")

with tab_risks:
    active_risks = neoj4Client.load_active_risks_from_neo4j()
    resolved_risks = neoj4Client.load_resolved_risks_from_neo4j()

    if active_risks:
        st.subheader("Open Risks")
        for risk in active_risks:
            raised_by = ", ".join(risk["raised_by"]) if risk["raised_by"] else "Unknown"
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 3, 1])
                c1.markdown(f"**{risk['name']}**")
                c2.markdown(f"⚠️ Raised by {raised_by}")
                c3.markdown("🔴 Open")

    if resolved_risks:
        st.subheader("Mitigated Risks")
        for risk in resolved_risks:
            raised_by = ", ".join(risk["raised_by"]) if risk["raised_by"] else "Unknown"
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 3, 1])
                c1.markdown(f"**{risk['name']}**")
                c2.markdown(f"⚠️ Raised by {raised_by}")
                c3.markdown("✅ Mitigated")

    if not active_risks and not resolved_risks:
        st.info("No risks found.")

st.markdown("---")


def get_component_positions(graph):
    components = sorted(nx_weakly_connected_components(graph), key=len, reverse=True)
    positions = {}
    zone_width = 800
    for i, component in enumerate(components):
        cx = i * zone_width
        for j, node_id in enumerate(component):
            positions[node_id] = (cx + (j % 3) * 150, (j // 3) * 150)
    return positions


def nx_weakly_connected_components(graph):
    import networkx as nx
    return list(nx.weakly_connected_components(graph))


NODE_STYLES = {
    "Person":          ("#0d47a1", "dot"),
    "Task":            ("#ffb300", "hexagon"),
    "Risk":            ("#d32f2f", "triangle"),
    "Client":          ("#2e7d32", "star"),
    "Event":           ("#ab47bc", "diamond"),
    "SystemComponent": ("#82b1ff", "dot"),
}

GRAPH_CONFIG = {
    "width": "100%",
    "height": 800,
    "directed": True,
    "nodes": {
        "font": {"color": "#e0e0e0", "size": 13, "face": "Arial"},
        "borderWidthSelected": 2,
        "widthConstraint": {"maximum": 140}
    },
    "edges": {
        "font": {"color": "#757575", "size": 10, "align": "top", "strokeWidth": 0, "background": "transparent"},
        "smooth": {"type": "curvedCW", "roundness": 0.2},
        "arrows": {"to": {"enabled": True, "scaleFactor": 0.4}}
    },
    "physics": {
        "enabled": True,
        "solver": "repulsion",
        "repulsion": {
            "nodeDistance": 300,
            "centralGravity": 0.001,
            "springLength": 350,
            "springConstant": 0.003,
            "damping": 0.15
        },
        "stabilization": {"enabled": True, "iterations": 2000}
    }
}


def build_vis_nodes(graph, positions, include_resolved=False):
    nodes = []
    for node_id, data in graph.nodes(data=True):
        node_type = data.get("type", "Unknown")
        status = data.get("status", "Active")

        if include_resolved and status in ("Done", "Resolved"):
            color, shape = "#444444", "dot"
        else:
            color, shape = NODE_STYLES.get(node_type, ("#82b1ff", "dot"))

        x, y = positions.get(node_id, (0, 0))
        nodes.append(Node(id=node_id, label=data.get("name", node_id), size=20, shape=shape, color=color, x=x, y=y))
    return nodes


def build_vis_edges(graph, color="#757575", label_color="#bdbdbd"):
    return [
        Edge(source=s, target=t, label=d.get("relationship_type", ""), type="CURVE_SMOOTH", color=color, label_color=label_color)
        for s, t, d in graph.edges(data=True)
    ]


# Active State Graph
st.header("Knowledge Graph — Active State")
st.write("Showing active and pending entities only.")

if 'graph' in st.session_state:
    g = st.session_state['graph']
    pos = get_component_positions(g)
    with st.container(border=True):
        agraph(nodes=build_vis_nodes(g, pos), edges=build_vis_edges(g), config=Config(**GRAPH_CONFIG))
else:
    st.info("No data yet. Upload a document to generate the knowledge graph.")

st.markdown("---")

# Full Historical Graph
st.header("Knowledge Graph — Historical")
st.write("Complete view including resolved and completed entities.")

full_graph = graphEngine.load_full_graph_from_neo4j(graphEngine.driver)

if full_graph.number_of_nodes() == 0:
    st.info("No data in the knowledge base yet.")
else:
    pos_full = get_component_positions(full_graph)
    with st.container(border=True):
        agraph(
            nodes=build_vis_nodes(full_graph, pos_full, include_resolved=True),
            edges=build_vis_edges(full_graph, color="#444444", label_color="#666666"),
            config=Config(**GRAPH_CONFIG)
        )

st.markdown("---")

# Analytics
st.header("Analytics")

task_dates, risk_dates = neoj4Client.load_completion_chart_data()
tab_tasks_chart, tab_risks_chart = st.tabs(["Task Completion", "Risk Mitigation"])

with tab_tasks_chart:
    if not task_dates:
        st.info("No completed tasks to display yet.")
    else:
        counts = Counter(task_dates)
        df = pd.DataFrame(sorted(counts.items()), columns=["Date", "Completed"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        df["Cumulative"] = df["Completed"].cumsum()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Completed per Day")
            st.bar_chart(df["Completed"])
        with c2:
            st.subheader("Cumulative Completion")
            st.line_chart(df["Cumulative"])

with tab_risks_chart:
    if not risk_dates:
        st.info("No mitigated risks to display yet.")
    else:
        counts = Counter(risk_dates)
        df = pd.DataFrame(sorted(counts.items()), columns=["Date", "Mitigated"])
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
        df["Cumulative"] = df["Mitigated"].cumsum()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Mitigated per Day")
            st.bar_chart(df["Mitigated"])
        with c2:
            st.subheader("Cumulative Mitigation")
            st.line_chart(df["Cumulative"])
