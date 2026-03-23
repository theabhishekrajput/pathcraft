"""
Stop Planner - Decides where to stop and for how long
Rules-based system for rest stops and overnight stays
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
import math


@dataclass
class Stop:
    location: str
    type: str  # "rest", "overnight", "fuel", "meal"
    distance_from_start: float
    recommended_duration: str
    reason: str
    facilities: List[str]


class StopPlanner:
    def __init__(self):
        self.rest_interval = 2.5  # Hours between rest stops
        self.max_driving_hours = 8  # Maximum driving hours per day
        self.overnight_distance = 400  # Maximum distance for overnight stop
        
        # City facilities data
        self.city_facilities = {
            "bangalore": {
                "type": "major_city",
                "facilities": ["hotels", "restaurants", "fuel", "atm", "hospitals"],
                "overnight_suitable": True
            },
            "goa": {
                "type": "major_city", 
                "facilities": ["hotels", "restaurants", "fuel", "atm", "beaches"],
                "overnight_suitable": True
            },
            "chikmagalur": {
                "type": "hill_station",
                "facilities": ["hotels", "restaurants", "fuel", "atm"],
                "overnight_suitable": True
            },
            "coorg": {
                "type": "hill_station",
                "facilities": ["hotels", "restaurants", "fuel", "atm"],
                "overnight_suitable": True
            },
            "mangalore": {
                "type": "coastal_city",
                "facilities": ["hotels", "restaurants", "fuel", "atm", "hospitals"],
                "overnight_suitable": True
            },
            "udupi": {
                "type": "temple_city",
                "facilities": ["hotels", "restaurants", "fuel", "atm"],
                "overnight_suitable": True
            },
            "shimoga": {
                "type": "city",
                "facilities": ["hotels", "restaurants", "fuel", "atm"],
                "overnight_suitable": True
            },
            "hubli": {
                "type": "city",
                "facilities": ["hotels", "restaurants", "fuel", "atm", "hospitals"],
                "overnight_suitable": True
            },
            "belgaum": {
                "type": "city",
                "facilities": ["hotels", "restaurants", "fuel", "atm"],
                "overnight_suitable": True
            },
            "sirsi": {
                "type": "town",
                "facilities": ["restaurants", "fuel", "atm"],
                "overnight_suitable": False
            },
            "agumbe": {
                "type": "village",
                "facilities": ["restaurants"],
                "overnight_suitable": False
            },
            "murudeshwar": {
                "type": "pilgrimage",
                "facilities": ["restaurants", "fuel", "atm"],
                "overnight_suitable": True
            },
            "gokarna": {
                "type": "pilgrimage_beach",
                "facilities": ["hotels", "restaurants", "fuel", "atm"],
                "overnight_suitable": True
            },
            "hampi": {
                "type": "heritage",
                "facilities": ["hotels", "restaurants", "fuel", "atm"],
                "overnight_suitable": True
            },
            "mysore": {
                "type": "city",
                "facilities": ["hotels", "restaurants", "fuel", "atm", "hospitals"],
                "overnight_suitable": True
            }
        }
    
    def calculate_driving_time(self, distance: float, road_type: str = "highway") -> float:
        """Calculate driving time based on distance and road type"""
        speed_limits = {
            "highway": 65,  # km/h
            "state": 50,    # km/h
            "city": 30      # km/h
        }
        
        speed = speed_limits.get(road_type, 50)
        return distance / speed
    
    def plan_stops(self, route: Dict) -> List[Dict]:
        """Plan rest and overnight stops for a route"""
        stops = []
        
        if "path" not in route or len(route["path"]) < 2:
            return stops
        
        path = route["path"]
        total_distance = route.get("distance", 0)
        segments = route.get("segments", [])
        
        # Calculate cumulative distances
        cumulative_distances = {path[0]: 0}
        current_distance = 0
        
        for i in range(len(path) - 1):
            from_city = path[i]
            to_city = path[i + 1]
            
            # Find segment distance
            segment_distance = 0
            for segment in segments:
                if segment["from"] == from_city and segment["to"] == to_city:
                    segment_distance = segment["distance"]
                    break
            
            current_distance += segment_distance
            cumulative_distances[to_city] = current_distance
        
        # Plan stops based on driving time and distance
        driving_time = route.get("time", 0)
        
        # Rule 1: Every 2-3 hours → rest stop
        rest_stops = self._plan_rest_stops(path, cumulative_distances, driving_time)
        stops.extend(rest_stops)
        
        # Rule 2: Every 400-500 km → overnight stop
        overnight_stops = self._plan_overnight_stops(path, cumulative_distances, total_distance)
        stops.extend(overnight_stops)
        
        # Rule 3: Meal stops (every 4-5 hours)
        meal_stops = self._plan_meal_stops(path, cumulative_distances, driving_time)
        stops.extend(meal_stops)
        
        # Sort stops by distance and remove duplicates
        unique_stops = {}
        for stop in stops:
            location = stop["location"]
            distance = stop["distance_from_start"]
            
            # Keep the stop with highest priority for each location
            if location not in unique_stops or distance < unique_stops[location]["distance_from_start"]:
                unique_stops[location] = stop
        
        # Convert back to list and sort
        final_stops = sorted(unique_stops.values(), key=lambda x: x["distance_from_start"])
        
        return final_stops
    
    def _plan_rest_stops(self, path: List[str], cumulative_distances: Dict[str, float], 
                        total_time: float) -> List[Dict]:
        """Plan rest stops every 2-3 hours"""
        stops = []
        rest_interval_km = self.rest_interval * 60  # Convert hours to km (assuming 60 km/h)
        
        for i, city in enumerate(path[1:-1], 1):  # Skip start and end
            distance = cumulative_distances[city]
            
            # Check if we need a rest stop around this distance
            for target_distance in range(int(rest_interval_km), int(cumulative_distances[path[-1]]), int(rest_interval_km)):
                if abs(distance - target_distance) <= 50:  # Within 50 km of target
                    if city in self.city_facilities:
                        facilities = self.city_facilities[city]
                        stops.append({
                            "location": city,
                            "type": "rest",
                            "distance_from_start": distance,
                            "recommended_duration": "30 minutes",
                            "reason": "Regular rest break",
                            "facilities": facilities["facilities"]
                        })
                    break
        
        return stops
    
    def _plan_overnight_stops(self, path: List[str], cumulative_distances: Dict[str, float], 
                             total_distance: float) -> List[Dict]:
        """Plan overnight stops every 400-500 km"""
        stops = []
        
        for i, city in enumerate(path[1:-1], 1):  # Skip start and end
            distance = cumulative_distances[city]
            
            # Check if this is a good overnight stop location
            if city in self.city_facilities:
                facilities = self.city_facilities[city]
                
                if facilities["overnight_suitable"]:
                    # Check if we need an overnight stop around this distance
                    for target_distance in range(int(self.overnight_distance), int(total_distance), int(self.overnight_distance)):
                        if abs(distance - target_distance) <= 100:  # Within 100 km of target
                            stops.append({
                                "location": city,
                                "type": "overnight",
                                "distance_from_start": distance,
                                "recommended_duration": "Overnight",
                                "reason": "Overnight stay for long journey",
                                "facilities": facilities["facilities"]
                            })
                            break
        
        return stops
    
    def _plan_meal_stops(self, path: List[str], cumulative_distances: Dict[str, float], 
                        total_time: float) -> List[Dict]:
        """Plan meal stops every 4-5 hours"""
        stops = []
        meal_interval_km = 4.5 * 60  # 4.5 hours = 270 km
        
        for i, city in enumerate(path[1:-1], 1):  # Skip start and end
            distance = cumulative_distances[city]
            
            # Check if we need a meal stop around this distance
            for target_distance in range(int(meal_interval_km), int(cumulative_distances[path[-1]]), int(meal_interval_km)):
                if abs(distance - target_distance) <= 50:  # Within 50 km of target
                    if city in self.city_facilities:
                        facilities = self.city_facilities[city]
                        if "restaurants" in facilities["facilities"]:
                            stops.append({
                                "location": city,
                                "type": "meal",
                                "distance_from_start": distance,
                                "recommended_duration": "1 hour",
                                "reason": "Meal break",
                                "facilities": facilities["facilities"]
                            })
                    break
        
        return stops
    
    def optimize_stop_sequence(self, stops: List[Dict], total_distance: float) -> List[Dict]:
        """Optimize the sequence of stops to minimize total journey time"""
        if not stops:
            return stops
        
        # Sort by distance
        sorted_stops = sorted(stops, key=lambda x: x["distance_from_start"])
        
        # Remove stops that are too close to each other (within 30 km)
        optimized_stops = []
        last_stop_distance = 0
        
        for stop in sorted_stops:
            if stop["distance_from_start"] - last_stop_distance >= 30:
                optimized_stops.append(stop)
                last_stop_distance = stop["distance_from_start"]
        
        return optimized_stops
    
    def get_stop_recommendations(self, city: str) -> Dict:
        """Get detailed recommendations for a specific stop city"""
        if city not in self.city_facilities:
            return {"error": f"No data available for {city}"}
        
        facilities = self.city_facilities[city]
        
        recommendations = {
            "city": city,
            "type": facilities["type"],
            "facilities": facilities["facilities"],
            "overnight_suitable": facilities["overnight_suitable"],
            "recommended_stops": []
        }
        
        if facilities["overnight_suitable"]:
            recommendations["recommended_stops"].append({
                "type": "overnight",
                "duration": "Overnight",
                "reason": "Good accommodation options available"
            })
        
        if "restaurants" in facilities["facilities"]:
            recommendations["recommended_stops"].append({
                "type": "meal",
                "duration": "1 hour",
                "reason": "Good food options available"
            })
        
        if "fuel" in facilities["facilities"]:
            recommendations["recommended_stops"].append({
                "type": "fuel",
                "duration": "15 minutes",
                "reason": "Fuel station available"
            })
        
        return recommendations
