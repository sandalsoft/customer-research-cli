# ChatGPT PromptQL Analysis Tool

A Python application that leverages the ChatGPT API to analyze email addresses and generate insights about PromptQL application in different professional contexts.

## Features

- Infer potential roles and responsibilities from email addresses
- Generate tailored PromptQL use cases for each inferred role
- Create example PromptQL queries for specific use cases
- Conceptualize data visualizations to showcase PromptQL capabilities
- Output results in JSON or Markdown format

## Requirements

- Python 3.12 or higher
- OpenAI API key

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd chatgpt-research
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -e .
   ```

4. For development, install additional dependencies:
   ```
   pip install -e ".[dev]"
   ```

## Configuration

1. Copy the example environment file:

   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and add your OpenAI API key and other configurations:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_API_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4-turbo
   ```

## Usage

### Command Line Interface

Analyze a list of email addresses:

```
python promptql_analysis.py --emails user1@example.com user2@example.com
```

Output the results in Markdown format:

```
python promptql_analysis.py --emails user1@example.com --output-format markdown
```

Specify a custom output file:

```
python promptql_analysis.py --emails user1@example.com --output-file my_results
```

### Full Options

```
python promptql_analysis.py --help
```

This will display all available options and their descriptions.

## Example Output

### JSON Format

```json
[
  {
    "email": "datascientist@example.com",
    "inferred_role": "Data Scientist",
    "use_cases": {
      "use_cases": [
        {
          "title": "Dataset Exploration",
          "description": "Quickly analyze and understand patterns in large datasets."
        },
        ...
      ]
    },
    "example_queries": {
      "queries": [
        {
          "title": "Sentiment Analysis",
          "description": "Analyze sentiment in customer feedback data.",
          "query": "SELECT sentiment_score, COUNT(*) FROM feedback GROUP BY sentiment_score USING PromptQL"
        },
        ...
      ]
    },
    "visualizations": {
      "visualizations": [
        {
          "title": "Topic Distribution",
          "description": "Visualize the distribution of topics in a corpus of text.",
          "visualization_type": "Treemap"
        },
        ...
      ]
    }
  }
]
```

### Markdown Format

The Markdown output provides a more human-readable format with sections for each email address, including use cases, example queries, and visualization ideas.

## Running Tests

Run the test suite:

```
pytest
```

Run with coverage report:

```
pytest --cov=promptql_analysis
```

## Architecture

The application follows a functional programming approach, minimizing state and side effects. Key components:

1. **Environment Configuration**: Loads and validates environment variables
2. **Role Inference**: Uses ChatGPT to infer professional roles from email addresses
3. **PromptQL Insight Generation**: Creates use cases, queries, and visualization ideas
4. **Result Formatting**: Outputs results in JSON or Markdown

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
