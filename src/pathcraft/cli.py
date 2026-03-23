#!/usr/bin/env python3
"""CLI entry point for the PathCraft package."""

from __future__ import annotations

import argparse
import json
import sys

from .services.planner import TravelPlanner


def main() -> None:
    parser = argparse.ArgumentParser(description="PathCraft")
    parser.add_argument("route", help="Route in format 'Origin to Destination'")
    parser.add_argument("--prefer-scenic", action="store_true", help="Prefer scenic routes")
    parser.add_argument("--avoid-tolls", action="store_true", help="Avoid toll roads")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        parts = args.route.lower().split(" to ")
        if len(parts) != 2:
            raise ValueError("Route must be in format 'Origin to Destination'")
        origin, destination = parts[0].strip(), parts[1].strip()
    except Exception as exc:
        print(f"Error parsing route: {exc}")
        sys.exit(1)

    preferences = {
        "prefer_scenic": args.prefer_scenic,
        "avoid_tolls": args.avoid_tolls,
    }

    planner = TravelPlanner()
    results = planner.plan_trip(origin, destination, preferences)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        planner.display_results(results)


if __name__ == "__main__":
    main()
