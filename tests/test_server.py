#!/usr/bin/env python3
# tests/test_server.py
"""Tests for the MCP server components."""

import csv
import io
import unittest
from unittest.mock import patch

import server


class TestTools(unittest.TestCase):
    """Test cases for MCP tools."""

    def test_add(self):
        """Test the add tool."""
        self.assertEqual(server.add(2, 3), 5)
        self.assertEqual(server.add(-1, 1), 0)
        self.assertEqual(server.add(0, 0), 0)

    def test_ancient_latin_text(self):
        """Test the ancient Latin text transformation tool."""
        # Test basic word replacements
        text = "The quick brown fox jumps over the lazy dog."
        result = server.ancient_latin_text(text)
        
        # Check that some replacements were made
        self.assertNotEqual(text, result)
        self.assertIn("thy", result.lower())  # "the" should be replaced with "thy"
        
        # Test with empty string
        self.assertEqual(server.ancient_latin_text(""), "")


class TestResources(unittest.TestCase):
    """Test cases for MCP resources."""

    def test_get_greek_gods(self):
        """Test the Greek gods resource."""
        # Test with default limit
        gods = server.get_greek_gods()
        self.assertLessEqual(len(gods), 10)
        
        # Test with custom limit
        gods = server.get_greek_gods(limit=5)
        self.assertEqual(len(gods), 5)
        
        # Test with limit larger than available data
        all_gods = server.get_greek_gods(limit=100)
        csv_file = io.StringIO(server.GREEK_GODS_CSV)
        reader = csv.DictReader(csv_file)
        expected_count = sum(1 for _ in reader)
        self.assertEqual(len(all_gods), expected_count)
        
        # Check data structure
        self.assertTrue(all(isinstance(god, dict) for god in gods))
        self.assertTrue(all("name" in god for god in gods))
        self.assertTrue(all("domain" in god for god in gods))
        self.assertTrue(all("symbol" in god for god in gods))
        self.assertTrue(all("roman_name" in god for god in gods))

    def test_get_greeting(self):
        """Test the greeting resource."""
        self.assertEqual(server.get_greeting("World"), "Hello, World!")
        self.assertEqual(server.get_greeting("MCP"), "Hello, MCP!")

    def test_get_ancient_latin_text(self):
        """Test the ancient Latin text resource."""
        # Test basic word replacements
        text = "The quick brown fox jumps over the lazy dog."
        result = server.get_ancient_latin_text(text)
        
        # Check that some replacements were made
        self.assertNotEqual(text, result)
        self.assertIn("thy", result.lower())  # "the" should be replaced with "thy"
        
        # Test with empty string
        self.assertEqual(server.get_ancient_latin_text(""), "")
        
        # Verify it uses the tool function
        with patch('server.ancient_latin_text') as mock_tool:
            mock_tool.return_value = "Mocked Latin text"
            self.assertEqual(server.get_ancient_latin_text("Test"), "Mocked Latin text")
            mock_tool.assert_called_once_with("Test")


class TestPrompts(unittest.TestCase):
    """Test cases for MCP prompts."""

    def test_get_mcp_expert_prompt(self):
        """Test the MCP expert prompt."""
        # Test with no topic
        prompt = server.get_mcp_expert_prompt()
        
        # Check the structure
        self.assertIsInstance(prompt, dict)
        self.assertIn("messages", prompt)
        self.assertIsInstance(prompt["messages"], list)
        self.assertEqual(len(prompt["messages"]), 2)
        
        # Check system message
        system_message = prompt["messages"][0]
        self.assertEqual(system_message["role"], "system")
        self.assertIn("content", system_message)
        self.assertIn("type", system_message["content"])
        self.assertEqual(system_message["content"]["type"], "text")
        self.assertIn("text", system_message["content"])
        self.assertIn("MCP", system_message["content"]["text"])
        self.assertIn("Tools", system_message["content"]["text"])
        self.assertIn("Resources", system_message["content"]["text"])
        self.assertIn("Prompts", system_message["content"]["text"])
        
        # Check user message
        user_message = prompt["messages"][1]
        self.assertEqual(user_message["role"], "user")
        self.assertIn("content", user_message)
        self.assertIn("type", user_message["content"])
        self.assertEqual(user_message["content"]["type"], "text")
        self.assertIn("text", user_message["content"])
        self.assertIn("MCP in general", user_message["content"]["text"])
        
        # Test with specific topic
        for topic in ["tools", "resources", "prompts"]:
            prompt = server.get_mcp_expert_prompt(topic=topic)
            system_message = prompt["messages"][0]
            self.assertIn(topic.capitalize(), system_message["content"]["text"])
            user_message = prompt["messages"][1]
            self.assertIn(topic, user_message["content"]["text"])

    def test_get_code_review_prompt(self):
        """Test the code review prompt."""
        code = "def hello():\n    print('Hello, world!')"
        prompt = server.get_code_review_prompt(code=code, language="python")
        
        # Check the structure
        self.assertIsInstance(prompt, dict)
        self.assertIn("messages", prompt)
        self.assertIsInstance(prompt["messages"], list)
        self.assertEqual(len(prompt["messages"]), 2)
        
        # Check system message
        system_message = prompt["messages"][0]
        self.assertEqual(system_message["role"], "system")
        self.assertIn("content", system_message)
        self.assertIn("type", system_message["content"])
        self.assertEqual(system_message["content"]["type"], "text")
        self.assertIn("text", system_message["content"])
        self.assertIn("python", system_message["content"]["text"])
        
        # Check user message
        user_message = prompt["messages"][1]
        self.assertEqual(user_message["role"], "user")
        self.assertIn("content", user_message)
        self.assertIn("type", user_message["content"])
        self.assertEqual(user_message["content"]["type"], "text")
        self.assertIn("text", user_message["content"])
        self.assertIn(code, user_message["content"]["text"])

    def test_get_git_commit_prompt(self):
        """Test the Git commit prompt."""
        changes = "Added new feature X"
        prompt = server.get_git_commit_prompt(changes=changes)
        
        # Check the structure
        self.assertIsInstance(prompt, dict)
        self.assertIn("messages", prompt)
        self.assertIsInstance(prompt["messages"], list)
        self.assertEqual(len(prompt["messages"]), 2)
        
        # Check system message
        system_message = prompt["messages"][0]
        self.assertEqual(system_message["role"], "system")
        self.assertIn("content", system_message)
        self.assertIn("type", system_message["content"])
        self.assertEqual(system_message["content"]["type"], "text")
        self.assertIn("text", system_message["content"])
        self.assertIn("commit", system_message["content"]["text"].lower())
        
        # Check user message
        user_message = prompt["messages"][1]
        self.assertEqual(user_message["role"], "user")
        self.assertIn("content", user_message)
        self.assertIn("type", user_message["content"])
        self.assertEqual(user_message["content"]["type"], "text")
        self.assertIn("text", user_message["content"])
        self.assertIn(changes, user_message["content"]["text"])


if __name__ == "__main__":
    unittest.main() 