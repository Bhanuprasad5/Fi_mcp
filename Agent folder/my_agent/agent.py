import os
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService  # NEW # NEW
from google.adk.tools import google_search
# from google.adk.sessions import DatabaseSessionService        # swap later
from google.adk.tools.mcp_tool.mcp_session_manager import \
    StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

PERSONAL_FINANCE_PROMPT = """
You are a helpful and empathetic personal-finance assistant.
Track expenses, manage money, analyse spending, and offer insights.
Be polite, concise, and confirm actions with the user.
"""

SECOND_AGENT_PROMPT = """
You are a highly professional and specialized real-time financial advisory agent for retirement planning.
Your goal is to provide personalized retirement plans based on real-time information.
You are connected to a free web browser tool to gather real-time data for your analysis.
You can also request information from the 'personal_finance_agent' to get user-specific financial data.
"""


root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="personal_finance_agent",
    instruction=PERSONAL_FINANCE_PROMPT,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPServerParams(
                url="http://localhost:8080/mcp/stream",
                # headers={"Authorization": "Bearer <YOUR_API_KEY>"}
            )
        )
    ],
)
second_agent = LlmAgent(
    model="gemini-1.5-pro",
    name="retirement_planner_agent",
    instruction=SECOND_AGENT_PROMPT,
    tools=[google_search],
)
# Link agents for communication after creation
try:
    root_agent.agents.append(second_agent)
    second_agent.agents.append(root_agent)
except AttributeError:
    # If agents attribute doesn't exist, we'll handle communication through MCP
    pass