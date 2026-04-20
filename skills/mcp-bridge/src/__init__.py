"""
Openclaw MCP Bridge - Generic MCP server for Openclaw agents.

A Model Context Protocol (MCP) server that enables any MCP-compatible agent
to communicate with Openclaw agents running locally or remotely.
"""

__version__ = "0.1.0"
__author__ = "Openclaw MCP Bridge Contributors"

from .server import mcp, call_openclaw, list_openclaw_agents

__all__ = ["mcp", "call_openclaw", "list_openclaw_agents"]
