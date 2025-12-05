"""
The Edge class represents a connection between two stops in the transit graph.
"""

from stop import Stop


class Edge:
    """Represents an edge (connection) between two stops in the transit graph."""
    
    def __init__(self, start_stop: Stop, end_stop: Stop, route_id: int, transit_time: float):
        """
        Initialize an Edge object.
        
        Args:
            start_stop: Starting stop
            end_stop: Ending stop
            route_id: Route ID connecting the stops (-1 for transfer edges)
            transit_time: Travel time in minutes
        """
        self.start_stop = start_stop
        self.end_stop = end_stop
        self.route_id = route_id
        self.transit_time = transit_time
    
    def get_start_stop(self) -> Stop:
        """Get the starting stop."""
        return self.start_stop
    
    def get_end_stop(self) -> Stop:
        """Get the ending stop."""
        return self.end_stop
    
    def get_route_id(self) -> int:
        """Get the route ID."""
        return self.route_id
    
    def get_transit_time(self) -> float:
        """Get the transit time in minutes."""
        return self.transit_time
    
    def __repr__(self):
        """String representation of the edge."""
        return (f"Edge(Stop {self.start_stop.stop_id} -> Stop {self.end_stop.stop_id}, "
                f"Route {self.route_id}, Time: {self.transit_time} min)")
    
    def __str__(self):
        """Human-readable string representation."""
        return (f"Edge from {self.start_stop.name} to {self.end_stop.name} "
                f"(Route {self.route_id}), Travel Time: {self.transit_time} minutes")
