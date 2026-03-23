"""
Itinerary Generator - Creates day-wise travel plans with stop durations and timing
Generates complete itineraries with optimal scheduling
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass
class ItineraryDay:
    day_number: int
    date: str
    start_location: str
    end_location: str
    driving_distance: float
    driving_time: float
    activities: List[Dict]
    overnight_stay: str
    total_time: float


@dataclass
class Activity:
    type: str  # "drive", "sightseeing", "meal", "rest", "fuel"
    location: str
    start_time: str
    duration: str
    description: str
    priority: str  # "high", "medium", "low"


class ItineraryGenerator:
    def __init__(self):
        self.start_time = "08:00"  # Default start time
        self.end_time = "18:00"    # Default end time for driving
        self.lunch_time = "13:00"   # Default lunch time
        self.max_driving_hours = 8  # Maximum driving hours per day
        
        # Activity duration defaults (in hours)
        self.activity_durations = {
            "meal": 1.0,
            "rest": 0.5,
            "fuel": 0.25,
            "sightseeing": 2.0,
            "overnight": 12.0
        }
        
        # City accommodation suggestions
        self.accommodation_suggestions = {
            "bangalore": {
                "budget": ["Hotel Swagath", "The Park"],
                "mid_range": ["Vivanta by Taj", "ITC Gardenia"],
                "luxury": ["The Leela Palace", "Ritz Carlton"]
            },
            "goa": {
                "budget": ["Coco Shambhala", "La Calypso"],
                "mid_range": ["Taj Fort Aguada", "W Goa"],
                "luxury": ["The Leela Goa", "Grand Hyatt Goa"]
            },
            "chikmagalur": {
                "budget": ["Plantation Trails", "Coffee Estate Homestays"],
                "mid_range": ["The Gateway Hotel", "JLR River Tern"],
                "luxury": ["Amanvana Spa Resort", "Taj Madikeri"]
            },
            "coorg": {
                "budget": ["Coorg Cliffs", "Plantation Stay"],
                "mid_range": ["The Tamara", "Orange County"],
                "luxury": ["Evolve Back, Coorg", "Taj Madikeri"]
            },
            "mangalore": {
                "budget": ["Hotel Poonja", "Deepa Comforts"],
                "mid_range": ["The Ocean Pearl", "Goldfinch"],
                "luxury": ["Taj Gateway Hotel", "Radisson Blu"]
            },
            "udupi": {
                "budget": ["Hotel Udupi", "Paradise Isle"],
                "mid_range": ["Manipal County", "Kediyoor Hotel"],
                "luxury": ["Sharada International", "Daiwik Hotels"]
            },
            "hampi": {
                "budget": ["Hampi Boulders", "Mowgli Guest House"],
                "mid_range": ["Hyatt Place Hampi", "Clarks Inn"],
                "luxury": ["Evolve Back Hampi", "Heritage Resort Hampi"]
            },
            "mysore": {
                "budget": ["Hotel Regenta", "Royal Orchid"],
                "mid_range": ["Radisson Blu", "Lemon Tree"],
                "luxury": ["Lalitha Mahal Palace", "The Metropole"]
            }
        }
    
    def generate_itinerary(self, route: Dict, preferences: Dict = None) -> Dict:
        """Generate complete day-wise itinerary"""
        if preferences is None:
            preferences = {"budget": "mid_range", "pace": "moderate"}
        
        path = route.get("path", [])
        scenic_spots = route.get("scenic_spots", [])
        stops = route.get("stops", [])
        fuel_stops = route.get("fuel_stops", [])
        total_distance = route.get("distance", 0)
        total_time = route.get("time", 0)
        
        if not path or len(path) < 2:
            return {"error": "Invalid route for itinerary generation"}
        
        # Initialize itinerary
        itinerary = {
            "trip_overview": {
                "origin": path[0],
                "destination": path[-1],
                "total_distance": total_distance,
                "total_time": total_time,
                "estimated_days": self._estimate_days(total_time),
                "best_season": self._get_best_season(path, scenic_spots)
            },
            "days": [],
            "summary": {
                "total_sightseeing_spots": len(scenic_spots),
                "total_stops": len(stops) + len(fuel_stops),
                "overnight_stays": 0
            }
        }
        
        # Generate day-wise plan
        days = self._plan_days(path, scenic_spots, stops, fuel_stops, preferences)
        itinerary["days"] = days
        
        # Update summary
        itinerary["summary"]["overnight_stays"] = len([d for d in days if d.get("overnight_stay")])
        
        # Add packing tips
        itinerary["packing_tips"] = self._generate_packing_tips(path, scenic_spots)
        
        # Add budget estimate
        itinerary["budget_estimate"] = self._estimate_budget(days, preferences)
        
        return itinerary
    
    def _estimate_days(self, total_time: float) -> int:
        """Estimate number of days needed for the trip"""
        # Assume 6-8 hours of effective travel per day
        daily_travel_time = 7.0
        days_needed = math.ceil(total_time / daily_travel_time)
        return max(1, days_needed)

    def _parse_duration_hours(self, duration: str) -> float:
        """Parse simple hour strings, including ranges like '2-3 hours'."""
        token = duration.split()[0]
        if "-" in token:
            start, end = token.split("-", 1)
            return (float(start) + float(end)) / 2
        return float(token)
    
    def _get_best_season(self, path: List[str], scenic_spots: List[Dict]) -> str:
        """Determine best season to visit based on route"""
        # Check for monsoon-dependent attractions
        waterfalls = [spot for spot in scenic_spots if spot.get("type") == "waterfall"]
        beaches = [spot for spot in scenic_spots if spot.get("type") == "beach"]
        
        if waterfalls and beaches:
            return "October to March (pleasant weather, good for both waterfalls and beaches)"
        elif waterfalls:
            return "July to September (monsoon season for best waterfall views)"
        elif beaches:
            return "November to February (winter season for beach activities)"
        else:
            return "October to March (overall best travel season)"
    
    def _plan_days(self, path: List[str], scenic_spots: List[Dict], 
                   stops: List[Dict], fuel_stops: List[Dict], 
                   preferences: Dict) -> List[Dict]:
        """Plan day-wise activities"""
        days = []
        current_day = 1
        current_time = 8.0  # Start at 8 AM
        
        # Group scenic spots by city
        spots_by_city = {}
        for spot in scenic_spots:
            city = spot.get("city", "")
            if city not in spots_by_city:
                spots_by_city[city] = []
            spots_by_city[city].append(spot)
        
        # Plan each day
        for i in range(len(path) - 1):
            from_city = path[i]
            to_city = path[i + 1]
            
            # Get driving time between cities (simplified)
            driving_time = 2.0  # Default 2 hours between cities
            
            # Check if we need to start a new day
            if current_time + driving_time > 18.0:  # After 6 PM
                # End current day
                if days:
                    days[-1]["end_location"] = from_city
                    days[-1]["total_time"] = current_time - 8.0
                
                # Start new day
                current_day += 1
                current_time = 8.0
            
            # Create or update current day
            if not days or len(days) < current_day:
                day_plan = {
                    "day": f"Day {current_day}",
                    "activities": [],
                    "start_location": from_city,
                    "driving_distance": 0,
                    "driving_time": 0
                }
                days.append(day_plan)
            
            current_day_plan = days[-1]
            
            # Add driving activity
            current_day_plan["activities"].append({
                "time": f"{int(current_time):02d}:00",
                "activity": f"Drive from {from_city} to {to_city}",
                "duration": f"{int(driving_time)} hours",
                "type": "drive"
            })
            
            current_time += driving_time
            current_day_plan["driving_distance"] += 150  # Estimated distance
            current_day_plan["driving_time"] += driving_time
            
            # Add scenic spots in current city
            if to_city in spots_by_city:
                for spot in spots_by_city[to_city][:2]:  # Max 2 spots per city
                    visit_duration = spot.get("visit_duration", "2 hours")
                    
                    current_day_plan["activities"].append({
                        "time": f"{int(current_time):02d}:00",
                        "activity": f"Visit {spot['place']}",
                        "duration": visit_duration,
                        "type": "sightseeing",
                        "description": spot.get("description", "")
                    })
                    
                    # Parse duration (simplified)
                    if "hour" in visit_duration:
                        hours = self._parse_duration_hours(visit_duration)
                    else:
                        hours = 2.0
                    
                    current_time += hours
            
            # Add meal break if it's lunch time
            if 13 <= current_time <= 14:
                current_day_plan["activities"].append({
                    "time": f"{int(current_time):02d}:00",
                    "activity": "Lunch break",
                    "duration": "1 hour",
                    "type": "meal",
                    "location": to_city
                })
                current_time += 1
            
            # Add rest stop if needed
            if current_time > 16:  # After 4 PM
                current_day_plan["activities"].append({
                    "time": f"{int(current_time):02d}:00",
                    "activity": "Rest break",
                    "duration": "30 minutes",
                    "type": "rest",
                    "location": to_city
                })
                current_time += 0.5
        
        # Set overnight stays
        for i, day in enumerate(days):
            if i < len(days) - 1:
                # Find next day's start location
                next_day_start = days[i + 1]["start_location"]
                day["overnight_stay"] = next_day_start
            else:
                day["overnight_stay"] = path[-1]  # Final destination
            
            # Add accommodation suggestions
            if day["overnight_stay"] in self.accommodation_suggestions:
                budget = preferences.get("budget", "mid_range")
                suggestions = self.accommodation_suggestions[day["overnight_stay"]].get(budget, [])
                day["accommodation_suggestions"] = suggestions[:2]  # Top 2 suggestions
        
        return days
    
    def _generate_packing_tips(self, path: List[str], scenic_spots: List[Dict]) -> List[str]:
        """Generate packing tips based on route and attractions"""
        tips = []

        mountain_cities = ["chikmagalur", "coorg", "agumbe", "shimoga"]
        if any(city in path for city in mountain_cities):
            tips.append("Light jackets for hill stations (evenings can be cool)")
            tips.append("Comfortable walking shoes for trekking")

        beach_cities = ["goa", "mangalore", "udupi", "gokarna", "murudeshwar"]
        if any(city in path for city in beach_cities):
            tips.append("Swimwear and beach essentials")
            tips.append("Sunscreen and sunglasses")

        heritage_spots = [spot for spot in scenic_spots if spot.get("type") == "heritage"]
        if heritage_spots:
            tips.append("Camera with extra batteries for heritage sites")
            tips.append("Comfortable shoes for walking through ruins")

        waterfall_spots = [spot for spot in scenic_spots if spot.get("type") == "waterfall"]
        if waterfall_spots:
            tips.append("Raincoat or umbrella (especially during monsoon)")
            tips.append("Anti-slip footwear for waterfall areas")

        tips.append("Basic first-aid kit and personal medications")
        tips.append("Power bank and car charger")
        tips.append("Offline maps downloaded")
        tips.append("Cash for rural areas with limited ATMs")
        tips.append("Hand sanitizer and wet wipes")

        return tips
    
    def _estimate_budget(self, days: List[Dict], preferences: Dict) -> Dict:
        """Estimate trip budget"""
        budget_level = preferences.get("budget", "mid_range")
        
        # Daily cost estimates (per person)
        daily_costs = {
            "budget": {"accommodation": 800, "food": 600, "fuel": 400, "activities": 300},
            "mid_range": {"accommodation": 2000, "food": 1000, "fuel": 400, "activities": 500},
            "luxury": {"accommodation": 5000, "food": 2000, "fuel": 600, "activities": 1000}
        }
        
        costs = daily_costs.get(budget_level, daily_costs["mid_range"])
        
        # Calculate totals
        num_days = len(days)
        total_accommodation = costs["accommodation"] * (num_days - 1)  # No accommodation on last day
        total_food = costs["food"] * num_days
        total_fuel = costs["fuel"] * num_days
        total_activities = costs["activities"] * num_days
        
        total_budget = total_accommodation + total_food + total_fuel + total_activities
        
        return {
            "per_person": {
                "accommodation": total_accommodation,
                "food": total_food,
                "fuel": total_fuel,
                "activities": total_activities,
                "total": total_budget
            },
            "group_estimate": {
                "2_people": total_budget * 2,
                "4_people": total_budget * 4
            },
            "budget_level": budget_level,
            "notes": "Estimates are per person, excluding shopping and emergencies"
        }
    
    def format_itinerary(self, itinerary: Dict) -> str:
        """Format itinerary for display"""
        if "error" in itinerary:
            return f"❌ Error: {itinerary['error']}"
        
        formatted = ""
        
        # Trip overview
        overview = itinerary["trip_overview"]
        formatted += f"🗺️  TRIP OVERVIEW\n"
        formatted += f"Route: {overview['origin']} → {overview['destination']}\n"
        formatted += f"Distance: {overview['total_distance']} km\n"
        formatted += f"Duration: {overview['total_time']:.1f} hours ({overview['estimated_days']} days)\n"
        formatted += f"Best Season: {overview['best_season']}\n\n"
        
        # Day-wise plan
        for day in itinerary["days"]:
            formatted += f"📅 {day['day']}\n"
            formatted += f"Route: {day['start_location']} → {day.get('overnight_stay', day['start_location'])}\n"
            formatted += f"Driving: {day['driving_distance']:.0f} km, {day['driving_time']:.1f} hours\n\n"
            
            for activity in day["activities"]:
                formatted += f"  {activity['time']} - {activity['activity']}"
                if activity.get("duration"):
                    formatted += f" ({activity['duration']})"
                formatted += "\n"
                
                if activity.get("description"):
                    formatted += f"    📝 {activity['description']}\n"
            
            if day.get("accommodation_suggestions"):
                formatted += f"\n  🏨 Stay Options: {', '.join(day['accommodation_suggestions'])}\n"
            
            formatted += "\n"
        
        # Summary
        summary = itinerary["summary"]
        formatted += f"📊 TRIP SUMMARY\n"
        formatted += f"Sightseeing Spots: {summary['total_sightseeing_spots']}\n"
        formatted += f"Total Stops: {summary['total_stops']}\n"
        formatted += f"Overnight Stays: {summary['overnight_stays']}\n\n"
        
        # Budget estimate
        if "budget_estimate" in itinerary:
            budget = itinerary["budget_estimate"]
            formatted += f"💰 BUDGET ESTIMATE ({budget['budget_level'].title()})\n"
            formatted += f"Per Person: ₹{budget['per_person']['total']:,}\n"
            formatted += f"  - Accommodation: ₹{budget['per_person']['accommodation']:,}\n"
            formatted += f"  - Food: ₹{budget['per_person']['food']:,}\n"
            formatted += f"  - Fuel: ₹{budget['per_person']['fuel']:,}\n"
            formatted += f"  - Activities: ₹{budget['per_person']['activities']:,}\n\n"
        
        # Packing tips
        if "packing_tips" in itinerary:
            formatted += "🎒 PACKING TIPS\n"
            for tip in itinerary["packing_tips"]:
                formatted += f"  {tip}\n"
        
        return formatted

