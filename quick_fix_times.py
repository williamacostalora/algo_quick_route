"""
Simple transit time estimator based on geographic distance.

This calculates realistic times by:
1. Measuring actual distance between stops
2. Using appropriate speeds for each transit type
3. Adding stop dwell time

This is how Google Maps and other transit apps estimate times when
real-time schedule data isn't available.
"""

import pickle
import math


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points."""
    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def estimate_time(distance_km, route_type):
    """
    Estimate transit time like Google Maps does.

    Uses realistic average speeds including stops:
    - Light Rail: ~25 mph (40 km/h) between stops
    - BRT: ~15 mph (24 km/h) between stops
    - Bus: ~12 mph (19 km/h) between stops
    - Walking: ~3 mph (5 km/h)
    """
    if route_type in [901, 902]:  # Light Rail
        speed_kmh = 40
    elif route_type == 921:  # BRT
        speed_kmh = 24
    elif route_type == -1:  # Transfer/walk
        speed_kmh = 5
    else:  # Regular bus
        speed_kmh = 19

    time_hours = distance_km / speed_kmh
    time_minutes = time_hours * 60

    # Add dwell time (30 sec for stops, 0 for transfers)
    if route_type != -1:
        time_minutes += 0.5

    return max(0.5, round(time_minutes, 1))


# Load graph
print("Loading graph...")
with open('graph_data.pkl', 'rb') as f:
    graph = pickle.load(f)

print(f"Graph has {len(graph.stops)} stops")

# Update transit times
print("Calculating transit times...")
updated = 0

for stop_id, edges in graph.edges.items():
    for edge in edges:
        # Get coordinates
        lat1 = edge.start_stop.get_latitude()
        lon1 = edge.start_stop.get_longitude()
        lat2 = edge.end_stop.get_latitude()
        lon2 = edge.end_stop.get_longitude()

        # Calculate distance
        dist_km = haversine_distance(lat1, lon1, lat2, lon2)

        # Estimate time
        time_min = estimate_time(dist_km, edge.route_id)

        # Update edge
        edge.transit_time = time_min
        updated += 1

print(f"Updated {updated} edges")

# Show sample
print("\nSample transit times:")
for i, (stop_id, edges) in enumerate(list(graph.edges.items())[:5]):
    if edges:
        e = edges[0]
        print(f"  {e.start_stop.get_name()[:35]:35} → {e.end_stop.get_name()[:35]:35} = {e.transit_time:.1f} min")

# Save
print("\nSaving...")
with open('graph_data.pkl', 'wb') as f:
    pickle.dump(graph, f)

print("✓ Done! Transit times added based on real distances.")
print("Now run: python3 quickroute.py")