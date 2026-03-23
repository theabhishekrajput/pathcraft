"""LangChain-powered conversational layer for PathCraft."""

from __future__ import annotations

import re
from typing import Dict, Iterable, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from config import LLMSettings
from services.planner import TravelPlanner


class TravelChatAssistant:
    def __init__(self, settings: Optional[LLMSettings] = None) -> None:
        self.settings = settings or LLMSettings.from_env()
        self.planner = TravelPlanner()
        self.llm = ChatOpenAI(
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
            model=self.settings.model,
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_tokens,
            streaming=True,
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are PathCraft, a travel planning assistant for a route-planning application. "
                    "Use planner context when it is provided and do not invent distances, "
                    "routes, stops, or attractions that are not in the context. "
                    "If no route is available yet, ask the user for an origin and destination "
                    "in the format 'Origin to Destination'. Keep answers practical and concise.",
                ),
                MessagesPlaceholder("history"),
                (
                    "human",
                    "User request:\n{user_message}\n\n"
                    "Planner context:\n{planner_context}\n\n"
                    "Respond with a helpful travel-planning answer.",
                ),
            ]
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    async def answer(
        self,
        user_message: str,
        history: Optional[Iterable[BaseMessage]] = None,
        prior_results: Optional[Dict] = None,
    ) -> tuple[Dict | None, str]:
        plan_results = self._resolve_plan(user_message, prior_results)
        planner_context = self._build_planner_context(plan_results, prior_results)
        response = await self.chain.ainvoke(
            {
                "history": list(history or []),
                "user_message": user_message,
                "planner_context": planner_context,
            }
        )
        return plan_results, response

    async def stream_answer(
        self,
        user_message: str,
        history: Optional[Iterable[BaseMessage]] = None,
        prior_results: Optional[Dict] = None,
    ):
        plan_results = self._resolve_plan(user_message, prior_results)
        planner_context = self._build_planner_context(plan_results, prior_results)
        stream = self.chain.astream(
            {
                "history": list(history or []),
                "user_message": user_message,
                "planner_context": planner_context,
            }
        )
        return plan_results, stream

    def _resolve_plan(self, user_message: str, prior_results: Optional[Dict]) -> Optional[Dict]:
        route = self._extract_route(user_message)
        preferences = self._extract_preferences(user_message)

        if route:
            origin, destination = route
            return self.planner.plan_trip(origin, destination, preferences)

        if prior_results and preferences:
            return self.planner.plan_trip(
                prior_results["origin"],
                prior_results["destination"],
                preferences,
            )

        return None

    def _extract_route(self, user_message: str) -> Optional[tuple[str, str]]:
        match = re.search(
            r"(?P<origin>[A-Za-z ]+?)\s+to\s+(?P<destination>[A-Za-z ]+)",
            user_message.strip(),
            flags=re.IGNORECASE,
        )
        if not match:
            return None

        origin = self._normalize_origin(match.group("origin"))
        destination = self._normalize_destination(match.group("destination"))
        if not origin or not destination:
            return None

        return origin, destination

    def _normalize_origin(self, value: str) -> str:
        cleaned = value.strip().lower()
        cleaned = re.sub(
            r"^(plan|show|show me|create|build|find|suggest|route|trip|travel|itinerary)\s+",
            "",
            cleaned,
        )
        if " from " in cleaned:
            cleaned = cleaned.rsplit(" from ", 1)[-1]
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def _normalize_destination(self, value: str) -> str:
        cleaned = value.strip().lower()
        cleaned = re.split(r"\b(?:with|prefer|avoiding|avoid|and|for|using)\b", cleaned, maxsplit=1)[0]
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def _extract_preferences(self, user_message: str) -> Dict[str, bool]:
        lowered = user_message.lower()
        return {
            "prefer_scenic": any(
                token in lowered for token in ["scenic", "beautiful route", "more views"]
            ),
            "avoid_tolls": "avoid toll" in lowered or "no toll" in lowered,
        }

    def _build_planner_context(
        self, plan_results: Optional[Dict], prior_results: Optional[Dict]
    ) -> str:
        results = plan_results or prior_results
        if not results:
            return (
                "No planner route is loaded yet. Ask the user for a route like "
                "'Bangalore to Goa' and optional preferences like scenic or avoid tolls."
            )

        if "error" in results:
            return f"Planner error: {results['error']}"

        recommended = results["recommended_route"]
        highlights = ", ".join(
            spot["place"] for spot in recommended.get("scenic_spots", [])[:5]
        ) or "None"
        stops = ", ".join(
            f"{stop['location']} ({stop['type']})"
            for stop in recommended.get("stops", [])[:4]
        ) or "None"
        fuel_stops = ", ".join(
            stop["location"] for stop in recommended.get("fuel_stops", [])[:4]
        ) or "None"
        itinerary_lines = []
        for day in results.get("itinerary", {}).get("days", [])[:2]:
            items = "; ".join(
                activity.get("activity", "") for activity in day.get("activities", [])[:4]
            )
            itinerary_lines.append(f"{day['day']}: {items}")

        return (
            f"Origin: {results['origin']}\n"
            f"Destination: {results['destination']}\n"
            f"Recommended route type: {recommended.get('type', 'unknown')}\n"
            f"Distance: {recommended.get('distance', 0)} km\n"
            f"Travel time: {recommended.get('time', 0)} hours\n"
            f"Scenic score: {recommended.get('scenic_score', 0)}/10\n"
            f"Route path: {' -> '.join(recommended.get('path', []))}\n"
            f"Highlights: {highlights}\n"
            f"Rest stops: {stops}\n"
            f"Fuel stops: {fuel_stops}\n"
            f"Itinerary snapshot: {' | '.join(itinerary_lines) or 'None'}"
        )


def append_history(history: list[BaseMessage], user_message: str, ai_message: str) -> list[BaseMessage]:
    history.append(HumanMessage(content=user_message))
    history.append(AIMessage(content=ai_message))
    return history
