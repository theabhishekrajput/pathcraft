"""
Fuel Engine - Optimizes fuel stops based on car mileage and route distance
Calculates fuel requirements and suggests optimal refueling points
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class FuelStop:
    location: str
    distance_from_start: float
    distance_from_previous: float
    fuel_needed: float  # Liters
    reason: str
    fuel_price_range: str  # Estimated price range


class FuelEngine:
    def __init__(self):
        # Default car specifications
        self.default_mileage = 15.0  # km/l (average for Indian cars)
        self.fuel_tank_capacity = 45.0  # liters
        self.reserve_fuel = 5.0  # liters to keep as reserve
        
        # City fuel station availability
        self.fuel_stations = {
            "bangalore": {"available": True, "price_range": "₹100-110", "highway": True},
            "goa": {"available": True, "price_range": "₹105-115", "highway": True},
            "chikmagalur": {"available": True, "price_range": "₹102-112", "highway": False},
            "coorg": {"available": True, "price_range": "₹103-113", "highway": False},
            "mangalore": {"available": True, "price_range": "₹101-111", "highway": True},
            "udupi": {"available": True, "price_range": "₹102-112", "highway": True},
            "shimoga": {"available": True, "price_range": "₹101-111", "highway": False},
            "hubli": {"available": True, "price_range": "₹99-109", "highway": True},
            "belgaum": {"available": True, "price_range": "₹98-108", "highway": True},
            "sirsi": {"available": True, "price_range": "₹104-114", "highway": False},
            "agumbe": {"available": False, "price_range": "N/A", "highway": False},
            "murudeshwar": {"available": True, "price_range": "₹103-113", "highway": True},
            "gokarna": {"available": True, "price_range": "₹104-114", "highway": True},
            "hampi": {"available": True, "price_range": "₹105-115", "highway": False},
            "mysore": {"available": True, "price_range": "₹100-110", "highway": True}
        }
    
    def calculate_fuel_consumption(self, distance: float, mileage: float = None) -> float:
        """Calculate fuel consumption for a given distance"""
        if mileage is None:
            mileage = self.default_mileage
        
        return distance / mileage
    
    def calculate_range(self, current_fuel: float, mileage: float = None) -> float:
        """Calculate how far can go with current fuel"""
        if mileage is None:
            mileage = self.default_mileage
        
        return current_fuel * mileage
    
    def plan_fuel_stops(self, route: Dict, mileage: float = None, 
                        initial_fuel: float = None) -> List[Dict]:
        """Plan optimal fuel stops for a route"""
        if mileage is None:
            mileage = self.default_mileage
        if initial_fuel is None:
            initial_fuel = self.fuel_tank_capacity
        
        stops = []
        
        if "path" not in route or "distance" not in route:
            return stops
        
        path = route["path"]
        total_distance = route["distance"]
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
        
        # Calculate maximum range with full tank
        max_range = self.calculate_range(self.fuel_tank_capacity - self.reserve_fuel, mileage)
        
        # Plan fuel stops
        current_fuel_level = initial_fuel
        last_stop_distance = 0
        last_stop_city = path[0]
        
        for i, city in enumerate(path[1:], 1):  # Skip starting city
            distance_from_start = cumulative_distances[city]
            distance_since_last_stop = distance_from_start - last_stop_distance
            
            # Calculate fuel consumed since last stop
            fuel_consumed = self.calculate_fuel_consumption(distance_since_last_stop, mileage)
            current_fuel_level -= fuel_consumed
            
            # Check if we need to refuel at this city
            should_refuel = False
            refuel_reason = ""
            
            # Condition 1: Low fuel (below reserve)
            if current_fuel_level <= self.reserve_fuel:
                should_refuel = True
                refuel_reason = "Low fuel - refueling required"
            
            # Condition 2: Can't reach next fuel station
            elif i < len(path) - 1:  # Not the last city
                next_city = path[i + 1]
                next_distance = cumulative_distances[next_city] - distance_from_start
                
                # Check if there are fuel stations in the next few cities
                future_range = 0
                for j in range(i + 1, min(i + 4, len(path))):
                    future_city = path[j]
                    if future_city in self.fuel_stations and self.fuel_stations[future_city]["available"]:
                        future_distance = cumulative_distances[future_city] - distance_from_start
                        future_range = future_distance
                        break
                
                if future_range > 0:
                    fuel_needed_to_reach = self.calculate_fuel_consumption(future_range, mileage)
                    if current_fuel_level <= fuel_needed_to_reach + self.reserve_fuel:
                        should_refuel = True
                        refuel_reason = f"Fuel needed to reach {future_city}"
            
            # Condition 3: Good opportunity (highway fuel station)
            elif (city in self.fuel_stations and 
                  self.fuel_stations[city]["available"] and 
                  self.fuel_stations[city]["highway"] and
                  current_fuel_level <= self.fuel_tank_capacity * 0.5):
                should_refuel = True
                refuel_reason = "Good refueling opportunity (highway)"
            
            # Add fuel stop if needed
            if should_refuel and city in self.fuel_stations and self.fuel_stations[city]["available"]:
                fuel_to_add = self.fuel_tank_capacity - current_fuel_level
                
                stops.append({
                    "location": city,
                    "distance_from_start": distance_from_start,
                    "distance_from_previous": distance_since_last_stop,
                    "fuel_needed": round(fuel_to_add, 1),
                    "reason": refuel_reason,
                    "fuel_price_range": self.fuel_stations[city]["price_range"],
                    "highway": self.fuel_stations[city]["highway"]
                })
                
                # Reset fuel level and tracking
                current_fuel_level = self.fuel_tank_capacity
                last_stop_distance = distance_from_start
                last_stop_city = city
        
        return stops
    
    def calculate_total_fuel_cost(self, stops: List[Dict], fuel_prices: Dict[str, float] = None) -> Dict:
        """Calculate total fuel cost for the journey"""
        if fuel_prices is None:
            # Use average prices from ranges
            fuel_prices = {}
            for city, info in self.fuel_stations.items():
                if info["available"]:
                    price_range = info["price_range"].replace("₹", "").split("-")
                    avg_price = (float(price_range[0]) + float(price_range[1])) / 2
                    fuel_prices[city] = avg_price
        
        total_cost = 0
        total_fuel = 0
        
        for stop in stops:
            city = stop["location"]
            fuel_needed = stop["fuel_needed"]
            
            if city in fuel_prices:
                cost = fuel_needed * fuel_prices[city]
                total_cost += cost
                total_fuel += fuel_needed
        
        return {
            "total_fuel_liters": round(total_fuel, 1),
            "total_cost": round(total_cost, 2),
            "average_price_per_liter": round(total_cost / total_fuel if total_fuel > 0 else 0, 2)
        }
    
    def get_fuel_efficiency_tips(self, route: Dict, mileage: float = None) -> List[str]:
        """Get fuel efficiency tips based on route characteristics"""
        tips = []
        
        if mileage is None:
            mileage = self.default_mileage
        
        # Analyze route segments
        segments = route.get("segments", [])
        highway_distance = 0
        state_road_distance = 0
        
        for segment in segments:
            if segment.get("road_type") == "highway":
                highway_distance += segment["distance"]
            else:
                state_road_distance += segment["distance"]
        
        total_distance = route.get("distance", 0)
        
        # Generate tips
        if highway_distance > total_distance * 0.7:
            tips.append("🛣️ Mostly highway driving - maintain steady speed for better mileage")
        
        if state_road_distance > total_distance * 0.5:
            tips.append("🏔️ Mountain roads expected - mileage may decrease by 10-15%")
        
        if total_distance > 500:
            tips.append("⛽ Long journey - consider refueling at cheaper highway stations")
        
        tips.append("🚗 Maintain tire pressure for optimal fuel efficiency")
        tips.append("🌡️ Avoid excessive AC usage on hilly sections")
        
        return tips
    
    def optimize_fuel_strategy(self, route: Dict, preferences: Dict = None) -> Dict:
        """Optimize fuel strategy based on user preferences"""
        if preferences is None:
            preferences = {"priority": "cost"}  # or "time", "convenience"
        
        priority = preferences.get("priority", "cost")
        mileage = preferences.get("mileage", self.default_mileage)
        
        # Get basic fuel plan
        fuel_stops = self.plan_fuel_stops(route, mileage)
        
        # Optimize based on priority
        if priority == "cost":
            # Prefer cheaper fuel stations
            optimized_stops = []
            for stop in fuel_stops:
                # Keep stops that are necessary or significantly cheaper
                if ("required" in stop["reason"].lower() or 
                    stop["highway"] or
                    "Low fuel" in stop["reason"]):
                    optimized_stops.append(stop)
            fuel_stops = optimized_stops
        
        elif priority == "time":
            # Prefer highway fuel stations for faster access
            highway_stops = [stop for stop in fuel_stops if stop["highway"]]
            if highway_stops:
                fuel_stops = highway_stops
        
        # Calculate costs
        cost_info = self.calculate_total_fuel_cost(fuel_stops)
        
        # Get efficiency tips
        tips = self.get_fuel_efficiency_tips(route, mileage)
        
        return {
            "fuel_stops": fuel_stops,
            "cost_analysis": cost_info,
            "efficiency_tips": tips,
            "strategy": priority,
            "estimated_mileage": mileage
        }
