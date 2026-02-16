"""
Utility functions for LLM framework.
"""
import json
import re
from typing import Any, Optional


def extract_json_from_response(response_text: str) -> Optional[dict]:
    """
    Extract JSON from agent response text.

    Handles various formats:
    - Pure JSON
    - JSON in markdown code blocks
    - JSON with surrounding text

    Args:
        response_text: Agent response text

    Returns:
        Parsed JSON dict or None if not found
    """
    if not response_text:
        return None

    # Try direct JSON parse first
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON in markdown code blocks
    json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_block_pattern, response_text, re.DOTALL)
    if matches:
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError:
            pass

    # Try to find raw JSON object
    json_pattern = r'\{[^}]*(?:\{[^}]*\}[^}]*)*\}'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    return None


def extract_html_from_response(response_text: str) -> Optional[str]:
    """
    Extract HTML from agent response.

    Args:
        response_text: Agent response text

    Returns:
        HTML string or None if not found
    """
    if not response_text:
        return None

    # Check if entire response is HTML
    if response_text.strip().startswith('<') and 'html' in response_text.lower():
        return response_text.strip()

    # Try to find HTML in code blocks
    html_block_pattern = r'```(?:html)?\s*(<!DOCTYPE.*?</html>)\s*```'
    matches = re.findall(html_block_pattern, response_text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0]

    # Try to find HTML without code blocks
    html_pattern = r'(<!DOCTYPE.*?</html>)'
    matches = re.findall(html_pattern, response_text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[0]

    return None


def truncate_for_logging(text: str, max_length: int = 500) -> str:
    """
    Truncate text for logging purposes.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def count_tokens_estimate(text: str) -> int:
    """
    Rough estimate of token count (not exact).

    Uses simple heuristic: ~4 characters per token.
    For accurate counts, use tiktoken library.

    Args:
        text: Text to count

    Returns:
        Estimated token count
    """
    return len(text) // 4


def format_error_for_display(error: Exception) -> str:
    """
    Format exception for user-friendly display.

    Args:
        error: Exception instance

    Returns:
        Formatted error string
    """
    error_type = type(error).__name__
    error_msg = str(error)
    return f"{error_type}: {error_msg}"


def merge_tool_responses(responses: list[dict]) -> dict:
    """
    Merge multiple tool responses into single structure.

    Args:
        responses: List of tool execution results

    Returns:
        Merged response dictionary
    """
    merged = {
        "tools_called": [],
        "successes": 0,
        "failures": 0,
        "results": {}
    }

    for response in responses:
        tool_name = response.get("tool", "unknown")
        merged["tools_called"].append(tool_name)

        if response.get("success"):
            merged["successes"] += 1
        else:
            merged["failures"] += 1

        merged["results"][tool_name] = response

    return merged
