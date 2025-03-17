#!/usr/bin/env python3
# tests/test_client.py
"""Tests for the MCP client implementation."""

import unittest
from unittest.mock import MagicMock, patch

from client import MCPDemoClient, OllamaClient


class TestOllamaClient(unittest.TestCase):
    """Test cases for the Ollama Client."""

    def setUp(self):
        """Set up test fixtures."""
        self.ollama = OllamaClient("http://test-ollama:11434", "test-model")
        # Mock the requests.post method
        self.post_patcher = patch("requests.post")
        self.mock_post = self.post_patcher.start()
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.post_patcher.stop()

    def test_generate(self):
        """Test the generate method."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Generated text"}
        self.mock_post.return_value = mock_response
        
        # Call the method
        result = self.ollama.generate("Test prompt", "System message")
        
        # Check that requests.post was called correctly
        self.mock_post.assert_called_once()
        args, kwargs = self.mock_post.call_args
        self.assertEqual(args[0], "http://test-ollama:11434/api/generate")
        self.assertEqual(kwargs["json"]["model"], "test-model")
        self.assertEqual(kwargs["json"]["prompt"], "Test prompt")
        self.assertEqual(kwargs["json"]["system"], "System message")
        
        # Check the result
        self.assertEqual(result, "Generated text")

    def test_process_mcp_prompt(self):
        """Test the process_mcp_prompt method."""
        # Set up mock response for generate
        self.ollama.generate = MagicMock(return_value="Generated response")
        
        # Test with valid prompt data
        prompt_data = {
            "messages": [
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": "System message"
                    }
                },
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "User message"
                    }
                }
            ]
        }
        
        result = self.ollama.process_mcp_prompt(prompt_data)
        
        # Check that generate was called correctly
        self.ollama.generate.assert_called_once_with("User message", "System message")
        
        # Check the result
        self.assertEqual(result, "Generated response")
        
        # Test with invalid prompt data
        self.ollama.generate.reset_mock()
        result = self.ollama.process_mcp_prompt({})
        self.assertEqual(result, "Error: Invalid prompt format")
        self.ollama.generate.assert_not_called()


class TestMCPDemoClient(unittest.TestCase):
    """Test cases for the MCP Demo Client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MCPDemoClient("http://test-server:8000", "http://test-ollama:11434", "test-model")
        # Mock the MCP client
        self.client.client = MagicMock()
        # Mock the Ollama client
        self.client.ollama = MagicMock()

    def test_transform_to_ancient_latin(self):
        """Test the ancient Latin text transformation client method."""
        # Set up mock return value
        self.client.client.invoke.return_value = "Thy quickus brown fox jumps over thy lazy dog."
        
        # Call the method
        result = self.client.transform_to_ancient_latin("The quick brown fox jumps over the lazy dog.")
        
        # Check that the client was called correctly
        self.client.client.invoke.assert_called_once_with(
            "ancient_latin_text", 
            {"text": "The quick brown fox jumps over the lazy dog."}
        )
        
        # Check the result
        self.assertEqual(result, "Thy quickus brown fox jumps over thy lazy dog.")

    def test_get_ancient_latin_text_resource(self):
        """Test the ancient Latin text resource client method."""
        # Set up mock return value
        self.client.client.get.return_value = "Thy quickus brown fox jumps over thy lazy dog."
        
        # Call the method
        result = self.client.get_ancient_latin_text_resource("The quick brown fox jumps over the lazy dog.")
        
        # Check that the client was called correctly
        self.client.client.get.assert_called_once_with(
            "ancientlatin://The quick brown fox jumps over the lazy dog."
        )
        
        # Check the result
        self.assertEqual(result, "Thy quickus brown fox jumps over thy lazy dog.")

    def test_get_greek_gods(self):
        """Test the Greek gods client method."""
        # Set up mock return value
        mock_gods = [
            {"name": "Zeus", "domain": "Sky and Thunder", "symbol": "Lightning bolt", "roman_name": "Jupiter"},
            {"name": "Poseidon", "domain": "Sea and Earthquakes", "symbol": "Trident", "roman_name": "Neptune"}
        ]
        self.client.client.get.return_value = mock_gods
        
        # Call the method with no limit
        result = self.client.get_greek_gods()
        
        # Check that the client was called correctly
        self.client.client.get.assert_called_with("gods://", {})
        
        # Check the result
        self.assertEqual(result, mock_gods)
        
        # Reset mock
        self.client.client.get.reset_mock()
        
        # Call the method with a limit
        result = self.client.get_greek_gods(limit=5)
        
        # Check that the client was called correctly
        self.client.client.get.assert_called_with("gods://", {"limit": 5})

    def test_get_greeting(self):
        """Test the greeting client method."""
        # Set up mock return value
        self.client.client.get.return_value = "Hello, Test!"
        
        # Call the method
        result = self.client.get_greeting("Test")
        
        # Check that the client was called correctly
        self.client.client.get.assert_called_once_with("greeting://Test")
        
        # Check the result
        self.assertEqual(result, "Hello, Test!")

    def test_chat_about_mcp(self):
        """Test the MCP chat client method."""
        # Set up mock return values
        mock_prompt = {
            "messages": [
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": "You are an MCP expert assistant."
                    }
                },
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Please tell me about MCP in general"
                    }
                }
            ]
        }
        self.client.client.get.return_value = mock_prompt
        self.client.ollama.process_mcp_prompt.return_value = "MCP is a protocol for controlling AI models."
        
        # Call the method
        result = self.client.chat_about_mcp("What is MCP?")
        
        # Check that the clients were called correctly
        self.client.client.get.assert_called_with("mcp_expert", {})
        self.client.ollama.process_mcp_prompt.assert_called_with(mock_prompt)
        
        # Check the result
        self.assertEqual(result, "MCP is a protocol for controlling AI models.")
        
        # Test with topic
        self.client.client.get.reset_mock()
        self.client.ollama.process_mcp_prompt.reset_mock()
        
        result = self.client.chat_about_mcp("Tell me about tools in MCP")
        
        self.client.client.get.assert_called_with("mcp_expert", {"topic": "tools"})
        self.client.ollama.process_mcp_prompt.assert_called_with(mock_prompt)

    def test_get_code_review(self):
        """Test the code review client method."""
        # Set up mock return values
        mock_prompt = {
            "messages": [
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": "You are an expert python developer."
                    }
                },
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Please review this code."
                    }
                }
            ]
        }
        self.client.client.get.return_value = mock_prompt
        self.client.ollama.process_mcp_prompt.return_value = "This code looks good."
        
        # Call the method
        code = "def hello():\n    print('Hello, world!')"
        result = self.client.get_code_review(code)
        
        # Check that the clients were called correctly
        self.client.client.get.assert_called_with("code_review", {"code": code, "language": "python"})
        self.client.ollama.process_mcp_prompt.assert_called_with(mock_prompt)
        
        # Check the result
        self.assertEqual(result, "This code looks good.")

    def test_get_commit_message(self):
        """Test the commit message client method."""
        # Set up mock return values
        mock_prompt = {
            "messages": [
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": "You are an expert at writing commit messages."
                    }
                },
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Generate a commit message."
                    }
                }
            ]
        }
        self.client.client.get.return_value = mock_prompt
        self.client.ollama.process_mcp_prompt.return_value = "feat: add new feature"
        
        # Call the method
        changes = "Added new feature X"
        result = self.client.get_commit_message(changes)
        
        # Check that the clients were called correctly
        self.client.client.get.assert_called_with("git_commit", {"changes": changes})
        self.client.ollama.process_mcp_prompt.assert_called_with(mock_prompt)
        
        # Check the result
        self.assertEqual(result, "feat: add new feature")


if __name__ == "__main__":
    unittest.main() 