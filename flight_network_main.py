import pandas as pd
import networkx as nx

def load_data():
    """
    Load airport and route data from local .dat files into pandas DataFrames.
    
    Returns:
        airports_df (pd.DataFrame): Contains details for each airport.
        routes_df   (pd.DataFrame): Contains flight route information.
    """
    # Load airport data and assign column names
    airports_df = pd.read_csv(
        "airports.dat", header=None,
        names=[
            "Airport_ID", "Name", "City", "Country",
            "IATA", "ICAO", "Latitude", "Longitude",
            "Altitude", "Timezone", "DST", "Tz",
            "Type", "Source"
        ]
    )
    
    # Load route data and assign column names
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
    Build an undirected graph from airport and route data.
    
    Each node is an airport (IATA code). Each edge represents a direct route
    (with 0 stops) between two valid airports.
    
    Args:
        airports_df (pd.DataFrame): Airport metadata.
        routes_df (pd.DataFrame): Route connections between airports.
    
    Returns:
        G (nx.Graph): NetworkX graph representing the airline network.
    """
    G = nx.Graph()

    # Add airport nodes with valid IATA codes
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

    # Add edges only for direct flights (Stops == 0)
    for _, row in routes_df.iterrows():
        src = row["Source_Airport"]
        dst = row["Destination_Airport"]
        if src in G and dst in G and row["Stops"] == 0:
            G.add_edge(src, dst)

    return G

def validate_iata(code, G):
    """
    Validate whether a given IATA code exists in the graph.
    
    Args:
        code (str): IATA airport code.
        G (nx.Graph): The airport graph.
    
    Returns:
        bool: True if valid, False otherwise. Also prints an error message if invalid.
    """
    if code not in G:
        print(f"Error: '{code}' is not a valid IATA code.\n")
        return False
    return True

def find_shortest_path(G, src, dst):
    """
    Print the shortest path (fewest number of flights) between two airports.
    
    Args:
        G (nx.Graph): The airport graph.
        src (str): Departure airport IATA code.
        dst (str): Arrival airport IATA code.
    """
    try:
        path = nx.shortest_path(G, source=src, target=dst)
        print(" -> ".join(path))
    except nx.NetworkXNoPath:
        print(f"No path found from {src} to {dst}")

def show_top_hubs(G, top_n=5):
    """
    Show the top N airports with the most direct connections.
    
    Args:
        G (nx.Graph): The airport graph.
        top_n (int): Number of top hubs to display.
    """
    hubs = sorted(G.degree, key=lambda x: x[1], reverse=True)[:top_n]
    for code, count in hubs:
        print(f"{code}: {count} connections")

def show_neighbors(G, code):
    """
    Print a list of airports directly connected to the given airport.
    
    Args:
        G (nx.Graph): The airport graph.
        code (str): Airport IATA code.
    """
    neighbors = sorted(G.neighbors(code))
    print(", ".join(neighbors))

def show_stats(G, code):
    """
    Display airport name, location, coordinates, and number of connections.
    
    Args:
        G (nx.Graph): The airport graph.
        code (str): Airport IATA code.
    """
    data = G.nodes[code]
    count = G.degree(code)
    print(f"Airport: {data['name']} ({code})")
    print(f"Location: {data['city']}, {data['country']}")
    print(f"Coordinates: ({data['lat']:.4f}, {data['lon']:.4f})")
    print(f"Direct connections: {count}")

def interactive_mode(G):
    """
    Run the interactive command-line menu for user input and exploration.
    
    The menu allows the user to:
      1. Find the shortest path between two airports.
      2. View the top hub airports.
      3. List direct connections from an airport.
      4. View airport information.
      5. Exit the program.
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
            # Prompt for and validate departure IATA code
            while True:
                src = input(" Departure airport IATA code: ").upper().strip()
                if validate_iata(src, G):
                    break

            # Prompt for and validate arrival IATA code
            while True:
                dst = input(" Arrival airport IATA code: ").upper().strip()
                if validate_iata(dst, G):
                    break

            print()
            print(f"This is the shortest path from {src} to {dst}:")
            find_shortest_path(G, src, dst)
            print()

        elif choice == "2":
            # Prompt for valid integer input for number of top hubs
            while True:
                n = input(" How many top hubs? (must be a number): ").strip()
                if n.isdigit():
                    n = int(n)
                    break
                else:
                    print("Invalid input. Please enter a valid number.\n")

            print()
            print(f"Top {n} airports by number of direct connections:")
            show_top_hubs(G, n)
            print()

        elif choice == "3":
            # Prompt for and validate airport code before showing neighbors
            code = input(" Airport IATA code: ").upper().strip()
            if not validate_iata(code, G):
                continue

            print()
            print(f"Direct connections from {code}:")
            show_neighbors(G, code)
            print()

        elif choice == "4":
            # Prompt for and validate airport code before showing stats
            code = input(" Airport IATA code: ").upper().strip()
            if not validate_iata(code, G):
                continue

            print()
            print(f"Details for airport {code}:")
            show_stats(G, code)
            print()

        elif choice == "5":
            # Exit the program
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.\n")

if __name__ == "__main__":
    # Load data files and build the airport network graph
    airports_df, routes_df = load_data()
    graph = build_graph(airports_df, routes_df)
    # Launch the interactive interface
    interactive_mode(graph)
