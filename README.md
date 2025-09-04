🚀 API Test Case Generator
A minimal web tool that generates exhaustive REST API test cases from OpenAPI/Swagger specifications using FastAPI backend and Gemini AI.

✨ Features
Simple Web Interface: Clean HTML/CSS/JS frontend for pasting OpenAPI specs
Intelligent Test Generation: Uses Google Gemini 2.0 Flash to generate comprehensive test cases
Comprehensive Coverage: Generates tests for valid, boundary, invalid, and null parameters
Edge Case Testing: Includes error scenarios (400, 401, 404, 500)
Easy Export: Download generated test cases as JSON or copy to clipboard
No Database Required: Stateless operation, no data persistence needed
🏗️ Project Structure
project/
├── app/
│   ├── main.py           # FastAPI main application
│   ├── llm_client.py     # Gemini API client
│   └── utils.py          # OpenAPI processing utilities
├── frontend/
│   ├── index.html        # Main web interface
│   ├── style.css         # Styling and responsive design
│   └── app.js           # Frontend JavaScript logic
├── requirements.txt      # Python dependencies
└── README.md            # This file
🚀 Quick Start
Prerequisites
Python 3.8 or higher
Google Gemini API key (optional - falls back to mock data)
Installation
Clone/Download the project files
Install Python dependencies:
bash
pip install -r requirements.txt
Set up your Gemini API key (optional):
bash
export GEMINI_API_KEY="your-actual-gemini-api-key"
Or set it directly in app/llm_client.py
Run the application:
bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Open your browser: Navigate to http://localhost:8000
📖 Usage
Paste OpenAPI Spec: Copy your OpenAPI/Swagger JSON specification into the textarea
Generate Test Cases: Click "Generate Test Cases" button
View Results: See the generated test cases in structured JSON format
Export: Download as JSON file or copy to clipboard
Sample Usage
The application includes a "Load Sample" button that provides a complete Pet Store API example to demonstrate functionality.

🔧 Configuration
Gemini API Setup
Get your API key from Google AI Studio
Set the environment variable:
bash
export GEMINI_API_KEY="your_api_key_here"
Mock Mode
If no API key is configured, the application automatically falls back to generating mock test cases based on the OpenAPI specification structure.

📝 API Endpoints
GET / - Serves the main web interface
POST /generate-tests - Generates test cases from OpenAPI spec
GET /health - Health check endpoint
Request Format
json
{
  "openapi_spec": {
    "openapi": "3.0.0",
    "info": { ... },
    "paths": { ... }
  }
}
Response Format
json
{
  "test_cases": {
    "testcase1": {
      "api_name": "listPets",
      "api_summary": "List all pets",
      "endpoint": "/pets",
      "method": "GET",
      "parameters": {
        "valid": { "limit": 10 },
        "boundary": { "limit": 1000 },
        "invalid": { "limit": "invalid" },
        "null": { "limit": null }
      },
      "expected_response": {
        "success": { "status": 200, "data": {} },
        "error_400": { "status": 400, "error": "Bad Request" }
      },
      "edge_cases": ["Test with empty parameters", "..."]
    }
  },
  "status": "success",
  "message": "Generated test cases for 3 endpoints"
}
🎨 Features Breakdown
Backend Features
OpenAPI Processing: Extracts endpoints, methods, parameters, and responses
LLM Integration: Uses Gemini 2.0 Flash for intelligent test case generation
Error Handling: Graceful fallback to mock data if API fails
CORS Support: Configured for web browser requests
Frontend Features
Responsive Design: Works on desktop and mobile devices
Real-time Validation: JSON format validation before submission
Loading States: Visual feedback during processing
Toast Notifications: User-friendly status messages
Auto-resize Textarea: Adapts to content size
🔍 Generated Test Case Types
The tool generates comprehensive test cases including:

Valid Parameters: Typical use cases with expected values
Boundary Testing: Edge values (min/max limits)
Invalid Data: Wrong data types, formats, or values
Null/Empty Testing: Missing or null parameter scenarios
Error Scenarios: HTTP 400, 401, 404, 500 responses
Edge Cases: Special situations and corner cases
🛠️ Development
Running in Development Mode
bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Project Dependencies
FastAPI: Modern web framework for APIs
Uvicorn: ASGI server for FastAPI
httpx: Async HTTP client for API calls
Pydantic: Data validation and settings management
🚀 Deployment
Docker (Optional)
Create a Dockerfile:

dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
Environment Variables
GEMINI_API_KEY: Your Google Gemini API key
PORT: Server port (default: 8000)
📄 License
This project is open source and available under the MIT License.

🤝 Contributing
Fork the repository
Create a feature branch
Make your changes
Test thoroughly
Submit a pull request
📞 Support
For issues or questions:

Check the health endpoint: http://localhost:8000/health
Review the console logs for debugging
Ensure your OpenAPI specification is valid JSON
Built with ❤️ using FastAPI, Gemini AI, and modern web technologies

