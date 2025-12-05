"""
Test various routes to demonstrate the system working correctly.
"""

import pickle
from graph import Graph


def test_routes():
    """Test several interesting routes."""
    
    print("=" * 80)
    print("QUICKROUTE - ROUTE TESTING")
    print("=" * 80)
    
    # Load graph
    print("\nLoading graph...")
    try:
        with open('graph_data.pkl', 'rb') as f:
            graph = pickle.load(f)
        print(f"✓ Graph loaded: {len(graph.stops)} stops, {sum(len(e) for e in graph.edges.values())} connections")
    except Exception as e:
        print(f"✗ Error loading graph: {e}")
        return
    
    # Define test routes based on the diagnostic output
    test_cases = [
        {
            'name': 'Mall of America to Downtown Minneapolis',
            'start': 'MAAM',  # Mall of America Station
            'end': 'WARE',    # Warehouse District/Hennepin Ave Station
            'description': 'Blue Line route through city'
        },
        {
            'name': 'Terminal 1 to Union Depot',
            'start': 'LIND',  # Terminal 1 Station
            'end': 'UNDP',    # Union Depot Station
            'description': 'Airport to St Paul - requires transfer'
        },
        {
            'name': 'Grand Ave to Sun Ray',
            'start': 'DAGR',  # Grand Ave and Dale St
            'end': 'SURA',    # Sun Ray Transit Center
            'description': 'Route 63 eastbound'
        },
        {
            'name': 'Snelling & Grand to Rosedale',
            'start': 'GRSN',  # Snelling & Grand Station
            'end': 'ROSE',    # Rosedale Transit Center
            'description': 'A Line northbound'
        },
        {
            'name': 'West Bank to Central Station',
            'start': 'WEBK',  # West Bank Station
            'end': 'CNST',    # Central Station
            'description': 'Green Line through downtown'
        }
    ]
    
    # Helper to find stop by code
    def find_stop(code):
        for stop in graph.stops:
            if str(stop.get_stop_id()) == code:
                return stop
        return None
    
    # Test each route
    for i, test in enumerate(test_cases, 1):
        print("\n" + "=" * 80)
        print(f"TEST {i}: {test['name']}")
        print(f"Description: {test['description']}")
        print("=" * 80)
        
        start_stop = find_stop(test['start'])
        end_stop = find_stop(test['end'])
        
        if not start_stop or not end_stop:
            print(f"⚠ Could not find stops: {test['start']} -> {test['end']}")
            continue
        
        print(f"\nFrom: {start_stop.get_name()} (ID: {start_stop.get_stop_id()})")
        print(f"To:   {end_stop.get_name()} (ID: {end_stop.get_stop_id()})")
        
        # Try Dijkstra
        try:
            print(f"\nRunning Dijkstra's algorithm...")
            path, time, metrics = graph.dijkstra(start_stop.get_stop_id(), end_stop.get_stop_id())
            
            if path:
                print(f"✓ Route found!")
                print(f"  - Stops: {len(path)}")
                print(f"  - Transit time: {time:.1f} minutes")
                print(f"  - Execution time: {metrics['execution_time']:.6f} seconds")
                print(f"  - Nodes explored: {metrics['nodes_explored']}")
                
                # Show path
                print(f"\n  Route:")
                for j, stop in enumerate(path):
                    routes = ", ".join(map(str, stop.get_route_ids()))
                    if j == 0:
                        print(f"    START: {stop.get_name()} (Routes: {routes})")
                    elif j == len(path) - 1:
                        print(f"    END:   {stop.get_name()} (Routes: {routes})")
                    else:
                        # Check for transfers
                        if j > 0:
                            prev_routes = set(path[j-1].get_route_ids())
                            curr_routes = set(stop.get_route_ids())
                            if not prev_routes & curr_routes:  # No common routes = transfer
                                print(f"    ➜ TRANSFER")
                        print(f"      {j+1}. {stop.get_name()} (Routes: {routes})")
            else:
                print(f"✗ No route found")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✓ TESTING COMPLETE")
    print("=" * 80)
    print("\nAll routes tested. You can now use quickroute.py interactively!")


if __name__ == "__main__":
    test_routes()
