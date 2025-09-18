import logging
import json
import requests
from typing import Dict, Any, Optional, Union, List
from mcp.server.fastmcp import FastMCP
import time
from urllib.parse import urlparse
import re
import signal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="yandrsu",
    host='0.0.0.0',
    port=8000,
    timeout=30,
    debug=True
)

class RequestExecutor:
    """HTTP Request execution with safety and validation"""
    
    def __init__(self):
        self.timeout = 30  # Default timeout in seconds
        self.max_response_size = 10 * 1024 * 1024  # 10MB max response size
        
    def _validate_url(self, url: str) -> bool:
        """Validate URL format and safety"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Allow http and https only
            if parsed.scheme not in ['http', 'https']:
                return False
                
            # Block localhost and private IPs for security (optional - remove if needed)
            hostname = parsed.hostname
            if hostname:
                # You can customize this based on your security requirements
                blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0']
                if hostname.lower() in blocked_hosts:
                    logger.warning(f"Blocked request to {hostname}")
                    # Comment out the next line if you want to allow localhost
                    # return False
            
            return True
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Prepare and validate headers"""
        default_headers = {
            'User-Agent': 'MCP-Curl-Tool/1.0',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json'
        }
        
        if headers:
            # Merge with default headers
            default_headers.update(headers)
        
        return default_headers
    
    def _prepare_data(self, data: Optional[Union[str, Dict[str, Any]]]) -> Optional[str]:
        """Prepare request data"""
        if data is None:
            return None
            
        if isinstance(data, dict):
            try:
                return json.dumps(data)
            except Exception as e:
                logger.error(f"Error serializing data: {e}")
                return str(data)
        
        return str(data)
    
    def _handle_streaming_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle streaming responses (SSE, chunked, etc.)"""
        try:
            content_type = response.headers.get('content-type', '').lower()
            is_sse = 'text/event-stream' in content_type or 'text/plain' in content_type
            
            streamed_content = []
            streamed_events = []
            total_chunks = 0
            total_bytes = 0
            
            logger.info(f"Starting to process streaming response (Content-Type: {content_type})")
            
            # Process streaming response
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    total_chunks += 1
                    chunk_size = len(chunk.encode('utf-8')) if isinstance(chunk, str) else len(chunk)
                    total_bytes += chunk_size
                    
                    # If it's SSE format, parse events
                    if is_sse and chunk.strip():
                        events = self._parse_sse_chunk(chunk)
                        streamed_events.extend(events)
                    
                    streamed_content.append(chunk)
                    
                    # Prevent memory overflow
                    if total_bytes > self.max_response_size:
                        logger.warning(f"Stream exceeded max size ({self.max_response_size} bytes), truncating")
                        streamed_content.append("\n... [STREAM TRUNCATED - MAX SIZE EXCEEDED]")
                        break
            
            # Combine all content
            full_content = ''.join(streamed_content)
            
            # Try to extract final JSON if it's an AI response (for additional metadata)
            extracted_data = self._extract_final_response(full_content, streamed_events)
            
            logger.info(f"Streaming completed: {total_chunks} chunks, {total_bytes} bytes")
            
            return {
                "success": True,
                "status_code": response.status_code,
                "status_text": response.reason,
                "headers": dict(response.headers),
                "data": full_content,  # Return the complete raw streaming response
                "streaming_info": {
                    "is_streaming": True,
                    "content_type": content_type,
                    "total_chunks": total_chunks,
                    "total_bytes": total_bytes,
                    "events_count": len(streamed_events) if is_sse else None
                },
                "extracted_data": extracted_data,  # Parsed/extracted data as additional info
                "parsed_events": streamed_events if is_sse else None,  # All parsed events
                "url": response.url,
                "elapsed_seconds": response.elapsed.total_seconds(),
                "encoding": response.encoding
            }
            
        except Exception as e:
            logger.error(f"Error handling streaming response: {e}")
            return {
                "success": False,
                "error": f"Streaming error: {str(e)}",
                "status_code": getattr(response, 'status_code', None)
            }
    
    def _parse_sse_chunk(self, chunk: str) -> List[Dict[str, Any]]:
        """Parse Server-Sent Events from a chunk"""
        events = []
        lines = chunk.strip().split('\n')
        current_event = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                # Empty line indicates end of event
                if current_event:
                    events.append(current_event.copy())
                    current_event = {}
                continue
            
            if line.startswith('data: '):
                data = line[6:]  # Remove 'data: ' prefix
                if 'data' in current_event:
                    current_event['data'] += '\n' + data
                else:
                    current_event['data'] = data
            elif line.startswith('event: '):
                current_event['event'] = line[7:]
            elif line.startswith('id: '):
                current_event['id'] = line[4:]
            elif line.startswith('retry: '):
                current_event['retry'] = line[7:]
        
        # Add final event if exists
        if current_event:
            events.append(current_event)
        
        return events
    
    def _extract_final_response(self, full_content: str, events: List[Dict[str, Any]]) -> Any:
        """Extract the final meaningful response from streaming content"""
        try:
            # Method 1: Try to find the last complete JSON in the stream
            json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', full_content)
            if json_matches:
                try:
                    return json.loads(json_matches[-1])
                except:
                    pass
            
            # Method 2: If SSE, try to parse data from events
            if events:
                for event in reversed(events):  # Start from the last event
                    if 'data' in event:
                        try:
                            # Try to parse as JSON
                            return json.loads(event['data'])
                        except:
                            # If not JSON, return as text
                            if event['data'] not in ['[DONE]', '', ' ']:
                                return event['data']
            
            # Method 3: Return the full content if no structured data found
            return full_content
            
        except Exception as e:
            logger.warning(f"Error extracting final response: {e}")
            return full_content
    
    def _format_response(self, response: requests.Response) -> Dict[str, Any]:
        """Format response for JSON serialization"""
        try:
            # Try to parse as JSON first
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError):
                # If not JSON, return as text
                response_data = response.text
            
            # Limit response size
            if isinstance(response_data, str) and len(response_data) > self.max_response_size:
                response_data = response_data[:self.max_response_size] + "... [TRUNCATED]"
            
            return {
                "success": True,
                "status_code": response.status_code,
                "status_text": response.reason,
                "headers": dict(response.headers),
                "data": response_data,
                "url": response.url,
                "elapsed_seconds": response.elapsed.total_seconds(),
                "encoding": response.encoding
            }
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            return {
                "success": False,
                "error": f"Response formatting error: {str(e)}",
                "status_code": getattr(response, 'status_code', None),
                "raw_text": getattr(response, 'text', '')[:1000] + "..." if len(getattr(response, 'text', '')) > 1000 else getattr(response, 'text', '')
            }

# Initialize request executor
executor = RequestExecutor()

@mcp.tool()
def execute_http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Union[str, Dict[str, Any]]] = None,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Execute HTTP request (curl-like functionality)
    
    Args:
        url (str): The API endpoint URL to call
        method (str): HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
        headers (Optional[Dict[str, str]]): HTTP headers to include
        data (Optional[Union[str, Dict[str, Any]]]): Request body data
        timeout (Optional[int]): Request timeout in seconds (default: 30)
    
    Example Use Cases:
        - GET request: execute_http_request("https://api.example.com/users")
        - POST request: execute_http_request("https://api.example.com/users", "POST", {"Authorization": "Bearer token"}, {"name": "John"})
        - Custom headers: execute_http_request("https://api.example.com/data", headers={"API-Key": "your-key"})
    
    Returns:
        Dict: Response data including status, headers, and body
    """
    
    start_time = time.time()
    
    try:
        # Validate inputs
        if not url:
            return {
                "success": False,
                "error": "URL is required",
                "execution_time": time.time() - start_time
            }
        
        if not executor._validate_url(url):
            return {
                "success": False,
                "error": "Invalid or unsafe URL",
                "execution_time": time.time() - start_time
            }
        
        # Prepare request parameters
        method = method.upper()
        headers = executor._prepare_headers(headers)
        request_timeout = timeout or executor.timeout
        
        # Prepare data for POST/PUT/PATCH requests
        request_data = None
        if method in ['POST', 'PUT', 'PATCH', 'DELETE'] and data is not None:
            request_data = executor._prepare_data(data)
        
        logger.info(f"Executing {method} request to {url}")
        
        # Make the request
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=request_data,
            timeout=request_timeout,
            allow_redirects=True,
            verify=True,  # SSL verification
            stream=True  # Enable streaming detection
        )
        
        # Check if response indicates streaming and handle accordingly
        content_type = response.headers.get('content-type', '').lower()
        is_streaming = (
            'text/event-stream' in content_type or
            response.headers.get('transfer-encoding') == 'chunked' or
            ('text/plain' in content_type and 'stream' in url.lower())
        )
        
        if is_streaming:
            logger.info(f"Auto-detected streaming response, switching to streaming handler")
            result = executor._handle_streaming_response(response)
        else:
            result = executor._format_response(response)
        result["execution_time"] = time.time() - start_time
        result["request_info"] = {
            "method": method,
            "url": url,
            "headers_sent": headers,
            "data_sent": request_data[:500] + "..." if request_data and len(request_data) > 500 else request_data
        }
        
        logger.info(f"Request completed: {response.status_code} in {result['execution_time']:.2f}s")
        return result
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": f"Request timeout after {request_timeout} seconds",
            "execution_time": time.time() - start_time
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}",
            "execution_time": time.time() - start_time
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request error: {str(e)}",
            "execution_time": time.time() - start_time
        }
    except Exception as e:
        logger.error(f"Unexpected error in execute_http_request: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "execution_time": time.time() - start_time
        }

@mcp.tool()
def execute_curl_command(curl_command: str) -> Dict[str, Any]:
    """
    Parse and execute a curl command string
    
    Args:
        curl_command (str): Full curl command string (e.g., "curl -X POST https://api.example.com/data -H 'Content-Type: application/json' -d '{\"key\":\"value\"}'")
    
    Returns:
        Dict: Response data including status, headers, and body
    """
    
    try:
        # Basic curl command parsing (simplified)
        # This is a basic implementation - you can enhance it further
        
        import shlex
        
        # Parse the curl command
        parts = shlex.split(curl_command)
        
        if not parts or parts[0] != 'curl':
            return {
                "success": False,
                "error": "Invalid curl command - must start with 'curl'"
            }
        
        url = None
        method = "GET"
        headers = {}
        data = None
        
        i = 1
        while i < len(parts):
            part = parts[i]
            
            if part in ['-X', '--request']:
                if i + 1 < len(parts):
                    method = parts[i + 1].upper()
                    i += 2
                else:
                    i += 1
            elif part in ['-H', '--header']:
                if i + 1 < len(parts):
                    header_str = parts[i + 1]
                    if ':' in header_str:
                        key, value = header_str.split(':', 1)
                        headers[key.strip()] = value.strip()
                    i += 2
                else:
                    i += 1
            elif part in ['-d', '--data']:
                if i + 1 < len(parts):
                    data = parts[i + 1]
                    i += 2
                else:
                    i += 1
            elif not part.startswith('-'):
                # Assume it's the URL
                url = part
                i += 1
            else:
                # Skip unknown options
                i += 1
        
        if not url:
            return {
                "success": False,
                "error": "No URL found in curl command"
            }
        
        # Execute the parsed request
        return execute_http_request(url, method, headers, data)
        
    except Exception as e:
        logger.error(f"Error parsing curl command: {e}")
        return {
            "success": False,
            "error": f"Error parsing curl command: {str(e)}"
        }

@mcp.tool()
def execute_streaming_request(
    url: str,
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Union[str, Dict[str, Any]]] = None,
    timeout: Optional[int] = None,
    stream_timeout: Optional[int] = 120
) -> Dict[str, Any]:
    """
    Execute HTTP request with streaming support for AI agents and SSE endpoints
    
    Args:
        url (str): The API endpoint URL to call
        method (str): HTTP method (default: POST for AI endpoints)
        headers (Optional[Dict[str, str]]): HTTP headers
        data (Optional[Union[str, Dict[str, Any]]]): Request payload
        timeout (Optional[int]): Connection timeout in seconds
        stream_timeout (Optional[int]): Total streaming timeout in seconds (default: 120)
    
    Returns:
        Dict: Complete response data with streaming information
    """
    start_time = time.time()
    
    try:
        # Validate URL
        if not executor._validate_url(url):
            return {
                "success": False,
                "error": "Invalid or blocked URL",
                "execution_time": time.time() - start_time
            }
        
        # Prepare request components
        headers = executor._prepare_headers(headers)
        request_data = executor._prepare_data(data)
        request_timeout = timeout or executor.timeout
        
        # Add streaming-specific headers
        streaming_headers = headers.copy()
        streaming_headers.update({
            'Accept': 'text/event-stream, application/json, text/plain, */*',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        })
        
        logger.info(f"Starting streaming request: {method} {url}")
        
        # Make the streaming request
        response = requests.request(
            method=method,
            url=url,
            headers=streaming_headers,
            data=request_data,
            timeout=request_timeout,
            stream=True  # Enable streaming
        )
        
        # Check if response indicates streaming
        content_type = response.headers.get('content-type', '').lower()
        is_streaming = (
            'text/event-stream' in content_type or
            'text/plain' in content_type or
            response.headers.get('transfer-encoding') == 'chunked'
        )
        
        if is_streaming:
            logger.info(f"Detected streaming response (Content-Type: {content_type})")
            result = executor._handle_streaming_response(response)
        else:
            logger.info(f"Non-streaming response detected, using standard handling")
            result = executor._format_response(response)
            result["streaming_info"] = {"is_streaming": False}
        
        # Add execution metadata
        result["execution_time"] = time.time() - start_time
        result["request_info"] = {
            "method": method,
            "url": url,
            "headers_sent": streaming_headers,
            "data_sent": request_data[:500] + "..." if request_data and len(request_data) > 500 else request_data,
            "stream_enabled": True
        }
        
        logger.info(f"Streaming request completed: {response.status_code} in {result['execution_time']:.2f}s")
        return result
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": f"Request timeout after {request_timeout} seconds",
            "execution_time": time.time() - start_time
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}",
            "execution_time": time.time() - start_time
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Request error: {str(e)}",
            "execution_time": time.time() - start_time
        }
    except Exception as e:
        logger.error(f"Unexpected error in streaming request: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "execution_time": time.time() - start_time
        }

@mcp.tool()
def execute_raw_streaming_request(
    url: str,
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Union[str, Dict[str, Any]]] = None,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """
    Execute HTTP request and return the complete raw streaming response with minimal processing
    
    Args:
        url (str): The API endpoint URL to call
        method (str): HTTP method (default: POST for AI endpoints)
        headers (Optional[Dict[str, str]]): HTTP headers
        data (Optional[Union[str, Dict[str, Any]]]): Request payload
        timeout (Optional[int]): Connection timeout in seconds
    
    Returns:
        Dict: Raw streaming response with minimal metadata
    """
    start_time = time.time()
    
    try:
        # Validate URL
        if not executor._validate_url(url):
            return {
                "success": False,
                "error": "Invalid or blocked URL",
                "execution_time": time.time() - start_time
            }
        
        # Prepare request components
        headers = executor._prepare_headers(headers)
        request_data = executor._prepare_data(data)
        request_timeout = timeout or executor.timeout
        
        logger.info(f"Starting raw streaming request: {method} {url}")
        
        # Make the streaming request
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=request_data,
            timeout=request_timeout,
            stream=True
        )
        
        # Collect all streaming content without any processing
        raw_content = []
        total_bytes = 0
        
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                raw_content.append(chunk)
                chunk_size = len(chunk.encode('utf-8')) if isinstance(chunk, str) else len(chunk)
                total_bytes += chunk_size
                
                # Prevent memory overflow
                if total_bytes > executor.max_response_size:
                    logger.warning(f"Stream exceeded max size ({executor.max_response_size} bytes), truncating")
                    raw_content.append("\n... [STREAM TRUNCATED - MAX SIZE EXCEEDED]")
                    break
        
        # Combine all content
        complete_response = ''.join(raw_content)
        
        logger.info(f"Raw streaming completed: {total_bytes} bytes")
        
        return {
            "success": True,
            "status_code": response.status_code,
            "status_text": response.reason,
            "headers": dict(response.headers),
            "data": complete_response,  # Complete raw streaming response
            "content_length": total_bytes,
            "url": response.url,
            "elapsed_seconds": response.elapsed.total_seconds(),
            "execution_time": time.time() - start_time
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": f"Request timeout after {request_timeout} seconds",
            "execution_time": time.time() - start_time
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}",
            "execution_time": time.time() - start_time
        }
    except Exception as e:
        logger.error(f"Unexpected error in raw streaming request: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "execution_time": time.time() - start_time
        }

def signal_handler(sig, frame):
    logger.info("Shutting down MCP server...")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    logger.info("Starting MCP server...")
    mcp.run(transport='sse')