"""
Improved pathfinding with transfer penalties.

This adds a time penalty for transfers to make routes more realistic.
"""

import pickle


def add_transfer_penalty(graph, penalty_minutes=5.0):
    """
    Add a time penalty to all transfer edges.

    Args:
        graph: The loaded graph
        penalty_minutes: Minutes to add for each transfer (default 5)

    Returns:
        Modified graph
    """
    print(f"Adding {penalty_minutes} minute penalty to all transfers...")

    count = 0
    for stop_id, edge_list in graph.edges.items():
        for edge in edge_list:
            if edge.route_id == -1:  # Transfer edge
                # Modify the transit time
                edge.transit_time = penalty_minutes
                count += 1

    print(f"✓ Modified {count} transfer edges")
    return graph


def main():
    """Load graph, add transfer penalties, and save."""

    print("=" * 80)
    print("GRAPH TRANSFER PENALTY TOOL")
    print("=" * 80)

    # Load original graph
    print("\nLoading graph_data.pkl...")
    try:
        with open('graph_data.pkl', 'rb') as f:
            graph = pickle.load(f)
        print(f"✓ Loaded: {len(graph.stops)} stops, {sum(len(e) for e in graph.edges.values())} edges")
    except Exception as e:
        print(f"✗ Error: {e}")
        return

    # Add transfer penalty
    print("\nModifying transfer edges...")
    graph = add_transfer_penalty(graph, penalty_minutes=5.0)

    # Save modified graph
    print("\nSaving modified graph...")
    try:
        with open('graph_data_with_penalties.pkl', 'wb') as f:
            pickle.dump(graph, f)
        print("✓ Saved to: graph_data_with_penalties.pkl")

        # Also update the main graph
        with open('graph_data.pkl', 'wb') as f:
            pickle.dump(graph, f)
        print("✓ Updated: graph_data.pkl")

    except Exception as e:
        print(f"✗ Error saving: {e}")
        return

    print("\n" + "=" * 80)
    print(" COMPLETE!")
    print("=" * 80)
    print("\nTransfers now have a 5-minute penalty.")
    print("This makes routes prefer staying on the same line.")
    print("\nYou can now run quickroute.py again!")


if __name__ == "__main__":
    main()