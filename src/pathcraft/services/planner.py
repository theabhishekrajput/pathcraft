#!/usr/bin/env python3
"""Application service that coordinates the PathCraft planning pipeline."""

from __future__ import annotations

from typing import Any, Dict, Optional

from engines.fuel_engine import FuelEngine
from engines.route_engine import RouteEngine
from engines.scenic_engine import ScenicEngine
from engines.stop_planner import StopPlanner
from services.itinerary import ItineraryGenerator
from services.recommender import RecommendationEngine


class TravelPlanner:
    def __init__(self) -> None:
        self.route_engine = RouteEngine()
        self.scenic_engine = ScenicEngine()
        self.stop_planner = StopPlanner()
        self.fuel_engine = FuelEngine()
        self.recommender = RecommendationEngine()
        self.itinerary_generator = ItineraryGenerator()

    def plan_trip(
        self,
        origin: str,
        destination: str,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run the full planning pipeline for a trip."""
        print(f"Planning trip: {origin} -> {destination}")

        routes = self.route_engine.generate_routes(origin, destination)
        if not routes:
            return {"error": f"No routes found from {origin} to {destination}"}

        for route in routes:
            route["scenic_spots"] = self.scenic_engine.find_scenic_spots(route["path"])

        scored_routes = self.recommender.score_routes(routes, preferences)
        best_route = scored_routes[0]
        best_route["stops"] = self.stop_planner.plan_stops(best_route)
        best_route["fuel_stops"] = self.fuel_engine.plan_fuel_stops(best_route)
        itinerary = self.itinerary_generator.generate_itinerary(best_route)

        return {
            "origin": origin,
            "destination": destination,
            "routes": scored_routes,
            "recommended_route": best_route,
            "itinerary": itinerary,
        }

    def display_results(self, results: Dict[str, Any]) -> None:
        """Render planning results for CLI usage."""
        if "error" in results:
            print(f"Error: {results['error']}")
            return

        print("\n" + "=" * 60)
        print("PATHCRAFT RESULTS")
        print("=" * 60)

        print(f"\nRoute: {results['origin']} -> {results['destination']}")
        print(f"Total Distance: {results['recommended_route']['distance']} km")
        print(f"Estimated Time: {results['recommended_route']['time']} hours")
        print(f"Scenic Score: {results['recommended_route']['scenic_score']}/10")

        print("\nRECOMMENDED ROUTE HIGHLIGHTS:")
        for index, spot in enumerate(results["recommended_route"]["scenic_spots"][:5], 1):
            print(f"  {index}. {spot['place']} (Score: {spot['score']}/10)")

        print("\nFUEL STOPS:")
        for stop in results["recommended_route"]["fuel_stops"]:
            print(f"  - {stop['location']} (After {stop['distance']} km)")

        print("\nREST STOPS:")
        for stop in results["recommended_route"]["stops"]:
            print(f"  - {stop['location']} ({stop['type']})")

        print("\nDETAILED ITINERARY:")
        for day in results["itinerary"]["days"]:
            print(f"\n  {day['day']}:")
            for activity in day["activities"]:
                time_label = activity.get("time", "TBD")
                activity_label = activity.get("activity", "Activity")
                duration = activity.get("duration")
                if duration:
                    print(f"    - {time_label}: {activity_label} ({duration})")
                else:
                    print(f"    - {time_label}: {activity_label}")
