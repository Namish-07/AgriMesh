
import networkx as nx

# AgriMesh: Rural agricultural sensor network
network = nx.Graph()

# Sensor nodes and the central gateway
nodes = [
    "Gateway",
    "Sensor_A",
    "Sensor_B",
    "Sensor_C",
    "Sensor_D",
]

network.add_nodes_from(nodes)

# Wireless communication links between nearby devices
links = [
    ("Gateway", "Sensor_A"),
    ("Gateway", "Sensor_B"),
    ("Sensor_A", "Sensor_C"),
    ("Sensor_B", "Sensor_C"),
    ("Sensor_C", "Sensor_D"),
    ("Sensor_B", "Sensor_D"),
]

network.add_edges_from(links)


def send_data(source, destination):
    """Find a route for agricultural sensor data."""
    try:
        route = nx.shortest_path(
            network,
            source=source,
            target=destination,
        )
        print(f"Route: {' -> '.join(route)}")
        print("Status: Data delivered successfully")
        return True

    except nx.NetworkXNoPath:
        print(f"Route: {source} -> {destination}")
        print("Status: Delivery failed; no route available")
        return False


print("=== AGRIMESH NETWORK SIMULATION ===")

print("\n1. Normal network operation")
send_data("Sensor_D", "Gateway")

print("\n2. Simulating a wireless link failure")
network.remove_edge("Sensor_B", "Sensor_D")
send_data("Sensor_D", "Gateway")

print("\n3. Simulating another link failure")
network.remove_edge("Sensor_C", "Sensor_D")
send_data("Sensor_D", "Gateway")
