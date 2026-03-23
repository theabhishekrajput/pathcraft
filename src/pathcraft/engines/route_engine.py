"""
Route Engine - Handles route generation and pathfinding
Implements Dijkstra's algorithm and custom scenic scoring
"""

import heapq
from typing import Dict, List, Tuple, Set, Optional
import math


class City:
    def __init__(self, name: str, lat: float, lon: float):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.connections: Dict[str, Dict] = {}
    
    def add_connection(self, to_city: str, distance: float, road_type: str = "highway", toll: bool = False):
        """Add connection to another city"""
        self.connections[to_city] = {
            "distance": distance,
            "road_type": road_type,
            "toll": toll
        }
    
    def distance_to(self, other_city: 'City') -> float:
        """Calculate straight-line distance between cities"""
        # Haversine formula
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(self.lat), math.radians(self.lon)
        lat2, lon2 = math.radians(other_city.lat), math.radians(other_city.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c


class RouteEngine:
    def __init__(self):
        self.cities: Dict[str, City] = {}
        self._load_city_network()
    
    def _load_city_network(self):
        """Load pre-defined city network for India"""
        # Major South Indian cities with coordinates
        cities_data = {
            "bangalore": City("Bangalore", 12.9716, 77.5946),
            "goa": City("Goa", 15.2993, 74.1240),
            "chikmagalur": City("Chikmagalur", 13.3168, 75.7718),
            "mangalore": City("Mangalore", 12.9141, 74.8560),
            "hubli": City("Hubli", 15.3647, 75.1240),
            "belgaum": City("Belgaum", 15.8481, 74.5124),
            "sirsi": City("Sirsi", 14.6198, 74.8426),
            "shimoga": City("Shimoga", 13.9289, 75.5694),
            "udupi": City("Udupi", 13.3409, 74.7421),
            "hampi": City("Hampi", 15.3350, 76.4600),
            "coorg": City("Coorg", 12.4184, 75.7394),
            "mysore": City("Mysore", 12.2958, 76.6394),
            "gokarna": City("Gokarna", 14.5437, 74.3187),
            "murudeshwar": City("Murudeshwar", 14.0943, 74.4819),
            "agumbe": City("Agumbe", 13.5065, 75.0936),
        }
        
        self.cities = cities_data
        
        # Define connections with distances and road types
        connections = [
            # Bangalore connections
            ("bangalore", "chikmagalur", 250, "highway", False),
            ("bangalore", "mysore", 150, "highway", False),
            ("bangalore", "hubli", 410, "highway", True),
            
            # Chikmagalur connections
            ("chikmagalur", "shimoga", 130, "state", False),
            ("chikmagalur", "mangalore", 200, "state", False),
            ("chikmagalur", "coorg", 120, "state", False),
            
            # Mangalore connections
            ("mangalore", "udupi", 60, "highway", False),
            ("mangalore", "murudeshwar", 160, "highway", False),
            ("mangalore", "shimoga", 200, "state", False),
            
            # Hubli connections
            ("hubli", "belgaum", 80, "highway", False),
            ("hubli", "goa", 150, "highway", False),
            ("hubli", "sirsi", 90, "state", False),
            
            # Goa connections
            ("goa", "belgaum", 110, "highway", False),
            ("goa", "gokarna", 140, "highway", False),
            
            # Shimoga connections
            ("shimoga", "sirsi", 110, "state", False),
            ("shimoga", "hampi", 150, "state", False),
            ("shimoga", "agumbe", 70, "state", False),
            
            # Udupi connections
            ("udupi", "murudeshwar", 100, "highway", False),
            ("udupi", "gokarna", 80, "highway", False),
            
            # Sirsi connections
            ("sirsi", "gokarna", 60, "state", False),
            ("sirsi", "murudeshwar", 90, "state", False),
            
            # Agumbe connections
            ("agumbe", "udupi", 55, "state", False),
            ("agumbe", "shimoga", 70, "state", False),
            
            # Coorg connections
            ("coorg", "mysore", 120, "state", False),
            ("coorg", "mangalore", 140, "state", False),
            
            # Mysore connections
            ("mysore", "hampi", 200, "highway", True),
        ]
        
        for from_city, to_city, distance, road_type, toll in connections:
            if from_city in self.cities and to_city in self.cities:
                self.cities[from_city].add_connection(to_city, distance, road_type, toll)
                self.cities[to_city].add_connection(from_city, distance, road_type, toll)
    
    def dijkstra(self, start: str, end: str) -> Optional[Tuple[float, List[str]]]:
        """Find shortest path using Dijkstra's algorithm"""
        if start not in self.cities or end not in self.cities:
            return None
        
        distances = {city: float('inf') for city in self.cities}
        distances[start] = 0
        previous = {city: None for city in self.cities}
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == end:
                break
            
            for neighbor, info in self.cities[current].connections.items():
                if neighbor in visited:
                    continue
                
                distance = info["distance"]
                new_dist = current_dist + distance
                
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))
        
        if distances[end] == float('inf'):
            return None
        
        # Reconstruct path
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return distances[end], path
    
    def scenic_route_score(self, path: List[str]) -> float:
        """Calculate scenic score for a route based on intermediate locations"""
        scenic_locations = {
            "chikmagalur": 9.0,  # Coffee plantations, mountains
            "coorg": 9.2,        # Hills, waterfalls
            "agumbe": 8.8,       # Sunset point, rainforest
            "gokarna": 8.5,      # Beaches, temples
            "murudeshwar": 8.3,  # Beach, statue
            "sirsi": 8.0,        # Forests, waterfalls
            "shimoga": 7.5,      # Nature, historical
            "udupi": 7.8,        # Beaches, temples
            "hampi": 9.5,        # UNESCO heritage
        }
        
        total_score = 0
        for city in path[1:-1]:  # Exclude start and end
            if city in scenic_locations:
                total_score += scenic_locations[city]
        
        # Normalize by path length
        return total_score / max(len(path) - 2, 1)
    
    def generate_routes(self, origin: str, destination: str) -> List[Dict]:
        """Generate multiple route options with different priorities"""
        routes = []
        
        # 1. Shortest route (Dijkstra)
        shortest_result = self.dijkstra(origin, destination)
        if shortest_result:
            distance, path = shortest_result
            scenic_score = self.scenic_route_score(path)
            estimated_time = distance / 60  # Assuming 60 km/h average
            
            routes.append({
                "type": "shortest",
                "path": path,
                "distance": distance,
                "time": estimated_time,
                "scenic_score": scenic_score,
                "total_score": distance  # Lower is better for shortest
            })
        
        # 2. Scenic route (modified scoring)
        # Try paths through scenic locations
        scenic_waypoints = ["chikmagalur", "coorg", "agumbe", "gokarna", "hampi"]
        
        for waypoint in scenic_waypoints:
            if waypoint not in self.cities:
                continue
            
            # Route: origin -> waypoint -> destination
            leg1 = self.dijkstra(origin, waypoint)
            leg2 = self.dijkstra(waypoint, destination)
            
            if leg1 and leg2:
                distance1, path1 = leg1
                distance2, path2 = leg2
                
                # Combine paths (avoid duplicate waypoint)
                full_path = path1 + path2[1:]
                total_distance = distance1 + distance2
                scenic_score = self.scenic_route_score(full_path)
                estimated_time = total_distance / 55  # Slightly slower for scenic routes
                
                routes.append({
                    "type": f"scenic_via_{waypoint}",
                    "path": full_path,
                    "distance": total_distance,
                    "time": estimated_time,
                    "scenic_score": scenic_score,
                    "total_score": scenic_score  # Higher is better for scenic
                })
        
        # Sort by total score (descending)
        routes.sort(key=lambda x: x["total_score"], reverse=True)
        
        return routes[:5]  # Return top 5 routes
    
    def get_route_details(self, path: List[str]) -> Dict:
        """Get detailed information about a specific route"""
        if len(path) < 2:
            return {}
        
        total_distance = 0
        segments = []
        has_tolls = False
        
        for i in range(len(path) - 1):
            from_city = path[i]
            to_city = path[i + 1]
            
            if from_city in self.cities and to_city in self.cities:
                connection = self.cities[from_city].connections.get(to_city)
                if connection:
                    segments.append({
                        "from": from_city,
                        "to": to_city,
                        "distance": connection["distance"],
                        "road_type": connection["road_type"],
                        "toll": connection["toll"]
                    })
                    total_distance += connection["distance"]
                    if connection["toll"]:
                        has_tolls = True
        
        return {
            "path": path,
            "total_distance": total_distance,
            "segments": segments,
            "has_tolls": has_tolls,
            "estimated_time": total_distance / 60  # Default 60 km/h
        }
