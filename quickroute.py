"""
QuickRoute - Main application for transit route finding.
"""

import pickle
from typing import Dict, List
from graph import Graph
from stop import Stop


class QuickRoute:
    """Main application for finding optimal transit routes."""
    
    def __init__(self):
        """Initialize QuickRoute application."""
        self.graph = None
        self.stop_name_to_id: Dict[str, int] = {}
        self.stop_id_to_name: Dict[int, str] = {}
    
    def load_graph(self, filename: str = 'graph_data.pkl'):
        """
        Load the serialized graph.
        
        Args:
            filename: Path to the serialized graph file
        """
        print("Loading transit graph...")
        try:
            with open(filename, 'rb') as f:
                self.graph = pickle.load(f)
            print("Graph loaded successfully!")
            
            # Create name-to-id mappings
            for stop in self.graph.stops:
                self.stop_name_to_id[stop.get_name()] = stop.get_stop_id()
                self.stop_id_to_name[stop.get_stop_id()] = stop.get_name()
                
        except FileNotFoundError:
            print(f"Error: Graph file '{filename}' not found.")
            print("Please run graph_serializer.py first to create the graph.")
            raise
    
    def display_available_stops(self) -> List[Stop]:
        """
        Display available stops from the loaded graph.
        
        Returns:
            List of available stops
        """
        # Get all unique stops from the graph
        available_stops = self.graph.stops
        
        # Sort alphabetically for easier browsing
        available_stops_sorted = sorted(available_stops, key=lambda s: s.get_name())
        
        print("\n" + "=" * 60)
        print(f"AVAILABLE STOPS ({len(available_stops_sorted)} total)")
        print("=" * 60)
        
        # Display in columns for better readability
        for i, stop in enumerate(available_stops_sorted, 1):
            print(f"{i:3}. {stop.get_name()}")
        
        print("=" * 60)
        print("TIP: You can enter the number or type part of the stop name")
        print("=" * 60)
        
        return available_stops_sorted
    
    def get_user_input(self, available_stops: List[Stop]) -> tuple:
        """
        Get departure and destination from user.
        
        Args:
            available_stops: List of available stops
            
        Returns:
            Tuple of (departure_id, destination_id)
        """
        print("\n" + "=" * 60)
        print("Enter Departure Stop (number or partial name):")
        departure_input = input("> ").strip()
        
        print("\nEnter Destination Stop (number or partial name):")
        destination_input = input("> ").strip()
        
        # Parse inputs
        departure_id = self._parse_stop_input(departure_input, available_stops)
        destination_id = self._parse_stop_input(destination_input, available_stops)
        
        if departure_id is None or destination_id is None:
            raise ValueError("Invalid stop selection. Please try again.")
        
        return departure_id, destination_id
    
    def _parse_stop_input(self, user_input: str, available_stops: List[Stop]) -> int:
        """Parse user input to get stop ID."""
        # Try parsing as number
        try:
            index = int(user_input) - 1
            if 0 <= index < len(available_stops):
                return available_stops[index].get_stop_id()
        except ValueError:
            pass
        
        # Try matching by name
        if user_input in self.stop_name_to_id:
            return self.stop_name_to_id[user_input]
        
        # Try partial matching
        for name, stop_id in self.stop_name_to_id.items():
            if user_input.lower() in name.lower():
                return stop_id
        
        return None
    
    def find_and_display_route(self, departure_id: int, destination_id: int, 
                               algorithm: str = 'dijkstra'):
        """
        Find and display the optimal route.
        
        Args:
            departure_id: Starting stop ID
            destination_id: Destination stop ID
            algorithm: Algorithm to use ('dijkstra', 'a_star', 'floyd_warshall', 'weighted_a_star')
        """
        print("\n" + "=" * 60)
        print(f"FINDING ROUTE USING {algorithm.upper()}")
        print("=" * 60)
        
        # Find path based on algorithm
        if algorithm == 'dijkstra':
            path, total_time, metrics = self.graph.dijkstra(departure_id, destination_id)
        elif algorithm == 'a_star':
            path, total_time, metrics = self.graph.a_star(departure_id, destination_id)
        elif algorithm == 'floyd_warshall':
            path, total_time, metrics = self.graph.floyd_warshall(departure_id, destination_id)
        elif algorithm == 'weighted_a_star':
            path, total_time, metrics = self.graph.weighted_a_star(departure_id, destination_id)
        else:
            print(f"Unknown algorithm: {algorithm}")
            return
        
        if not path:
            print("No route found between the selected stops.")
            return
        
        # Display route
        print("\nDETAILED ROUTE:")
        print("-" * 60)
        
        cumulative_time = 0.0
        current_route = None
        
        for i in range(len(path)):
            current_stop = path[i]
            
            # Display current stop
            if i == 0:
                print(f"\n🚏 START: {current_stop.get_name()}")
            elif i == len(path) - 1:
                print(f"\n🎯 DESTINATION: {current_stop.get_name()}")
            else:
                # Show intermediate stop
                # Find which route we're on
                if i < len(path) - 1:
                    next_stop = path[i + 1]
                    
                    # Find the edge to determine route
                    edge_route = None
                    transit_time = 0.0
                    for edge in current_stop.get_edges():
                        if edge.get_end_stop() == next_stop:
                            edge_route = edge.get_route_id()
                            transit_time = edge.get_transit_time()
                            break
                    
                    # Check for route change
                    if current_route is not None and edge_route != current_route and edge_route != -1:
                        print(f"\n🔄 TRANSFER at {current_stop.get_name()}")
                        print(f"   Change from Route {current_route} to Route {edge_route}")
                    
                    current_route = edge_route if edge_route != -1 else current_route
                    
                    # Show stop on route
                    if edge_route == -1:
                        print(f"   ↓ Walk to: {current_stop.get_name()}")
                    else:
                        print(f"   ↓ Stop: {current_stop.get_name()} (Route {current_route})")
                    
                    if transit_time > 0:
                        print(f"      [{transit_time:.1f} minutes to next stop]")
                        cumulative_time += transit_time
        
        print("-" * 60)
        print(f"\n📊 SUMMARY:")
        print(f"   Total Stops: {len(path)}")
        print(f"   Total Transit Time: {total_time:.1f} minutes")
        print(f"   Algorithm: {algorithm}")
        print(f"   Execution Time: {metrics['execution_time']:.6f} seconds")
        print(f"   Nodes Explored: {metrics['nodes_explored']}")
        print("=" * 60)
    
    def run(self):
        """Run the QuickRoute application."""
        print("\n" + "=" * 60)
        print("WELCOME TO QUICKROUTE!")
        print("Twin Cities Metro Transit Route Finder")
        print("=" * 60)
        
        try:
            self.load_graph()
        except Exception as e:
            print(f"Failed to load graph: {e}")
            return
        
        # Display available stops
        available_stops = self.display_available_stops()
        
        # Get user input
        try:
            departure_id, destination_id = self.get_user_input(available_stops)
        except ValueError as e:
            print(f"Error: {e}")
            return
        
        # Ask which algorithm to use
        print("\nSelect algorithm:")
        print("1. Dijkstra's Algorithm (default)")
        print("2. A* Algorithm")
        print("3. Floyd-Warshall Algorithm")
        print("4. Weighted A* Algorithm")
        
        algorithm_choice = input("\nEnter choice (1-4, or press Enter for default): ").strip()
        
        algorithm_map = {
            '1': 'dijkstra',
            '2': 'a_star',
            '3': 'floyd_warshall',
            '4': 'weighted_a_star',
            '': 'dijkstra'
        }
        
        algorithm = algorithm_map.get(algorithm_choice, 'dijkstra')
        
        # Find and display route
        self.find_and_display_route(departure_id, destination_id, algorithm)
        
        print("\nThank you for using QuickRoute!")


def main():
    """Main entry point."""
    app = QuickRoute()
    app.run()


if __name__ == "__main__":
    main()
