"""Chainlit UI for the PathCraft assistant."""

from __future__ import annotations

import chainlit as cl
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory


load_dotenv("...env")

from services.chat_assistant import TravelChatAssistant, append_history


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("history", [])
    cl.user_session.set("plan_results", None)
    try:
        assistant = TravelChatAssistant()
    except ValueError as exc:
        cl.user_session.set("assistant", None)
        await cl.Message(content=str(exc)).send()
        return

    cl.user_session.set("assistant", assistant)

    await cl.Message(
        content=(
            "🗺️ **Welcome to PathCraft - Your Intelligent Travel Planner!**\n\n"
            "I can help you plan amazing trips with scenic routes, hidden gems, and optimized itineraries.\n\n"
            "**Try these examples:**\n"
            "• `Plan a trip from Bangalore to Goa`\n"
            "• `Bangalore to Goa, prefer scenic route`\n"
            "• `Chikmagalur to Hampi with heritage sites`\n"
            "• `Mysore to Coorg, avoid tolls`\n\n"
            "**What I can do:**\n"
            "🌟 Find scenic spots and hidden gems\n"
            "⚡ Optimize routes for experience + efficiency\n"
            "🛏️ Plan fuel stops and overnight stays\n"
            "📅 Generate complete day-wise itineraries\n\n"
            "**Ready to explore? Tell me about your trip!** 🚗✨"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    assistant = cl.user_session.get("assistant")
    if assistant is None:
        await cl.Message(
            content="LLM is not configured. Set OPENCHATAI_API_KEY and restart Chainlit."
        ).send()
        return

    history = cl.user_session.get("history") or []
    prior_results = cl.user_session.get("plan_results")

    outgoing = cl.Message(content="")
    await outgoing.send()

    plan_results, stream = await assistant.stream_answer(
        user_message=message.content,
        history=history,
        prior_results=prior_results,
    )

    chunks: list[str] = []
    async for chunk in stream:
        chunks.append(chunk)
        await outgoing.stream_token(chunk)

    outgoing.content = "".join(chunks)
    await outgoing.update()

    updated_history = append_history(history, message.content, outgoing.content)
    cl.user_session.set("history", updated_history)
    cl.user_session.set("plan_results", plan_results or prior_results)

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

@cl.on_chat_resume
async def on_chat_resume(thread):
    memory = InMemoryChatMessageHistory()
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.add_user_message(message["content"])
        else:
            memory.add_ai_message(message["content"])

    cl.user_session.set("memory", memory)
