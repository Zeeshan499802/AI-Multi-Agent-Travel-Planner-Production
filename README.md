# ✈️ AI Travel Planner — Multi-Agent Travel Intelligence System

> An AI-powered multi-agent travel planning system built with **LangGraph, LangChain, Groq LLaMA 3.3 70B, MCP tools, Tavily Search, AviationStack, Weather APIs, PostgreSQL, and Streamlit**.

The system turns a natural-language travel request into a structured travel plan by routing the request through specialized AI agents for **flights, hotels, weather, budget, and itinerary planning**, followed by a **human approval step** and a final polished response.

---

## 📌 Project Overview

Planning a trip usually requires collecting information from several different sources:

- Flights and airports
- Airlines and routes
- Hotels and accommodation areas
- Weather and forecast information
- Budget considerations
- Daily activities and itinerary planning

Instead of handling all of these tasks with one large prompt, this project uses a **multi-agent architecture**.

A supervisor agent first understands the user's request and decides which specialist agents are required. Each specialist performs its own task using external tools or search. Their results are then combined by the itinerary agent into a draft plan.

Before the final response is generated, the system pauses for **Human-in-the-Loop approval**, allowing the user to approve the itinerary or provide feedback for revision.

---

## ✨ Key Features

### 🤖 Multi-Agent Architecture

The application separates travel planning into specialized agents:

| Agent | Responsibility |
|---|---|
| 🧠 Supervisor Agent | Validates the request and routes work to specialist agents |
| ✈️ Flight Agent | Airport, airline and flight-planning guidance |
| 🏨 Hotel Agent | Hotel and area/stay research |
| 🌤️ Weather Agent | Current weather and forecast information |
| 💰 Budget Agent | Cost analysis, risks and money-saving suggestions |
| 🗓️ Itinerary Agent | Creates the complete draft travel itinerary |
| 🤝 Human Approval | Allows the user to approve or request changes |
| ✨ Final Response Agent | Produces the final user-ready travel plan |

---

## 🛡️ Input Guardrail

The system includes an input validation layer before agent routing.

The supervisor checks whether the user's request is actually related to travel planning, such as:

- Flights
- Hotels
- Destinations
- Tourism
- Vacation
- Business travel
- Transportation
- Airports
- Airlines
- Weather for a trip
- Itinerary planning
- Travel budget

Invalid or unrelated requests can be blocked before specialist agents are executed.

---

## 🧠 How the System Works

```text
                         ┌──────────────────────┐
                         │      User Request    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Supervisor Agent  │
                         │ + Input Guardrail   │
                         └──────────┬───────────┘
                                    │
                         Select Required Agents
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
      │Flight Agent │       │ Hotel Agent │       │Weather Agent│
      └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
             │                     │                     │
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                                   ▼
                            ┌─────────────┐
                            │Budget Agent │
                            └──────┬──────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │  Itinerary Agent  │
                         │  Draft Generation  │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │  Human Approval   │
                         └─────────┬──────────┘
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                      Approved            Revision
                         │                   │
                         └─────────┬─────────┘
                                   ▼
                       ┌──────────────────────┐
                       │ Final Response Agent│
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │  Final Travel Plan  │
                       └──────────────────────┘
```

> The exact execution path depends on the agents selected by the supervisor for the user's request.

---

# 🏗️ Architecture

The application follows a **state-driven multi-agent workflow**.

A shared `TravelState` carries information between agents, including data such as:

```text
user_query
trip_constraints
selected_agents
supervisor_reasoning
flight_results
hotel_results
weather_results
budget_results
itinerary
approval_request
approved
human_feedback
final_response
llm_calls
messages
```

This allows each agent to focus on one responsibility while still contributing to the overall travel plan.

---

## 🔄 Agent Workflow

### 1. User Request

The user enters a natural-language request such as:

```text
Plan a 7-day Japan trip under Rs. 2 lakh.
I prefer budget hotels and no overnight flights.
```

The Streamlit frontend sends the request into the LangGraph application.

---

### 2. Supervisor Agent

The supervisor performs two major tasks.

#### Input validation

It first checks whether the request is travel-related.

#### Agent routing

It extracts trip constraints such as:

```json
{
  "destination": "",
  "origin": "",
  "duration": "",
  "budget": "",
  "travel_style": "",
  "special_preferences": []
}
```

It then selects the specialist agents required for the request.

The system also ensures that the `itinerary_agent` is included so that a complete travel plan can be generated.

---

### 3. Flight Agent ✈️

The flight agent retrieves airport and airline information through MCP tools.

It can use information such as:

- Departure airport
- Arrival airport
- Relevant airlines
- Estimated duration
- Fare range when available
- Peak-season warnings
- Booking guidance

The agent is explicitly instructed not to invent exact flight schedules, prices, or confirmed bookings when that information is unavailable.

---

### 4. Hotel Agent 🏨

The hotel agent creates a hotel/stay research query from the user's request and sends it to the search layer.

It focuses on:

- Recommended areas
- Accommodation options
- Hotel research
- Neighborhood/stay considerations

Search results are passed into the shared travel state.

---

### 5. Weather Agent 🌤️

The weather agent uses the destination extracted by the supervisor and retrieves:

- Current weather
- Forecast information

This information can later be used for:

- Activity planning
- Seasonal considerations
- Packing advice

---

### 6. Budget Agent 💰

The budget agent analyzes the available travel information against the user's stated budget.

It considers:

1. Estimated cost categories
2. Risk areas
3. Money-saving suggestions
4. Whether the available information appears consistent with the user's budget

When exact prices are unavailable, the system is instructed to use ranges or qualitative guidance rather than inventing prices.

---

### 7. Itinerary Agent 🗓️

The itinerary agent combines information from the other agents.

The draft itinerary can contain:

- Destination overview
- Day-by-day activities
- Flight summary
- Hotel/stay summary
- Weather and packing advice
- Budget considerations

The agent is instructed to distinguish estimates from confirmed information and not invent:

- Exact prices
- Confirmed bookings
- Flight schedules

---

# 🤝 Human-in-the-Loop

One of the main features of this project is **Human-in-the-Loop workflow execution**.

After the itinerary draft is generated, the system pauses and asks the user:

```text
Do you approve this itinerary?
```

The user can choose:

### ✅ Approve

The approved itinerary is sent to the final response agent.

### 🔄 Request Revision

The user can provide feedback such as:

```text
Replace the hotel with a cheaper option
and reduce the number of activities on Day 3.
```

The final response agent then creates a revised plan using the feedback.

This workflow is implemented using LangGraph's interrupt/resume capability.

---

# ✨ Final Response Agent

The final response agent produces the user-ready travel plan.

If the itinerary is approved:

```text
Draft → Final polished travel plan
```

If the itinerary is rejected:

```text
Draft + Human feedback → Revised travel plan
```

The final agent is also instructed not to invent bookings, exact prices, or schedules.

---

# 🧰 Technology Stack

## AI / Agent Framework

- **Python**
- **LangGraph**
- **LangChain Core**
- **Groq**
- **LLaMA 3.3 70B**

## External Tools / Data

- **MCP (Model Context Protocol)**
- **Tavily Search**
- **AviationStack**
- **Weather API / weather MCP tools**

## State / Persistence

- **PostgreSQL**
- **LangGraph checkpointing / thread-based state**

## Frontend

- **Streamlit**
- Custom responsive UI
- Session/thread management
- Human approval interface

---

# 🎨 Frontend

The Streamlit interface provides a modern travel-planning dashboard.

The UI includes:

- Dark responsive design
- Travel request input
- User ID
- Thread ID
- New Thread functionality
- Agent pipeline display
- Supervisor reasoning
- Selected agents
- Flight results
- Hotel results
- Weather results
- Budget analysis
- Draft itinerary
- Human approval controls
- Final travel plan

The frontend uses a persistent `thread_id` so the LangGraph workflow can continue from the human approval step.

---

# 🔌 MCP Integration

The project uses MCP-based tools to separate external data access from the agent logic.

The flight workflow uses MCP functionality for airport and airline data.

Weather information is also retrieved through tool functions exposed by the MCP layer.

This approach makes the system easier to extend because additional tools can be connected without rewriting the core agent architecture.

---

# 🔍 Search Integration

The Hotel Agent uses Tavily-powered search to research accommodation and areas to stay.

The general flow is:

```text
User Request
     ↓
Hotel Agent
     ↓
Search Query
     ↓
Tavily
     ↓
Search Results
     ↓
Travel State
     ↓
Itinerary Agent
```

---

# 🗃️ Thread & State Management

Each user session receives a unique thread identifier.

Example:

```text
demo_user_a81f2c91
```

The frontend creates a thread using the user's ID and a generated UUID fragment.

The same thread configuration is reused when the user submits approval or revision feedback.

This allows the LangGraph workflow to resume instead of starting the travel-planning process again.

---

# 📁 Suggested Project Structure

```text
AI-Travel-Planner/
│
├── frontend.py              # Streamlit frontend
├── graph.py                 # LangGraph workflow / graph definition
├── agents.py                # Supervisor and specialist agents
├── state.py                 # TravelState definition
├── config.py                # LLM configuration
├── mcp_client.py            # MCP client and external tools
│
├── .env                     # API keys and database configuration
├── .gitignore
├── requirements.txt
├── README.md
│
└── assets/                  # Optional project assets
```

> File names can be adjusted to match the final repository structure.

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

---

## 3. Install Dependencies

If a `requirements.txt` file is included:

```bash
pip install -r requirements.txt
```

If dependencies are managed differently in your repository, use the project's dependency manager instead.

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_groq_api_key

TAVILY_API_KEY=your_tavily_api_key

AVIATION_STACK_API_KEY=your_aviationstack_api_key

WHEATER_API_KEY=your_weather_api_key

DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### Important

Never commit your real API keys or database passwords to GitHub.

Add `.env` to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# 🗄️ PostgreSQL

The application is designed to use PostgreSQL for persistent workflow/checkpoint state.

Make sure PostgreSQL is running and create a database for the project.

Example:

```text
Database:
travel_planner
```

Then configure the connection string in `.env`.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/travel_planner
```

> Make sure special characters in database passwords are correctly URL-encoded when required by the connection string format.

---

# ▶️ Run the Application

Start the Streamlit frontend:

```bash
streamlit run frontend.py
```

The application will open in your browser.

Typical local URL:

```text
http://localhost:8501
```

---

# 🧪 Example Requests

### Example 1 — Complete Trip

```text
Plan a 7-day trip to Japan from Islamabad under Rs. 250,000.
I prefer budget hotels and want a practical itinerary.
```

### Example 2 — Weather + Itinerary

```text
I am planning a 5-day trip to Dubai.
Tell me about the weather and create an itinerary.
```

### Example 3 — Budget Focused

```text
Plan a 6-day trip to Turkey with a limited budget.
Suggest affordable accommodation and money-saving options.
```

### Example 4 — Flight Focused

```text
I want to travel from Islamabad to Dubai.
Give me flight planning guidance and then create a short itinerary.
```

---

# 🔒 Reliability & Safety Design

The agents contain several protections against unsupported information.

### No invented bookings

The system is instructed not to claim that a flight or hotel has been booked when it has not.

### No invented exact prices

When exact prices are unavailable, the agents should use ranges or qualitative guidance.

### No invented schedules

The flight agent should not create fictional flight schedules.

### Human review

The itinerary is presented to a human before the final response is produced.

### Output limiting

Large intermediate agent results are truncated before being inserted into later prompts to control prompt size.

---

# 📊 Why Multi-Agent?

A single AI agent could theoretically answer the entire travel request, but separating responsibilities provides clearer control.

```text
                 Single Agent
                     │
        ┌────────────┴────────────┐
        │                         │
   One large prompt        Difficult to control
                              responsibilities
```

The multi-agent design instead provides:

```text
                  Supervisor
                      │
       ┌──────┬───────┼───────┬──────┐
       ▼      ▼       ▼       ▼      ▼
    Flight  Hotel  Weather  Budget Itinerary
```

Each agent has a focused responsibility and the workflow combines their outputs.

---

# 🧠 Design Principles

This project follows several important AI engineering principles:

### 1. Separation of Concerns

Each agent performs a specialized task.

### 2. State-Driven Workflow

Agents communicate through a shared LangGraph state.

### 3. Tool-Augmented AI

Agents can use external data sources instead of relying only on model knowledge.

### 4. Guardrails

Travel requests are validated before specialist routing.

### 5. Human-in-the-Loop

The user remains involved before the final travel plan is generated.

### 6. Structured LLM Output

The supervisor uses JSON-based routing information to make agent selection easier to process programmatically.

### 7. Context Control

Intermediate results are limited before being passed into subsequent prompts.

---

# 🚀 Future Improvements

Potential improvements for future versions include:

- Real-time flight availability
- Real-time hotel availability
- Direct booking integrations
- Currency conversion
- Visa requirement checking
- Travel document checklist
- Interactive maps
- Flight price comparison
- Hotel price comparison
- Calendar integration
- Email itinerary delivery
- PDF itinerary export
- User preference memory
- Multi-language support
- Better structured tool outputs
- Agent observability with LangSmith
- Production deployment with Docker
- REST API using FastAPI
- Authentication and user accounts

---

# 🐛 Troubleshooting

## `ModuleNotFoundError`

Make sure the virtual environment is activated and dependencies are installed:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## API Key Errors

Check that `.env` exists in the project root and that the variable names match the names expected by the application.

---

## PostgreSQL Connection Error

Check:

1. PostgreSQL service is running.
2. Database exists.
3. Username is correct.
4. Password is correct.
5. Host and port are correct.
6. `DATABASE_URL` is correctly formatted.

---

## MCP Tool Errors

Check:

1. MCP server configuration.
2. API keys.
3. Tool names.
4. Python environment.
5. MCP adapter package installation.
6. External API availability.

---

# 📸 Application Flow

The user experience is designed around the following sequence:

```text
1. Enter travel request
        ↓
2. Supervisor validates request
        ↓
3. Required agents are selected
        ↓
4. External tools/search collect information
        ↓
5. Specialist agents analyze information
        ↓
6. Itinerary agent creates draft
        ↓
7. User reviews draft
        ↓
8. User approves OR provides feedback
        ↓
9. Final response agent generates final plan
```

---

# 💡 Example Final Output

A typical final plan can contain:

```text
Destination Overview

Day 1
- Arrival
- Hotel check-in
- Nearby activities

Day 2
- Main attractions
- Local food recommendations

Flight Summary
- Departure/arrival guidance
- Airline information
- Estimated duration

Accommodation
- Recommended areas
- Hotel considerations

Weather & Packing
- Current conditions
- Forecast
- Packing suggestions

Budget
- Major cost categories
- Risk areas
- Saving suggestions
```

The exact content depends on the information returned by the connected tools and the user's request.

---

# 🔮 Project Vision

The long-term goal of this project is to evolve from an AI itinerary generator into a complete **AI Travel Operations Assistant** capable of researching, comparing, validating, and organizing an entire trip while keeping a human in control of important decisions.

The current architecture provides a foundation for adding more agents, tools, APIs, and production services without replacing the core workflow.

---

# 👨‍💻 Author

**Zeeshan Hameed**

AI / Machine Learning Engineer  
Interested in:

- Generative AI
- Multi-Agent Systems
- LangGraph
- LangChain
- RAG
- MCP
- AI Automation
- FastAPI
- Production AI Systems

---

# 📄 License

Add your preferred license here, for example:

```text
MIT License
```

If this repository is intended for private/commercial use, replace this section with the appropriate license or project usage terms.

---

## ⭐ If you find this project useful

Consider starring the repository and following the project for future improvements.

---

**Built with Python · LangGraph · LangChain · Groq · MCP · Tavily · AviationStack · PostgreSQL · Streamlit**
