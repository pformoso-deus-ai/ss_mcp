#!/usr/bin/env python3
# client.py
"""
MCP Client implementation for interacting with the MCP Demo Server.

This client demonstrates how to interact with the three main components of MCP:
- Tools: Invoking the ancient Latin text transformation
- Resources: Querying Greek gods data
- Prompts: Chatting with an MCP expert using Ollama LLM
"""

import argparse
import json
import sys
import os
import asyncio
import subprocess
from typing import Dict, List, Optional, Union, Any, Tuple
from contextlib import AsyncExitStack

import requests
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        """
        Initialize the Ollama Client.
        
        Args:
            base_url: URL of the Ollama API
            model: The model to use for generation
        """
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
    
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """
        Generate a response from the Ollama model.
        
        Args:
            prompt: The prompt to send to the model
            system: Optional system message
            
        Returns:
            The generated response
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return f"Error: {e}"
    
    def process_mcp_prompt(self, prompt_data: Dict[str, Any]) -> str:
        """
        Process an MCP prompt with Ollama.
        
        Args:
            prompt_data: The MCP prompt data
            
        Returns:
            The generated response
        """
        if not isinstance(prompt_data, dict) or "messages" not in prompt_data:
            return "Error: Invalid prompt format"
        
        # Extract system and user messages
        system_message = next((m for m in prompt_data["messages"] if m["role"] == "system"), None)
        user_message = next((m for m in prompt_data["messages"] if m["role"] == "user"), None)
        
        if not user_message or "content" not in user_message or "text" not in user_message["content"]:
            return "Error: Missing user message"
        
        system_text = None
        if system_message and "content" in system_message and "text" in system_message["content"]:
            system_text = system_message["content"]["text"]
        
        user_text = user_message["content"]["text"]
        
        # Generate response
        return self.generate(user_text, system_text)


class MCPDemoClient:
    """Client for interacting with the MCP Demo Server."""

    def __init__(self, server_path: str = "./server.py", ollama_url: str = "http://localhost:11434", ollama_model: str = "llama3"):
        """
        Initialize the MCP Demo Client.
        
        Args:
            server_path: Path to the server script
            ollama_url: URL of the Ollama API
            ollama_model: The Ollama model to use
        """
        self.server_path = server_path
        self.ollama = OllamaClient(ollama_url, ollama_model)
        self.session = None
        
    async def connect(self):
        """
        Connect to the MCP server.
        
        This method establishes a connection to the MCP server using stdio transport.
        """
        # Ensure the server script exists
        if not os.path.exists(self.server_path):
            raise FileNotFoundError(f"Server script not found at {self.server_path}")
        
        # Set up server parameters with the correct Python interpreter
        python_executable = sys.executable
        server_params = StdioServerParameters(
            command=python_executable,
            args=[self.server_path],
            env=os.environ,
        )
        
        # Create a simple sampling callback
        async def sampling_callback(
            context: Any, params: types.CreateMessageRequestParams
        ) -> types.CreateMessageResult:
            return types.CreateMessageResult(
                role="assistant",
                content=types.TextContent(
                    type="text",
                    text="Sample response from MCP client",
                ),
                model="sample-model",
                stopReason="endTurn",
            )
        
        # Use the async context manager properly
        async with stdio_client(server_params) as (read_stream, write_stream):
            # Create and initialize the session
            self.session = ClientSession(
                read_stream, 
                write_stream,
                sampling_callback=sampling_callback
            )
            
            # Initialize the session
            await self.session.initialize()
            
            return self.session
    
    async def disconnect(self):
        """
        Disconnect from the MCP server.
        
        This method closes the connection to the MCP server.
        """
        if self.session:
            await self.session.aclose()
            self.session = None
    
    async def transform_to_ancient_latin(self, text: str) -> str:
        """
        Transform text to appear as if written in ancient Latin.
        
        Args:
            text: The text to transform
            
        Returns:
            Text transformed to resemble ancient Latin
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        response = await self.session.call_tool("ancient_latin_text", {"text": text})
        return response
    
    async def get_ancient_latin_text_resource(self, text: str) -> str:
        """
        Get text transformed to ancient Latin using the resource endpoint.
        
        Args:
            text: The text to transform
            
        Returns:
            Text transformed to resemble ancient Latin
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        content, _ = await self.session.read_resource(f"ancientlatin://{text}")
        return content
    
    async def get_greek_gods(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get information about Greek gods.
        
        Args:
            limit: Maximum number of records to return (default: all available)
            
        Returns:
            List of dictionaries containing information about Greek gods
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        uri = "gods://"
        if limit is not None:
            uri += f"?limit={limit}"
        
        content, _ = await self.session.read_resource(uri)
        return json.loads(content)
    
    async def get_greeting(self, name: str) -> str:
        """
        Get a personalized greeting.
        
        Args:
            name: The name to include in the greeting
            
        Returns:
            A personalized greeting message
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        content, _ = await self.session.read_resource(f"greeting://{name}")
        return content
    
    async def chat_about_mcp(self, message: str) -> str:
        """
        Chat with an MCP expert about the Model Control Protocol using Ollama.
        
        Args:
            message: The user's message or question about MCP
            
        Returns:
            Response from the MCP expert via Ollama
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        # Determine the topic based on the message
        topic = None
        if "tools" in message.lower():
            topic = "tools"
        elif "resources" in message.lower():
            topic = "resources"
        elif "prompts" in message.lower():
            topic = "prompts"
        
        # Get the MCP expert prompt with the appropriate topic
        params = {}
        if topic:
            params["topic"] = topic
        
        prompt_data = await self.session.get_prompt("mcp_expert", params)
        
        # Process the prompt with Ollama
        return self.ollama.process_mcp_prompt(prompt_data)
    
    async def get_code_review(self, code: str, language: str = "python") -> str:
        """
        Get a code review using the code_review prompt and Ollama.
        
        Args:
            code: The code to review
            language: The programming language of the code
            
        Returns:
            A code review response from Ollama
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        prompt_data = await self.session.get_prompt("code_review", {"code": code, "language": language})
        
        # Process the prompt with Ollama
        return self.ollama.process_mcp_prompt(prompt_data)
    
    async def get_commit_message(self, changes: str) -> str:
        """
        Get a Git commit message suggestion using Ollama.
        
        Args:
            changes: Git diff or description of changes
            
        Returns:
            A suggested commit message from Ollama
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        prompt_data = await self.session.get_prompt("git_commit", {"changes": changes})
        
        # Process the prompt with Ollama
        return self.ollama.process_mcp_prompt(prompt_data)


def print_json(data: Union[Dict, List]) -> None:
    """
    Print data as formatted JSON.
    
    Args:
        data: The data to print
    """
    print(json.dumps(data, indent=2))


async def run_command(args):
    """
    Run the specified command with the MCP client.
    
    Args:
        args: Command line arguments
    """
    # Create client
    client = MCPDemoClient(
        server_path=args.server_path,
        ollama_url=args.ollama_url, 
        ollama_model=getattr(args, "model", "llama3")
    )
    
    try:
        # Connect to the server
        await client.connect()
        
        # Execute command
        if args.command == "latin":
            result = await client.transform_to_ancient_latin(args.text)
            print(result)
        elif args.command == "latin-resource":
            result = await client.get_ancient_latin_text_resource(args.text)
            print(result)
        elif args.command == "gods":
            result = await client.get_greek_gods(args.limit)
            print_json(result)
        elif args.command == "greeting":
            result = await client.get_greeting(args.name)
            print(result)
        elif args.command == "chat":
            result = await client.chat_about_mcp(args.message)
            print(result)
        elif args.command == "review":
            result = await client.get_code_review(args.code, args.language)
            print(result)
        elif args.command == "commit":
            result = await client.get_commit_message(args.changes)
            print(result)
    finally:
        # Disconnect from the server
        await client.disconnect()


def main() -> None:
    """Run the MCP Demo Client CLI."""
    parser = argparse.ArgumentParser(description="MCP Demo Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Latin text transformation (tool)
    latin_parser = subparsers.add_parser("latin", help="Transform text to ancient Latin using tool")
    latin_parser.add_argument("text", help="Text to transform")
    
    # Latin text transformation (resource)
    latin_resource_parser = subparsers.add_parser("latin-resource", help="Transform text to ancient Latin using resource")
    latin_resource_parser.add_argument("text", help="Text to transform")
    
    # Greek gods data
    gods_parser = subparsers.add_parser("gods", help="Get Greek gods data")
    gods_parser.add_argument("--limit", type=int, help="Maximum number of records to return")
    
    # Greeting
    greeting_parser = subparsers.add_parser("greeting", help="Get a personalized greeting")
    greeting_parser.add_argument("name", help="Name to greet")
    
    # Chat about MCP
    chat_parser = subparsers.add_parser("chat", help="Chat about MCP")
    chat_parser.add_argument("message", help="Message or question about MCP")
    chat_parser.add_argument("--model", default="llama3", help="Ollama model to use")
    
    # Code review
    review_parser = subparsers.add_parser("review", help="Get a code review")
    review_parser.add_argument("code", help="Code to review")
    review_parser.add_argument("--language", default="python", help="Programming language")
    review_parser.add_argument("--model", default="llama3", help="Ollama model to use")
    
    # Commit message
    commit_parser = subparsers.add_parser("commit", help="Get a commit message suggestion")
    commit_parser.add_argument("changes", help="Git diff or description of changes")
    commit_parser.add_argument("--model", default="llama3", help="Ollama model to use")
    
    # Add global arguments
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--server-path", default="./server.py", help="Path to the MCP server script")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run the command asynchronously
    asyncio.run(run_command(args))


if __name__ == "__main__":
    main()
