# import os
# import asyncio

# from dotenv import load_dotenv
# from langchain_mcp_adapters.client import MultiServerMCPClient

# # load_dotenv()
# load_dotenv(override=True)
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
# AVIATION_STACK_API_KEY = os.getenv("AVIATION_STACK_API_KEY")
# WHEATER_API_KEY = os.getenv("WHEATER_API_KEY")

# client = MultiServerMCPClient(
#     {
#         "tavily": {
#             "transport": "streamable_http",
#             "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
#         },

#         "aviationstack": {
#             "transport": "stdio",
#             "command": r"D:\Projects\Deploy Projects\MultiAgent_FlightTicket_withMCP\MultiAgent_FlightTicket\aviationstack-mcp\.venv\Scripts\python.exe",
#             "args": [
#                 "-m",
#                 "aviationstack_mcp",
#                 "mcp",
#                 "run"
#             ],
#             "env": {
#                 "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY
#             }
#         },

#         "weather": {
#             "transport": "stdio",
#             "command": r"D:\Projects\Deploy Projects\MultiAgent_FlightTicket_withMCP\MultiAgent_FlightTicket\.venv\Scripts\python.exe",
#             "args": [
#                 r"D:\Projects\Deploy Projects\MultiAgent_FlightTicket_withMCP\MultiAgent_FlightTicket\custom_wheater_serverMCP.py"
#             ],
#             "env": {
#                 "WHEATER_API_KEY": WHEATER_API_KEY
#             }
#         }



#     }

# )




# # Cache tools so we don't load them repeatedly
# _tools_cache = None


# async def get_tools():
#     global _tools_cache

#     if _tools_cache is None:
#         try:
#             _tools_cache = await client.get_tools()

#         except Exception as e:
#             print("\n========== FULL ERROR ==========")
#             print(type(e))
#             print(repr(e))

#             if hasattr(e, "exceptions"):
#                 print("\nSUB EXCEPTIONS:")
#                 for i, sub in enumerate(e.exceptions):
#                     print(f"\n--- Exception {i+1} ---")
#                     print(type(sub))
#                     print(repr(sub))

#             raise

#     return _tools_cache

# async def call_tool(tool_name: str, args: dict = None):
#     tools = await get_tools()

#     tool = next(
#         (tool for tool in tools if tool.name == tool_name),
#         None,
#     )

#     if tool is None:
#         raise ValueError(f"Tool '{tool_name}' not found")

#     return await tool.ainvoke(args or {})


# # ------------------------
# # Tavily MCP Tools
# # ------------------------



# async def tavily_search(query: str):
#     return await call_tool("tavily_search", {"query": query})


# async def list_airports(search: str = "", limit: int = 10):
#     return await call_tool("list_airports", {"search": search, "limit": limit, "offset": 0})


# async def list_airlines(search: str = "", limit: int = 10):
#     return await call_tool("list_airlines", {"search": search, "limit": limit, "offset": 0})


# async def current_weather(city: str):
#     return await call_tool("get_current_weather", {"city": city})


# async def forecast(city: str):
#     return await call_tool("get_forecast", {"city": city})

import os
import sys

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(override=True)


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATION_STACK_API_KEY")
WHEATER_API_KEY = os.getenv("WHEATER_API_KEY")


# ============================================================
# PROJECT DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WEATHER_SERVER_PATH = os.path.join(
    BASE_DIR,
    "custom_wheater_serverMCP.py",
)


# ============================================================
# MCP CLIENT
# ============================================================

client = MultiServerMCPClient(
    {

        # ========================================================
        # TAVILY MCP
        # ========================================================

        "tavily": {
            "transport": "streamable_http",

            "url": (
                "https://mcp.tavily.com/mcp/"
                f"?tavilyApiKey={TAVILY_API_KEY}"
            ),
        },


        # ========================================================
        # AVIATIONSTACK MCP
        # ========================================================

        "aviationstack": {
            "transport": "stdio",

            # Use the Python interpreter of the current
            # environment.
            #
            # This works locally and on Streamlit Cloud.
            "command": sys.executable,

            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run",
            ],

            "env": {
                "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY,
            },
        },


        # ========================================================
        # WEATHER MCP
        # ========================================================

        "weather": {
            "transport": "stdio",

            # Use the Python interpreter of the current
            # environment.
            "command": sys.executable,

            # Use an absolute path so Streamlit Cloud does not
            # depend on the current working directory.
            "args": [
                WEATHER_SERVER_PATH,
            ],

            "env": {
                "WHEATER_API_KEY": WHEATER_API_KEY,
            },
        },
    }
)


# ============================================================
# TOOL CACHE
# ============================================================

_tools_cache = None


# ============================================================
# GET ALL MCP TOOLS
# ============================================================

async def get_tools():
    global _tools_cache

    if _tools_cache is None:

        try:
            print("\n========================================")
            print("Starting MCP servers...")
            print("========================================")

            print("\nPython executable:")
            print(sys.executable)

            print("\nWeather server:")
            print(WEATHER_SERVER_PATH)

            print("\nTavily API key loaded:")
            print(bool(TAVILY_API_KEY))

            print("\nAviationStack API key loaded:")
            print(bool(AVIATION_STACK_API_KEY))

            print("\nWeather API key loaded:")
            print(bool(WHEATER_API_KEY))

            print("\nLoading MCP tools...")

            _tools_cache = await client.get_tools()

            print("\n========================================")
            print("MCP TOOLS LOADED SUCCESSFULLY")
            print("========================================")

            print(
                "Available tools:",
                [tool.name for tool in _tools_cache]
            )

        except Exception as e:

            print("\n========================================")
            print("MCP ERROR")
            print("========================================")

            print("\nException type:")
            print(type(e))

            print("\nException:")
            print(repr(e))

            print("\nException string:")
            print(str(e))

            if hasattr(e, "exceptions"):

                print("\n========================================")
                print("SUB EXCEPTIONS")
                print("========================================")

                for i, sub in enumerate(e.exceptions):

                    print(f"\n--- Exception {i + 1} ---")

                    print("Type:")
                    print(type(sub))

                    print("Error:")
                    print(repr(sub))

                    print("String:")
                    print(str(sub))

            raise

    return _tools_cache


# ============================================================
# GENERIC MCP TOOL CALL
# ============================================================

async def call_tool(
    tool_name: str,
    args: dict = None,
):

    tools = await get_tools()

    tool = next(
        (
            tool
            for tool in tools
            if tool.name == tool_name
        ),
        None,
    )

    if tool is None:

        available_tools = [
            tool.name
            for tool in tools
        ]

        raise ValueError(
            f"Tool '{tool_name}' not found. "
            f"Available tools: {available_tools}"
        )

    return await tool.ainvoke(
        args or {}
    )


# ============================================================
# TAVILY MCP TOOLS
# ============================================================

async def tavily_search(
    query: str,
):

    return await call_tool(
        "tavily_search",
        {
            "query": query,
        },
    )


# ============================================================
# AVIATIONSTACK MCP TOOLS
# ============================================================

async def list_airports(
    search: str = "",
    limit: int = 10,
):

    return await call_tool(
        "list_airports",
        {
            "search": search,
            "limit": limit,
            "offset": 0,
        },
    )


async def list_airlines(
    search: str = "",
    limit: int = 10,
):

    return await call_tool(
        "list_airlines",
        {
            "search": search,
            "limit": limit,
            "offset": 0,
        },
    )


# ============================================================
# WEATHER MCP TOOLS
# ============================================================

async def current_weather(
    city: str,
):

    return await call_tool(
        "get_current_weather",
        {
            "city": city,
        },
    )


async def forecast(
    city: str,
):

    return await call_tool(
        "get_forecast",
        {
            "city": city,
        },
    )