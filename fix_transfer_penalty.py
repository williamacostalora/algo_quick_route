"""
Fix transfer edges to only be used when actually necessary.

The problem: Transfers have low penalties, so the algorithm uses them as shortcuts
even when a direct route exists.

Solution: Make transfers expensive (10-15 minutes), so they're only used when
there's no direct route on a single line.
"""

import pickle
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def estimate_time(distance_km, route_id):
    """Estimate time based on distance and route type."""
    if route_id in [901, 902]:  # Light rail
        speed = 40  # km/h
    elif route_id == 921:  # BRT
        speed = 24
    elif route_id == -1:  # Transfer - will be handled separately
        return 15.0  # High penalty
    else:  # Bus
        speed = 19
    
    time_min = (distance_km / speed) * 60 + 0.5  # Add 30 sec dwell time
    return max(1.0, round(time_min, 1))


print("=" * 80)
print("TRANSFER PENALTY ADJUSTER")
print("=" * 80)
print("\nThis will make transfers expensive so they're only used when necessary.")

# Load graph
print("\nLoading graph...")
with open('graph_data.pkl', 'rb') as f:
    graph = pickle.load(f)

print(f"Loaded: {len(graph.stops)} stops")

# First pass: Calculate realistic times for all route edges
print("\nCalculating transit times for route segments...")
route_edges_updated = 0

for edges in graph.edges.values():
    for edge in edges:
        if edge.route_id != -1:  # Regular route edge
            lat1 = edge.start_stop.get_latitude()
            lon1 = edge.start_stop.get_longitude()
            lat2 = edge.end_stop.get_latitude()
            lon2 = edge.end_stop.get_longitude()
            
            dist_km = haversine_distance(lat1, lon1, lat2, lon2)
            time_min = estimate_time(dist_km, edge.route_id)
            
            edge.transit_time = time_min
            route_edges_updated += 1

print(f"✓ Updated {route_edges_updated} route edges")

# Second pass: Set HIGH penalty for transfers
TRANSFER_PENALTY = 15.0  # 15 minutes - makes transfers very unattractive

print(f"\nSetting {TRANSFER_PENALTY}-minute penalty for transfers...")
transfer_count = 0

for edges in graph.edges.values():
    for edge in edges:
        if edge.route_id == -1:  # Transfer edge
            edge.transit_time = TRANSFER_PENALTY
            transfer_count += 1

print(f"✓ Updated {transfer_count} transfer edges")

# Show what we have
print("\n" + "=" * 80)
print("EDGE SUMMARY")
print("=" * 80)

route_stats = {}
for edges in graph.edges.values():
    for edge in edges:
        route = edge.route_id
        if route not in route_stats:
            route_stats[route] = {'count': 0, 'total_time': 0}
        route_stats[route]['count'] += 1
        route_stats[route]['total_time'] += edge.transit_time

print("\nEdges by route:")
for route_id in sorted(route_stats.keys()):
    count = route_stats[route_id]['count']
    avg_time = route_stats[route_id]['total_time'] / count if count > 0 else 0
    
    route_name = {
        901: "Blue Line (901)",
        902: "Green Line (902)", 
        921: "A Line (921)",
        63: "Route 63",
        -1: "Transfers"
    }.get(route_id, f"Route {route_id}")
    
    print(f"  {route_name:20} = {count:4} edges, avg {avg_time:.1f} min/segment")

# Show sample times
print("\nSample segment times:")
samples = []

for edges in graph.edges.values():
    for edge in edges[:1]:
        if edge.route_id == 901 and len(samples) < 5:  # Show Blue Line examples
            samples.append(edge)
        elif edge.route_id == -1 and len([s for s in samples if s.route_id == -1]) < 2:
            samples.append(edge)

for edge in samples:
    route_type = "TRANSFER" if edge.route_id == -1 else f"Route {edge.route_id}"
    print(f"  {route_type:12} {edge.start_stop.get_name()[:30]:30} → "
          f"{edge.end_stop.get_name()[:30]:30} = {edge.transit_time:.1f} min")

# Save
print("\n" + "=" * 80)
print("Saving updated graph...")
with open('graph_data.pkl', 'wb') as f:
    pickle.dump(graph, f)

print("✓ Graph saved!")
print("=" * 80)

print(f"""
✅ TRANSFER PENALTIES APPLIED

Key changes:
  - Route edges: Realistic times based on distance
  - Transfer edges: {TRANSFER_PENALTY} minute penalty
  
This means:
  ✓ Direct routes (e.g., Blue Line Mall → Target Field) will be preferred
  ✓ Transfers only used when no direct route exists
  ✓ More realistic routing behavior

Test it:
  python3 quickroute.py
  Try: Mall of America (#30) → Target Field (#44)
  Should now show ~20 stops on Blue Line with NO transfers!
""")
