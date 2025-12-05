"""
Fix the graph by removing unrealistic transfer edges.

The issue: When graphs were combined, transfer edges were created between
ALL nearby stops, even ones on the same route. This creates shortcuts.

Solution: Only keep transfer edges between stops on DIFFERENT routes,
and add a realistic 5-minute penalty for transfers.
"""

import pickle
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def estimate_time(distance_km, route_id):
    """Estimate time based on distance and route type."""
    if route_id in [901, 902]:  # Light rail
        speed = 40
    elif route_id == 921:  # BRT
        speed = 24
    elif route_id == -1:  # Transfer
        return 5.0  # Fixed 5-minute penalty for transfers
    else:  # Bus
        speed = 19

    time_min = (distance_km / speed) * 60 + 0.5
    return max(0.5, round(time_min, 1))


print("=" * 80)
print("GRAPH REPAIR TOOL")
print("=" * 80)

# Load graph
print("\nLoading graph...")
with open('graph_data.pkl', 'rb') as f:
    graph = pickle.load(f)

print(f"Loaded: {len(graph.stops)} stops")

# Analyze transfers
print("\nAnalyzing transfer edges...")
transfer_edges = []
for stop_id, edges in graph.edges.items():
    for edge in edges:
        if edge.route_id == -1:
            transfer_edges.append((stop_id, edge))

print(f"Found {len(transfer_edges)} transfer edges")

# Remove bad transfers (same route or very close)
print("\nRemoving problematic transfers...")
removed = 0

for stop_id, edge in transfer_edges:
    start_routes = set(edge.start_stop.get_route_ids())
    end_routes = set(edge.end_stop.get_route_ids())

    # Check if stops share any routes (shouldn't transfer within same route!)
    if start_routes & end_routes:
        # Remove this edge
        try:
            graph.edges[stop_id].remove(edge)
            removed += 1
        except (KeyError, ValueError):
            pass

print(f"Removed {removed} bad transfer edges")

# Update remaining transfer edges with 5-minute penalty
print("\nAdding 5-minute penalty to valid transfers...")
transfer_count = 0

for edges in graph.edges.values():
    for edge in edges:
        if edge.route_id == -1:
            edge.transit_time = 5.0
            transfer_count += 1

print(f"Updated {transfer_count} valid transfer edges")

# Calculate transit times for regular edges
print("\nCalculating transit times for route edges...")
updated = 0

for edges in graph.edges.values():
    for edge in edges:
        if edge.route_id != -1:  # Not a transfer
            lat1 = edge.start_stop.get_latitude()
            lon1 = edge.start_stop.get_longitude()
            lat2 = edge.end_stop.get_latitude()
            lon2 = edge.end_stop.get_longitude()

            dist_km = haversine_distance(lat1, lon1, lat2, lon2)
            time_min = estimate_time(dist_km, edge.route_id)

            edge.transit_time = time_min
            updated += 1

print(f"Updated {updated} regular edges")

# Show statistics
print("\n" + "=" * 80)
print("GRAPH STATISTICS")
print("=" * 80)

route_edges = {}
for edges in graph.edges.values():
    for edge in edges:
        route = edge.route_id
        if route not in route_edges:
            route_edges[route] = 0
        route_edges[route] += 1

print("\nEdges by route:")
for route_id in sorted(route_edges.keys()):
    route_name = {
        901: "Blue Line",
        902: "Green Line",
        921: "A Line",
        63: "Route 63",
        -1: "Transfers"
    }.get(route_id, f"Route {route_id}")
    print(f"  {route_name:20} = {route_edges[route_id]:4} edges")

# Show sample times
print("\nSample segment times:")
samples_shown = 0
for edges in graph.edges.values():
    if samples_shown >= 8:
        break
    for edge in edges[:1]:
        if edge.route_id != -1:  # Show regular routes
            print(f"  Route {edge.route_id}: {edge.start_stop.get_name()[:30]:30} → "
                  f"{edge.end_stop.get_name()[:30]:30} = {edge.transit_time:.1f} min")
            samples_shown += 1
            if samples_shown >= 8:
                break

# Save
print("\n" + "=" * 80)
print("Saving repaired graph...")
with open('graph_data.pkl', 'wb') as f:
    pickle.dump(graph, f)

print("✓ Graph saved!")
print("=" * 80)
print("\n✅ REPAIR COMPLETE")
print("\nChanges made:")
print(f"  - Removed {removed} invalid transfer edges (between stops on same route)")
print(f"  - Added 5-minute penalty to {transfer_count} valid transfers")
print(f"  - Calculated realistic times for {updated} route segments")
print("\nNow routes will follow the actual transit lines!")
print("Run: python3 quickroute.py")