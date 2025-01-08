import socket
from urllib.request import Request, urlopen, HTTPError
import os
import argparse

CACHE_DIR = "Cache-X"

def main():
    # Get CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, help="Port for the proxy server to listen on.")
    parser.add_argument('--origin', type=str, help="Origin server URL to proxy requests to.")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the cahce files.")
    args = parser.parse_args()
    
     # Check for clear cache
    if args.clear_cache:
        clear_cache()
        return
    
    # Validate args for server setup
    if not args.port or not args.origin:
        print_help()
        return
    
    server_host = '0.0.0.0'
    server_port = args.port
    origin_url = args.origin
    
    # Create cache directory if it doesn't exist
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Set up socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)
    
    print(f"\r\nCache proxy is listening on port {server_port}, forwarding to {origin_url}...")
    
    # Set up caching proxy server
    while True:
        client_connection, client_address = server_socket.accept()
        handle_client(client_connection, origin_url)

def handle_client(client_connection, origin_url):
    try:
        # Receive client request
        request = client_connection.recv(1024).decode()
        if not request:
            client_connection.close()
            return
        
        headers = request.split('\r\n')
        top_header = headers[0].split()
        method, path = top_header[0], top_header[1]
        
        if method != "GET":
            client_connection.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            client_connection.close()
            return

        # Fetch content (from cache or server)
        content = fetch_file(path, origin_url)
        
        if content:
            response = f"HTTP/1.1 200 OK\r\n\r\n{content}"
        else:
            response = "HTTP/1.1 404 NOT FOUND\r\n\r\nFile Not Found"
        
        client_connection.sendall(response.encode())
    except Exception as e:
        print(f"Error handling client request: {e}")
        client_connection.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
    finally:
        client_connection.close()

def fetch_file(path, origin_url):
    # Try to find file in cache
    file_from_cache = fetch_from_cache(path)
    if file_from_cache:
        print(f"\r\n{CACHE_DIR}: HIT")
        return file_from_cache
    
    print(f"\r\n{CACHE_DIR}: MISS")
    file_from_server = fetch_from_server(origin_url + path)
    if file_from_server:
        save_in_cache(path, file_from_server)
        return file_from_server
    return None

def fetch_from_cache(path):
    try:
        # Look for file path 
        with open(os.path.join(CACHE_DIR, path.strip('/')), 'r') as cached_file:
            return cached_file.read() # Read and return file
    except FileNotFoundError:
        return None

def fetch_from_server(url):
    try:
        q = Request(url)
        response = urlopen(q)
        return response.read().decode('utf-8')
    except HTTPError as e:
        print(f"HTTPError fetching {url}: {e}")
        return None

def save_in_cache(path, content):
    try:
        cache_path = os.path.join(CACHE_DIR, path.strip('/'))
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w') as cached_file:
            cached_file.write(content)
        print(f"Saved {path} to cache.")
    except Exception as e:
        print(f"Error saving to cache: {e}")

def clear_cache():
    dir = "./Cache-X"
    
    # Check if path exists
    if not os.path.exists(dir):
        print(f"\r\nCache directory '{dir}' does not exist.")
        return
    
    # Iterate through files
    for file in os.listdir(dir):
        path = os.path.join(dir, file) # Join dir and file
        try:
            if os.path.isfile(path):
                os.remove(path) # Remove file
                print(f"\r\nDeleted file {path}")
        except Exception as e:
            print(f"Error deleting file {path}: {e}")
    
    print("Cache cleared successfully.")

def print_help():
    help_message = """
    Caching Proxy Server - A simple caching proxy for HTTP requests.

    Usage:
      Run the proxy server:
        python caching_proxy.py --port <PORT> --origin <ORIGIN_URL>
          --port <PORT>:       Port for the proxy server to listen on.
          --origin <ORIGIN_URL>: Origin server URL to forward requests to.

      Clear the cache:
        python caching_proxy.py --clear-cache
          --clear-cache:       Clears all cached files in the cache directory.

    Examples:
      Start the proxy server on port 8080 and forward requests to http://example.com:
        python caching_proxy.py --port 8080 --origin http://example.com

      Clear the cache:
        python caching_proxy.py --clear-cache

    Notes:
      - The `--port` and `--origin` arguments are required when starting the server.
      - The `--clear-cache` argument is a standalone operation and does not require `--port` or `--origin`.

    For additional information, see the documentation or contact the developer.
    """
    print(help_message)

# Call main function
if __name__ == "__main__":
    main()