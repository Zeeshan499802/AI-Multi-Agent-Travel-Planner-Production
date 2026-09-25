import asyncio
import json
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import interrupt

from config import get_llm
from mcp_client import *
from state import TravelState


llm = get_llm()


# ============================================================
# LLM HELPER
# ============================================================

def _llm_text(system: str, prompt: str) -> str:
    """
    Call the LLM and return only the text content.
    """

    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ]
    )

    return response.content


# ============================================================
# JSON PARSER
# ============================================================

def _json_from_llm(text: str) -> dict[str, Any]:
    """
    Extract JSON object from LLM response
    and convert it into a Python dictionary.
    """

    print("\n========== RAW LLM RESPONSE ==========")
    print(text)
    print("======================================\n")

    if not text:
        raise ValueError("LLM returned an empty response.")

    text = text.strip()

    # --------------------------------------------------------
    # Remove markdown code fences if LLM returns:
    #
    # ```json
    # {...}
    # ```
    # --------------------------------------------------------

    if text.startswith("```"):
        lines = text.splitlines()

        # Remove first line: ```json / ```
        lines = lines[1:]

        # Remove last ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # --------------------------------------------------------
    # Find JSON object
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"No valid JSON object found in LLM response:\n{text}"
        )

    json_text = text[start:end + 1]

    print("\n========== EXTRACTED JSON ==========")
    print(json_text)
    print("====================================\n")

    try:
        parsed = json.loads(json_text)

    except json.JSONDecodeError as e:
        print("\n========== JSON PARSE ERROR ==========")
        print(e)
        print("======================================\n")

        raise ValueError(
            f"LLM returned invalid JSON:\n{json_text}"
        ) from e

    if not isinstance(parsed, dict):
        raise ValueError(
            "Expected JSON object but received something else."
        )

    return parsed


# ============================================================
# SUPERVISOR AGENT
# ============================================================

def supervisor_agent(state: TravelState):

    query = state["user_query"]

    print("\n")
    print("================================================")
    print("             SUPERVISOR AGENT")
    print("================================================")
    print("User Query:")
    print(query)

    # ========================================================
    # INPUT GUARDRAIL
    # ========================================================

    guardrail_prompt = f"""
Determine whether the following request is a valid travel
planning request.

A valid travel request can include things such as:

- flights
- hotels
- destinations
- travel planning
- weather for a trip
- itinerary
- budget
- tourism
- vacation
- business travel
- transportation
- airports
- airlines
- accommodation

Return ONLY valid JSON.

Required format:

{{
    "allowed": true,
    "reason": ""
}}

User request:
{query}
"""

    guardrail_raw = _llm_text(
        "You are an input validation guardrail. Return strict JSON only.",
        guardrail_prompt,
    )

    guardrail_result = _json_from_llm(guardrail_raw)

    print("\n========== GUARDRAIL RESULT ==========")
    print(json.dumps(guardrail_result, indent=2))
    print("======================================\n")

    allowed = guardrail_result.get("allowed", False)

    # ========================================================
    # BLOCK INVALID REQUEST
    # ========================================================

    if not allowed:

        reason = guardrail_result.get(
            "reason",
            "Request rejected by input guardrail.",
        )

        return {
            "selected_agents": [],
            "trip_constraints": {},
            "supervisor_reasoning": reason,
            "final_response": reason,
            "messages": [
                AIMessage(
                    content=f"Guardrail blocked request: {reason}"
                )
            ],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    # ========================================================
    # SUPERVISOR ROUTING
    # ========================================================

    prompt = f"""
You are the supervisor of a real-world multi-agent travel
planning system.

Decide which specialist agents are needed for this user request.

Available agents:

- flight_agent:
  Use when flights, airports, airlines, routes, or airfare
  guidance are needed.

- hotel_agent:
  Use when hotels, accommodation, stays, or neighborhoods
  are needed.

- weather_agent:
  Use when weather, climate, season, packing, or forecast
  information is useful.

- budget_agent:
  Use when budget, affordability, cost, or price constraints
  are mentioned.

- itinerary_agent:
  Use almost always because the system must create the
  final travel plan.

Important:

If itinerary_agent is selected, select the specialist agents
needed to create a useful itinerary.

Return ONLY valid JSON.

Schema:

{{
    "selected_agents": [
        "flight_agent",
        "hotel_agent",
        "weather_agent",
        "budget_agent",
        "itinerary_agent"
    ],

    "trip_constraints": {{
        "destination": "",
        "origin": "",
        "duration": "",
        "budget": "",
        "travel_style": "",
        "special_preferences": []
    }},

    "reasoning": ""
}}

User request:
{query}
"""

    raw = _llm_text(
        "You route work to specialist agents. Return strict JSON only.",
        prompt,
    )

    parsed = _json_from_llm(raw)

    print("\n========== SUPERVISOR PARSED JSON ==========")
    print(json.dumps(parsed, indent=2))
    print("============================================\n")

    # ========================================================
    # SAFE EXTRACTION
    # ========================================================

    selected = parsed.get("selected_agents", [])

    trip_constraints = parsed.get(
        "trip_constraints",
        {},
    )

    reasoning = parsed.get(
        "reasoning",
        "",
    )

    # --------------------------------------------------------
    # Make sure itinerary agent is always included
    # --------------------------------------------------------

    if "itinerary_agent" not in selected:
        selected.append("itinerary_agent")

    # --------------------------------------------------------
    # Remove invalid agent names
    # --------------------------------------------------------

    valid_agents = {
        "flight_agent",
        "hotel_agent",
        "weather_agent",
        "budget_agent",
        "itinerary_agent",
    }

    selected = [
        agent
        for agent in selected
        if agent in valid_agents
    ]

    print("\n========== SELECTED AGENTS ==========")
    print(selected)
    print("=====================================\n")

    return {
        "selected_agents": selected,
        "trip_constraints": trip_constraints,
        "supervisor_reasoning": reasoning,
        "messages": [
            AIMessage(
                content="Supervisor created the agent plan."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 2,
    }


# ============================================================
# FLIGHT AGENT
# ============================================================

def flight_agent(state: TravelState):

    query = state["user_query"]

    constraints = state.get(
        "trip_constraints",
        {},
    )

    destination = constraints.get(
        "destination",
        "",
    )

    print("\n========== FLIGHT AGENT INPUT ==========")
    print("Query:", query)
    print("Constraints:", constraints)
    print("Destination:", destination)
    print("========================================\n")

    # ========================================================
    # MCP AIRPORT DATA
    # ========================================================

    airports = asyncio.run(
        list_airports(
            destination,
            limit=10,
        )
    )

    # ========================================================
    # MCP AIRLINE DATA
    # ========================================================

    airlines = asyncio.run(
        list_airlines(
            "",
            limit=10,
        )
    )

    print("\n========== AIRPORT MCP DATA ==========")
    print(airports)
    print("======================================\n")

    print("\n========== AIRLINE MCP DATA ==========")
    print(airlines)
    print("======================================\n")

    # ========================================================
    # LLM PROMPT
    # ========================================================

    prompt = f"""
Create flight guidance for this trip.

User request:
{query}

Trip constraints:
{constraints}

Airport MCP data:
{str(airports)[:3000]}

Airline MCP data:
{str(airlines)[:3000]}

Include:

1. Likely departure airport
2. Likely arrival airport
3. Relevant airlines
4. Estimated flight duration
5. Estimated fare range if available
6. Peak season warning
7. Booking advice

Important:

Do not invent exact flight schedules,
prices, or bookings if they are not present
in the provided MCP data.
"""

    result = _llm_text(
        "You are a flight planning specialist.",
        prompt,
    )

    print("\n========== FLIGHT AGENT OUTPUT ==========")
    print(result)
    print("=========================================\n")

    return {
        "flight_results": result,
        "messages": [
            AIMessage(
                content="Flight agent completed."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# HOTEL AGENT
# ============================================================

def hotel_agent(state: TravelState):

    query = (
        f"Best hotels and areas to stay for: "
        f"{state['user_query']}"
    )

    print("\n========== HOTEL AGENT INPUT ==========")
    print(query)
    print("=======================================\n")

    result = asyncio.run(
        tavily_search(query)
    )

    print("\n========== HOTEL SEARCH RESULT ==========")
    print(result)
    print("=========================================\n")

    return {
        "hotel_results": str(result),
        "messages": [
            AIMessage(
                content="Hotel agent completed."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# WEATHER AGENT
# ============================================================

def weather_agent(state: TravelState):

    constraints = state.get(
        "trip_constraints",
        {},
    )

    city = constraints.get(
        "destination",
        "",
    )

    print("\n========== WEATHER AGENT INPUT ==========")
    print("City:", city)
    print("=========================================\n")

    if not city:
        result = (
            "Weather information could not be retrieved "
            "because destination was not provided."
        )

        return {
            "weather_results": result,
            "messages": [
                AIMessage(
                    content="Weather agent completed."
                )
            ],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    # ========================================================
    # CURRENT WEATHER
    # ========================================================

    weather_data = asyncio.run(
        current_weather(city)
    )

    # ========================================================
    # FORECAST
    # ========================================================

    forecast_data = asyncio.run(
        forecast(city)
    )

    print("\n========== CURRENT WEATHER ==========")
    print(weather_data)
    print("=====================================\n")

    print("\n========== WEATHER FORECAST ==========")
    print(forecast_data)
    print("======================================\n")

    result = f"""
Current weather:
{weather_data}

Forecast:
{forecast_data}
"""

    print("\n========== WEATHER AGENT OUTPUT ==========")
    print(result)
    print("==========================================\n")

    return {
        "weather_results": result,
        "messages": [
            AIMessage(
                content="Weather agent completed."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# BUDGET AGENT
# ============================================================

def budget_agent(state: TravelState):

    print("\n========== BUDGET AGENT INPUT ==========")

    print("Trip Constraints:")
    print(state.get("trip_constraints"))

    print("\nFlight Results:")
    print(state.get("flight_results"))

    print("\nHotel Results:")
    print(state.get("hotel_results"))

    print("\nWeather Results:")
    print(state.get("weather_results"))

    print("=========================================\n")

    prompt = f"""
Analyze whether this trip plan is realistic for the user's
budget.

User request:
{state['user_query']}

Trip constraints:
{state.get('trip_constraints', {})}

Flight results:
{str(state.get('flight_results', ''))[:2500]}

Hotel results:
{str(state.get('hotel_results', ''))[:2500]}

Weather results:
{str(state.get('weather_results', ''))[:1500]}

Return a concise budget assessment containing:

1. Estimated cost categories
2. Risk areas
3. Money-saving suggestions
4. Whether the available information appears consistent
   with the user's stated budget

Important:

Do not invent exact prices.
Use ranges or qualitative statements when actual prices
are unavailable.
"""

    result = _llm_text(
        "You are a practical travel budget analyst.",
        prompt,
    )

    print("\n========== BUDGET AGENT OUTPUT ==========")
    print(result)
    print("=========================================\n")

    return {
        "budget_results": result,
        "messages": [
            AIMessage(
                content="Budget agent completed."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# ITINERARY AGENT
# ============================================================

def itinerary_agent(state: TravelState):

    print("\n========== ITINERARY AGENT INPUT ==========")

    print("Trip Constraints:")
    print(state.get("trip_constraints"))

    print("\nFlight Results:")
    print(state.get("flight_results"))

    print("\nHotel Results:")
    print(state.get("hotel_results"))

    print("\nWeather Results:")
    print(state.get("weather_results"))

    print("\nBudget Results:")
    print(state.get("budget_results"))

    print("===========================================\n")

    # ========================================================
    # LIMIT LARGE OUTPUTS
    # ========================================================

    flight_results = str(
        state.get("flight_results", "")
    )[:2500]

    hotel_results = str(
        state.get("hotel_results", "")
    )[:2000]

    weather_results = str(
        state.get("weather_results", "")
    )[:1500]

    budget_results = str(
        state.get("budget_results", "")
    )[:1500]

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
Create a clear draft travel itinerary.

User request:
{state['user_query']}

Trip constraints:
{state.get('trip_constraints', {})}

Flight information:
{flight_results}

Hotel information:
{hotel_results}

Weather information:
{weather_results}

Budget information:
{budget_results}

Create a practical itinerary with:

1. Destination overview
2. Day-by-day activities
3. Flight summary
4. Hotel/stay summary
5. Weather and packing advice
6. Budget considerations

Keep the response concise and practical.

Important:

- Do not invent exact prices.
- Do not invent confirmed bookings.
- Do not invent flight schedules.
- Clearly distinguish estimates from confirmed information.
- Make the output structured and ready for human review.
"""

    result = _llm_text(
        "You are an expert itinerary planner. Keep the response concise.",
        prompt,
    )

    print("\n========== ITINERARY OUTPUT ==========")
    print(result)
    print("======================================\n")

    # ========================================================
    # HUMAN APPROVAL REQUEST
    # ========================================================

    approval_request = f"""
Please review this draft travel plan.

{result}

Reply with approval or feedback.
"""

    return {
        "itinerary": result,
        "approval_request": approval_request,
        "messages": [
            AIMessage(
                content="Draft itinerary created for human review."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# ============================================================
# HUMAN APPROVAL
# ============================================================

def human_approval_agent(state: TravelState):

    feedback = interrupt(
        {
            "question": "Do you approve this itinerary?",
            "draft_itinerary": state.get(
                "itinerary",
                "",
            ),
            "approval_request": state.get(
                "approval_request",
                "",
            ),
            "expected_response": {
                "approved": True,
                "feedback": "Optional feedback for revision",
            },
        }
    )

    # ========================================================
    # SAFE FEEDBACK EXTRACTION
    # ========================================================

    if not isinstance(feedback, dict):
        feedback = {
            "approved": False,
            "feedback": str(feedback),
        }

    approved = bool(
        feedback.get(
            "approved",
            False,
        )
    )

    human_feedback = feedback.get(
        "feedback",
        "",
    )

    print("\n========== HUMAN APPROVAL ==========")
    print("Approved:", approved)
    print("Feedback:", human_feedback)
    print("====================================\n")

    return {
        "approved": approved,
        "human_feedback": human_feedback,
        "messages": [
            AIMessage(
                content="Human approval step completed."
            )
        ],
    }


# ============================================================
# FINAL RESPONSE AGENT
# ============================================================

def final_response_agent(state: TravelState):

    approved = state.get(
        "approved",
        False,
    )

    human_feedback = state.get(
        "human_feedback",
        "",
    )

    itinerary = state.get(
        "itinerary",
        "",
    )

    budget_results = state.get(
        "budget_results",
        "",
    )

    print("\n========== FINAL AGENT INPUT ==========")
    print("Approved:", approved)
    print("Feedback:", human_feedback)
    print("=======================================\n")

    # ========================================================
    # APPROVED
    # ========================================================

    if approved:

        prompt = f"""
The human approved this draft itinerary.

Produce the final polished travel plan.

Draft itinerary:
{itinerary}

Budget notes:
{budget_results}

Human feedback:
{human_feedback}

Keep the final response practical and concise.

Do not invent bookings, exact prices, or schedules.
"""

    # ========================================================
    # NOT APPROVED
    # ========================================================

    else:

        prompt = f"""
The human did not approve the draft itinerary.

Original user request:
{state['user_query']}

Draft itinerary:
{itinerary}

Human feedback:
{human_feedback}

Budget notes:
{budget_results}

Create a revised travel plan that addresses the human's
feedback.

Do not invent bookings, exact prices, or schedules.
"""

    result = _llm_text(
        "You produce final user-ready travel plans.",
        prompt,
    )

    print("\n========== FINAL RESPONSE ==========")
    print(result)
    print("====================================\n")

    return {
        "final_response": result,
        "messages": [
            AIMessage(
                content=result
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }