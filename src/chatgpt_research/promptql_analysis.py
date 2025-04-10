#!/usr/bin/env python
import os
import json
import argparse
import logging
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global client variable
client = None


def load_environment():
    """Load environment variables from .env file and initialize OpenAI client."""
    global client

    dotenv_path = Path(".env")
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
    else:
        logger.warning(
            ".env file not found, using system environment variables")

    # Validate required environment variables
    required_vars = ["OPENAI_API_KEY", "OPENAI_API_URL", "OPENAI_MODEL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}")

    # Initialize OpenAI client
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_URL")
    )


def infer_role_from_email(email: str) -> str:
    """
    Infer potential role/responsibility from email address using ChatGPT.

    Args:
        email: The email address to analyze

    Returns:
        A string describing the inferred role
    """
    logger.info(f"Inferring role for email: {email}")

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role": "system", "content": "You are an expert at inferring professional roles from email addresses. Provide concise, specific role descriptions."},
            {"role": "user", "content": f"Based on this email address, what professional role might this person have? Email: {email}. Respond with just the role or job title, no explanation."}
        ],
        temperature=0.3,
    )

    role = response.choices[0].message.content.strip()
    logger.info(f"Inferred role for {email}: {role}")
    return role


def generate_promptql_insights(email: str, role: str) -> Dict[str, Any]:
    """
    Generate PromptQL insights for the given email and inferred role.

    Args:
        email: The email address
        role: The inferred role or responsibility

    Returns:
        Dictionary containing use cases, example queries, and visualization ideas
    """
    logger.info(f"Generating PromptQL insights for {email} with role {role}")

    # Query for PromptQL use cases
    use_cases_response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role": "system",
                "content": "You are an expert in PromptQL, an AI tool that provides AI-powered insights from internal company structured data (e.g. databases, and APIs). Provide specific, practical use cases relevant to the role of the user."},
            {"role": "user", "content": f"For someone in the role of '{role}', what are 3 specific use cases where PromptQL could be valuable to discover insights from internal company structured data? Respond in JSON format with an array of use case objects, each with 'title' and 'description' fields."}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    use_cases = json.loads(use_cases_response.choices[0].message.content)

    # Generate example PromptQL queries
    queries_response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role": "system", "content": "You are an expert in PromptQL, a query language for large language models. Create specific, well-structured example queries."},
            {"role": "user", "content": f"Create 3 example PromptQL queries for someone in the role of '{role}' that would help them in their daily work. Each query should demonstrate a different PromptQL feature or capability. Respond in JSON format with an array of query objects, each with 'title', 'description', and 'query' fields."}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    queries = json.loads(queries_response.choices[0].message.content)

    # Generate visualization ideas
    viz_response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role": "system", "content": "You are an expert in data visualization and PromptQL. Suggest innovative but practical visualization approaches."},
            {"role": "user", "content": f"For a '{role}' using PromptQL queries, suggest 3 data visualizations that would effectively showcase the results and capabilities of PromptQL. These should be specific to their role and responsibilities. Respond in JSON format with an array of visualization objects, each with 'title', 'description', and 'visualization_type' fields."}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    visualizations = json.loads(viz_response.choices[0].message.content)

    # Combine all insights
    return {
        "email": email,
        "inferred_role": role,
        "use_cases": use_cases,
        "example_queries": queries,
        "visualizations": visualizations
    }


def load_role_context(context_file_path: str) -> Dict[str, str]:
    """
    Load role context from a file.

    Args:
        context_file_path: Path to the context file

    Returns:
        Dictionary mapping email addresses to their associated role context
    """
    if not os.path.exists(context_file_path):
        raise FileNotFoundError(f"Context file not found: {context_file_path}")

    logger.info(f"Loading role context from {context_file_path}")

    try:
        with open(context_file_path, 'r') as f:
            # Expected format is a JSON file with email:role mapping
            context = json.load(f)

        # Validate the structure (simple email->role dictionary)
        if not isinstance(context, dict):
            raise ValueError(
                "Context file must contain a JSON object (dictionary)")

        # Check if all values are strings
        invalid_entries = [email for email,
                           role in context.items() if not isinstance(role, str)]
        if invalid_entries:
            raise ValueError(
                f"Invalid role entries for emails: {', '.join(invalid_entries)}")

        logger.info(f"Loaded context for {len(context)} email(s)")
        return context
    except json.JSONDecodeError:
        raise ValueError(
            f"Context file is not valid JSON: {context_file_path}")


def analyze_emails(emails: List[str], role_context: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """
    Analyze a list of email addresses and generate PromptQL insights.

    Args:
        emails: List of email addresses to analyze
        role_context: Optional dictionary mapping emails to roles (bypasses inference)

    Returns:
        List of dictionaries containing analysis results for each email
    """
    results = []

    for email in emails:
        try:
            # If we have a context for this email, use it instead of inference
            if role_context and email in role_context:
                role = role_context[email]
                logger.info(f"Using provided role context for {email}: {role}")
            else:
                # Otherwise perform inference
                role = infer_role_from_email(email)

            insights = generate_promptql_insights(email, role)
            results.append(insights)
        except Exception as e:
            logger.error(f"Error processing email {email}: {e}")
            results.append({
                "email": email,
                "error": str(e)
            })

    return results


def save_results(results: List[Dict[str, Any]], output_format: str, output_file: str):
    """
    Save analysis results to a file in the specified format.

    Args:
        results: Analysis results
        output_format: 'json' or 'markdown'
        output_file: Path to output file
    """
    if output_format.lower() == 'json':
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    else:  # markdown
        with open(output_file, 'w') as f:
            f.write("# PromptQL Analysis Results\n\n")

            for result in results:
                f.write(f"## {result['email']}\n\n")
                f.write(f"**Inferred Role:** {result['inferred_role']}\n\n")

                f.write("### Use Cases\n\n")
                for use_case in result.get("use_cases", {}).get("use_cases", []):
                    f.write(f"#### {use_case['title']}\n")
                    f.write(f"{use_case['description']}\n\n")

                f.write("### Example Queries\n\n")
                for query in result.get("example_queries", {}).get("queries", []):
                    f.write(f"#### {query['title']}\n")
                    f.write(f"{query['description']}\n\n")
                    f.write("```\n")
                    f.write(f"{query['query']}\n")
                    f.write("```\n\n")

                f.write("### Visualization Ideas\n\n")
                for viz in result.get("visualizations", {}).get("visualizations", []):
                    f.write(f"#### {viz['title']}\n")
                    f.write(f"{viz['description']}\n\n")
                    f.write(
                        f"**Visualization Type:** {viz['visualization_type']}\n\n")

                f.write("---\n\n")

    logger.info(f"Results saved to {output_file}")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze email addresses for PromptQL applications")
    parser.add_argument("--emails", nargs="+", required=True,
                        help="List of email addresses to analyze")
    parser.add_argument("--output-format", choices=[
                        "json", "markdown"], default="json", help="Output format (json or markdown)")
    parser.add_argument("--output-file", default="promptql_results",
                        help="Output file name (without extension)")
    parser.add_argument(
        "--context-file", help="Path to a JSON file mapping emails to roles, bypassing the inference step")
    args = parser.parse_args()

    try:
        load_environment()

        # Load role context if provided
        role_context = None
        if args.context_file:
            role_context = load_role_context(args.context_file)

        # Ensure output file has the correct extension
        output_file = args.output_file
        if not output_file.endswith(f".{args.output_format}"):
            output_file = f"{output_file}.{args.output_format}"

        results = analyze_emails(args.emails, role_context)
        save_results(results, args.output_format, output_file)

        logger.info(
            f"Analysis completed successfully for {len(args.emails)} email addresses")
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
