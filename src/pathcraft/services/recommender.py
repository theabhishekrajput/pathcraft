"""
AI Recommendation Engine - Scores routes and provides intelligent recommendations
Uses rule-based scoring system with optional local LLM integration
"""

from typing import List, Dict, Tuple, Optional
import math
from dataclasses import dataclass


@dataclass
class RouteScore:
    route_index: int
    scenic_score: float
    efficiency_score: float
    experience_score: float
    total_score: float
    reasoning: List[str]


class RecommendationEngine:
    def __init__(self):
        # Scoring weights (can be adjusted based on preferences)
        self.scenic_weight = 0.4
        self.efficiency_weight = 0.3
        self.experience_weight = 0.3
        
        # Route type preferences
        self.route_preferences = {
            "prefer_scenic": {"scenic_weight": 0.6, "efficiency_weight": 0.2, "experience_weight": 0.2},
            "prefer_fast": {"scenic_weight": 0.1, "efficiency_weight": 0.6, "experience_weight": 0.3},
            "balanced": {"scenic_weight": 0.33, "efficiency_weight": 0.33, "experience_weight": 0.34}
        }
        
        # Attraction type multipliers
        self.attraction_multipliers = {
            "heritage": 1.2,      # UNESCO sites get bonus
            "waterfall": 1.1,     # Waterfalls are highly valued
            "mountain": 1.15,     # Mountains and viewpoints
            "beach": 1.05,        # Beaches
            "temple": 1.0,        # Temples
            "nature": 1.1,        # Nature spots
            "viewpoint": 1.15     # Viewpoints
        }
    
    def calculate_scenic_score(self, route: Dict) -> float:
        """Calculate scenic score based on attractions along route"""
        scenic_spots = route.get("scenic_spots", [])
        
        if not scenic_spots:
            return 0.0
        
        # Weight attractions by type and rating
        total_score = 0
        max_possible_score = 0
        
        for spot in scenic_spots:
            spot_type = spot.get("type", "nature")
            rating = spot.get("rating", 5.0)
            proximity_score = spot.get("proximity_score", 0)
            
            # Apply type multiplier
            multiplier = self.attraction_multipliers.get(spot_type, 1.0)
            
            # Calculate weighted score
            weighted_score = rating * multiplier * (proximity_score / 10.0)
            total_score += weighted_score
            max_possible_score += 10.0 * multiplier  # Max rating is 10
        
        # Normalize to 0-10 scale
        if max_possible_score > 0:
            normalized_score = (total_score / max_possible_score) * 10
        else:
            normalized_score = 0.0
        
        return min(normalized_score, 10.0)
    
    def calculate_efficiency_score(self, route: Dict) -> float:
        """Calculate efficiency score based on time, distance, and road quality"""
        distance = route.get("distance", 0)
        time = route.get("time", 0)
        route_type = route.get("type", "shortest")
        
        # Base score from time efficiency (lower time = higher score)
        if distance > 0:
            avg_speed = distance / time if time > 0 else 0
            
            # Ideal speed is 60-80 km/h for good balance
            if 60 <= avg_speed <= 80:
                speed_score = 10.0
            elif avg_speed < 60:
                speed_score = (avg_speed / 60) * 10.0
            else:
                speed_score = max(0, 10.0 - ((avg_speed - 80) / 20))
        else:
            speed_score = 5.0
        
        # Penalty for toll roads
        toll_penalty = 0
        segments = route.get("segments", [])
        for segment in segments:
            if segment.get("toll", False):
                toll_penalty += 0.5
        
        # Bonus for highway roads
        highway_bonus = 0
        for segment in segments:
            if segment.get("road_type") == "highway":
                highway_bonus += 0.3
        
        # Calculate final efficiency score
        efficiency_score = speed_score - toll_penalty + highway_bonus
        efficiency_score = max(0, min(efficiency_score, 10.0))
        
        return efficiency_score
    
    def calculate_experience_score(self, route: Dict) -> float:
        """Calculate experience score based on variety and uniqueness"""
        scenic_spots = route.get("scenic_spots", [])
        path = route.get("path", [])
        
        if not scenic_spots:
            return 3.0  # Base score for direct routes
        
        # Variety bonus - different types of attractions
        attraction_types = set()
        for spot in scenic_spots:
            attraction_types.add(spot.get("type", "nature"))
        
        variety_score = min(len(attraction_types) * 2, 6.0)  # Max 6 points for variety
        
        # Uniqueness bonus - less common attractions
        unique_attractions = 0
        for spot in scenic_spots:
            spot_type = spot.get("type", "nature")
            if spot_type in ["heritage", "waterfall", "mountain"]:
                unique_attractions += 1
        
        uniqueness_score = min(unique_attractions * 1.5, 4.0)  # Max 4 points for uniqueness
        
        # Path diversity bonus - more cities visited
        path_diversity = min(len(path) * 0.5, 2.0)  # Max 2 points for path diversity
        
        total_score = variety_score + uniqueness_score + path_diversity
        
        return min(total_score, 10.0)
    
    def calculate_detour_penalty(self, route: Dict, shortest_distance: float) -> float:
        """Calculate penalty for routes that are much longer than shortest"""
        route_distance = route.get("distance", 0)
        
        if shortest_distance <= 0:
            return 0.0
        
        detour_ratio = route_distance / shortest_distance
        
        # No penalty for routes up to 1.3x shortest distance
        if detour_ratio <= 1.3:
            return 0.0
        elif detour_ratio <= 1.5:
            return 1.0  # Small penalty
        elif detour_ratio <= 2.0:
            return 2.5  # Moderate penalty
        else:
            return 4.0  # High penalty
    
    def score_routes(self, routes: List[Dict], preferences: Dict = None) -> List[Dict]:
        """Score and rank multiple routes"""
        if not routes:
            return routes
        
        # Adjust weights based on preferences
        if preferences:
            if preferences.get("prefer_scenic"):
                weights = self.route_preferences["prefer_scenic"]
            elif preferences.get("avoid_tolls"):
                weights = self.route_preferences["prefer_fast"]  # Prioritize efficiency
            else:
                weights = self.route_preferences["balanced"]
        else:
            weights = self.route_preferences["balanced"]
        
        # Find shortest distance for detour calculations
        shortest_distance = min(route.get("distance", float('inf')) for route in routes)
        
        scored_routes = []
        
        for i, route in enumerate(routes):
            # Calculate individual scores
            scenic_score = self.calculate_scenic_score(route)
            efficiency_score = self.calculate_efficiency_score(route)
            experience_score = self.calculate_experience_score(route)
            
            # Calculate detour penalty
            detour_penalty = self.calculate_detour_penalty(route, shortest_distance)
            
            # Apply weights and calculate total score
            total_score = (
                scenic_score * weights["scenic_weight"] +
                efficiency_score * weights["efficiency_weight"] +
                experience_score * weights["experience_weight"] -
                detour_penalty
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                scenic_score, efficiency_score, experience_score, 
                detour_penalty, route, weights
            )
            
            # Update route with scores
            scored_route = route.copy()
            scored_route.update({
                "scenic_score": round(scenic_score, 1),
                "efficiency_score": round(efficiency_score, 1),
                "experience_score": round(experience_score, 1),
                "total_score": round(total_score, 1),
                "reasoning": reasoning,
                "rank": 0  # Will be set after sorting
            })
            
            scored_routes.append(scored_route)
        
        # Sort by total score (descending)
        scored_routes.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Assign ranks
        for i, route in enumerate(scored_routes):
            route["rank"] = i + 1
        
        return scored_routes
    
    def _generate_reasoning(self, scenic: float, efficiency: float, experience: float,
                           detour: float, route: Dict, weights: Dict) -> List[str]:
        """Generate human-readable reasoning for route score"""
        reasoning = []
        
        # Scenic reasoning
        if scenic >= 8.0:
            reasoning.append("🌟 Exceptional scenic attractions")
        elif scenic >= 6.0:
            reasoning.append("🏔️ Good scenic value")
        elif scenic >= 4.0:
            reasoning.append("🌄 Moderate scenic spots")
        else:
            reasoning.append("🛣️ Limited scenic attractions")
        
        # Efficiency reasoning
        if efficiency >= 8.0:
            reasoning.append("⚡ Very efficient route")
        elif efficiency >= 6.0:
            reasoning.append("⏱️ Good time efficiency")
        elif efficiency >= 4.0:
            reasoning.append("🐌 Moderate efficiency")
        else:
            reasoning.append("⏳ Less efficient route")
        
        # Experience reasoning
        if experience >= 8.0:
            reasoning.append("🎯 Rich travel experience")
        elif experience >= 6.0:
            reasoning.append("🗺️ Good variety of experiences")
        elif experience >= 4.0:
            reasoning.append("📍 Limited experiences")
        else:
            reasoning.append("🚗 Basic travel route")
        
        # Detour reasoning
        if detour >= 3.0:
            reasoning.append("⚠️ Significant detour from shortest path")
        elif detour >= 1.0:
            reasoning.append("📍 Moderate detour")
        
        return reasoning
    
    def get_route_recommendations(self, scored_routes: List[Dict]) -> Dict:
        """Generate detailed recommendations for the best routes"""
        if not scored_routes:
            return {"error": "No routes to analyze"}
        
        best_route = scored_routes[0]
        recommendations = {
            "recommended_route": best_route,
            "why_recommended": self._explain_recommendation(best_route),
            "alternatives": [],
            "tips": []
        }
        
        # Add alternative routes
        for i, route in enumerate(scored_routes[1:3], 2):  # Top 2 alternatives
            alt_reason = f"Rank #{i}: "
            if route["scenic_score"] > best_route["scenic_score"]:
                alt_reason += "More scenic "
            if route["efficiency_score"] > best_route["efficiency_score"]:
                alt_reason += "More efficient "
            if route["experience_score"] > best_route["experience_score"]:
                alt_reason += "Richer experience "
            
            recommendations["alternatives"].append({
                "route": route,
                "reason": alt_reason.strip()
            })
        
        # Add travel tips
        recommendations["tips"] = self._generate_travel_tips(best_route)
        
        return recommendations
    
    def _explain_recommendation(self, route: Dict) -> str:
        """Generate explanation for why this route is recommended"""
        scenic = route["scenic_score"]
        efficiency = route["efficiency_score"]
        experience = route["experience_score"]
        
        explanation = f"Recommended for its "
        
        if scenic >= 7.0 and efficiency >= 7.0:
            explanation += "excellent balance of scenic beauty and efficiency"
        elif scenic >= 8.0:
            explanation += "outstanding scenic attractions and experiences"
        elif efficiency >= 8.0:
            explanation += "optimal time and fuel efficiency"
        elif experience >= 8.0:
            explanation += "rich and diverse travel experiences"
        else:
            explanation += "good overall travel value"
        
        explanation += f" (Score: {route['total_score']}/10)"
        
        return explanation
    
    def _generate_travel_tips(self, route: Dict) -> List[str]:
        """Generate travel tips based on route characteristics"""
        tips = []
        
        scenic_spots = route.get("scenic_spots", [])
        path = route.get("path", [])
        
        # Tips based on scenic spots
        heritage_spots = [spot for spot in scenic_spots if spot.get("type") == "heritage"]
        if heritage_spots:
            tips.append("🏛️ Carry camera for heritage sites - early morning visits recommended")
        
        waterfalls = [spot for spot in scenic_spots if spot.get("type") == "waterfall"]
        if waterfalls:
            tips.append("💧 Best waterfall views during monsoon season (July-September)")
        
        beaches = [spot for spot in scenic_spots if spot.get("type") == "beach"]
        if beaches:
            tips.append("🏖️ Beach activities best during winter months (November-February)")
        
        # Tips based on route length
        distance = route.get("distance", 0)
        if distance > 600:
            tips.append("🌙 Plan overnight stay for long journeys")
        elif distance > 400:
            tips.append("⏰ Start early to avoid night driving")
        
        # General tips
        if len(path) > 4:
            tips.append("🗺️ Download offline maps for remote areas")
        
        tips.append("📱 Keep emergency contacts handy")
        tips.append("⛽ Check fuel status before entering ghat sections")
        
        return tips
    
    def generate_description(self, route: Dict, use_llm: bool = False) -> str:
        """Generate route description (with optional LLM enhancement)"""
        base_description = self._generate_base_description(route)
        
        if use_llm:
            # Placeholder for LLM integration (Ollama, etc.)
            # This would require additional setup
            return base_description + " [LLM enhancement available with local model]"
        
        return base_description
    
    def _generate_base_description(self, route: Dict) -> str:
        """Generate basic route description without LLM"""
        path = route.get("path", [])
        distance = route.get("distance", 0)
        time = route.get("time", 0)
        scenic_spots = route.get("scenic_spots", [])
        
        description = f"This route covers {distance} km in approximately {time:.1f} hours"
        
        if len(path) > 2:
            description += f", passing through {', '.join(path[1:-1])}"
        
        if scenic_spots:
            top_spots = scenic_spots[:3]
            spot_names = [spot["place"] for spot in top_spots]
            description += f". Key attractions include {', '.join(spot_names)}"
        
        description += f". Overall route score: {route.get('total_score', 0)}/10."
        
        return description
