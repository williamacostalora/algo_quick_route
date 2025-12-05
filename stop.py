"""
The Stop class represents a transit stop (vertex in the graph).
"""

from typing import List, Set
import pickle


class Stop:
    """Represents a stop in the transit system (vertex in graph)."""
    
    def __init__(self, stop_id: int, name: str):
        """
        Initialize a Stop object.
        
        Args:
            stop_id: Unique identifier for the station
            name: Human-readable name of the station
        """
        self.stop_id = stop_id
        self.name = name
        self.route_ids: Set[int] = set()
        self.edges: List['Edge'] = []
        self.shortest_path: List['Stop'] = []
        self.transit_time = float('inf')
        self.latitude = 0.0
        self.longitude = 0.0
        
        # Lazy load coordinates when needed
        self._coordinates_loaded = False
    
    def _load_coordinates(self):
        """Lazy load coordinates from API."""
        if not self._coordinates_loaded:
            from api_caller import ApiCaller
            caller = ApiCaller()
            self.latitude = caller.get_coordinate("latitude", self.stop_id)
            self.longitude = caller.get_coordinate("longitude", self.stop_id)
            self._coordinates_loaded = True
    
    def add_route(self, route_id: int):
        """Add a route to this stop."""
        self.route_ids.add(route_id)
    
    def add_edge(self, edge: 'Edge'):
        """Add an edge (connection) to another stop."""
        self.edges.append(edge)
    
    def get_stop_id(self) -> int:
        """Get the stop ID."""
        return self.stop_id
    
    def get_name(self) -> str:
        """Get the stop name."""
        return self.name
    
    def get_route_ids(self) -> List[int]:
        """Get list of routes servicing this stop."""
        return list(self.route_ids)
    
    def get_edges(self) -> List['Edge']:
        """Get list of edges from this stop."""
        return self.edges
    
    def set_transit_time(self, transit_time: float):
        """Set the transit time for pathfinding algorithms."""
        self.transit_time = transit_time
    
    def get_transit_time(self) -> float:
        """Get the transit time."""
        return self.transit_time
    
    def set_shortest_path(self, path: List['Stop']):
        """Set the shortest path for pathfinding algorithms."""
        self.shortest_path = path
    
    def get_shortest_path(self) -> List['Stop']:
        """Get the shortest path."""
        return self.shortest_path
    
    def get_latitude(self) -> float:
        """Get the latitude coordinate."""
        if not self._coordinates_loaded:
            self._load_coordinates()
        return self.latitude
    
    def get_longitude(self) -> float:
        """Get the longitude coordinate."""
        if not self._coordinates_loaded:
            self._load_coordinates()
        return self.longitude
    
    def __eq__(self, other):
        """Check equality based on stop_id."""
        if isinstance(other, Stop):
            return self.stop_id == other.stop_id
        return False
    
    def __hash__(self):
        """Hash based on stop_id for use in sets and dicts."""
        return hash(self.stop_id)
    
    def __lt__(self, other):
        """Less than comparison for priority queue."""
        if isinstance(other, Stop):
            return self.stop_id < other.stop_id
        return NotImplemented
    
    def __le__(self, other):
        """Less than or equal comparison."""
        if isinstance(other, Stop):
            return self.stop_id <= other.stop_id
        return NotImplemented
    
    def __gt__(self, other):
        """Greater than comparison."""
        if isinstance(other, Stop):
            return self.stop_id > other.stop_id
        return NotImplemented
    
    def __ge__(self, other):
        """Greater than or equal comparison."""
        if isinstance(other, Stop):
            return self.stop_id >= other.stop_id
        return NotImplemented
    
    def __repr__(self):
        """String representation of the stop."""
        return f"Stop({self.stop_id}, '{self.name}')"
    
    def __str__(self):
        """Human-readable string representation."""
        return f"{self.name} (ID: {self.stop_id})"
