"""
Graph serializer - Pre-build and save transit graphs.
CORRECTED VERSION: Queries API for available directions first.
"""

import pickle
import requests
from graph import Graph


def get_available_directions(route_id):
    """
    Query the API to get valid direction IDs for a route.

    Args:
        route_id: The route ID (e.g., 901, 63, 902, 921)

    Returns:
        List of (direction_id, direction_name) tuples
    """
    try:
        url = f"https://svc.metrotransit.org/nextrip/directions/{route_id}"
        response = requests.get(url, headers={'Accept': 'application/json'}, timeout=10)

        if response.status_code == 200:
            directions = response.json()
            return [(d['direction_id'], d['direction_name']) for d in directions]
    except Exception as e:
        print(f"   ⚠ Could not get directions for route {route_id}: {e}")

    return []


def create_and_serialize_graph():
    """Create graphs for multiple routes and serialize them."""
    print("=" * 80)
    print("TRANSIT GRAPH BUILDER (API-Aware Version)")
    print("=" * 80)
    print("\nThis will query the API for available routes and directions,")
    print("then build a complete transit graph.")
    print("This may take several minutes.\n")

    graph_list = []

    # Routes to include
    routes = [
        (901, "Blue Line"),
        (902, "Green Line"),
        (921, "A Line"),
        (63, "Route 63"),
    ]

    total_created = 0

    for route_id, route_name in routes:
        print(f"\n📍 Processing {route_name} (Route {route_id})...")

        # Query API for available directions
        directions = get_available_directions(route_id)

        if not directions:
            print(f"   ⚠ No directions found for {route_name}")
            continue

        print(f"   Found {len(directions)} direction(s):")
        for dir_id, dir_name in directions:
            print(f"     - Direction {dir_id}: {dir_name}")

        # Create graph for each direction
        for dir_id, dir_name in directions:
            try:
                graph = Graph(route_id, dir_id)
                if len(graph.stops) > 0:
                    graph_list.append(graph)
                    total_created += 1
                    print(f"   ✓ Created {route_name} - {dir_name} with {len(graph.stops)} stops")
                else:
                    print(f"   ⊗ No stops returned for {route_name} - {dir_name}")
            except Exception as e:
                print(f"   ✗ Error creating {route_name} - {dir_name}: {e}")
                continue

    if not graph_list:
        print("\n" + "=" * 80)
        print(" No graphs were created successfully.")
        print("=" * 80)
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify Metro Transit API is accessible:")
        print("   https://svc.metrotransit.org/swagger/index.html")
        print("3. The API may be temporarily down")
        return

    # Combine into multi-route graph
    print("\n" + "=" * 80)
    print(" Combining graphs and creating transfer connections...")
    print("=" * 80)

    combined_graph = Graph(graph_list=graph_list)

    print(f"\n✓ Combined graph created:")
    print(f"   Total stops: {len(combined_graph.stops)}")
    print(f"   Total connections: {sum(len(edges) for edges in combined_graph.edges.values())}")
    print(f"   Route directions: {total_created}")

    # Serialize to file
    filename = 'graph_data.pkl'
    print(f"\n Saving graph to {filename}...")

    try:
        with open(filename, 'wb') as f:
            pickle.dump(combined_graph, f)
        print(f"✓ Graph successfully saved to {filename}")

    except Exception as e:
        print(f" Error saving graph: {e}")
        return

    print("\n" + "=" * 80)
    print(" GRAPH SERIALIZATION COMPLETE!")
    print("=" * 80)
    print(f"\nYou can now run quickroute.py to find transit routes.")
    print(f"\nGraph statistics:")
    print(f"  - {len(combined_graph.stops)} transit stops")
    print(f"  - {total_created} route directions")
    print(f"  - {sum(len(edges) for edges in combined_graph.edges.values())} connections")


def create_small_test_graph():
    """Create a smaller test graph for development/testing."""
    print("Creating small test graph...")
    print("\nQuerying API for a working route...")

    # Try Route 63 first
    test_routes = [(63, "Route 63"), (902, "Green Line")]

    graph = None
    for route_id, route_name in test_routes:
        print(f"\n  Trying {route_name} (Route {route_id})...")

        directions = get_available_directions(route_id)
        if not directions:
            print(f"    No directions found")
            continue

        # Use first available direction
        dir_id, dir_name = directions[0]
        print(f"    Using Direction {dir_id}: {dir_name}")

        try:
            test_graph = Graph(route_id, dir_id)
            if len(test_graph.stops) > 0:
                graph = test_graph
                print(f"    ✓ Created with {len(graph.stops)} stops")
                break
        except Exception as e:
            print(f"    ✗ Failed: {e}")
            continue

    if not graph:
        print("\n Could not create test graph")
        return

    filename = 'test_graph.pkl'
    try:
        with open(filename, 'wb') as f:
            pickle.dump(graph, f)

        print(f"\n✓ Test graph saved to {filename}")
        print(f"   Stops: {len(graph.stops)}")

    except Exception as e:
        print(f" Error creating test graph: {e}")


def main():
    """Main entry point."""
    print("\nSelect option:")
    print("1. Create full multi-route graph (recommended)")
    print("2. Create small test graph (single route, for testing)")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == '1':
        create_and_serialize_graph()
    elif choice == '2':
        create_small_test_graph()
    else:
        print("Invalid choice. Exiting.")

##May change graphs for new algorithms added, or gui


if __name__ == "__main__":
    main()