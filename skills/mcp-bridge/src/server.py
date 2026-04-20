#!/usr/bin/env python3
"""
Openclaw MCP Bridge - Generic MCP server for communicating with Openclaw agents.

This MCP server provides a bridge between any MCP-compatible agent (Claude, A0, etc.)
and Openclaw agents running locally or remotely.
"""

from fastmcp import FastMCP
import httpx
import os
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import logging

# Configure logging
log_level = os.getenv("OPENCLAW_MCP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("openclaw-mcp")

mcp = FastMCP("Openclaw Bridge")


@dataclass
class AgentConfig:
    """Configuration for an Openclaw agent."""
    name: str
    url: str
    token: str
    endpoint: str = "/v1/chat/completions"
    enabled: bool = True
    timeout: int = 120


class AgentManager:
    """Manages multiple Openclaw agent configurations from environment variables."""
    
    def __init__(self):
        self.agents: Dict[str, AgentConfig] = {}
        self._load_agents()
    
    def _mask_token(self, token: str) -> str:
        """Mask token for logging."""
        if len(token) <= 8:
            return "***"
        return f"{token[:4]}...{token[-4:]}"
    
    def _load_agents(self):
        """Load agent configurations from environment variables."""
        # Look for agents numbered 1-10
        for i in range(1, 11):
            prefix = f"OPENCLAW_AGENT_{i}"
            
            name = os.getenv(f"{prefix}_NAME")
            if not name:
                continue
            
            url = os.getenv(f"{prefix}_URL", "")
            token = os.getenv(f"{prefix}_TOKEN", "")
            endpoint = os.getenv(f"{prefix}_ENDPOINT", "/v1/chat/completions")
            enabled = os.getenv(f"{prefix}_ENABLED", "true").lower() == "true"
            timeout = int(os.getenv(f"{prefix}_TIMEOUT", "120"))
            
            if not url or not token:
                logger.warning(f"Agent '{name}' (index {i}) missing URL or token, skipping")
                continue
            
            self.agents[name] = AgentConfig(
                name=name,
                url=url,
                token=token,
                endpoint=endpoint,
                enabled=enabled,
                timeout=timeout
            )
            
            logger.info(f"Loaded agent: {name} at {url} (enabled: {enabled})")
        
        if not self.agents:
            logger.warning("No agents configured. Set OPENCLAW_AGENT_* environment variables.")
    
    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """Get agent configuration by name."""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all configured agent names."""
        return list(self.agents.keys())
    
    def validate_config(self) -> tuple[bool, str]:
        """Validate that at least one agent is configured and enabled."""
        if not self.agents:
            return False, "No agents configured. Please set OPENCLAW_AGENT_* environment variables."
        
        enabled_agents = [name for name, agent in self.agents.items() if agent.enabled]
        if not enabled_agents:
            return False, "No agents enabled. Please set at least one agent as enabled."
        
        return True, f"Configuration valid. {len(enabled_agents)} agent(s) enabled: {', '.join(enabled_agents)}"


# Initialize agent manager
agent_manager = AgentManager()


class OpenclawClient:
    """HTTP client for communicating with Openclaw agents."""
    
    def __init__(self, agent_config: AgentConfig):
        self.config = agent_config
    
    async def send_message(
        self, 
        message: str, 
        attachments: Optional[List[str]] = None
    ) -> str:
        """Send a message to the Openclaw agent and return the response."""
        
        # Process attachments if provided
        full_message = message
        if attachments:
            attachment_text = await self._process_attachments(attachments)
            if attachment_text:
                full_message = f"{message}\n\n{attachment_text}"
        
        url = f"{self.config.url}{self.config.endpoint}"
        
        # Mask token for logging
        masked_token = self._mask_token(self.config.token)
        logger.info(f"Sending message to agent '{self.config.name}' at {url}")
        logger.debug(f"Using token: {masked_token}")
        
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "X-API-Key": self.config.token,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openclaw:main",
            "messages": [{"role": "user", "content": full_message}],
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                
                logger.info(f"Response status: {resp.status_code}")
                
                if resp.status_code != 200:
                    error_msg = f"HTTP Error {resp.status_code}: {resp.text[:500]}"
                    logger.error(error_msg)
                    return f"Error communicating with {self.config.name}: {error_msg}"
                
                data = resp.json()
                
                # Extract response from OpenAI format
                choices = data.get("choices", [])
                if choices and len(choices) > 0:
                    content = choices[0].get("message", {}).get("content", "")
                    logger.info(f"Received response from {self.config.name} ({len(content)} chars)")
                    return content
                else:
                    return "No response received from agent"
                    
        except httpx.TimeoutException:
            error_msg = f"Request timed out after {self.config.timeout} seconds"
            logger.error(error_msg)
            return f"Error: {self.config.name} did not respond in time. {error_msg}"
        except httpx.ConnectError as e:
            error_msg = f"Cannot connect to {self.config.name} at {url}: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return f"Error communicating with {self.config.name}: {error_msg}"
    
    def _mask_token(self, token: str) -> str:
        """Mask token for logging."""
        if len(token) <= 8:
            return "***"
        return f"{token[:4]}...{token[-4:]}"
    
    async def _process_attachments(self, file_paths: List[str]) -> str:
        """Process file attachments and return as formatted text."""
        attachment_parts = []
        
        for file_path in file_paths:
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Format as markdown code block
                filename = os.path.basename(file_path)
                attachment_parts.append(
                    f"[Attached file: {filename}]\n```\n{content}\n```"
                )
                logger.info(f"Attached file: {filename} ({len(content)} chars)")
            except Exception as e:
                logger.warning(f"Could not read attachment {file_path}: {e}")
                attachment_parts.append(f"[Error reading file: {file_path}]")
        
        return "\n\n".join(attachment_parts) if attachment_parts else ""


@mcp.tool()
async def call_openclaw(
    instruction: str,
    agent: str,
    attachments: Optional[List[str]] = None
) -> str:
    """
    Send an instruction to an Openclaw agent and receive a response.
    
    This tool communicates with Openclaw agents (local Docker, native Windows, 
    or remote instances) to execute tasks, run commands, or get information.
    
    Args:
        instruction: The task or question for the Openclaw agent
        agent: The name of the configured agent to use (e.g., 'docker', 'native', 'remote')
        attachments: Optional list of file paths to attach to the message (text files only)
    
    Returns:
        The agent's response as a string
    
    Examples:
        "Check system status using the docker agent"
        "List files in workspace with attachments: ['/path/to/file.txt']"
    """
    # Get agent configuration
    agent_config = agent_manager.get_agent(agent)
    
    if not agent_config:
        available = ", ".join(agent_manager.list_agents())
        return f"Error: Agent '{agent}' not found. Available agents: {available if available else 'none configured'}"
    
    if not agent_config.enabled:
        return f"Error: Agent '{agent}' is disabled in configuration"
    
    # Create client and send message
    client = OpenclawClient(agent_config)
    response = await client.send_message(instruction, attachments)
    
    return response


@mcp.tool()
async def list_openclaw_agents() -> str:
    """
    List all configured Openclaw agents.
    
    Returns a list of available agent names and their status.
    
    Returns:
        Formatted list of configured agents
    """
    agents = agent_manager.agents
    
    if not agents:
        return "No agents configured. Please set OPENCLAW_AGENT_* environment variables."
    
    lines = ["Configured Openclaw Agents:", "=" * 40]
    
    for name, config in agents.items():
        status = "✅ enabled" if config.enabled else "❌ disabled"
        url = config.url
        lines.append(f"\n{name}:")
        lines.append(f"  Status: {status}")
        lines.append(f"  URL: {url}")
        lines.append(f"  Endpoint: {config.endpoint}")
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    # Validate configuration on startup
    is_valid, message = agent_manager.validate_config()
    
    if is_valid:
        logger.info(message)
    else:
        logger.warning(message)
        logger.warning("Server will start but tools may fail if no agents are configured.")
    
    # Start MCP server
    logger.info("Starting Openclaw MCP Bridge...")
    mcp.run()


if __name__ == "__main__":
    main()
