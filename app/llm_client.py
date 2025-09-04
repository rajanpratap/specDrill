# app/llm_client.py
import httpx
import json
import os
import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

# --- NEW AND IMPROVED PROMPT TEMPLATE ---
PROMPT_TEMPLATE = """
You are a meticulous and expert QA Automation Engineer specializing in API testing and security.
Your task is to analyze the provided OpenAPI specification and generate a comprehensive, exhaustive suite of test cases.

The output MUST be a single, strictly valid JSON array. Do not include any explanatory text, markdown formatting like ```json, or anything outside of the JSON structure.

The JSON structure must follow this exact schema for each endpoint in the specification:
[
  {{
    "endpoint": "string (e.g., /users/{{id}})",
    "method": "string (e.g., GET, POST)",
    "summary": "string (from OpenAPI spec)",
    "operationId": "string (from OpenAPI spec)",
    "testCases": [
      {{
        "testId": "string (a unique readable ID, e.g., TC001_GetUser_HappyPath)",
        "description": "string (A clear, one-sentence objective for the test case)",
        "category": "string (One of: 'Positive', 'Negative', 'Boundary', 'DataValidation', 'Security', 'Authentication')",
        "request": {{
          "pathParams": {{ "key": "value" }},
          "queryParams": {{ "key": "value" }},
          "headers": {{ "Content-Type": "application/json", "Authorization": "Bearer <VALID_TOKEN>" }},
          "body": {{ /* JSON body or appropriate payload based on the test */ }}
        }},
        "expectedResponse": {{
          "statusCode": "integer (e.g., 200, 400, 404)",
          "bodyContract": {{ /* A JSON schema, key-value pairs, or a description of the expected response body structure */ }},
          "headers": {{ "key": "value" }}
        }}
      }}
    ]
  }}
]

For each endpoint, generate test cases covering ALL of the following scenarios where applicable:

1.  **Positive Scenarios (Happy Path):**
    - Test with all required fields correctly filled.
    - Test with required and optional fields correctly filled.

2.  **Negative Scenarios & Data Validation:**
    - Test with missing required fields (in body, query, path, headers).
    - Test with incorrect data types (e.g., string for a number, number for a boolean).
    - Test with invalid enum values.
    - Test with null values for non-nullable fields.
    - Test with empty strings/arrays for fields that require data.
    - Test with malformed JSON in the request body.

3.  **Boundary Value Analysis (BVA):**
    - For numeric fields: test with minimum, maximum, just below min, and just above max values.
    - For string fields: test with minimum and maximum length, empty string, and a very long string.
    - For arrays: test with empty array, array with one item, and array at max capacity (if defined).

4.  **Authentication & Authorization:**
    - Test without any authentication token.
    - Test with an invalid or expired token.
    - Test with a token that lacks the necessary permissions/scope (simulate 403 Forbidden).

5.  **Security Snippets:**
    - For string parameters, include basic payloads to check for vulnerabilities like SQL Injection (e.g., `' OR 1=1 --`) and XSS (e.g., `<script>alert(1)</script>`).

6.  **Error Handling:**
    - Explicitly create tests that should trigger defined error responses (e.g., 400, 404, 409, 422) based on the spec.

Now, generate the test cases for the following OpenAPI Specification:
{spec}
"""

async def generate_test_cases(processed_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate test cases using Gemini API
    """
    try:
        spec_json = json.dumps(processed_spec, indent=2)
        prompt = PROMPT_TEMPLATE.format(spec=spec_json)

        if GEMINI_API_KEY == "your-gemini-api-key-here":
            logger.warning("Gemini API key not configured, using mock response")
            return generate_mock_test_cases(processed_spec)

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2, # Slightly increased for creativity within constraints
                "maxOutputTokens": 8192, # Increased for more detailed outputs
                "responseMimeType": "application/json"
            }
        }

        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=120.0) as client: # Increased timeout
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json=payload,
                headers=headers
            )

        if response.status_code != 200:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return generate_mock_test_cases(processed_spec)

        result = response.json()

        if "candidates" not in result or not result["candidates"]:
            logger.error("No candidates in Gemini response")
            return generate_mock_test_cases(processed_spec)

        generated_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        cleaned_text = cleanup_json_text(generated_text)

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Raw response: {generated_text}")
            return generate_mock_test_cases(processed_spec)

    except Exception as e:
        logger.error(f"Unexpected error calling Gemini API: {e}")
        return generate_mock_test_cases(processed_spec)


def cleanup_json_text(text: str) -> str:
    """
    Extract first valid JSON block from text, removing markdown and junk.
    """
    # remove markdown code fencing
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text)
        text = text.replace("```", "")

    # find first { ... } or [ ... ] block
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if match:
        return match.group(0)
    return text


def generate_mock_test_cases(processed_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate mock test cases when Gemini API is unavailable, matching the new structure.
    """
    logger.info("Generating mock test cases...")

    mock_endpoints = []
    endpoints = processed_spec.get("endpoints", [])

    for i, endpoint in enumerate(endpoints, 1):
        mock_endpoint_data = {
            "endpoint": endpoint.get("path", "/"),
            "method": endpoint.get("method", "GET").upper(),
            "summary": endpoint.get("summary", f"Mock summary for {endpoint.get('path', 'unknown')}"),
            "operationId": endpoint.get("operationId", f"mock_op_{i}"),
            "testCases": [
                {
                    "testId": f"TC{i:03d}_Mock_HappyPath",
                    "description": "Verify the API works correctly with valid required parameters.",
                    "category": "Positive",
                    "request": {
                        "pathParams": {"id": 123},
                        "queryParams": {"filter": "active"},
                        "headers": {"Content-Type": "application/json", "Authorization": "Bearer <VALID_TOKEN>"},
                        "body": {"name": "Test Item", "value": 100}
                    },
                    "expectedResponse": {
                        "statusCode": 200,
                        "bodyContract": {"id": "integer", "name": "string", "status": "string"},
                        "headers": {"Content-Type": "application/json"}
                    }
                },
                {
                    "testId": f"TC{i:03d}_Mock_MissingAuth",
                    "description": "Verify the API returns an unauthorized error when the auth token is missing.",
                    "category": "Authentication",
                    "request": {
                        "pathParams": {}, "queryParams": {},
                        "headers": {"Content-Type": "application/json"},
                        "body": {}
                    },
                    "expectedResponse": {
                        "statusCode": 401,
                        "bodyContract": {"error": "Unauthorized", "message": "string"},
                        "headers": {}
                    }
                }
            ]
        }
        mock_endpoints.append(mock_endpoint_data)

    return mock_endpoints