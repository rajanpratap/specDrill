# app/utils.py
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def preprocess_openapi_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocess OpenAPI specification to extract relevant information
    """
    try:
        if not spec:
            return {}
        
        processed = {
            "info": spec.get("info", {}),
            "servers": spec.get("servers", []),
            "endpoints": []
        }
        
        paths = spec.get("paths", {})
        
        for path, path_item in paths.items():
            # Extract operations for this path
            for method, operation in path_item.items():
                if method.lower() in ["get", "post", "put", "patch", "delete", "head", "options"]:
                    endpoint = {
                        "path": path,
                        "method": method.upper(),
                        "operationId": operation.get("operationId", f"{method}_{path.replace('/', '_')}"),
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "parameters": extract_parameters(operation),
                        "requestBody": extract_request_body(operation),
                        "responses": extract_responses(operation),
                        "tags": operation.get("tags", [])
                    }
                    processed["endpoints"].append(endpoint)
        
        logger.info(f"Processed OpenAPI spec: {len(processed['endpoints'])} endpoints found")
        return processed
        
    except Exception as e:
        logger.error(f"Error processing OpenAPI spec: {e}")
        return {}

def extract_parameters(operation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract parameters from operation
    """
    parameters = {
        "path": {},
        "query": {},
        "header": {},
        "cookie": {}
    }
    
    for param in operation.get("parameters", []):
        param_in = param.get("in", "query")
        param_name = param.get("name", "unknown")
        param_info = {
            "type": param.get("schema", {}).get("type", "string"),
            "required": param.get("required", False),
            "description": param.get("description", ""),
            "example": param.get("example"),
            "schema": param.get("schema", {})
        }
        
        if param_in in parameters:
            parameters[param_in][param_name] = param_info
    
    return parameters

def extract_request_body(operation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract request body schema from operation
    """
    request_body = operation.get("requestBody", {})
    if not request_body:
        return {}
    
    content = request_body.get("content", {})
    
    # Extract schema for common content types
    for content_type in ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"]:
        if content_type in content:
            return {
                "content_type": content_type,
                "required": request_body.get("required", False),
                "schema": content[content_type].get("schema", {}),
                "description": request_body.get("description", "")
            }
    
    return {}

def extract_responses(operation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract response schemas from operation
    """
    responses = {}
    
    for status_code, response_info in operation.get("responses", {}).items():
        response_data = {
            "description": response_info.get("description", ""),
            "headers": response_info.get("headers", {}),
            "content": {}
        }
        
        content = response_info.get("content", {})
        for content_type, content_info in content.items():
            response_data["content"][content_type] = {
                "schema": content_info.get("schema", {}),
                "example": content_info.get("example")
            }
        
        responses[status_code] = response_data
    
    return responses

def validate_openapi_spec(spec: Dict[str, Any]) -> bool:
    """
    Basic validation of OpenAPI specification
    """
    try:
        # Check for required fields
        if "openapi" not in spec and "swagger" not in spec:
            logger.error("Missing OpenAPI/Swagger version")
            return False
        
        if "info" not in spec:
            logger.error("Missing info section")
            return False
        
        if "paths" not in spec:
            logger.error("Missing paths section")
            return False
        
        # Check if paths is not empty
        if not spec["paths"]:
            logger.error("Paths section is empty")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating OpenAPI spec: {e}")
        return False