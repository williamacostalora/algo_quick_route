"""
Graph class with multiple pathfinding algorithm implementations.
"""

from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict, deque
import heapq
import math
import time
from stop import Stop
from edge import Edge
from api_caller import ApiCaller
from queue import Queue

class Graph:
    """Transit graph with multiple pathfinding algorithms."""
    
    def __init__(self, route_id: int = None, direction_id: int = None, 
                 graph_list: List['Graph'] = None):
        """
        Initialize a Graph.
        
        Args:
            route_id: Single route ID (for single-route graph)
            direction_id: Direction (1=East/North, 2=West/South)
            graph_list: List of graphs to combine (for multi-route graph)
        """
        self.coordinate_threshold = 0.001  # For detecting nearby stops
        self.api_caller = ApiCaller()
        
        if graph_list:
            # Multi-route graph constructor
            self.route_id = 0
            self.direction_id = 0
            self.stops: List[Stop] = []
            self.edges: Dict[int, List[Edge]] = {}
            
            for graph in graph_list:
                for stop in graph.stops:
                    if stop not in self.stops:
                        self.stops.append(stop)
                
                for stop_id, edge_list in graph.edges.items():
                    if stop_id not in self.edges:
                        self.edges[stop_id] = []
                    self.edges[stop_id].extend(edge_list)
            
            self._create_connecting_edges()
        else:
            # Single-route graph constructor
            self.route_id = route_id
            self.direction_id = direction_id
            self.stops: List[Stop] = []
            self.edges: Dict[int, List[Edge]] = {}
            
            self._create_stop_list()
            self._create_edge_map()
    
    def _create_stop_list(self):
        """Create the list of all stops for this route."""
        all_stops = self.api_caller.get_all_stops(self.route_id, self.direction_id)
        
        if not all_stops:
            raise ValueError(f"API returned no stops for route {self.route_id}, "
                           f"direction {self.direction_id}")
        
        self.stops = all_stops
    
    def _create_edge_map(self):
        """Create edges connecting consecutive stops."""
        for i in range(len(self.stops) - 1):
            start_stop = self.stops[i]
            end_stop = self.stops[i + 1]
            
            try:
                # Skip problematic stop
                if start_stop.stop_id == 11838 or end_stop.stop_id == 11838:
                    if start_stop in self.stops:
                        self.stops.remove(start_stop)
                    if end_stop in self.stops:
                        self.stops.remove(end_stop)
                    continue
                
                # Check if coordinates are identical (same location)
                start_lat = start_stop.get_latitude()
                start_lon = start_stop.get_longitude()
                end_lat = end_stop.get_latitude()
                end_lon = end_stop.get_longitude()
                
                if (abs(start_lat - end_lat) < self.coordinate_threshold and 
                    abs(start_lon - end_lon) < self.coordinate_threshold):
                    transit_time = 0.0
                else:
                    transit_time = self.api_caller.get_transit_time(
                        self.route_id, start_stop.stop_id, 
                        end_stop.stop_id, self.direction_id
                    )
                
                edge = Edge(start_stop, end_stop, self.route_id, transit_time)
                
                if start_stop.stop_id not in self.edges:
                    self.edges[start_stop.stop_id] = []
                
                self.edges[start_stop.stop_id].append(edge)
                start_stop.add_edge(edge)
                
            except Exception as e:
                print(f"Error creating edge: {e}")
    
    def _create_connecting_edges(self):
        """Create transfer edges between nearby stops on different routes."""
        for i in range(len(self.stops)):
            for j in range(i + 1, len(self.stops)):
                stop_a = self.stops[i]
                stop_b = self.stops[j]
                
                # Check if stops are nearby and on different routes
                lat_diff = abs(stop_a.get_latitude() - stop_b.get_latitude())
                lon_diff = abs(stop_a.get_longitude() - stop_b.get_longitude())
                
                if (lat_diff < self.coordinate_threshold and 
                    lon_diff < self.coordinate_threshold and 
                    stop_a.get_route_ids() != stop_b.get_route_ids()):
                    
                    # Create bidirectional transfer edges with 0 time
                    edge_a_to_b = Edge(stop_a, stop_b, -1, 0.0)
                    edge_b_to_a = Edge(stop_b, stop_a, -1, 0.0)
                    
                    if stop_a.stop_id in self.edges and stop_b.stop_id in self.edges:
                        self.edges[stop_a.stop_id].append(edge_a_to_b)
                        self.edges[stop_b.stop_id].append(edge_b_to_a)
    
    def get_stop(self, stop_id: int) -> Optional[Stop]:
        """Get a stop by its ID."""
        for stop in self.stops:
            if stop.stop_id == stop_id:
                return stop
        return None
    
    def get_connections(self, stop_id: int) -> List[Edge]:
        """Get all edges departing from a stop."""
        return self.edges.get(stop_id, [])
    
    def is_same_route(self, start_id: int, destination_id: int) -> bool:
        """Check if two stops are on the same route."""
        start = self.get_stop(start_id)
        dest = self.get_stop(destination_id)
        
        if start and dest:
            return start.get_route_ids() == dest.get_route_ids()
        return False
    
    # ==================== DIJKSTRA'S ALGORITHM ====================
    
    def dijkstra(self, start_id: int, destination_id: int) -> Tuple[List[Stop], float, Dict]:
        """
        Find shortest path using Dijkstra's algorithm.
        
        Returns:
            Tuple of (path, total_time, metrics)
        """
        start_time = time.time()
        
        start = self.get_stop(start_id)
        destination = self.get_stop(destination_id)
        
        if not start or not destination:
            return [], float('inf'), {}
        
        # Initialize distances and tracking
        distances = {stop: float('inf') for stop in self.stops}
        distances[start] = 0.0
        previous = {}
        
        # Priority queue: (distance, stop)
        pq = [(0.0, start)]
        visited = set()
        nodes_explored = 0
        
        while pq:
            current_dist, current_stop = heapq.heappop(pq)
            
            if current_stop in visited:
                continue
            
            visited.add(current_stop)
            nodes_explored += 1
            
            if current_stop == destination:
                break
            
            for edge in self.get_connections(current_stop.stop_id):
                neighbor = edge.get_end_stop()
                new_dist = current_dist + edge.get_transit_time()
                
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_stop
                    heapq.heappush(pq, (new_dist, neighbor))
        
        path = self._reconstruct_path(previous, start, destination)
        total_time = distances[destination]
        
        metrics = {
            'algorithm': 'Dijkstra',
            'execution_time': time.time() - start_time,
            'nodes_explored': nodes_explored,
            'path_length': len(path),
            'total_transit_time': total_time
        }
        
        return path, total_time, metrics
    
    # ==================== FLOYD-WARSHALL ALGORITHM ====================
    
    def floyd_warshall(self, start_id: int, destination_id: int) -> Tuple[List[Stop], float, Dict]:
        """
        Find shortest path using Floyd-Warshall algorithm.
        All-pairs shortest path algorithm.
        
        Returns:
            Tuple of (path, total_time, metrics)
        """
        start_time = time.time()
        
        start = self.get_stop(start_id)
        destination = self.get_stop(destination_id)
        
        if not start or not destination:
            return [], float('inf'), {}
        
        n = len(self.stops)
        stop_index = {stop: i for i, stop in enumerate(self.stops)}
        index_stop = {i: stop for i, stop in enumerate(self.stops)}
        
        # Initialize distance and next matrices
        dist = [[float('inf')] * n for _ in range(n)]
        next_stop = [[None] * n for _ in range(n)]
        
        # Set diagonal to 0
        for i in range(n):
            dist[i][i] = 0.0
        
        # Initialize with direct edges
        for stop in self.stops:
            i = stop_index[stop]
            for edge in self.get_connections(stop.stop_id):
                j = stop_index[edge.get_end_stop()]
                dist[i][j] = edge.get_transit_time()
                next_stop[i][j] = j
        
        # Floyd-Warshall main loop
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_stop[i][j] = next_stop[i][k]
        
        # Reconstruct path
        path = []
        i = stop_index[start]
        j = stop_index[destination]
        
        if next_stop[i][j] is None:
            return [], float('inf'), {}
        
        path.append(start)
        while i != j:
            i = next_stop[i][j]
            path.append(index_stop[i])
        
        total_time = dist[stop_index[start]][stop_index[destination]]
        
        metrics = {
            'algorithm': 'Floyd-Warshall',
            'execution_time': time.time() - start_time,
            'nodes_explored': n * n * n,  # Triple nested loop
            'path_length': len(path),
            'total_transit_time': total_time
        }
        
        return path, total_time, metrics
    
    # ==================== A* ALGORITHM ====================
    
    def a_star(self, start_id: int, destination_id: int) -> Tuple[List[Stop], float, Dict]:
        """
        Find shortest path using A* algorithm with Euclidean distance heuristic.
        
        Returns:
            Tuple of (path, total_time, metrics)
        """
        start_time = time.time()
        
        start = self.get_stop(start_id)
        destination = self.get_stop(destination_id)
        
        if not start or not destination:
            return [], float('inf'), {}
        
        def heuristic(stop: Stop) -> float:
            """Euclidean distance heuristic (straight-line distance)."""
            lat1, lon1 = stop.get_latitude(), stop.get_longitude()
            lat2, lon2 = destination.get_latitude(), destination.get_longitude()
            
            # Convert to radians and calculate great circle distance
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Earth radius in km, convert to rough time estimate
            distance_km = 6371 * c
            # Assume average speed of 30 km/h for transit
            return distance_km / 30 * 60  # Convert to minutes
        
        # Initialize
        g_score = {stop: float('inf') for stop in self.stops}
        g_score[start] = 0.0
        
        f_score = {stop: float('inf') for stop in self.stops}
        f_score[start] = heuristic(start)
        
        previous = {}
        open_set = [(f_score[start], start)]
        closed_set = set()
        nodes_explored = 0
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current in closed_set:
                continue
            
            closed_set.add(current)
            nodes_explored += 1
            
            if current == destination:
                break
            
            for edge in self.get_connections(current.stop_id):
                neighbor = edge.get_end_stop()
                
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current] + edge.get_transit_time()
                
                if tentative_g < g_score[neighbor]:
                    previous[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        path = self._reconstruct_path(previous, start, destination)
        total_time = g_score[destination]
        
        metrics = {
            'algorithm': 'A*',
            'execution_time': time.time() - start_time,
            'nodes_explored': nodes_explored,
            'path_length': len(path),
            'total_transit_time': total_time
        }
        
        return path, total_time, metrics
    
    # ==================== WEIGHTED A* ALGORITHM ====================
    
    def weighted_a_star(self, start_id: int, destination_id: int, 
                       weight: float = 1.5) -> Tuple[List[Stop], float, Dict]:
        """
        Find shortest path using Weighted A* algorithm.
        Weight > 1 makes the search more greedy (faster but potentially suboptimal).
        
        Args:
            start_id: Starting stop ID
            destination_id: Destination stop ID
            weight: Heuristic weight factor (default 1.5)
        
        Returns:
            Tuple of (path, total_time, metrics)
        """
        start_time = time.time()
        
        start = self.get_stop(start_id)
        destination = self.get_stop(destination_id)
        
        if not start or not destination:
            return [], float('inf'), {}
        
        def heuristic(stop: Stop) -> float:
            """Weighted Euclidean distance heuristic."""
            lat1, lon1 = stop.get_latitude(), stop.get_longitude()
            lat2, lon2 = destination.get_latitude(), destination.get_longitude()
            
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            distance_km = 6371 * c
            return distance_km / 30 * 60 * weight  # Apply weight to heuristic
        
        # Initialize
        g_score = {stop: float('inf') for stop in self.stops}
        g_score[start] = 0.0
        
        f_score = {stop: float('inf') for stop in self.stops}
        f_score[start] = heuristic(start)
        
        previous = {}
        open_set = [(f_score[start], start)]
        closed_set = set()
        nodes_explored = 0
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current in closed_set:
                continue
            
            closed_set.add(current)
            nodes_explored += 1
            
            if current == destination:
                break
            
            for edge in self.get_connections(current.stop_id):
                neighbor = edge.get_end_stop()
                
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current] + edge.get_transit_time()
                
                if tentative_g < g_score[neighbor]:
                    previous[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        path = self._reconstruct_path(previous, start, destination)
        total_time = g_score[destination]
        
        metrics = {
            'algorithm': f'Weighted A* (w={weight})',
            'execution_time': time.time() - start_time,
            'nodes_explored': nodes_explored,
            'path_length': len(path),
            'total_transit_time': total_time,
            'weight': weight
        }
        
        return path, total_time, metrics

    # ==================== BFS ALGORITHM ====================
    def BFS(self, start_id: int, destination_id: int) -> Tuple[List[Stop], float, Dict]:
        """
        Find shortest path using Breadth-First Search algorithm.

        Returns:
            Tuple of (path, total_time, metrics)
        """
        start_time = time.time()

        start = self.get_stop(start_id)
        destination = self.get_stop(destination_id)

        if not start or not destination:
            return [], float('inf'), {}

        # Initialize empty distances + start for all stops in "dist" dictionary
        dist = {stop: float('inf') for stop in self.stops}
        dist[start] = 0.0
        previous = {}
        state = {}
        nodes_explored = 0

        for v in self.stops:
            if v not in state:
                state[v] = "undiscovered"
                previous[v] = None
        state[start] = "discovered"
        nodes_explored += 1
        myqueue = Queue()
        myqueue.put(start)
        while not myqueue.empty():
            u = myqueue.get()
            for edge in self.get_connections(u.stop_id):
                end = edge.get_end_stop()
                if state[end] == "undiscovered":
                    state[end] = "discovered"
                    nodes_explored += 1
                    previous[end] = u
                    dist[end] = edge.get_transit_time()
                    myqueue.put(end)
                    
            state[u] = "processed"

        path = self._reconstruct_path(previous, start, destination)

        total_time = 0
        for aStop in path:
            total_time = dist[aStop] + total_time

        total_time = dist[destination]

        metrics = {
            'algorithm': 'BFS',
            'execution_time': time.time() - start_time,
            'nodes_explored': nodes_explored,
            'path_length': len(path),
            'total_transit_time': total_time
        }

        return path, total_time, metrics
    
    # ==================== HELPER METHODS ====================
    
    def _reconstruct_path(self, previous: Dict, start: Stop, destination: Stop) -> List[Stop]:
        """Reconstruct the path from the previous dictionary."""
        path = deque()
        current = destination
        
        while current and current != start:
            path.appendleft(current)
            current = previous.get(current)
        
        if current is None:
            return []
        
        path.appendleft(start)
        return list(path)
    
    def print_graph(self):
        """Print the graph structure for debugging."""
        for stop_id, edge_list in self.edges.items():
            print(f"{stop_id} -> {[str(e) for e in edge_list]}")