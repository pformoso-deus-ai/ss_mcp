# MCP Demo Project

This repository contains a demonstration of the Model Control Protocol (MCP) with examples of tools, resources, and prompts. The project includes both a server and a client implementation to showcase the capabilities of MCP.

## What is MCP?

The Model Control Protocol (MCP) is a protocol for controlling AI models safely and effectively. It consists of three main components:

1. **Tools**: Model-controlled functions that allow AI models to take actions
2. **Resources**: Application-controlled data that models can access but not modify
3. **Prompts**: User-controlled templates for AI interactions

## Features

- **Tools**: Ancient Latin text transformation
- **Resources**: 
  - Greek gods data from CSV (`gods://`)
  - Ancient Latin text transformation (`ancientlatin://`)
  - Personalized greetings (`greeting://`)
- **Prompts**: MCP-compliant structured prompts for:
  - MCP expertise (with topic-specific variations)
  - Code review
  - Git commit message generation
- **LLM Integration**: Ollama integration for processing prompts with local LLMs

## MCP Prompt Implementation

Our implementation follows the MCP specification for prompts:

- Prompts return structured messages with roles (system/user) and content types
- Prompts support dynamic content through parameters
- Each prompt has a clear purpose and documentation
- Messages follow the standard format with role and content fields

Example prompt structure:
```json
{
  "messages": [
    {
      "role": "system",
      "content": {
        "type": "text",
        "text": "System instructions here"
      }
    },
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "User query here"
      }
    }
  ]
}
```

## Ollama Integration

The client integrates with [Ollama](https://ollama.ai/) to process prompts with local LLMs:

- Automatically extracts system and user messages from MCP prompts
- Sends them to Ollama for processing
- Supports different Ollama models (llama3 by default)
- Handles error cases gracefully

## Getting Started

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- [Ollama](https://ollama.ai/) installed and running locally (for LLM features)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp-demo.git
   cd mcp-demo
   ```

2. Install dependencies using uv:
   ```bash
   make install
   ```

3. Install and start Ollama:
   ```bash
   # Follow instructions at https://ollama.ai/
   # Pull the llama3 model (or another model of your choice)
   ollama pull llama3
   ```

### Running the Server

Start the MCP server:

```bash
make server
```

The server will be available at http://localhost:8000.

### Using the Client

The client provides a command-line interface for interacting with the server:

```bash
# Transform text to ancient Latin using tool
make client ARGS='latin "The quick brown fox jumps over the lazy dog."'

# Transform text to ancient Latin using resource
make client ARGS='latin-resource "The quick brown fox jumps over the lazy dog."'

# Get information about Greek gods
make client ARGS='gods'

# Get information about a specific number of Greek gods
make client ARGS='gods --limit 5'

# Get a personalized greeting
make client ARGS='greeting "World"'

# Chat about MCP using Ollama
make client ARGS='chat "What is MCP?"'

# Chat about MCP using a specific Ollama model
make client ARGS='chat "What is MCP?" --model mistral'

# Get a code review using Ollama
make client ARGS='review "def hello():\n    print(\"Hello, world!\")"'

# Get a commit message suggestion using Ollama
make client ARGS='commit "Added new feature X"'

# Use a custom Ollama server
make client ARGS='chat "What is MCP?" --ollama-url http://custom-ollama-server:11434'
```

## Development

### Running Tests

```bash
make test
```

### Code Formatting and Linting

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make typecheck

# Run all checks
make check
```

### Cleaning Up

```bash
make clean
```

## Project Structure

- `server.py`: MCP server implementation with tools, resources, and prompts
- `client.py`: MCP client implementation with command-line interface and Ollama integration
- `tests/`: Test cases for the server and client
- `Makefile`: Build automation for common tasks
- `requirements.txt`: Project dependencies
- `pyproject.toml`: Configuration for linters and type checkers

## License

This project is licensed under the MIT License - see the LICENSE file for details. 