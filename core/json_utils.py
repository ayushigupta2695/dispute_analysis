import json
import re

def safe_json_loads(text: str) -> dict:
    """
    Safely extract and parse JSON from LLM output.
    Handles:
    - Empty output
    - Markdown fenced JSON
    - Extra text before/after JSON
    """

    if not text or not text.strip():
        raise ValueError("Empty LLM response")

    # Remove markdown fences if present
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text)
        text = re.sub(r"```$", "", text)
        text = text.strip()

    # Extract JSON object using regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM output:\n{text}")

    json_text = match.group(0)

    return json.loads(json_text)
