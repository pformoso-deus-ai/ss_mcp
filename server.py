#!/usr/bin/env python3
# server.py
"""
MCP Server implementation with examples of tools, resources, and prompts.

This server demonstrates the core components of the MCP protocol:
- Tools: Model-controlled functions (e.g., text transformation)
- Resources: Application-controlled data (e.g., CSV data access)
- Prompts: User-controlled templates for AI interactions
"""

import csv
import io
import random
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("MCP Demo Server")


# === TOOLS ===
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers together.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of the two numbers
    """
    return a + b


@mcp.tool()
def ancient_latin_text(text: str) -> str:
    """
    Transform text to appear as if written in ancient Latin.
    
    This tool applies various transformations to make modern text
    resemble ancient Latin writing style and vocabulary.
    
    Args:
        text: The input text to transform
        
    Returns:
        Text transformed to resemble ancient Latin
    """
    # Replace common English words with Latin-like equivalents
    replacements = {
        "the": "thy",
        "and": "et",
        "of": "de",
        "to": "ad",
        "in": "in",
        "is": "est",
        "for": "pro",
        "with": "cum",
        "you": "tu",
        "I": "ego",
        "we": "nos",
        "they": "illi",
        "this": "hic",
        "that": "ille",
        "have": "habeo",
        "be": "esse",
        "will": "voluntas",
    }
    
    # Apply replacements
    words = text.split()
    for i, word in enumerate(words):
        # Strip punctuation for comparison
        clean_word = word.lower().strip(".,;:!?")
        if clean_word in replacements:
            # Preserve capitalization and punctuation
            punctuation = ""
            if not word[-1].isalnum():
                punctuation = word[-1]
            
            if word[0].isupper():
                words[i] = replacements[clean_word].capitalize() + punctuation
            else:
                words[i] = replacements[clean_word] + punctuation
    
    # Add Latin-like suffixes to some words
    for i, word in enumerate(words):
        if len(word) > 4 and random.random() < 0.3:
            if word[-1].isalnum():
                if random.random() < 0.5:
                    words[i] = word + "us"
                else:
                    words[i] = word + "um"
    
    # Join words and add some Latin phrases
    latin_phrases = [
        "Veni, vidi, vici.",
        "Alea iacta est.",
        "Carpe diem.",
        "Et tu, Brute?",
        "Cogito, ergo sum."
    ]
    
    result = " ".join(words)
    
    # Randomly insert a Latin phrase
    if len(result) > 50 and random.random() < 0.5:
        phrase = random.choice(latin_phrases)
        insert_pos = random.randint(0, len(words) - 1)
        words.insert(insert_pos, phrase)
        result = " ".join(words)
    
    return result


# === RESOURCES ===
# Create a fake CSV with Greek gods data
GREEK_GODS_CSV = """name,domain,symbol,roman_name
Zeus,Sky and Thunder,Lightning bolt,Jupiter
Poseidon,Sea and Earthquakes,Trident,Neptune
Hades,Underworld,Helmet of darkness,Pluto
Athena,Wisdom and War,Owl,Minerva
Apollo,Sun and Music,Lyre,Apollo
Artemis,Moon and Hunt,Bow and arrow,Diana
Aphrodite,Love and Beauty,Dove,Venus
Hermes,Messengers and Travelers,Winged sandals,Mercury
Ares,War,Spear,Mars
Hephaestus,Fire and Forge,Hammer,Vulcan
Demeter,Agriculture,Wheat,Ceres
Dionysus,Wine and Festivity,Grapevine,Bacchus
Hera,Marriage and Family,Peacock,Juno
Hestia,Hearth and Home,Hearth,Vesta
"""


@mcp.resource("gods://text/{limit}")
def get_greek_gods(limit: Optional[int] = 10) -> List[Dict[str, str]]:
    """
    Get information about Greek gods from a CSV dataset.
    
    Args:
        limit: Maximum number of records to return (default: 10)
        
    Returns:
        List of dictionaries containing information about Greek gods
    """
    csv_file = io.StringIO(GREEK_GODS_CSV)
    reader = csv.DictReader(csv_file)
    
    result = []
    for i, row in enumerate(reader):
        if limit is not None and i >= limit:
            break
        result.append(row)
    
    return result


# Also add a resource version of the ancient Latin text transformation
@mcp.resource("ancientlatin://{text}")
def get_ancient_latin_text(text: str) -> str:
    """
    Get text transformed to appear as if written in ancient Latin.
    
    This resource applies the same transformations as the ancient_latin_text tool
    but is accessed as a resource rather than a tool.
    
    Args:
        text: The text to transform
        
    Returns:
        Text transformed to resemble ancient Latin
    """
    return ancient_latin_text(text)


# === PROMPTS ===
# Updated to follow MCP prompt specification
@mcp.prompt("mcp_expert")
def get_mcp_expert_prompt(topic: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a prompt template for answering questions about MCP.
    
    This prompt helps guide AI models to provide accurate and helpful
    information about the Model Control Protocol.
    
    Args:
        topic: Optional specific MCP topic to focus on
        
    Returns:
        A structured prompt with messages in MCP format
    """
    base_prompt = """You are an MCP (Model Control Protocol) expert assistant. Your goal is to provide accurate, 
helpful information about the MCP protocol, its components, and how to use it effectively.

The MCP protocol consists of three main components:
1. Tools: Model-controlled functions that allow AI models to take actions
2. Resources: Application-controlled data that models can access but not modify
3. Prompts: User-controlled templates for AI interactions

When answering questions about MCP, focus on:
- Explaining concepts clearly with examples
- Providing practical implementation advice
- Suggesting best practices for MCP architecture
- Helping troubleshoot common issues

Remember that MCP is designed to create safer, more controllable AI systems by clearly 
defining the boundaries between model control, application control, and user control."""

    topic_content = ""
    if topic:
        if topic.lower() == "tools":
            topic_content = """
Tools in MCP are model-controlled functions that allow AI models to take actions.
They are defined on the server side and can be invoked by the client.
Tools have a name, description, and parameters, and they return a result.
Examples include text transformation, data processing, or external API calls."""
        elif topic.lower() == "resources":
            topic_content = """
Resources in MCP are application-controlled data that models can access but not modify.
They are defined on the server side and can be accessed by the client.
Resources have a URI and can return various types of data.
Examples include database records, file contents, or API responses."""
        elif topic.lower() == "prompts":
            topic_content = """
Prompts in MCP are user-controlled templates for AI interactions.
They are defined on the server side and can be used by the client.
Prompts have a name, description, and optional arguments.
They return structured messages with roles and content.
Prompts can include dynamic content from resources and support multi-step workflows."""

    # Return structured messages in MCP format
    return {
        "messages": [
            {
                "role": "system",
                "content": {
                    "type": "text",
                    "text": base_prompt + topic_content
                }
            },
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": "Please tell me about " + (topic if topic else "MCP in general")
                }
            }
        ]
    }


@mcp.prompt("code_review")
def get_code_review_prompt(code: str, language: Optional[str] = "python") -> Dict[str, Any]:
    """
    Get a prompt template for code review.
    
    This prompt helps guide AI models to provide helpful code reviews.
    
    Args:
        code: The code to review
        language: The programming language of the code
        
    Returns:
        A structured prompt with messages in MCP format
    """
    return {
        "messages": [
            {
                "role": "system",
                "content": {
                    "type": "text",
                    "text": f"You are an expert {language} developer. Your task is to review code and provide constructive feedback."
                }
            },
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Please review this {language} code and suggest improvements:\n\n```{language}\n{code}\n```"
                }
            }
        ]
    }


@mcp.prompt("git_commit")
def get_git_commit_prompt(changes: str) -> Dict[str, Any]:
    """
    Get a prompt template for generating Git commit messages.
    
    This prompt helps guide AI models to write clear and concise commit messages.
    
    Args:
        changes: Git diff or description of changes
        
    Returns:
        A structured prompt with messages in MCP format
    """
    return {
        "messages": [
            {
                "role": "system",
                "content": {
                    "type": "text",
                    "text": "You are an expert at writing clear, concise, and informative Git commit messages."
                }
            },
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Generate a commit message for these changes:\n\n{changes}"
                }
            }
        ]
    }


# Dynamic greeting resource (from original example)
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """
    Get a personalized greeting for the given name.
    
    Args:
        name: The name to include in the greeting
        
    Returns:
        A personalized greeting message
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()