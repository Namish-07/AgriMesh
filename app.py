
import random

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AgriMesh | Precision Agriculture",
    page_icon="🌾",
    layout="wide",
)

st.title("🌾 AgriMesh")
st.subheader("Fault-Tolerant Mesh Network for Precision Agriculture")
st.caption(
    "A simulated rural agricultural sensor network demonstrating "
    "mesh topology, shortest-path routing, and fault tolerance."
)

NODES = ["Gateway", "Sensor_A", "Sensor_B", "Sensor_C", "Sensor_D"]

LINKS = [
    ("Gateway", "Sensor_A"),
    ("Gateway", "Sensor_B"),
    ("Sensor_A", "Sensor_C"),
    ("Sensor_B", "Sensor_C"),
    ("Sensor_C", "Sensor_D"),
    ("Sensor_B", "Sensor_D"),
]

POSITIONS = {
    "Gateway": (0, 1.3),
    "Sensor_A": (-1.2, 0.3),
    "Sensor_B": (1.2, 0.3),
    "Sensor_C": (-0.4, -0.7),
    "Sensor_D": (1.2, -1.1),
}

if "failed_links" not in st.session_state:
    st.session_state.failed_links = set()
if "history" not in st.session_state:
    st.session_state.history = []

def build_network():
    graph = nx.Graph()
    graph.add_nodes_from(NODES)
    for a, b in LINKS:
        edge = tuple(sorted((a, b)))
        if edge not in st.session_state.failed_links:
            graph.add_edge(a, b)
    return graph

def edge_key(a, b):
    return tuple(sorted((a, b)))

def transmit(graph, source, moisture, temperature):
    payload = {
        "sensor_id": source,
        "soil_moisture_pct": moisture,
        "temperature_c": temperature,
    }

    try:
        route = nx.shortest_path(graph, source, "Gateway")
        delivered = True
        hops = len(route) - 1
        message = "Packet delivered successfully"
    except nx.NetworkXNoPath:
        route = []
        delivered = False
        hops = None
        message = "Delivery failed: no route to gateway"

    st.session_state.history.append({
        "Source": source,
        "Payload": f"Moisture={moisture}%, Temp={temperature}°C",
        "Route": " → ".join(route) if route else "No route",
        "Hops": hops if hops is not None else "—",
        "Status": "Delivered" if delivered else "Failed",
    })

    return payload, route, delivered, hops, message

st.markdown("### 1. Wireless link controls")

left, right = st.columns([1, 1])

with left:
    for a, b in LINKS:
        key = edge_key(a, b)
        failed = key in st.session_state.failed_links
        label = f"{a} ↔ {b}"

        if failed:
            if st.button(f"Restore link: {label}", key=f"restore_{a}_{b}"):
                st.session_state.failed_links.remove(key)
                st.rerun()
        else:
            if st.button(f"Disable link: {label}", key=f"disable_{a}_{b}"):
                st.session_state.failed_links.add(key)
                st.rerun()

with right:
    st.markdown("**Link status**")
    st.write(f"Active links: {len(LINKS) - len(st.session_state.failed_links)}")
    st.write(f"Failed links: {len(st.session_state.failed_links)}")
    st.write("Routing method: NetworkX shortest path")

graph = build_network()

st.divider()
st.markdown("### 2. Network topology")

fig, ax = plt.subplots(figsize=(9, 5))
node_colors = [
    "#f4b942" if node == "Gateway"
    else "#55ad82" if nx.has_path(graph, node, "Gateway")
    else "#dc5555"
    for node in NODES
]

nx.draw_networkx_nodes(
    graph, POSITIONS, node_color=node_colors,
    node_size=2000, ax=ax,
)
nx.draw_networkx_labels(graph, POSITIONS, font_size=9, ax=ax)
nx.draw_networkx_edges(
    graph, POSITIONS, edge_color="#4682b4",
    width=2, ax=ax,
)

if st.session_state.failed_links:
    failed_graph = nx.Graph()
    failed_graph.add_edges_from(st.session_state.failed_links)
    nx.draw_networkx_edges(
        failed_graph, POSITIONS,
        edge_color="red", style="dashed",
        width=2.5, ax=ax,
    )

ax.set_title("AgriMesh: active and failed wireless links")
ax.axis("off")
st.pyplot(fig)
plt.close(fig)

st.caption(
    "Green = connected sensor; red = disconnected sensor; "
    "yellow = gateway; dashed red = failed link."
)

st.divider()
st.markdown("### 3. Agricultural data transmission")

sensor = st.selectbox(
    "Choose source sensor",
    ["Sensor_A", "Sensor_B", "Sensor_C", "Sensor_D"],
)

moisture = st.slider("Soil moisture (%)", 0, 100, 28)
temperature = st.slider("Temperature (°C)", 10, 50, 32)

if st.button("Transmit sensor data", type="primary"):
    payload, route, delivered, hops, message = transmit(
        graph, sensor, moisture, temperature
    )

    if delivered:
        st.success(message)
        st.write("**Selected route:**")
        st.code(" → ".join(route))
        st.metric("Hop count", hops)
        st.markdown("**Payload received at gateway**")
        st.json(payload)
        if moisture < 30:
            st.warning(
                "Illustrative alert: soil moisture is below 30%. "
                "This is a demo threshold, not an agronomic recommendation."
            )
    else:
        st.error(message)
        st.write("**Payload generated but not delivered:**")
        st.json(payload)

st.divider()
st.markdown("### 4. Network performance")

history = pd.DataFrame(st.session_state.history)

sent = len(history)
delivered_count = (
    int((history["Status"] == "Delivered").sum()) if sent else 0
)
failed_count = sent - delivered_count
pdr = 100 * delivered_count / sent if sent else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Packets attempted", sent)
m2.metric("Packets delivered", delivered_count)
m3.metric("Packets failed", failed_count)
m4.metric("Delivery ratio", f"{pdr:.1f}%")

if sent:
    st.dataframe(history, use_container_width=True, hide_index=True)
else:
    st.info("Transmit a packet to start collecting experiment results.")

st.caption(
    "Delivery ratio = delivered packets / attempted packets × 100. "
    "These are results from your interactive simulation, not a real radio network."
)

col1, col2 = st.columns(2)

with col1:
    if st.button("Reset experiment history"):
        st.session_state.history = []
        st.rerun()

with col2:
    if st.button("Restore all links"):
        st.session_state.failed_links = set()
        st.rerun()
