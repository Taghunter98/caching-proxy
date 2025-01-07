import socket
from urllib.request import Request, urlopen, HTTPError
import os
import argparse

CACHE_DIR = "cache"

def main():
    # Get CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, required=True, help="Port for the proxy server to listen on.")
    parser.add_argument('--origin', type=str, required=True, help="Origin server URL to proxy requests to.")
    args = parser.parse_args()
    
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
    
    print(f"Cache proxy is listening on port {server_port}, forwarding to {origin_url}...")
    
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
        print("Fetched successfully from cache.")
        return file_from_cache
    
    print("Not in cache. Fetching from server.")
    file_from_server = fetch_from_server(origin_url + path)
    if file_from_server:
        save_in_cache(path, file_from_server)
        return file_from_server
    return None

def fetch_from_cache(path):
    try:
        with open(os.path.join(CACHE_DIR, path.strip('/')), 'r') as cached_file:
            return cached_file.read()
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

# Call main function
if __name__ == "__main__":
    main()