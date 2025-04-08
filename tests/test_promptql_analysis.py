import unittest
from unittest.mock import patch, MagicMock
import json
import os
from io import StringIO
from pathlib import Path

from chatgpt_research.promptql_analysis import (
    load_environment,
    infer_role_from_email,
    generate_promptql_insights,
    analyze_emails,
    save_results,
    client
)


class TestPromptQLAnalysis(unittest.TestCase):

    def setUp(self):
        # Set up mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test_api_key',
            'OPENAI_API_URL': 'https://test.openai.com/v1',
            'OPENAI_MODEL': 'gpt-4-test'
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch('chatgpt_research.promptql_analysis.OpenAI')
    @patch('chatgpt_research.promptql_analysis.load_dotenv')
    @patch('pathlib.Path.exists')
    def test_load_environment(self, mock_exists, mock_load_dotenv, mock_openai_client):
        mock_exists.return_value = True
        load_environment()
        mock_load_dotenv.assert_called_once()
        mock_openai_client.assert_called_once_with(
            api_key='test_api_key',
            base_url='https://test.openai.com/v1'
        )

        # Test with missing environment variable
        with patch.dict('os.environ', {'OPENAI_API_KEY': '', 'OPENAI_API_URL': 'test', 'OPENAI_MODEL': 'test'}):
            with self.assertRaises(EnvironmentError):
                load_environment()

    @patch('chatgpt_research.promptql_analysis.client')
    def test_infer_role_from_email(self, mock_client):
        # Mock OpenAI API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Data Scientist"
        mock_client.chat.completions.create.return_value = mock_response

        role = infer_role_from_email("datascientist@example.com")
        self.assertEqual(role, "Data Scientist")

        # Verify OpenAI API was called with correct parameters
        mock_client.chat.completions.create.assert_called_once()
        args, kwargs = mock_client.chat.completions.create.call_args
        self.assertEqual(kwargs['model'], os.getenv("OPENAI_MODEL"))
        self.assertEqual(len(kwargs['messages']), 2)
        self.assertIn("datascientist@example.com",
                      kwargs['messages'][1]['content'])

    @patch('chatgpt_research.promptql_analysis.generate_promptql_insights')
    @patch('chatgpt_research.promptql_analysis.infer_role_from_email')
    def test_analyze_emails(self, mock_infer_role, mock_generate_insights):
        # Mock role inference and insights generation
        mock_infer_role.return_value = "Data Scientist"
        mock_insights = {
            "email": "test@example.com",
            "inferred_role": "Data Scientist",
            "use_cases": {"use_cases": []},
            "example_queries": {"queries": []},
            "visualizations": {"visualizations": []}
        }
        mock_generate_insights.return_value = mock_insights

        # Test successful analysis
        results = analyze_emails(["test@example.com"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], mock_insights)

        # Test handling of exceptions
        mock_infer_role.side_effect = Exception("Test error")
        results = analyze_emails(["test@example.com"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["email"], "test@example.com")
        self.assertEqual(results[0]["error"], "Test error")

    def test_save_results_json(self):
        # Create test results
        results = [{"email": "test@example.com",
                    "inferred_role": "Data Scientist"}]

        # Test JSON output
        with patch('builtins.open', create=True) as mock_open:
            mock_file = StringIO()
            mock_open.return_value.__enter__.return_value = mock_file

            save_results(results, "json", "test_output.json")

            mock_open.assert_called_once_with("test_output.json", "w")
            file_content = mock_file.getvalue()
            self.assertIn("test@example.com", file_content)

    def test_save_results_markdown(self):
        # Create test results with all required fields
        results = [{
            "email": "test@example.com",
            "inferred_role": "Data Scientist",
            "use_cases": {"use_cases": [{"title": "Test Case", "description": "Description"}]},
            "example_queries": {"queries": [{"title": "Test Query", "description": "Description", "query": "SELECT * FROM data"}]},
            "visualizations": {"visualizations": [{"title": "Test Viz", "description": "Description", "visualization_type": "Bar Chart"}]}
        }]

        # Test Markdown output
        with patch('builtins.open', create=True) as mock_open:
            mock_file = StringIO()
            mock_open.return_value.__enter__.return_value = mock_file

            save_results(results, "markdown", "test_output.md")

            mock_open.assert_called_once_with("test_output.md", "w")
            file_content = mock_file.getvalue()
            self.assertIn("# PromptQL Analysis Results", file_content)
            self.assertIn("## test@example.com", file_content)
            self.assertIn("**Inferred Role:** Data Scientist", file_content)
            self.assertIn("### Use Cases", file_content)
            self.assertIn("### Example Queries", file_content)
            self.assertIn("### Visualization Ideas", file_content)


if __name__ == "__main__":
    unittest.main()
