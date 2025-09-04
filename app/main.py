# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List # <-- Add List to the import
import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .llm_client import generate_test_cases
from .utils import preprocess_openapi_spec

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Test Case Generator", version="1.0.0")

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class OpenAPIRequest(BaseModel):
    openapi_spec: Dict[str, Any]

class TestCaseResponse(BaseModel):
    test_cases: List[Dict[str, Any]] # <-- Change this to a List of dictionaries
    status: str
    message: str = ""

@app.get("/")
async def root():
    """Serve the main frontend page"""
    return FileResponse("frontend/index.html")

@app.post("/generate-tests", response_model=TestCaseResponse)
async def generate_tests(request: OpenAPIRequest):
    """
    Generate test cases from OpenAPI specification
    """
    try:
        # Validate input
        if not request.openapi_spec:
            raise HTTPException(status_code=400, detail="OpenAPI spec is required")
        
        logger.info("Processing OpenAPI specification...")
        
        # Preprocess the OpenAPI spec
        processed_spec = preprocess_openapi_spec(request.openapi_spec)
        
        if not processed_spec:
            raise HTTPException(status_code=400, detail="Invalid or empty OpenAPI specification")
        
        logger.info(f"Found {len(processed_spec.get('endpoints', []))} endpoints")
        
        # Generate test cases using LLM
        test_cases = await generate_test_cases(processed_spec)
        
        return TestCaseResponse(
            test_cases=test_cases,
            status="success",
            message=f"Generated test cases for {len(processed_spec.get('endpoints', []))} endpoints"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating test cases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "API Test Case Generator"}

@app.get("/test-gemini")
async def test_gemini():
    """Simple test endpoint for Gemini API"""
    try:
        from .llm_client import GEMINI_API_KEY, GEMINI_API_URL
        import httpx
        
        if GEMINI_API_KEY == "your-gemini-api-key-here":
            return {"error": "Gemini API key not configured"}
        
        # Simple test prompt
        payload = {
            "contents": [{
                "parts": [{
                    "text": "Return only this JSON: {\"test\": \"hello world\"}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 100,
                "responseMimeType": "application/json"
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json=payload
            )
            
            result = response.json()
            return {
                "status_code": response.status_code,
                "response": result
            }
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)