"""
Scenic Engine - Finds scenic spots and hidden gems along routes
Preloaded dataset of waterfalls, mountains, temples, viewpoints
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ScenicSpot:
    name: str
    type: str  # waterfall, mountain, temple, viewpoint, beach, heritage
    lat: float
    lon: float
    city: str
    rating: float  # 1-10
    description: str
    visit_duration: str  # "1 hour", "2-3 hours", etc.
    best_time: str
    proximity_bonus: float = 0.0


class ScenicEngine:
    def __init__(self):
        self.scenic_spots: Dict[str, List[ScenicSpot]] = {}
        self._load_scenic_data()
    
    def _load_scenic_data(self):
        """Load pre-defined scenic spots dataset"""
        
        # Waterfalls
        waterfalls = [
            ScenicSpot("Jog Falls", "waterfall", 14.2034, 74.7943, "sirsi", 9.5, 
                      "Highest plunge waterfall in India, spectacular monsoon views", 
                      "2-3 hours", "Monsoon (Jul-Sep)"),
            ScenicSpot("Shivanasamudra Falls", "waterfall", 12.3059, 77.1738, "mysore", 8.8,
                      "Twin waterfalls on Kaveri River, powerful flow", 
                      "1-2 hours", "Monsoon (Jul-Oct)"),
            ScenicSpot("Abbey Falls", "waterfall", 12.4260, 75.7315, "coorg", 8.2,
                      "Coffee estate waterfall, misty surroundings", 
                      "1 hour", "Monsoon (Jun-Sep)"),
            ScenicSpot("Gokak Falls", "waterfall", 16.1633, 74.2833, "belgaum", 8.0,
                      "Gorge waterfall with historic bridge", 
                      "1-2 hours", "Monsoon (Jul-Sep)"),
            ScenicSpot("Unchalli Falls", "waterfall", 14.6833, 74.8167, "sirsi", 7.8,
                      "Hidden gem in dense forest", 
                      "2 hours", "Monsoon (Jul-Sep)"),
        ]
        
        # Mountains & Viewpoints
        mountains = [
            ScenicSpot("Mullayanagiri Peak", "mountain", 13.3667, 75.7333, "chikmagalur", 9.2,
                      "Highest peak in Karnataka, panoramic views", 
                      "2-3 hours", "Oct-Mar"),
            ScenicSpot("Kudremukh Peak", "mountain", 13.2167, 75.2500, "chikmagalur", 9.0,
                      "Horse-faced mountain range, trekking paradise", 
                      "4-5 hours", "Oct-Mar"),
            ScenicSpot("Agumbe Sunset Point", "viewpoint", 13.5065, 75.0936, "agumbe", 8.7,
                      "Sunset point with stunning valley views", 
                      "1 hour", "Oct-Feb"),
            ScenicSpot("Kemmanagundi", "mountain", 13.5500, 75.7500, "chikmagalur", 8.5,
                      "Hill station with rose gardens", 
                      "2-3 hours", "Year-round"),
            ScenicSpot("Baba Budangiri", "mountain", 13.3667, 75.6833, "chikmagalur", 8.3,
                      "Twin peaks with spiritual significance", 
                      "2-3 hours", "Oct-Mar"),
            ScenicSpot("Kudremukh National Park", "mountain", 13.2167, 75.2500, "chikmagalur", 8.8,
                      "UNESCO heritage site, rich biodiversity", 
                      "Full day", "Oct-Mar"),
        ]
        
        # Temples & Heritage
        temples = [
            ScenicSpot("Hampi Ruins", "heritage", 15.3350, 76.4600, "hampi", 9.8,
                      "UNESCO World Heritage site, ancient Vijayanagara empire", 
                      "Full day", "Oct-Mar"),
            ScenicSpot("Belur Halebidu", "heritage", 13.2167, 75.8833, "shimoga", 9.3,
                      "Hoysala architecture marvels", 
                      "3-4 hours", "Year-round"),
            ScenicSpot("Murudeshwar Temple", "temple", 14.0943, 74.4819, "murudeshwar", 8.6,
                      "Coastal temple with giant Shiva statue", 
                      "1-2 hours", "Year-round"),
            ScenicSpot("Gokarna Beach Temple", "temple", 14.5437, 74.3187, "gokarna", 8.4,
                      "Sacred beach town with ancient temples", 
                      "2-3 hours", "Oct-Mar"),
            ScenicSpot("Sringeri Sharada Peetham", "temple", 13.4233, 75.5250, "chikmagalur", 8.1,
                      "Ancient Advaita Vedanta monastery", 
                      "1-2 hours", "Year-round"),
            ScenicSpot("Udupi Krishna Temple", "temple", 13.3409, 74.7421, "udupi", 8.0,
                      "Famous Krishna temple with unique rituals", 
                      "1 hour", "Year-round"),
        ]
        
        # Beaches
        beaches = [
            ScenicSpot("Palolem Beach", "beach", 15.0104, 74.0189, "goa", 8.9,
                      "Crescent-shaped beach with palm trees", 
                      "2-3 hours", "Nov-Mar"),
            ScenicSpot("Anjuna Beach", "beach", 15.5713, 73.7446, "goa", 8.5,
                      "Famous flea market beach", 
                      "2 hours", "Nov-Mar"),
            ScenicSpot("Baga Beach", "beach", 15.5534, 73.7548, "goa", 8.3,
                      "Popular beach with water sports", 
                      "2-3 hours", "Nov-Mar"),
            ScenicSpot("Murudeshwar Beach", "beach", 14.0943, 74.4819, "murudeshwar", 8.2,
                      "Clean beach with temple backdrop", 
                      "1-2 hours", "Oct-Mar"),
            ScenicSpot("Maravanthe Beach", "beach", 13.7000, 74.7000, "udupi", 8.6,
                      "Unique beach with highway on one side, river on other", 
                      "1 hour", "Oct-Mar"),
            ScenicSpot("Om Beach", "beach", 14.5437, 74.3187, "gokarna", 8.4,
                      "Om-shaped beach, sacred and scenic", 
                      "2 hours", "Oct-Mar"),
        ]
        
        # Coffee Plantations & Nature
        nature = [
            ScenicSpot("Coorg Coffee Plantations", "nature", 12.4184, 75.7394, "coorg", 8.8,
                      "Lush coffee estates with colonial bungalows", 
                      "2-3 hours", "Oct-Mar"),
            ScenicSpot("Chikmagalur Coffee Estates", "nature", 13.3168, 75.7718, "chikmagalur", 8.7,
                      "Birthplace of coffee in India", 
                      "2 hours", "Oct-Mar"),
            ScenicSpot("Agumbe Rainforest", "nature", 13.5065, 75.0936, "agumbe", 8.5,
                      "Western Ghats rainforest, rich biodiversity", 
                      "3-4 hours", "Monsoon (Jul-Sep)"),
            ScenicSpot("Dandeli Wildlife Sanctuary", "nature", 15.2333, 74.6167, "hubli", 8.3,
                      "Adventure sports and wildlife", 
                      "Full day", "Oct-Mar"),
            ScenicSpot("Bhadra Wildlife Sanctuary", "nature", 13.2500, 75.6500, "chikmagalur", 8.1,
                      "Tiger reserve with diverse flora", 
                      "Full day", "Oct-Mar"),
        ]
        
        # Group spots by city
        all_spots = waterfalls + mountains + temples + beaches + nature
        
        for spot in all_spots:
            if spot.city not in self.scenic_spots:
                self.scenic_spots[spot.city] = []
            self.scenic_spots[spot.city].append(spot)
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def calculate_proximity_score(self, spot: ScenicSpot, route_path: List[str], 
                                city_coords: Dict[str, Tuple[float, float]]) -> float:
        """Calculate how close a spot is to the route"""
        if not route_path or spot.city not in city_coords:
            return 0.0
        
        # If spot is directly on the route path
        if spot.city in route_path:
            return 10.0  # Maximum proximity bonus
        
        # Calculate minimum distance to any city on the route
        min_distance = float('inf')
        for city in route_path:
            if city in city_coords:
                city_lat, city_lon = city_coords[city]
                distance = self.calculate_distance(spot.lat, spot.lon, city_lat, city_lon)
                min_distance = min(min_distance, distance)
        
        # Score based on proximity (closer = higher score)
        if min_distance <= 20:  # Within 20 km
            return 8.0
        elif min_distance <= 50:  # Within 50 km
            return 6.0
        elif min_distance <= 100:  # Within 100 km
            return 4.0
        elif min_distance <= 150:  # Within 150 km
            return 2.0
        else:
            return 0.0
    
    def find_scenic_spots(self, route_path: List[str], city_coords: Dict[str, Tuple[float, float]] = None) -> List[Dict]:
        """Find scenic spots along a route"""
        if city_coords is None:
            city_coords = {}
        
        found_spots = []
        
        for city in route_path:
            if city in self.scenic_spots:
                for spot in self.scenic_spots[city]:
                    # Calculate proximity score
                    proximity_score = self.calculate_proximity_score(spot, route_path, city_coords)
                    
                    # Calculate total score
                    total_score = (spot.rating * 0.7) + (proximity_score * 0.3)
                    
                    found_spots.append({
                        "place": spot.name,
                        "type": spot.type,
                        "city": spot.city,
                        "score": round(total_score, 1),
                        "rating": spot.rating,
                        "description": spot.description,
                        "visit_duration": spot.visit_duration,
                        "best_time": spot.best_time,
                        "proximity_score": proximity_score
                    })
        
        # Sort by total score (descending)
        found_spots.sort(key=lambda x: x["score"], reverse=True)
        
        return found_spots[:15]  # Return top 15 spots
    
    def get_spots_by_type(self, spot_type: str, limit: int = 10) -> List[Dict]:
        """Get scenic spots filtered by type"""
        filtered_spots = []
        
        for city_spots in self.scenic_spots.values():
            for spot in city_spots:
                if spot.type == spot_type:
                    filtered_spots.append({
                        "place": spot.name,
                        "city": spot.city,
                        "score": spot.rating,
                        "description": spot.description,
                        "visit_duration": spot.visit_duration,
                        "best_time": spot.best_time
                    })
        
        filtered_spots.sort(key=lambda x: x["score"], reverse=True)
        return filtered_spots[:limit]
    
    def get_city_highlights(self, city: str) -> List[Dict]:
        """Get top scenic spots for a specific city"""
        if city not in self.scenic_spots:
            return []
        
        spots = []
        for spot in self.scenic_spots[city]:
            spots.append({
                "place": spot.name,
                "type": spot.type,
                "score": spot.rating,
                "description": spot.description,
                "visit_duration": spot.visit_duration,
                "best_time": spot.best_time
            })
        
        spots.sort(key=lambda x: x["score"], reverse=True)
        return spots[:5]  # Top 5 spots per city
