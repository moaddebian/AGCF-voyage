"""
Vercel serverless function handler for Django
This file serves as the entry point for Vercel serverless functions.
"""
import os
import sys
from pathlib import Path
from io import BytesIO

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Initialize Django (this happens once when the module is imported)
django_app = get_wsgi_application()

def handler(request):
    """
    Vercel serverless function handler
    Converts Vercel request format to WSGI format
    
    Args:
        request: Vercel request object with 'method', 'path', 'headers', 'body', 'queryStringParameters'
    
    Returns:
        dict: Vercel response with 'statusCode', 'headers', 'body'
    """
    from urllib.parse import urlencode
    
    # Extract request data
    method = request.get('method', 'GET')
    path = request.get('path', '/')
    headers = request.get('headers', {}) or {}
    body = request.get('body', b'') or b''
    query_params = request.get('queryStringParameters', {}) or {}
    
    # Build query string
    qs = urlencode(query_params) if query_params else ''
    
    # Parse host header
    host = headers.get('host', 'localhost')
    server_name = host.split(':')[0] if ':' in host else host
    server_port = host.split(':')[1] if ':' in host else '80'
    
    # Prepare body
    if isinstance(body, str):
        body_bytes = body.encode('utf-8')
    else:
        body_bytes = body
    
    # Build WSGI environ
    environ = {
        'REQUEST_METHOD': method,
        'SCRIPT_NAME': '',
        'PATH_INFO': path,
        'QUERY_STRING': qs,
        'CONTENT_TYPE': headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(body_bytes)),
        'SERVER_NAME': server_name,
        'SERVER_PORT': server_port,
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': BytesIO(body_bytes),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers
    for key, value in headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key_upper}'] = value
    
    # Response data
    response_status = [200]
    response_headers = []
    response_body = []
    
    def start_response(status, headers_list):
        """WSGI start_response callback"""
        response_status[0] = int(status.split()[0])
        response_headers[:] = headers_list
    
    # Call Django application
    try:
        response = django_app(environ, start_response)
        
        # Collect response body
        for chunk in response:
            if isinstance(chunk, bytes):
                response_body.append(chunk)
            else:
                response_body.append(chunk.encode('utf-8'))
        
        # Close response if it has a close method
        if hasattr(response, 'close'):
            response.close()
    except Exception as e:
        # Error handling
        import traceback
        error_msg = f"Error processing request: {str(e)}\n{traceback.format_exc()}"
        response_status[0] = 500
        response_body = [error_msg.encode('utf-8')]
        response_headers = [('Content-Type', 'text/plain; charset=utf-8')]
    
    # Build response headers dict
    response_headers_dict = {h[0]: h[1] for h in response_headers}
    
    # Join response body
    body_content = b''.join(response_body)
    
    return {
        'statusCode': response_status[0],
        'headers': response_headers_dict,
        'body': body_content.decode('utf-8', errors='ignore')
    }

