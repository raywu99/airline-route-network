import pandas as pd
import networkx as nx

def load_data():
    """
    Load airports and routes data from local files.
    
    Returns:
        airports_df (pd.DataFrame): data on each airport
        routes_df   (pd.DataFrame): data on each flight route
    """
    # Read airports.dat (no header row), assign column names
    airports_df = pd.read_csv(
        "airports.dat", header=None,
        names=[
            "Airport_ID", "Name", "City", "Country",
            "IATA", "ICAO", "Latitude", "Longitude",
            "Altitude", "Timezone", "DST", "Tz",
            "Type", "Source"
        ]
    )
    
    # Read routes.dat (no header), assign column names
    routes_df = pd.read_csv(
        "routes.dat", header=None,
        names=[
            "Airline", "Airline_ID",
            "Source_Airport", "Source_Airport_ID",
            "Destination_Airport", "Destination_Airport_ID",
            "Codeshare", "Stops", "Equipment"
        ]
    )
    
    return airports_df, routes_df

def build_graph(airports_df, routes_df):
    """
    Build an undirected graph where:
      - Nodes are airports (keyed by IATA code)
      - Edges are direct flights (Stops == 0)
    
    Args:
        airports_df (pd.DataFrame): airport details
        routes_df   (pd.DataFrame): route connections
    
    Returns:
        G (nx.Graph): graph of airport network
    """
    G = nx.Graph()

    # Add a node for each airport with valid IATA code
    for _, row in airports_df.iterrows():
        code = row["IATA"]
        if code and code != r"\N":
            G.add_node(
                code,
                name=row["Name"],
                city=row["City"],
                country=row["Country"],
                lat=row["Latitude"],
                lon=row["Longitude"]
            )

    # Add an edge for each direct route (no intermediate stops)
    for _, row in routes_df.iterrows():
        src = row["Source_Airport"]
        dst = row["Destination_Airport"]
        if src in G and dst in G and row["Stops"] == 0:
            G.add_edge(src, dst)

    return G

def find_shortest_path(G, src, dst):
    """
    Print the shortest path (fewest flights) from src to dst.
    """
    try:
        path = nx.shortest_path(G, source=src, target=dst)
        print(" -> ".join(path))
    except nx.NetworkXNoPath:
        # No route exists in the data
        print(f"No path found from {src} to {dst}")

def show_top_hubs(G, top_n=5):
    """
    List the top_n airports by number of direct connections.
    """
    # G.degree gives (node, degree), sort by degree descending
    hubs = sorted(G.degree, key=lambda x: x[1], reverse=True)[:top_n]
    for code, count in hubs:
        print(f"{code}: {count} connections")

def show_neighbors(G, code):
    """
    Print all airports directly connected to the given code.
    """
    if code in G:
        neighbors = sorted(G.neighbors(code))
        # Show neighbors as comma-separated list
        print(", ".join(neighbors))
    else:
        print(f"{code} not found in network")

def show_stats(G, code):
    """
    Display details and connection count for a single airport.
    """
    if code in G:
        data = G.nodes[code]         # airport metadata
        count = G.degree(code)       # number of direct edges
        print(f"Airport: {data['name']} ({code})")
        print(f"Location: {data['city']}, {data['country']}")
        print(f"Coordinates: ({data['lat']:.4f}, {data['lon']:.4f})")
        print(f"Direct connections: {count}")
    else:
        print(f"{code} not found in network")

def interactive_mode(G):
    """
    Run a looped menu so the user can enter commands
    without restarting the script each time.
    """
    print("Welcome to the Flight Network Explorer!")
    menu = """
Choose an action:
 1) Find shortest path
 2) Show top hubs
 3) List neighbors
 4) Airport stats
 5) Exit
"""

    while True:
        print(menu)
        choice = input("Enter number: ").strip()

        if choice == "1":
            # User enters departure and arrival codes
            src = input(" Departure airport IATA code: ").upper().strip()
            dst = input(" Arrival   airport IATA code: ").upper().strip()
            print()  # blank line
            print(f"This is the shortest path from {src} to {dst}:")
            find_shortest_path(G, src, dst)
            print()  # blank line

        elif choice == "2":
            # User requests top hubs; default to 5 if no number given
            n = input(" How many top hubs? [default 5]: ").strip()
            n = int(n) if n.isdigit() else 5
            print()  # blank line
            print(f"Top {n} airports by number of direct connections:")
            show_top_hubs(G, n)
            print()  # blank line

        elif choice == "3":
            # User looks up neighbors for a given airport
            code = input(" Airport IATA code: ").upper().strip()
            print()  # blank line
            print(f"Direct connections from {code}:")
            show_neighbors(G, code)
            print()  # blank line

        elif choice == "4":
            # User requests detailed stats for one airport
            code = input(" Airport IATA code: ").upper().strip()
            print()  # blank line
            print(f"Details for airport {code}:")
            show_stats(G, code)
            print()  # blank line

        elif choice == "5":
            # Exit the interactive loop
            print("Goodbye!")
            break

        else:
            # Handle invalid menu choice
            print("Invalid choice, try again.\n")

if __name__ == "__main__":
    # Load data files and build the network graph
    airports_df, routes_df = load_data()
    graph = build_graph(airports_df, routes_df)
    # Start the interactive menu session
    interactive_mode(graph)