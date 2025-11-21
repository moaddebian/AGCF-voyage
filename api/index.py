"""
Vercel serverless function handler for Django
This handler works with Vercel's Python runtime
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Initialize PyMySQL BEFORE Django settings (critical for Vercel)
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass  # PyMySQL not available, will use SQLite or fail gracefully

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agcf_voyage.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application

# Initialize Django (lazy loading to avoid errors on import)
django_app = None

def get_django_app():
    """Lazy load Django app"""
    global django_app
    if django_app is None:
        django_app = get_wsgi_application()
    return django_app

def handler(request):
    """
    Vercel serverless function handler
    Compatible with Vercel's Python runtime v2
    
    Args:
        request: Vercel request object (dict)
    """
    from io import BytesIO
    from urllib.parse import urlencode, unquote
    
    try:
        # Get Django app (lazy load)
        app = get_django_app()
        
        # Extract request data from Vercel format
        # Vercel passes request as dict with: method, url, headers, body, query
        method = request.get('method', 'GET')
        url = request.get('url', '/')
        headers = request.get('headers', {}) or {}
        body = request.get('body', '') or ''
        query = request.get('query', {}) or {}
        
        # Normalize path
        if isinstance(url, str):
            if '?' in url:
                path = unquote(url.split('?')[0])
            else:
                path = unquote(url)
        else:
            path = '/'
        
        # Build query string
        if query and isinstance(query, dict):
            qs = urlencode(query)
        else:
            qs = ''
        
        # Parse host from headers
        host = headers.get('host', 'localhost')
        if isinstance(host, str):
            server_name = host.split(':')[0] if ':' in host else host
            server_port = host.split(':')[1] if ':' in host else '80'
        else:
            server_name = 'localhost'
            server_port = '80'
        
        # Prepare body
        if isinstance(body, str):
            body_bytes = body.encode('utf-8')
        elif isinstance(body, bytes):
            body_bytes = body
        else:
            body_bytes = b''
        
        # Build WSGI environ
        environ = {
            'REQUEST_METHOD': str(method).upper(),
            'SCRIPT_NAME': '',
            'PATH_INFO': path,
            'QUERY_STRING': qs,
            'CONTENT_TYPE': str(headers.get('content-type', '')),
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
            if key and value:
                key_upper = key.upper().replace('-', '_')
                if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                    environ[f'HTTP_{key_upper}'] = str(value)
        
        # Response containers
        response_status = [200]
        response_headers = []
        response_body = []
        
        def start_response(status, headers_list):
            """WSGI start_response callback"""
            try:
                response_status[0] = int(status.split()[0])
            except (ValueError, AttributeError):
                response_status[0] = 200
            response_headers[:] = headers_list
        
        # Call Django application
        django_response = app(environ, start_response)
        
        # Collect response body
        for chunk in django_response:
            if isinstance(chunk, bytes):
                response_body.append(chunk)
            else:
                response_body.append(str(chunk).encode('utf-8'))
        
        # Close response if it has a close method
        if hasattr(django_response, 'close'):
            try:
                django_response.close()
            except:
                pass
        
        # Build response headers dict
        response_headers_dict = {}
        for header_name, header_value in response_headers:
            response_headers_dict[str(header_name)] = str(header_value)
        
        # Join response body
        body_content = b''.join(response_body)
        
        return {
            'statusCode': response_status[0],
            'headers': response_headers_dict,
            'body': body_content.decode('utf-8', errors='ignore')
        }
        
    except Exception as e:
        # Error handling - return error page
        import traceback
        error_trace = traceback.format_exc()
        error_msg = str(e)
        
        # Log error (will appear in Vercel logs)
        print(f"ERROR in handler: {error_msg}")
        print(error_trace)
        sys.stderr.write(f"ERROR: {error_msg}\n{error_trace}\n")
        
        # Return error response
        error_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Server Error</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>Server Error (500)</h1>
    <p>An error occurred while processing your request.</p>
    <details>
        <summary>Error Details</summary>
        <pre>{error_msg}</pre>
    </details>
</body>
</html>"""
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html; charset=utf-8'
            },
            'body': error_html
        }
